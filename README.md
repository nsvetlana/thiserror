# thiserror

Declare named error variants with payloads and readable messages, then raise and handle them with Python's normal exception flow. Inspired by Rust's [thiserror](https://docs.rs/thiserror), thiserror is for Python 3.12 and newer.

## Install

Install it with pip:

```shell
pip install thiserror
```

Or add it to a uv-managed project:

```shell
uv add thiserror
```

## Quick start

```python
from thiserror import Error, TypedVariant, Variant


class StoreError(Error):
    Unavailable = Variant(OSError, lambda cause: f"Store unavailable: {cause}")


error = StoreError.Unavailable(OSError("disk offline"))

try:
    raise error
except TypedVariant as error:
    match error:
        case StoreError.Unavailable:
            print(error)
        case _:
            print("Unexpected error:", error)
```

Expected output: `Store unavailable: disk offline`.

## API

- `Error` is the base class for declaring named variants; it is not an exception class.
- `Variant(schema, message)` declares a variant and returns a `VariantSpec`.
- `VariantSpec` describes the payload schema and message; assigning one to an `Error` subclass makes it a named variant.
- Calling a named variant creates a `TypedVariant` exception. Catch it with `except TypedVariant` or `except Exception`; its payload is available as `.value`.

String messages use `.format`: `{0}` is the payload, and fields on dataclass or object payloads can be named, such as `{path}`. A callable message receives the payload and returns the displayed text. Unit variants use `Variant((), "unavailable")` and are called without a payload; a callable message for a unit variant receives the error object. If a payload is itself an exception, the `TypedVariant` chains it as its `__cause__`.

Schemas are hints and do not validate payloads at runtime. Python's `match` dispatches variants, but it does not require a case for every variant.
