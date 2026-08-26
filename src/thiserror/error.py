"""Core error-variant machinery porting Rust ``thiserror`` ergonomics."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any, overload


class _TemplatePath:
    """Declaration-time probe converting attribute/index access into
    ``str.format`` field references — Rust ``#[error("{0} …")]`` parity."""

    __slots__ = ("_path",)

    def __init__(self, path: str = "") -> None:
        self._path = path

    def __getitem__(self, key: Any) -> _TemplatePath:
        segment = repr(key) if isinstance(key, str) else str(key)
        return _TemplatePath(f"{self._path}[{segment}]" if self._path else segment)

    def __getattr__(self, name: str) -> _TemplatePath:
        return _TemplatePath(f"{self._path}.{name}" if self._path else name)

    def __format__(self, format_spec: str) -> str:
        suffix = f":{format_spec}" if format_spec else ""
        return f"{{{self._path}{suffix}}}"


class Variant[T]:
    """Declarative error variant: a payload schema plus a message.

    Assigned as a class attribute on an :class:`Error` subclass it becomes an
    enum member whose value is this Variant instance; calling the member builds
    a raisable :class:`TypedVariant`. Static strings render verbatim via
    ``str.format`` from the payload at raise time; callables render live
    with the raised instance as ``self``.
    """

    schema: type[T] | tuple[Any, ...]
    message: str | Callable[[Any], str]

    @overload
    def __init__(
        self: Variant[tuple[Any, ...]],
        schema: tuple[Any, ...],
        message: str | Callable[[Any], str],
    ) -> None: ...

    @overload
    def __init__(self, schema: type[T], message: str) -> None: ...

    @overload
    def __init__(self, schema: type[T], message: Callable[[T], str]) -> None: ...

    def __init__(
        self,
        schema: type[T] | tuple[Any, ...],
        message: str | Callable[[T], str],
    ) -> None:
        self.schema = schema
        self.message = message
        self.template = message if isinstance(message, str) else ""

    def render(self, instance: TypedVariant[T]) -> str:
        msg = self.message
        if isinstance(msg, str):
            value = instance.value
            return msg.format(
                value,
                **(value.__dict__ if hasattr(value, "__dict__") else {}),
            )
        return msg(instance)

    def __call__(self, *values: Any) -> TypedVariant[T]:
        # Arity check: tuple schema = unit (0 values); otherwise exactly 1
        is_unit = isinstance(self.schema, tuple)
        if (is_unit and values) or (not is_unit and len(values) != 1):
            raise TypeError(
                f"variant with message {self.message!r} and schema"
                f" {self.schema!r} takes {0 if is_unit else 1} argument(s),"
                f" got {len(values)}"
            )
        return TypedVariant(self, *values)


class TypedVariant[T](BaseException):
    """Raisable exception bound to the Variant that declared it.

    Presents the payload as a one-slot sequence: ``len`` counts payload slots
    (0 for unit schemas, 1 otherwise) and indexing obeys those bounds. Unknown
    attributes delegate to the wrapped payload.
    """

    def __init__(self, variant: Variant[T], *values: Any) -> None:
        self._variant = variant
        self.value = values[0] if values else None
        # #[from] parity: wrapping an exception preserves its traceback through
        # the cause chain.
        if isinstance(self.value, BaseException):
            self.__cause__ = self.value

    def __str__(self) -> str:
        return self._variant.render(self)

    def __repr__(self) -> str:
        if self.value is None:
            return f"{type(self).__qualname__}({self._variant.message!r})"
        return f"{type(self).__qualname__}({self._variant.message!r}, {self.value!r})"

    def __getitem__(self, index: int) -> Any:
        if index != 0 or isinstance(self._variant.schema, tuple):
            raise IndexError("variant payload exposes a single value slot")
        return self.value

    def __len__(self) -> int:
        return 0 if isinstance(self._variant.schema, tuple) else 1

    def __getattr__(self, name: str) -> Any:
        value = object.__getattribute__(self, "value")
        if value is None or not hasattr(value, name):
            raise AttributeError(name)
        return getattr(value, name)

    def __eq__(self, other: object) -> bool:
        # Value-pattern support: `case Owner.Member:` compares the subject against
        # the enum member, whose `.value` IS the owning Variant.
        if getattr(other, "value", None) is self._variant:
            return True
        if getattr(other, "_variant", None) is self._variant:
            return bool(getattr(other, "value", None) == self.value)
        return False

    __hash__ = object.__hash__


class Error(Enum):
    """An Enum replacement class that natively supports member execution routing."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.value(*args, **kwargs)
