"""Core error-variant machinery porting Rust ``thiserror`` ergonomics."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass(slots=True)
class _TemplatePath:
    """Declaration-time probe converting attribute/index access into
    ``str.format`` field references — Rust ``#[error("{0} …")]`` parity."""

    path: str = ""

    def __getitem__(self, key: Any) -> _TemplatePath:
        segment = repr(key) if isinstance(key, str) else str(key)
        return _TemplatePath(f"{self.path}[{segment}]" if self.path else segment)

    def __getattr__(self, name: str) -> _TemplatePath:
        return _TemplatePath(f"{self.path}.{name}" if self.path else name)

    def __format__(self, format_spec: str) -> str:
        suffix = f":{format_spec}" if format_spec else ""
        return f"{{{self.path}{suffix}}}"


@dataclass(slots=True)
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
    template: str = ""
    is_unit: bool = False

    def __post_init__(self) -> None:
        # Zero-copy: compute once at construction, never again
        object.__setattr__(self, "is_unit", isinstance(self.schema, tuple))
        if isinstance(self.message, str):
            object.__setattr__(self, "template", self.message)


    def render(self, instance: TypedVariant[T]) -> str:
        msg = self.message
        if isinstance(msg, str):
            value = instance.value
            # Zero-allocation format using precomputed template if available
            return self.template.format(value, **(value.__dict__ if hasattr(value, "__dict__") else {}))
        return msg(instance)

    def __call__(self, *values: Any) -> TypedVariant[T]:
        # Arity check using precomputed is_unit — no isinstance at call-time
        if (self.is_unit and values) or (not self.is_unit and len(values) != 1):
            raise TypeError(
                f"variant with message {self.message!r} and schema"
                f" {self.schema!r} takes {0 if self.is_unit else 1} argument(s),"
                f" got {len(values)}"
            )
        return TypedVariant(self, *values)


@dataclass(slots=True)
class TypedVariant[T](BaseException):
    """Raisable exception bound to the Variant that declared it.

    Presents the payload as a one-slot sequence: ``len`` counts payload slots
    (0 for unit schemas, 1 otherwise) and indexing obeys those bounds. Unknown
    attributes delegate to the wrapped payload.
    """

    variant: Variant[T]
    value: Any = None
    _is_unit: bool = False

    def __post_init__(self) -> None:
        # Zero-copy: hoist arity from variant at construction time
        object.__setattr__(self, "_is_unit", self.variant.is_unit)
        if isinstance(self.value, BaseException):
            self.__cause__ = self.value

    def __str__(self) -> str:
        return self.variant.render(self)

    def __repr__(self) -> str:
        if self.value is None:
            return f"{type(self).__qualname__}({self.variant.message!r})"
        return f"{type(self).__qualname__}({self.variant.message!r}, {self.value!r})"

    def __getitem__(self, index: int) -> Any:
        # Task 3: avoid isinstance(self._variant.schema, tuple)
        if index != 0 or self._is_unit:
            raise IndexError("variant payload exposes a single value slot")
        return self.value

    def __len__(self) -> int:
        # Task 3: avoid isinstance check
        return 0 if self._is_unit else 1

    def __getattr__(self, name: str) -> Any:
        # Zero-allocation delegation; no extra hasattr on self
        value = object.__getattribute__(self, "value")
        try:
            return getattr(value, name)
        except AttributeError:
            raise AttributeError(name) from None

    def __eq__(self, other: object) -> bool:
        if getattr(other, "value", None) is self.variant:
            return True
        if getattr(other, "variant", None) is self.variant:
            return bool(getattr(other, "value", None) == self.value)
        return False

    __hash__ = object.__hash__


class Error(Enum):
    """An Enum replacement class that natively supports member execution routing."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.value(*args, **kwargs)
