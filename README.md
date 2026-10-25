# thiserror

Declare typed error variants and messages for Python 3.12 and newer. Inspired by Rust's [thiserror](https://docs.rs/thiserror).

## Install

Install it with `pip`:

```shell
pip install thiserror
```

Or add it to a `uv`-managed project:

```shell
uv add thiserror
```

## Quick start

```python
from dataclasses import dataclass

from thiserror import Error, TypedVariant, Variant


@dataclass(frozen=True, slots=True)
class InvalidHeaderFields:
    expected: str
    found: str


class DataStoreError(Error):
    Disconnected = Variant(OSError, "data store disconnected")
    Redaction = Variant(str, lambda payload: f"the data for key `{payload}` is not available")
    InvalidHeader = Variant(
        InvalidHeaderFields,
        lambda payload: f"invalid header (expected {payload.expected}, found {payload.found})",
    )
    Unknown = Variant((), "unknown data store error")


fields = InvalidHeaderFields(expected="content-type", found="x-type")
header_error = DataStoreError.InvalidHeader.value(fields)
print(header_error)

try:
    raise DataStoreError.Disconnected(OSError("disk offline"))
except TypedVariant as error:
    match error:
        case DataStoreError.Disconnected:
            print(error)
        case DataStoreError.Unknown:
            print(error)
```

Output: the invalid-header message, then `data store disconnected`.

## Handling errors

Calling a variant creates a `TypedVariant` exception. Catch it with
`except TypedVariant` or `except Exception`; the `Error` declaration itself is
not an exception class. Dotted `match` cases dispatch variants at runtime, but
Python does not check that every case is handled or narrow each case to its
payload type as Rust does.

## Messages and payloads

A payload variant takes one value; `Variant((), message)` declares a unit
variant. String messages use `str.format`. A callable message receives the
payload when the error is rendered; a unit variant callback receives the error.
Schemas provide type hints, not runtime validation. The package ships inline
type annotations and `py.typed`.

For API details, see the [source docstrings](src/thiserror/error.py).
