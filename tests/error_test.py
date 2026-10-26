import pickle
import traceback
from dataclasses import InitVar, dataclass
from enum import Enum
from typing import Any, assert_type

import pytest

from thiserror import Error, TypedVariant, Variant, VariantSpec


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


# Where Error and Variant are provided by the package.
class DataStoreError(Error):
    # Static variants safely ingest explicit strings directly
    Disconnect = Variant(OSError, "data store disconnected")
    Redaction = Variant(str, lambda payload: f"the data for key `{payload}` is not available")
    InvalidHeader = Variant(
        InvalidHeaderFields,
        lambda payload: f"invalid header (expected {payload.expected}, found {payload.found})",
    )
    Unknown = Variant((), "unknown data store error")


class InvalidVariantError(Error):
    NotVariant = "not a variant"


_SHARED_VARIANT = Variant(str, "shared value: {0}")


class SharedFirstError(Error):
    Value = _SHARED_VARIANT


class SharedSecondError(Error):
    Value = _SHARED_VARIANT


def _call_error_member(member: Error, *args: Any) -> Any:
    return member(*args)


def _hash_runtime(value: Any) -> int:
    return hash(value)


def test_static_message_and_str():
    err = DataStoreError.Disconnect(OSError())
    assert str(err) == "data store disconnected"
    assert str(DataStoreError.Unknown()) == "unknown data store error"
    assert repr(DataStoreError.Unknown()) == "TypedVariant('unknown data store error')"
    # The member's stored value IS the Variant declared in the class body,
    # carried natively as an enum member value (no coercion).
    assert isinstance(DataStoreError.Disconnect.value, VariantSpec)
    assert DataStoreError.Disconnect.value.schema is OSError


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
    with pytest.raises(IndexError):
        _ = err[1]
    with pytest.raises(IndexError):
        _ = DataStoreError.Unknown()[0]


def test_lambda_message_dataclass_attributes():
    fields = InvalidHeaderFields(expected="a", found="b")
    err = DataStoreError.InvalidHeader(fields)
    typed_member_err: TypedVariant[InvalidHeaderFields] = DataStoreError.InvalidHeader.value(fields)
    assert_type(typed_member_err, TypedVariant[InvalidHeaderFields])
    assert_type(typed_member_err.value, InvalidHeaderFields)
    typed_match = False
    typed_subject: object = err
    match typed_subject:
        case DataStoreError.InvalidHeader:
            typed_match = True
    assert typed_match
    assert str(err) == "invalid header (expected a, found b)"
    assert err.expected == "a"
    assert err.found == "b"
    assert err.value is fields


def test_direct_variant_constructor_passes_schema_payload():
    variant = Variant(
        ValueFieldPayload,
        lambda payload: payload.value,
    )
    error = variant(ValueFieldPayload(value="payload field"))

    assert str(error) == "payload field"


def test_direct_variant_constructor_renders_builtin_payload():
    variant = Variant(str, lambda payload: f"redacted: {payload}")
    error = variant("secret")

    assert str(error) == "redacted: secret"


def test_direct_callable_evaluates_payload_dependent_branches_at_render_time():
    variant = Variant(
        type(None),
        lambda payload: "no payload" if payload is None else f"payload: {payload}",
    )

    assert str(variant(None)) == "no payload"


def test_schema_typed_callable_uses_payload_indexing():
    variant = Variant(str, lambda payload: payload[1])
    error = variant("key")

    assert str(error) == "e"


def test_callable_runs_only_when_the_error_is_rendered():
    evaluations: list[str] = []

    def render(payload: str) -> str:
        evaluations.append("called")
        return f"value: {payload}"

    variant = Variant(str, render)
    assert evaluations == []

    error = variant("key")

    assert str(error) == "value: key"
    assert evaluations == ["called"]
    assert str(error) == "value: key"
    assert evaluations == ["called", "called"]


def test_match_dispatches_by_variant():
    orig = OSError("disk offline")
    errors = (DataStoreError.Disconnect(orig), DataStoreError.Unknown())
    matched_arms: list[str] = []
    payload = None
    for err in errors:
        match err:
            case DataStoreError.Disconnect:
                matched_arms.append("Disconnect")
                payload = err.value
            case DataStoreError.Unknown:
                matched_arms.append("Unknown")

    assert matched_arms == ["Disconnect", "Unknown"]
    assert payload is orig


def test_equal_variant_errors_do_not_expose_inconsistent_hashes():
    first = DataStoreError.Redaction("same")
    second = DataStoreError.Redaction("same")

    assert first == second
    assert first != DataStoreError.Redaction("different")
    assert first != object()
    with pytest.raises(TypeError):
        _hash_runtime(first)


def test_error_enum_rejects_non_variant_members():
    with pytest.raises(TypeError, match="NotVariant is not a Variant"):
        _call_error_member(InvalidVariantError.NotVariant)


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


def test_typed_member_values_keep_enum_match_identity_after_pickle():
    original = DataStoreError.Disconnect.value(OSError("disk offline"))
    restored = pickle.loads(pickle.dumps(original))

    assert isinstance(restored.value, OSError)
    assert str(restored.value) == "disk offline"
    assert str(restored) == "data store disconnected"

    matched = False
    match restored:
        case DataStoreError.Disconnect:
            matched = True

    assert matched


def test_callable_typed_member_values_round_trip_through_pickle():
    original = DataStoreError.Redaction.value("typed-key")
    restored = pickle.loads(pickle.dumps(original))

    assert restored.value == "typed-key"
    assert str(restored) == "the data for key `typed-key` is not available"

    matched = False
    match restored:
        case DataStoreError.Redaction:
            matched = True

    assert matched


def test_typed_values_with_shared_specs_keep_shared_match_identity_after_pickle():
    original = SharedSecondError.Value.value("payload")
    restored = pickle.loads(pickle.dumps(original))

    assert restored == SharedFirstError.Value
    assert restored == SharedSecondError.Value


def test_standalone_variants_round_trip_through_pickle():
    value_spec = Variant(str, "value: {0}")
    unit_spec = Variant((), "empty")

    restored_value = pickle.loads(pickle.dumps(value_spec("payload")))
    restored_unit = pickle.loads(pickle.dumps(unit_spec()))

    assert str(restored_value) == "value: payload"
    assert str(restored_unit) == "empty"


def test_pickle_restore_rejects_invalid_state():
    variant = Variant(str, "value: {0}")
    invalid_owner = TypedVariant(variant, "payload", False, "not an enum")
    invalid_enum_member = TypedVariant(variant, "payload", False, InvalidVariantError.NotVariant)

    with pytest.raises(TypeError, match="owner must be an enum member"):
        pickle.loads(pickle.dumps(invalid_owner))
    with pytest.raises(TypeError, match="not backed by a Variant"):
        pickle.loads(pickle.dumps(invalid_enum_member))


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
    header_message = FormatStoreError.Header.value.message
    assert isinstance(header_message, str)
    assert header_message.endswith("{found})")


def test_named_templates_read_fields_from_slotted_dataclasses():
    error = SlottedError.Header(SlottedHeaderFields(code="E42"))

    assert str(error) == "invalid header E42"


def test_named_templates_skip_dataclass_init_only_values():
    payload = InitVarFields(name="value", temporary="ignored")
    error = InitVarError.Payload(payload)

    assert str(error) == "invalid payload value:ignored"


def test_callable_methods_use_the_actual_payload_on_each_render():
    evaluations: list[str] = []

    def shout(payload: str) -> str:
        evaluations.append("called")
        return f"{payload.upper()}!"

    shout_message = Variant(str, shout)
    error = shout_message("k9")
    assert evaluations == []

    assert str(error) == "K9!"
    assert evaluations == ["called"]
    assert str(error) == "K9!"
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
