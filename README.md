# thiserror

A declarative error-variant library for Python 3.12+, inspired by Rust's
[thiserror](https://docs.rs/thiserror).

Install a checkout with

```shell
python -m pip install .
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
    Redaction = Variant.for_schema(str).message(lambda payload: f"the data for key `{payload}` is not available")
    InvalidHeader = Variant.for_schema(InvalidHeaderFields).message(
        lambda payload: f"invalid header (expected {payload.expected}, found {payload.found})"
    )
    Unknown = Variant((), "unknown data store error")


raise DataStoreError.Disconnected(OSError("disk offline"))
```

A member call creates a fresh `TypedVariant` exception. Payload-bearing variants
take one value; use a dataclass when an error needs several named fields. The
empty tuple `()` declares a unit variant.

Use `Variant.for_schema(...).message(...)` for schema-typed callables. The
configured `ty` and `zuban` checkers infer the lambda parameter and reject unknown
payload attributes. This form passes the schema payload to the callable. Static
strings can use the direct constructor; the legacy direct callable form remains
available with wrapper and one-slot indexing semantics, but its lambda parameter
is dynamically typed.

The wrapper delegates unknown attributes to the payload, and index `0` returns the
full payload.
Each callback is probed once at declaration. Simple access-only callbacks are
rendered from the resulting template. Other callbacks run again when an error
message is rendered, so keep their declaration-time probe side-effect free.

For a typed construction path with `ty` and `zuban`, call the enum member's
`Variant` value:

```python
fields = InvalidHeaderFields(expected="content-type", found="x-type")
error: TypedVariant[InvalidHeaderFields] = DataStoreError.InvalidHeader.value(fields)
assert error.value.expected == "content-type"
```

The convenient `DataStoreError.InvalidHeader(fields)` syntax is also supported,
but Python's enum typing model leaves that call dynamically typed.

## Handling errors

Raised variants derive from `Exception`, so ordinary exception handlers catch
them. Enum value patterns dispatch by variant at runtime:

```python
from typing import Any

try:
    raise DataStoreError.Disconnected(OSError("disk offline"))
except Exception as error:
    variant_error: Any = error
    match variant_error:
        case DataStoreError.Disconnected:
            print(error)
        case DataStoreError.Unknown:
            print(error)
```

When the payload is an exception, it becomes `__cause__`; its existing traceback
is retained. Static string templates use `str.format` syntax, including
positional `{0}` and named `{field}` fields. Named fields are read from dataclass
fields or an object's `__dict__`.

## Typing and Python compatibility

The package uses inline annotations and ships a `py.typed` marker. Its minimum
runtime is Python 3.12, which supports the generic syntax used by the library.

The Enum-based declaration and Python's type system leave two limits:

- An error enum class is not itself an exception class, so catch raised variants
  with `except Exception`, then dispatch with `match`; `except DataStoreError` is
  not supported.
- A value-pattern match does not statically narrow the subject to one variant.
  Use a typed `TypedVariant[T]` returned from `Variant.__call__`; the enum
  member's `.value(payload)` calls that typed path.

Payload values are not checked against their schema at runtime. A schema describes
the static payload type and callable-message type; it is not a runtime validator.
