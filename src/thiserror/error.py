"""Core error-variant machinery porting Rust ``thiserror`` ergonomics."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, cast, overload

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["Error", "Variant"]


class _SelfProxy:
    """Declaration-time stand-in passed to callable message templates.

    Attribute and index access return itself and string formatting yields ``""``,
    so the one-time probe of a template factory is type-safe and string-safe.
    Never reaches runtime rendering.
    """

    def __getattr__(self, name: str) -> Any:
        return self

    def __getitem__(self, item: Any) -> Any:
        return self

    def __str__(self) -> str:
        return ""

    def __format__(self, format_spec: str) -> str:
        return ""


if TYPE_CHECKING:

    class TypedVariant[T](BaseException):
        """Static face satisfied by the lazily built per-Variant exception classes."""

        value: T | None
        _variant: Variant[T]

        def __getitem__(self, index: int) -> Any: ...

        def __len__(self) -> int: ...

        def __getattr__(self, name: str) -> Any: ...


class Variant[T]:
    """Declarative error variant: a payload schema plus a message template.

    Assigned as a class attribute on an :class:`Error` subclass it becomes an
    enum member whose value is this Variant instance; calling the member builds
    a raisable exception rendering the template.
    """

    schema: type[T] | tuple[Any, ...]
    template: str
    template_factory: str | Callable[[T], str]
    _typed_cls: type[BaseException] | None

    @overload
    def __init__(
        self: Variant[tuple[Any, ...]],
        schema: tuple[Any, ...],
        template_factory: str | Callable[[Any], str],
    ) -> None: ...

    @overload
    def __init__(self, schema: type[T], template_factory: str) -> None: ...

    @overload
    def __init__(self, schema: type[T], template_factory: Callable[[T], str]) -> None: ...

    def __init__(
        self,
        schema: type[T] | tuple[Any, ...],
        template_factory: str | Callable[[T], str],
    ) -> None:
        self.schema = schema
        self.template_factory = template_factory
        if isinstance(template_factory, str):
            self.template = template_factory
        else:
            # Declaration-time probe: the factory runs once against a stand-in so
            # bad templates surface at import time instead of first raise.
            self.template = str(template_factory(cast(T, _SelfProxy())))
        self._typed_cls = None

    def __call__(self, *values: Any) -> TypedVariant[T]:
        if isinstance(self.schema, tuple):
            if len(values) != 0:
                raise TypeError(
                    f"unit variant with template {self.template!r} takes no arguments,"
                    f" got {len(values)}"
                )
        elif len(values) != 1:
            raise TypeError(
                f"variant with template {self.template!r} and schema"
                f" {getattr(self.schema, '__name__', self.schema)!r} takes exactly one"
                f" argument, got {len(values)}"
            )

        typed_cls = self._typed_cls
        if typed_cls is None:
            variant = self

            def __init__(self_, *values_: Any) -> None:
                self_.value = values_[0] if values_ else None
                # #[from] parity: wrapping an exception preserves its traceback
                # through the cause chain.
                if isinstance(self_.value, BaseException):
                    self_.__cause__ = self_.value

            def __str__(self_) -> str:
                factory = self_._variant.template_factory
                if isinstance(factory, str):
                    return factory
                return factory(self_)

            def __repr__(self_) -> str:
                return (
                    f"{type(self_).__qualname__}"
                    f"({self_._variant.template!r}, {self_.value!r})"
                )

            def __getitem__(self_, index: int) -> Any:
                if index == 0:
                    return self_.value
                raise IndexError("variant payload exposes a single value slot")

            def __len__(self_) -> int:
                return 1

            def __getattr__(self_, name: str) -> Any:
                value = object.__getattribute__(self_, "value")
                if value is None or not hasattr(value, name):
                    raise AttributeError(name)
                return getattr(value, name)

            def __eq__(self_, other: object) -> bool:
                # Value pattern support: `case Owner.Member:` compares the subject
                # against the enum member, whose `.value` IS the owning Variant.
                if getattr(other, "value", None) is variant:
                    return True
                other_variant = getattr(other, "_variant", None)
                if other_variant is variant:
                    return bool(getattr(other, "value", None) == self_.value)
                return False

            ns: dict[str, Any] = {
                "_variant": variant,
                "__init__": __init__,
                "__str__": __str__,
                "__repr__": __repr__,
                "__getitem__": __getitem__,
                "__getattr__": __getattr__,
                "__eq__": __eq__,
                "__hash__": object.__hash__,
            }
            if not isinstance(variant.schema, tuple):
                ns["__len__"] = __len__
            typed_cls = cast(
                "type[BaseException]", type("TypedVariant", (BaseException,), ns)
            )
            # Cached per Variant: rebuilding per raise would break cross-raise
            # isinstance stability and waste allocations.
            self._typed_cls = typed_cls

        return cast("TypedVariant[T]", typed_cls(*values))


class Error(Enum):
    """An Enum replacement class that natively supports member execution routing."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.value(*args, **kwargs)
