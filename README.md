# thiserror

Declare error variants with typed payloads and messages for Python 3.12 and newer.
Inspired by Rust's [thiserror](https://docs.rs/thiserror).

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
header_error: TypedVariant[InvalidHeaderFields] = DataStoreError.InvalidHeader.value(fields)

try:
    raise header_error
except TypedVariant as caught:
    print(caught)

try:
    raise DataStoreError.Disconnected(OSError("disk offline"))
except TypedVariant as error:
    variant_error = error
    match variant_error:
        case DataStoreError.Disconnected:
            print(error)
        case DataStoreError.Unknown:
            print(error)
```

The example prints the invalid-header message, then `data store disconnected`.
Install this checkout with `python -m pip install .`.

## Match mechanics

`case DataStoreError.Disconnected` is a dotted value pattern. Python compares the
subject with that enum member using `==`; a bare name such as `Disconnected`
would instead capture the subject and match every value. `TypedVariant` equality
connects a raised wrapper to the enum member whose `VariantSpec` it carries, so
the example dispatches at runtime. The first matching case runs. Equality uses
`VariantSpec` identity: reusing one spec object across different `Error` enums
shares its match identity. Declare a fresh `Variant(...)` when those enums must
remain distinct.

Calling an enum member creates a `TypedVariant` exception. Catch it with
`except TypedVariant` or a broader handler such as `except Exception`;
`DataStoreError` is an enum, not an exception class, so `except DataStoreError`
is unsupported. A broader `except Exception` handler also runs, but Zuban flags
the enum-pattern arms as unreachable when it sees the subject's static type as
`Exception`. Catching `TypedVariant` lets the same value patterns
pass ty, Zuban, and PyCharm, but their refinement differs: ty keeps the subject
as `TypedVariant[Unknown]`, while Zuban treats a matched subject as the
enum-member literal, not as `TypedVariant[PayloadT]`. Neither checker supplies
the correct payload type in the arm or checks exhaustiveness. Widening a broad
handler's subject to `object` silences Zuban's warning but ty treats those arms
as `Never`; it is not a type-safe workaround. Keep a `TypedVariant[PayloadT]`
value from `.value(payload)` when the payload type matters. Rust enum matching
can narrow payloads and check exhaustiveness.

## Messages and typing

`Variant(schema, message)` stores a `VariantSpec[PayloadT]` on the enum member.
Payload variants take one value; `Variant((), message)` declares a unit variant.
String messages use `str.format`. A callable message receives the raw payload
and runs on each `str(error)` call; for a unit variant it receives the raised
wrapper. Keep callbacks side-effect free. Exception payloads are retained as
`__cause__`.

Use the member's `.value(payload)` path when the constructed
`TypedVariant[PayloadT]` type matters. Calling the enum member directly is
supported at runtime, but its return type is dynamic to Python's Enum typing.
Schemas describe static payload types; they do not validate values at runtime.
The package ships inline annotations and `py.typed` for PEP 561 type checkers.

For the public API, see the [source docstrings](src/thiserror/error.py).
