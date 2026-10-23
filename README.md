# thiserror

Declare error variants with payload schemas and messages. The package requires
Python 3.12 or newer and is inspired by Rust's [thiserror](https://docs.rs/thiserror).

Install a checkout with `python -m pip install .`.

## Example

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
error: TypedVariant[InvalidHeaderFields] = DataStoreError.InvalidHeader.value(fields)

try:
    raise error
except Exception as caught:
    print(caught)
```

## Behavior and typing

- `Variant(schema, message)` creates a `VariantSpec[PayloadT]` stored as the enum member's value. `()` declares a unit variant; other variants take one payload.
- Payload callbacks receive the raw payload and run each time `str(error)` is called. Unit callbacks receive the `TypedVariant` wrapper. Keep callbacks side-effect free.
- Static string messages use `str.format`, with positional `{0}` and named payload fields. Callable f-strings return their result directly.
- Use the enum member's `.value(payload)` path and annotate the result as `TypedVariant[PayloadT]` for a statically typed construction. Calling the member directly is supported at runtime, but Python's Enum typing leaves that call dynamically typed.
- `TypedVariant` derives from `Exception`. The `Error` enum itself is not an exception class, so `except DataStoreError` is unsupported. Value-pattern `match` dispatch works at runtime but does not statically narrow the matched value.
- Exception payloads become `__cause__`, with their traceback retained. Schemas describe static types; they do not validate payloads at runtime.

The package uses inline annotations. Its `py.typed` marker opts the installed
package into PEP 561 type checking so type checkers can use those annotations.
