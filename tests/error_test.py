import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Any

import pytest

from thiserror import Error, Variant


@dataclass(frozen=True)
class InvalidHeaderFields:
    expected: str
    found: str


# Where Error and Variant are provided by the package.
class DataStoreError(Error):
    # Static variants safely ingest explicit strings directly
    Disconnect = Variant(OSError, "data store disconnected")
    # Lambda provides standard list to formatting context via self[0]
    Redaction = Variant(str, lambda self: f"the data for key `{self[0]}` is not available")
    # IDE fully autocompletes '.expected' and '.found' here because self is inferred as InvalidHeaderFields
    InvalidHeader = Variant(
        InvalidHeaderFields,
        lambda self: f"invalid header (expected {self.expected}, found {self.found})",
    )
    Unknown = Variant((), "unknown data store error")


def test_static_message_and_str():
    err = DataStoreError.Disconnect(OSError())
    assert str(err) == "data store disconnected"
    assert str(DataStoreError.Unknown()) == "unknown data store error"
    # The member's stored value IS the Variant declared in the class body,
    # carried natively as an enum member value (no coercion).
    assert isinstance(DataStoreError.Disconnect.value, Variant)
    assert DataStoreError.Disconnect.value.schema is OSError


def test_lambda_message_sequence_access():
    err = DataStoreError.Redaction("k9")
    assert str(err) == "the data for key `k9` is not available"
    assert err[0] == "k9"
    assert len(err) == 1
    assert err.value == "k9"


def test_lambda_message_dataclass_attributes():
    fields = InvalidHeaderFields(expected="a", found="b")
    err = DataStoreError.InvalidHeader(fields)
    assert str(err) == "invalid header (expected a, found b)"
    assert err.expected == "a"
    assert err.found == "b"
    assert err.value is fields


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


def test_traceback_preserved_via_cause():
    orig = OSError("disk offline")
    try:
        raise DataStoreError.Disconnect(orig)
    # Raised variants are BaseException subclasses by contract; catching Exception
    # would defeat the dispatch guarantee under test.
    except BaseException as exc:  # noqa: BLE001
        caught = exc

    assert caught.__cause__ is orig
    formatted = "".join(traceback.format_exception(caught))
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
        DataStoreError.Unknown(1)


def test_value_schema_arity_enforced():
    with pytest.raises(TypeError):
        DataStoreError.Redaction("a", "b")


def test_messages_stored_verbatim_without_declaration_execution():
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


def test_format_string_templates_render_from_payload():
    assert str(FormatStoreError.Key("k9")) == "the data for key `k9` is not available"
    assert str(
        FormatStoreError.Header(InvalidHeaderFields(expected="a", found="b"))
    ) == "invalid header (expected a, found b)"
    assert str(FormatStoreError.Disconnected(OSError())) == "data store disconnected"
    assert str(FormatStoreError.Unit()) == "unit variant engaged"
    err = FormatStoreError.Key("k9")
    assert err[0] == "k9"
    assert len(err) == 1
    assert FormatStoreError.Header.value.template.endswith("{found})")


def test_live_fallback_when_lambda_not_statically_expressible():
    shout_template = Variant(str, lambda self: f"{self[0].upper()}!")
    assert str(shout_template("k9")) == "K9!"


def test_format_templates_still_raise_match_and_chain():
    orig = OSError("disk offline")
    try:
        raise FormatStoreError.Disconnected(orig)
    except BaseException as exc:  # noqa: BLE001 - raised variants are BaseException by contract
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
