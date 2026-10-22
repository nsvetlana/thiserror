import pickle
import traceback
from dataclasses import InitVar, dataclass
from enum import Enum
from typing import Any, assert_type

import pytest

from thiserror import Error, TypedVariant, Variant


@dataclass(frozen=True)
class InvalidHeaderFields:
    expected: str
    found: str


@dataclass(frozen=True, slots=True)
class SlottedHeaderFields:
    code: str


@dataclass
class InitVarFields:
    name: str
    temporary: InitVar[str]

    def __post_init__(self, temporary: str) -> None:
        self.name = f"{self.name}:{temporary}"


@dataclass(frozen=True)
class ValueFieldPayload:
    value: str


INVALID_HEADER_VARIANT = Variant.for_schema(InvalidHeaderFields).message(
    lambda self: f"invalid header (expected {assert_type(self.expected, str)}, found {self.found})"
)


# Where Error and Variant are provided by the package.
class DataStoreError(Error):
    # Static variants safely ingest explicit strings directly
    Disconnect = Variant(OSError, "data store disconnected")
    # The direct callable form retains its one-slot wrapper semantics.
    Redaction = Variant(str, lambda self: f"the data for key `{self[0]}` is not available")
    # IDE fully autocompletes '.expected' and '.found' here because self is inferred as InvalidHeaderFields
    InvalidHeader = INVALID_HEADER_VARIANT
    Unknown = Variant((), "unknown data store error")


def _call_error_member(member: Error, *args: Any) -> Any:
    return member(*args)


def _hash_runtime(value: Any) -> int:
    return hash(value)


def test_static_message_and_str():
    err = DataStoreError.Disconnect(OSError())
    assert str(err) == "data store disconnected"
    assert str(DataStoreError.Unknown()) == "unknown data store error"
    # The member's stored value IS the Variant declared in the class body,
    # carried natively as an enum member value (no coercion).
    assert isinstance(DataStoreError.Disconnect.value, Variant)
    assert DataStoreError.Disconnect.value.schema is OSError


def test_console_entry_point_describes_the_library(capsys: pytest.CaptureFixture[str]):
    import thiserror

    thiserror.main([])

    output = capsys.readouterr().out
    assert "thiserror" in output
    assert "library" in output


def test_raised_variants_follow_normal_exception_handling():
    error = DataStoreError.Redaction("key")
    with pytest.raises(Exception) as caught:
        raise error
    assert caught.value is error


def test_lambda_message_sequence_access():
    err = DataStoreError.Redaction("k9")
    assert str(err) == "the data for key `k9` is not available"
    assert err[0] == "k9"
    assert len(err) == 1
    assert err.value == "k9"


def test_lambda_message_dataclass_attributes():
    fields = InvalidHeaderFields(expected="a", found="b")
    err = DataStoreError.InvalidHeader(fields)
    typed_member_err: TypedVariant[InvalidHeaderFields] = DataStoreError.InvalidHeader.value(fields)
    assert_type(typed_member_err.value, InvalidHeaderFields)
    typed_err = INVALID_HEADER_VARIANT(fields)
    assert_type(typed_err, TypedVariant[InvalidHeaderFields])
    assert_type(typed_err.value, InvalidHeaderFields)
    typed_match = False
    typed_subject: Any = typed_err
    match typed_subject:
        case DataStoreError.InvalidHeader:
            typed_match = True
            assert_type(typed_err.value, InvalidHeaderFields)
    assert typed_match
    assert str(err) == "invalid header (expected a, found b)"
    assert err.expected == "a"
    assert err.found == "b"
    assert err.value is fields


def test_schema_typed_callable_receives_payload_without_wrapper_collisions():
    variant = Variant.for_schema(ValueFieldPayload).message(lambda payload: assert_type(payload.value, str))
    error = variant(ValueFieldPayload(value="payload field"))

    assert str(error) == "payload field"


def test_schema_typed_callable_uses_payload_indexing():
    variant = Variant.for_schema(str).message(lambda payload: assert_type(payload, str)[1])
    error = variant("key")

    assert str(error) == "e"


def test_simple_callable_is_probed_once_then_rendered_as_a_template():
    evaluations: list[str] = []

    def render(payload: str) -> str:
        evaluations.append("called")
        return f"value: {payload}"

    variant = Variant.for_schema(str).message(render)
    assert evaluations == ["called"]

    error = variant("key")

    assert str(error) == "value: key"
    assert evaluations == ["called"]


def test_legacy_callable_uses_wrapper_slots_and_caches_pure_messages():
    evaluations: list[str] = []

    def render(wrapper: Any) -> str:
        evaluations.append("called")
        return f"value: {wrapper[0]}"

    variant = Variant(str, render)
    assert evaluations == ["called"]
    assert str(variant("key")) == "value: key"
    assert evaluations == ["called"]

    live_variant = Variant(str, lambda wrapper: f"{wrapper[0].upper()}!")
    assert str(live_variant("k9")) == "K9!"


def test_match_dispatches_by_variant():
    orig = OSError("disk offline")
    err = DataStoreError.Disconnect(orig)

    arm = None
    payload = None
    match err:
        case DataStoreError.Disconnect:
            arm = "Disconnect"
            payload = err.value
        case DataStoreError.Unknown:
            arm = "Unknown"

    assert arm == "Disconnect"
    assert payload is orig

    unknown_hit = False
    match DataStoreError.Unknown():
        case DataStoreError.Unknown:
            unknown_hit = True

    assert unknown_hit


def test_equal_variant_errors_do_not_expose_inconsistent_hashes():
    first = DataStoreError.Redaction("same")
    second = DataStoreError.Redaction("same")

    assert first == second
    with pytest.raises(TypeError):
        _hash_runtime(first)


def test_pickled_variants_keep_their_enum_match_identity():
    assert pickle.loads(pickle.dumps(DataStoreError.Redaction)) is DataStoreError.Redaction
    payload_error = pickle.loads(pickle.dumps(DataStoreError.Redaction("key")))
    unit_error = pickle.loads(pickle.dumps(DataStoreError.Unknown()))

    payload_matched = False
    match payload_error:
        case DataStoreError.Redaction:
            payload_matched = True

    unit_matched = False
    match unit_error:
        case DataStoreError.Unknown:
            unit_matched = True

    assert payload_matched
    assert unit_matched
    assert str(payload_error) == "the data for key `key` is not available"
    assert str(unit_error) == "unknown data store error"


def test_traceback_preserved_via_cause():
    orig = OSError("disk offline")
    try:
        raise orig
    except OSError:
        original_traceback = orig.__traceback__

    with pytest.raises(Exception) as caught:
        raise DataStoreError.Disconnect(orig)

    caught_error = caught.value
    assert caught_error.__cause__ is orig
    assert orig.__traceback__ is original_traceback
    formatted = "".join(traceback.format_exception(caught_error))
    assert "data store disconnected" in formatted
    assert "disk offline" in formatted


def test_enum_nature_and_order():
    assert issubclass(DataStoreError, Enum)
    assert list(DataStoreError) == [
        DataStoreError.Disconnect,
        DataStoreError.Redaction,
        DataStoreError.InvalidHeader,
        DataStoreError.Unknown,
    ]


def test_unit_schema_rejects_arguments():
    with pytest.raises(TypeError):
        _call_error_member(DataStoreError.Unknown, 1)


def test_value_schema_arity_enforced():
    with pytest.raises(TypeError):
        _call_error_member(DataStoreError.Redaction, "a", "b")


def test_messages_keep_their_declared_string_or_callable_form():
    disconnect_message = DataStoreError.Disconnect.value.message
    assert isinstance(disconnect_message, str)
    assert disconnect_message == "data store disconnected"
    assert callable(DataStoreError.Redaction.value.message)


class FormatStoreError(Error):
    Disconnected = Variant(OSError, "data store disconnected")
    Key = Variant(str, "the data for key `{0}` is not available")
    Header = Variant(
        InvalidHeaderFields,
        "invalid header (expected {expected}, found {found})",
    )
    Unit = Variant((), "unit variant engaged")


class DuplicateMessageError(Error):
    First = Variant(str, "same message")
    Second = Variant(str, "same message")


class NullableError(Error):
    NoValue = Variant(type(None), "the payload is None")


class SlottedError(Error):
    Header = Variant(SlottedHeaderFields, "invalid header {code}")


class InitVarError(Error):
    Payload = Variant(InitVarFields, "invalid payload {name}")


def test_identical_variant_values_remain_distinct_enum_members():
    assert DuplicateMessageError.First is not DuplicateMessageError.Second
    assert list(DuplicateMessageError) == [
        DuplicateMessageError.First,
        DuplicateMessageError.Second,
    ]


def test_repr_keeps_none_payload_separate_from_unit_variants():
    error = NullableError.NoValue(None)

    assert repr(error).endswith(", None)")


def test_format_string_templates_render_from_payload():
    assert str(FormatStoreError.Key("k9")) == "the data for key `k9` is not available"
    assert (
        str(FormatStoreError.Header(InvalidHeaderFields(expected="a", found="b")))
        == "invalid header (expected a, found b)"
    )
    assert str(FormatStoreError.Disconnected(OSError())) == "data store disconnected"
    assert str(FormatStoreError.Unit()) == "unit variant engaged"
    err = FormatStoreError.Key("k9")
    assert err[0] == "k9"
    assert len(err) == 1
    assert FormatStoreError.Header.value.template.endswith("{found})")


def test_named_templates_read_fields_from_slotted_dataclasses():
    error = SlottedError.Header(SlottedHeaderFields(code="E42"))

    assert str(error) == "invalid header E42"


def test_named_templates_skip_dataclass_init_only_values():
    payload = InitVarFields(name="value", temporary="ignored")
    error = InitVarError.Payload(payload)

    assert str(error) == "invalid payload value:ignored"


def test_live_fallback_when_lambda_not_statically_expressible():
    shout_template = Variant.for_schema(str).message(lambda payload: f"{payload.upper()}!")
    assert str(shout_template("k9")) == "K9!"


def test_live_fallback_keeps_the_probe_and_per_render_evaluations():
    evaluations: list[str] = []

    def shout(payload: str) -> str:
        evaluations.append("called")
        return f"{payload.upper()}!"

    shout_template = Variant.for_schema(str).message(shout)
    assert evaluations == ["called"]

    assert str(shout_template("k9")) == "K9!"
    assert evaluations == ["called", "called"]


def test_format_templates_still_raise_match_and_chain():
    orig = OSError("disk offline")
    try:
        raise FormatStoreError.Disconnected(orig)
    except Exception as exc:  # noqa: BLE001
        caught = exc
    assert caught.__cause__ is orig
    # Value patterns are a runtime mechanism; the checker cannot narrow a
    # BaseException subject against enum members, so keep it dynamically typed.
    subject: Any = caught
    matched = False
    payload = None
    match subject:
        case FormatStoreError.Disconnected:
            matched = True
            payload = subject.value
    assert matched
    assert payload is orig
