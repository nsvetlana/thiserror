# thiserror

<div align="center">
<pre style='font-size:clamp(6px, 1.2vw, 12px);line-height:1.17;white-space:pre;background-color:#000;color:#fff;padding:8px;margin:0;max-width:100%;overflow-x:auto;'><span style="color:#FF55FF">█▀▀▀▀▀▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀█</span><span style="color:#AAAAAA"> </span><span style="color:#FFFFFF">█▀</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀█ ▓▀▀▀█</span><span style="color:#AAAAAA"> </span><span style="color:#FFFFFF">█▀</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀█</span><span style="color:#AAAAAA"> </span><span style="color:#FFFFFF">█▀</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀▀▀▀▀▀▀</span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF"> ▄▀▀▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀█</span><span style="color:#AAAAAA"> </span><span style="color:#FFFFFF">█▀</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀▀▀▀▀▀▄ </span><span style="color:#AAAAAA"> </span><span style="color:#FFFFFF">█▀</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀▀▀▀▀▀▄ </span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF"> </span><span style="color:#FFFFFF">▄</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀▀▄ </span><span style="color:#AAAAAA"> </span><span style="color:#FFFFFF">█▀</span><span style="color:#FF55FF">▀</span><span style="color:#AA00AA">▀</span><span style="color:#FF55FF">▀▀▀▀▀▀▄ </span>
<span style="color:#FF55FF">█▄▄▄</span><span style="color:#FFFFFF">·</span><span style="color:#FF55FF">   ▄▄</span><span style="color:#AA00AA">▄█</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▀</span><span style="color:#FF55FF">    ▓ ▒ </span><span style="color:#FFFFFF">∙</span><span style="color:#FF55FF"> █</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▀</span><span style="color:#FF55FF">    ▓</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▀</span><span style="color:#FF55FF">    ▄▄▄ </span><span style="color:#FFFFFF">∙</span><span style="color:#FF55FF"> </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF">█</span><span style="color:#FFFFFF">·</span><span style="color:#FF55FF">   ▄▄▄▄▄</span><span style="color:#AA00AA">▄█</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▀</span><span style="color:#FF55FF">    ▄▄  </span><span style="color:#FFFFFF">∙</span><span style="color:#FF55FF"> █</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▀</span><span style="color:#FF55FF">    ▄▄  </span><span style="color:#FFFFFF">∙</span><span style="color:#FF55FF"> █</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▀</span><span style="color:#FF55FF">    ▄▄ </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF">  █</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▀</span><span style="color:#FF55FF">    ▄▄  </span><span style="color:#FFFFFF">∙</span><span style="color:#FF55FF"> █</span>
<span style="color:#FF55FF">   </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">  </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">   </span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">    </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">▄░   </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">    </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">    </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF"> ▀</span><span style="color:#555555">▀</span><span style="color:#AA00AA">▀▀▀</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">  </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">▄▄▄▄▄▄</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">    </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">▄▌   </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">    </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">▄▌   </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">    </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF"> ▌   </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">    </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">▄▌   </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span>
<span style="color:#FF55FF">   </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#FF55FF"> ∙  </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#FF55FF">   </span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#FF55FF">   </span><span style="color:#FFFFFF">·</span><span style="color:#AA00AA">▄▄▄</span><span style="color:#FF55FF">   </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#FF55FF">   </span><span style="color:#FFFFFF">·</span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#AA00AA">▄▄▄</span><span style="color:#FF55FF"> </span><span style="color:#555555">▀</span><span style="color:#FF55FF">▀▀▀▀▀</span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#FF55FF"> ∙  </span><span style="color:#AA00AA">▄▄▄▄▄▄</span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#FF55FF">   </span><span style="color:#FFFFFF">·</span><span style="color:#AA00AA">▄▄▄</span><span style="color:#FF55FF">  </span><span style="color:#AA00AA">▀▄</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#FF55FF">   </span><span style="color:#FFFFFF">·</span><span style="color:#AA00AA">▄▄▄</span><span style="color:#FF55FF">  </span><span style="color:#AA00AA">▀▄</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#FF55FF">  </span><span style="color:#FFFFFF">·</span><span style="color:#FF55FF"> </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#FF55FF"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">   </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▒</span><span style="color:#FF55FF">   </span><span style="color:#FFFFFF">·</span><span style="color:#AA00AA">▄▄▄</span><span style="color:#FF55FF">  </span><span style="color:#AA00AA">▀▄</span>
<span style="color:#FF55FF">   </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF">    </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF">   </span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF"> </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF">  </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF">  </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF"> </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF">  </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF">▄▄▄▄▄  ▒  </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF">    </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#AA00AA">▄▄▄▄▄▄</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF"> </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF">  </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF">  </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF"> </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF">  </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF">  </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF">    </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#AA00AA">▄</span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#555555">·</span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF"> </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF">  </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#FF55FF">  </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF;background-color:#AA00AA">░</span>
<span style="color:#FF55FF">   </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF">    </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF">   </span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF">    </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF"> </span><span style="color:#AA00AA">█</span><span style="color:#FFFFFF">∙</span><span style="color:#FF55FF">  </span><span style="color:#AA00AA">█</span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF">    </span><span style="color:#AA00AA">█</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">▓</span><span style="color:#FF55FF">   ▀▀▀▀</span><span style="color:#FFFFFF">∙</span><span style="color:#FF55FF">  </span><span style="color:#AA00AA">█</span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF">    </span><span style="color:#FFFFFF">.</span><span style="color:#FF55FF">    </span><span style="color:#FFFFFF">·</span><span style="color:#AA00AA">█</span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF">    </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF"> </span><span style="color:#AA00AA">█</span><span style="color:#FFFFFF">∙</span><span style="color:#FF55FF">  </span><span style="color:#AA00AA">█</span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF">    </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF"> </span><span style="color:#AA00AA">█</span><span style="color:#FFFFFF">∙</span><span style="color:#FF55FF">  </span><span style="color:#AA00AA">█</span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF">   .      </span><span style="color:#AA00AA">█</span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF">    </span><span style="color:#AA00AA">█</span><span style="color:#FF55FF"> </span><span style="color:#AA00AA">█</span><span style="color:#FFFFFF">∙</span><span style="color:#FF55FF">  </span><span style="color:#AA00AA">█</span>
<span style="color:#FF55FF">   </span><span style="color:#AA00AA">█▄▄▄▄█</span><span style="color:#FF55FF">   </span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█▄▄▄▄█</span><span style="color:#FF55FF"> </span><span style="color:#AA00AA">█▄▄▄█</span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█▄▄▄▄█</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF;background-color:#AA00AA">░</span><span style="color:#AA00AA">▄▄▄▄▄▄▄▄▄▄█</span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█▄▄▄▄▄▄▄▄▄▄█</span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█▄▄▄▄█</span><span style="color:#FF55FF"> </span><span style="color:#AA00AA">█▄▄▄█</span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█▄▄▄▄█</span><span style="color:#FF55FF"> </span><span style="color:#AA00AA">█▄▄▄█</span><span style="color:#AAAAAA"> </span><span style="color:#FF55FF"> </span><span style="color:#AA00AA">▀▄▄▄▄▄▄▄▄▀</span><span style="color:#FF55FF"> </span><span style="color:#AAAAAA"> </span><span style="color:#AA00AA">█▄▄▄▄█</span><span style="color:#FF55FF"> </span><span style="color:#AA00AA">█▄▄▄█</span></pre>
</div>

> Typed, matchable error variants for Python, inspired by Rust's [`thiserror`](https://docs.rs/thiserror/).

Define related errors in one place, attach structured payloads, and give each variant a clear message. Raise the resulting exceptions normally and handle individual variants with Python's `match` statement.

## Features

- **Grouped error variants:** define named variants in an `Error` subclass (an enum); calling a variant creates a raisable `TypedVariant` exception.
- **Payload schemas:** declare one payload type per variant, or use `()` for a payload-free (unit) variant. Types are not validated at runtime.
- **Custom messages:** use a function (such as `lambda payload: f"..."`) or a string template rendered with `str.format`.
- **Pattern matching:** distinguish variants with qualified `case` patterns after catching a `TypedVariant` exception.
- **Automatic exception causes:** when the payload is an exception, it is assigned to the resulting error's `__cause__`.

Requires **Python 3.12+**. No third-party runtime dependencies.

## Installation

With [uv](https://docs.astral.sh/uv/):

```bash
uv add thiserror
```

With pip:

```bash
pip install thiserror
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
    Disconnect = Variant(OSError, "data store disconnected")
    Redaction = Variant(str, lambda payload: f"the data for key `{payload}` is not available")
    InvalidHeader = Variant(
        InvalidHeaderFields,
        lambda payload: f"invalid header (expected {payload.expected}, found {payload.found})",
    )
    Unknown = Variant((), "unknown data store error")


fields = InvalidHeaderFields(expected="content-type", found="x-type")
header_error = DataStoreError.InvalidHeader(fields)
print(header_error)

try:
    raise DataStoreError.Disconnect(OSError("disk offline"))
except TypedVariant as error:
    match error:
        case DataStoreError.Disconnect:
            print(error)
        case DataStoreError.Unknown:
            print(error)
```

Output:

```text
invalid header (expected content-type, found x-type)
data store disconnected
```

`DataStoreError` defines the variants; **`TypedVariant` is the exception class**. Catch `TypedVariant` (or `Exception`), not `DataStoreError`.

## Defining variants

Use `Variant(schema, message)` as a member of an `Error` subclass. `Variant` is an alias for `make_variant`.

```python
class LookupError(Error):
    Missing = Variant(str, "key {0!r} not found")
    InvalidStatus = Variant(int, lambda status: f"invalid status: {status}")
    Empty = Variant((), "no results available")


assert str(LookupError.Missing("account")) == "key 'account' not found"
assert str(LookupError.InvalidStatus(503)) == "invalid status: 503"
assert str(LookupError.Empty()) == "no results available"
```

A variant with a payload requires **exactly one argument**. A unit variant, declared with `Variant((), message)`, takes **no arguments**. Incorrect argument counts raise `TypeError`.

### Formatting messages

String messages use `str.format` when the error is converted to a string:

- `{0}` references the entire payload, as in `"I/O error: {0}"`.
- `{name}` references a field of a dataclass payload or a value in a payload object's `__dict__`.
- Python format conversions also work, such as `{0!r}` for `repr(payload)`.

Alternatively, pass a callable such as `lambda payload: f"invalid: {payload}"`. This is how the quick-start example uses **f-strings**: the f-string is evaluated inside the function when the exception is rendered, not when it is created. A plain string passed to `Variant` uses **`str.format`**, not f-string interpolation. For **unit variants**, a message callable receives the `TypedVariant` instance rather than a payload.

### Accessing the payload

A constructed exception exposes its original payload through `.value`:

```python
error = LookupError.Missing("account")
assert error.value == "account"
```

Unknown attributes on the exception are delegated to its payload, so structured payload fields can also be accessed directly (for example, `header_error.expected` in the quick-start example).

## Catching and matching errors

All constructed variants are instances of `TypedVariant`, which extends `Exception`. Match against qualified enum members to distinguish variants:

```python
try:
    raise LookupError.Empty()
except TypedVariant as error:
    match error:
        case LookupError.Missing:
            print("Missing:", error.value)
        case LookupError.Empty:
            print("Nothing to return")
        case _:
            raise
```

If a payload is itself an exception, it is assigned to `__cause__` automatically:

```python
original = OSError("disk offline")
error = DataStoreError.Disconnect(original)
assert error.__cause__ is original
```

## API overview

| Name                       | Description                                                                                      |
|----------------------------|--------------------------------------------------------------------------------------------------|
| `Error`                    | Base enum for declaring a related set of error variants. It is **not** an exception type.        |
| `Variant(schema, message)` | Declares a variant with a payload type or `()` for no payload.                                   |
| `TypedVariant`             | The raisable exception created by calling a declared variant. Its `.value` contains the payload. |

## Limitations

- **No runtime payload type validation:** schemas provide type information, but the implementation checks the number of arguments, not whether a payload is an instance of the declared type.
- **No exhaustiveness guarantees:** unlike Rust, Python does not require every variant to appear in a `match` statement.
- **No automatic type narrowing by variant:** a successful `case` does not, by itself, ensure static type checkers will infer a more specific payload type.
