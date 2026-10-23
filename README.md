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
    Redaction = Variant(str, lambda payload: f"the data for key `{payload}` is not available")
    InvalidHeader = Variant(
        InvalidHeaderFields,
        lambda payload: f"invalid header (expected {payload.expected}, found {payload.found})",
    )
    Unknown = Variant((), "unknown data store error")


# Equivalent direct declaration, kept as a side-by-side syntax example.
class DataStoreErrorAlt(Error):
    Disconnected = Variant(OSError, "data store disconnected")
    Redaction = Variant(str, lambda payload: f"the data for key `{payload}` is not available")
    InvalidHeader = Variant(
        InvalidHeaderFields,
        lambda payload: f"invalid header (expected {payload.expected}, found {payload.found})",
    )
    Unknown = Variant((), "unknown data store error")


raise DataStoreError.Disconnected(OSError("disk offline"))
```

A member call creates a fresh `TypedVariant` exception. Payload-bearing variants
take one value; use a dataclass when an error needs several named fields. The
empty tuple `()` declares a unit variant.

Callable messages receive the schema payload directly. The `ty` and `zuban`
checkers infer the lambda parameter for built-in schemas such as `str` and
user-defined schemas such as dataclasses. `Variant` is a generic factory and
returns a `VariantSpec[PayloadT]`; the spec is the enum member's stored value.
The earlier schema-first builder is replaced by this call form, and callback
parameters now refer to the payload instead of the raised wrapper.

The wrapper delegates unknown attributes to the payload, and index `0` returns the
full payload.
Callable messages run when the error is rendered and receive its actual payload.
They run again on each `str(error)` call, so keep callbacks side-effect free.
Static string messages use `str.format`; callable f-strings return their result
directly and do not need `str.format` brace escaping.

For a typed construction path with `ty` and `zuban`, call the enum member's
`VariantSpec` value:

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
  Use a typed `TypedVariant[T]` returned from `VariantSpec.__call__`; the enum
  member's `.value(payload)` calls that typed path.

Payload values are not checked against their schema at runtime. A schema describes
the static payload type and callable-message type; it is not a runtime validator.
