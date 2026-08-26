import traceback
from dataclasses import dataclass
from enum import Enum

import pytest

from thiserror import Error, Variant


@dataclass(frozen=True)
class InvalidHeaderFields:
    expected: str
    found: str


# Where Error and Variant are provided by the package.
class DataStoreError(Error):
    # Static variants safely ingest explicit strings directly
    Disconnect = Variant(IOError, "data store disconnected")
    # Lambda provides standard list to formatting context via self[0]
    Redaction = Variant(str, lambda self: f"the data for key `{self[0]}` is not available")
    # IDE fully autocompletes '.expected' and '.found' here because self is inferred as InvalidHeaderFields
    InvalidHeader = Variant(
        InvalidHeaderFields,
        lambda self: f"invalid header (expected {self.expected}, found {self.found})",
    )
    Unknown = Variant((), "unknown data store error")


def test_static_message_and_str():
    err = DataStoreError.Disconnect(IOError())
    assert str(err) == "data store disconnected"
    assert str(DataStoreError.Unknown()) == "unknown data store error"
    # The member's stored value IS the Variant declared in the class body,
    # carried natively as an enum member value (no coercion).
    assert isinstance(DataStoreError.Disconnect.value, Variant)
    assert DataStoreError.Disconnect.value.schema is IOError


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
    orig = IOError("disk offline")
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
    orig = IOError("disk offline")
    try:
        raise DataStoreError.Disconnect(orig)
    except BaseException as exc:
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
    assert DataStoreError.Disconnect.value.message == "data store disconnected"
    assert callable(DataStoreError.Redaction.value.message)
