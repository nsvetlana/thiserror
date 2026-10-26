"""Smoke-test the documented public API from an installed distribution."""

from collections.abc import Callable
from dataclasses import dataclass
from types import SimpleNamespace

from thiserror import Error, TypedVariant, Variant


@dataclass(frozen=True, slots=True)
class InvalidHeaderFields:
    expected: str
    found: str


message_calls: list[str] = []


def deferred_message(payload: str) -> str:
    message_calls.append(payload)
    return f"deferred: {payload}"


class DataStoreError(Error):
    Disconnect = Variant(OSError, "data store disconnected")
    Redaction = Variant(str, lambda payload: f"the data for key `{payload}` is not available")
    InvalidHeader = Variant(
        InvalidHeaderFields,
        lambda payload: f"invalid header (expected {payload.expected}, found {payload.found})",
    )
    Deferred = Variant(str, deferred_message)
    Unknown = Variant((), "unknown data store error")


class LookupIssue(Error):
    Missing = Variant(str, "key {0!r} not found")
    InvalidStatus = Variant(int, lambda status: f"invalid status: {status}")
    Empty = Variant((), "no results available")
    IoFailure = Variant(OSError, "I/O error: {0}")
    NamedHeader = Variant(InvalidHeaderFields, "invalid header (expected {expected}, found {found})")
    ObjectHeader = Variant(SimpleNamespace, "invalid header (expected {expected}, found {found})")
    UnitCallback = Variant((), lambda error: f"unit callback: {error.value}")


def expect_type_error(call: Callable[..., object], *args: object) -> None:
    try:
        call(*args)
    except TypeError:
        return
    raise AssertionError("expected TypeError")


def raise_and_match_lookup(error: TypedVariant) -> str:
    try:
        raise error
    except TypedVariant as caught:
        match caught:
            case LookupIssue.Missing:
                return str(caught)
            case LookupIssue.Empty:
                return "Nothing to return"
            case _:
                raise


def raise_and_match_data_store(error: TypedVariant) -> str:
    try:
        raise error
    except TypedVariant as caught:
        match caught:
            case DataStoreError.Disconnect:
                return str(caught)
            case DataStoreError.Unknown:
                return str(caught)
            case _:
                raise


def raise_and_catch_exception(error: TypedVariant) -> Exception:
    try:
        raise error
    except Exception as caught:  # noqa: BLE001 - smoke-test the documented Exception catch
        return caught


assert not issubclass(DataStoreError, Exception)
assert issubclass(TypedVariant, Exception)

assert str(LookupIssue.Missing("account")) == "key 'account' not found"
assert str(LookupIssue.InvalidStatus(503)) == "invalid status: 503"
assert str(LookupIssue.Empty()) == "no results available"
assert str(LookupIssue.IoFailure(OSError("disk offline"))) == "I/O error: disk offline"

header_fields = InvalidHeaderFields(expected="content-type", found="x-type")
header_error = DataStoreError.InvalidHeader(header_fields)
assert str(header_error) == "invalid header (expected content-type, found x-type)"
assert header_error.expected == "content-type"
assert LookupIssue.Missing("account").value == "account"
assert str(LookupIssue.NamedHeader(header_fields)) == "invalid header (expected content-type, found x-type)"
assert (
    str(LookupIssue.ObjectHeader(SimpleNamespace(expected="content-type", found="x-type")))
    == "invalid header (expected content-type, found x-type)"
)

assert str(DataStoreError.Redaction("k9")) == "the data for key `k9` is not available"
assert str(LookupIssue.UnitCallback()) == "unit callback: None"

deferred_error = DataStoreError.Deferred("render later")
assert message_calls == []
assert str(deferred_error) == "deferred: render later"
assert message_calls == ["render later"]

original = OSError("disk offline")
disconnect_error = DataStoreError.Disconnect(original)
assert disconnect_error.__cause__ is original
assert raise_and_catch_exception(disconnect_error) is disconnect_error

assert raise_and_match_lookup(LookupIssue.Missing("account")) == "key 'account' not found"
assert raise_and_match_lookup(LookupIssue.Empty()) == "Nothing to return"
assert raise_and_match_data_store(disconnect_error) == "data store disconnected"
assert raise_and_match_data_store(DataStoreError.Unknown()) == "unknown data store error"

expect_type_error(LookupIssue.Missing)
expect_type_error(LookupIssue.Missing, "one", "two")
expect_type_error(LookupIssue.Empty, "unexpected")

# Schemas provide type information but do not validate payloads at runtime.
unvalidated_payload = LookupIssue.Missing(503)
assert unvalidated_payload.value == 503
assert str(unvalidated_payload) == "key 503 not found"
