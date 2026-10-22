"""Core error-variant machinery porting Rust ``thiserror`` ergonomics."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Literal, Never, cast, overload

_UNIT_PAYLOAD = cast(Never, None)
_PROBE_FAILED = object()


class _Unrenderable(Exception):
    """Signal that a message needs its live callable instead of a template."""


class _TemplatePath:
    """Record field access performed by an f-string without a payload instance."""

    __slots__ = ("_field", "_wrapper")

    def __init__(self, field: str, *, wrapper: bool) -> None:
        self._field = field
        self._wrapper = wrapper

    def __getattr__(self, name: str) -> _TemplatePath:
        if self._wrapper and self._field == "0":
            if name == "value":
                return _TemplatePath("0", wrapper=False)
            if name in {"variant", "args", "__cause__", "__context__", "__traceback__"}:
                raise _Unrenderable
        return _TemplatePath(f"{self._field}.{name}", wrapper=False)

    def __getitem__(self, index: object) -> _TemplatePath:
        if self._wrapper and self._field == "0":
            if index != 0:
                raise _Unrenderable
            return _TemplatePath("0", wrapper=False)
        if isinstance(index, bool):
            selector = str(int(index))
        elif isinstance(index, str):
            selector = repr(index)
        elif isinstance(index, int):
            selector = str(index)
        else:
            raise _Unrenderable
        return _TemplatePath(f"{self._field}[{selector}]", wrapper=False)

    def __call__(self, *args: object, **kwargs: object) -> Never:
        raise _Unrenderable

    def __bool__(self) -> Never:
        raise _Unrenderable

    def __eq__(self, other: object) -> Never:
        raise _Unrenderable

    def __ne__(self, other: object) -> Never:
        raise _Unrenderable

    def __str__(self) -> str:
        return self.__format__("")

    def __repr__(self) -> str:
        if self._wrapper and self._field == "0":
            raise _Unrenderable
        return f"{{{self._field}!r}}"

    def __format__(self, format_spec: str) -> str:
        if self._wrapper and self._field == "0":
            raise _Unrenderable
        suffix = f":{format_spec}" if format_spec else ""
        return f"{{{self._field}{suffix}}}"


def _probe_template(message: Callable[..., str], *, wrapper: bool) -> str | None:
    result: object = _PROBE_FAILED
    with suppress(Exception):
        result = message(cast(Any, _TemplatePath("0", wrapper=wrapper)))
    return result if isinstance(result, str) else None


def _format_fields(value: object) -> dict[str, object]:
    if not isinstance(value, type):
        try:
            field_reader = cast(Callable[[Any], tuple[Any, ...]], fields)
            dataclass_fields = field_reader(value)
        except TypeError:
            pass
        else:
            return {field.name: getattr(value, field.name) for field in dataclass_fields}
    try:
        return vars(value)
    except TypeError:
        return {}


class _VariantBuilder[PayloadT]:
    """Bind a payload schema before giving a callable message to type checkers."""

    __slots__ = ("schema",)

    def __init__(self, schema: type[PayloadT]) -> None:
        self.schema = schema

    def message(self, message: Callable[[PayloadT], str]) -> Variant[PayloadT]:
        return Variant(self.schema, message, _typed_factory=True)


@dataclass(slots=True, eq=False, init=False)
class Variant[PayloadT]:
    """Declarative error variant: a payload schema plus a message.

    Assigned as a class attribute on an :class:`Error` subclass it becomes an
    enum member whose value is this Variant instance; calling the member builds
    a raisable :class:`TypedVariant`. Static strings render verbatim via
    ``str.format`` from the payload at raise time. Callable messages are probed
    for simple formatting paths and otherwise render live with their mode's
    payload or wrapper argument.
    """

    schema: type[PayloadT] | tuple[()]
    message: str | Callable[..., str]
    template: str = ""
    is_unit: bool = False
    _factory: Callable[..., str] | None = None
    _typed_factory: bool = False

    @overload
    def __init__(
        self: Variant[Never],
        schema: tuple[()],
        message: str | Callable[..., str],
    ) -> None: ...

    @overload
    def __init__(self, schema: type[PayloadT], message: str) -> None: ...

    @overload
    def __init__(self, schema: type[PayloadT], message: Callable[[Any], str]) -> None: ...

    @overload
    def __init__(
        self,
        schema: type[PayloadT],
        message: Callable[[PayloadT], str],
        *,
        _typed_factory: Literal[True],
    ) -> None: ...

    def __init__(
        self,
        schema: type[PayloadT] | tuple[()],
        message: str | Callable[..., str],
        *,
        _typed_factory: bool = False,
    ) -> None:
        self.schema = schema
        self.message = message
        self.is_unit = isinstance(schema, tuple)
        self._typed_factory = _typed_factory
        self._factory = None
        if isinstance(message, str):
            self.template = message
        else:
            template = _probe_template(message, wrapper=not _typed_factory)
            self.template = template if template is not None else ""
            if template is None:
                self._factory = message

    @staticmethod
    def for_schema[SchemaT](schema: type[SchemaT]) -> _VariantBuilder[SchemaT]:
        """Bind a schema first so all supported checkers type a message lambda."""
        return _VariantBuilder(schema)

    def render(self, instance: TypedVariant[PayloadT]) -> str:
        if self._factory is not None:
            value = instance.value if self._typed_factory else instance
            return self._factory(value)
        value = instance.value
        return self.template.format(value, **_format_fields(value))

    @overload
    def __call__(self: Variant[Never]) -> TypedVariant[Never]: ...

    @overload
    def __call__(self, value: PayloadT, /) -> TypedVariant[PayloadT]: ...

    def __call__(self, *values: PayloadT) -> TypedVariant[PayloadT]:
        return _make_typed_variant(self, None, *values)


def _make_typed_variant[PayloadT](
    variant: Variant[PayloadT],
    owner: object | None,
    *values: PayloadT,
) -> TypedVariant[PayloadT]:
    if (variant.is_unit and values) or (not variant.is_unit and len(values) != 1):
        raise TypeError(
            f"variant with message {variant.message!r} and schema"
            f" {variant.schema!r} takes {0 if variant.is_unit else 1} argument(s),"
            f" got {len(values)}"
        )
    value = values[0] if values else _UNIT_PAYLOAD
    return TypedVariant(variant, value, variant.is_unit, owner)


@dataclass(slots=True, eq=False, init=False)
class TypedVariant[PayloadT](Exception):
    """Raisable exception bound to the Variant that declared it.

    Presents the payload as a one-slot sequence: ``len`` counts payload slots
    (0 for unit schemas, 1 otherwise) and indexing obeys those bounds. Unknown
    attributes delegate to the wrapped payload.
    """

    variant: Variant[PayloadT]
    _payload: PayloadT
    _is_unit: bool
    _owner: object | None

    def __init__(
        self,
        variant: Variant[PayloadT],
        payload: PayloadT,
        is_unit: bool,
        owner: object | None,
    ) -> None:
        self.variant = variant
        self._payload = payload
        self._is_unit = is_unit
        self._owner = owner
        Exception.__init__(self, payload)
        if isinstance(payload, BaseException):
            self.__cause__ = payload

    @property
    def value(self) -> PayloadT:
        return self._payload

    def __str__(self) -> str:
        return self.variant.render(self)

    def __repr__(self) -> str:
        if self._is_unit:
            return f"{type(self).__qualname__}({self.variant.message!r})"
        return f"{type(self).__qualname__}({self.variant.message!r}, {self._payload!r})"

    def __getitem__(self, index: int) -> PayloadT:
        # Task 3: avoid isinstance(self.variant.schema, tuple)
        if index != 0 or self._is_unit:
            raise IndexError("variant payload exposes a single value slot")
        return self.value

    def __len__(self) -> int:
        # Task 3: avoid isinstance check
        return 0 if self._is_unit else 1

    def __getattr__(self, name: str) -> Any:
        # Zero-allocation delegation; no extra hasattr on self
        value = object.__getattribute__(self, "_payload")
        try:
            return getattr(value, name)
        except AttributeError:
            raise AttributeError(name) from None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Enum) and other.value is self.variant:
            return True
        if isinstance(other, TypedVariant):
            return other.variant is self.variant and other._payload == self._payload
        return False

    __hash__ = None

    def __reduce__(self) -> tuple[Any, tuple[Any, ...]]:
        variant = self.variant if self._owner is None else None
        return _restore_variant_error, (self._owner, variant, self._payload, self._is_unit)


class Error(Enum):
    """An Enum replacement class that natively supports member execution routing."""

    def __call__(self, *args: Any) -> Any:
        variant = self.value
        if not isinstance(variant, Variant):
            raise TypeError(f"{self.name} is not a Variant")
        return _make_typed_variant(variant, self, *args)

    def __reduce_ex__(self, proto: object) -> tuple[Any, ...]:
        return getattr, (type(self), self.name)


def _restore_variant_error(
    member: object | None,
    variant: Variant[Any] | None,
    payload: object,
    is_unit: bool,
) -> Any:
    if member is not None:
        if not isinstance(member, Enum):
            raise TypeError("the owner must be an enum member")
        owned_variant = member.value
        if not isinstance(owned_variant, Variant):
            raise TypeError("the enum member is not backed by a Variant")
        if is_unit:
            return _make_typed_variant(owned_variant, member)
        return _make_typed_variant(owned_variant, member, payload)
    if variant is None:
        raise TypeError("a standalone variant error requires its Variant")
    if is_unit:
        return _make_typed_variant(variant, None)
    return _make_typed_variant(variant, None, payload)
