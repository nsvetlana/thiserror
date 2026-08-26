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
    a raisable :class:`TypedVariant`. Callables are probed once at declaration
    against :class:`_TemplatePath`: lambdas reducible to pure field/index access
    become ``str.format`` templates (rendered from the payload at raise time),
    anything richer falls back to live rendering with the raised instance as
    ``self``. The overloads keep the expected callable unambiguous so IDEs
    infer lambda ``self`` from the schema.
    """

    schema: type[T] | tuple[Any, ...]
    message: str | Callable[[Any], str]
    template: str
    _factory: Callable[[Any], str] | None

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
        if isinstance(message, str):
            self.template = message
            self._factory = None
            return
        try:
            probe_target: Any = _TemplatePath()
            self.template = message(probe_target)
        except Exception:  # noqa: BLE001 - any failure means "not statically expressible"
            self.template = ""
            self._factory = message
        else:
            self._factory = None

    def __call__(self, *values: Any) -> TypedVariant[T]:
        if isinstance(self.schema, tuple):
            if values:
                raise TypeError(
                    f"unit variant with message {self.message!r} takes no arguments,"
                    f" got {len(values)}"
                )
        elif len(values) != 1:
            raise TypeError(
                f"variant with message {self.message!r} and schema"
                f" {self.schema!r} takes exactly one"
                f" argument, got {len(values)}"
            )
        return TypedVariant(self, *values)

    def render(self, instance: TypedVariant[T]) -> str:
        """Render the message for a raised instance.

        Template mode interpolates the payload positionally (slot 0) and, when
        the payload exposes attributes, as named fields; live mode delegates to
        the stored callable with the raised instance itself.
        """
        factory = self._factory
        if factory is not None:
            return factory(instance)
        value = instance.value
        if value is None:
            return self.template.format()
        fields: dict[str, Any] = getattr(value, "__dict__", None) or {}
        return self.template.format(value, **fields)


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
