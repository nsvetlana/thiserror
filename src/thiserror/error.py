"""Core error-variant machinery porting Rust ``thiserror`` ergonomics."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Never, cast, overload

_UNIT_PAYLOAD = cast(Never, None)


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


@dataclass(slots=True, eq=False, init=False)
class VariantSpec[PayloadT]:
    """A payload schema and message specification returned by :func:`Variant`.

    Assigned as a class attribute on an :class:`Error` subclass it becomes an
    enum member whose value is this specification instance; calling the member builds
    a raisable :class:`TypedVariant`. Static strings render via ``str.format``
    from the payload at raise time. Schema callables receive the raw payload
    whenever the raised error is rendered.
    """

    schema: type[PayloadT] | tuple[()]
    message: str | Callable[..., str]
    is_unit: bool = False

    def __init__(
        self,
        schema: type[Any] | tuple[()],
        message: str | Callable[..., str],
    ) -> None:
        self.schema = cast(type[PayloadT] | tuple[()], schema)
        self.message = message
        self.is_unit = isinstance(schema, tuple)

    def render(self, instance: TypedVariant[PayloadT]) -> str:
        payload = instance.value
        if isinstance(self.message, str):
            return self.message.format(payload, **_format_fields(payload))
        value = instance if self.is_unit else payload
        return self.message(value)

    @overload
    def __call__(self: VariantSpec[Never]) -> TypedVariant[Never]: ...

    @overload
    def __call__(self, value: PayloadT, /) -> TypedVariant[PayloadT]: ...

    def __call__(self, *values: PayloadT) -> TypedVariant[PayloadT]:
        return _make_typed_variant(self, None, *values)


@overload
def make_variant(
    schema: tuple[()],
    message: str | Callable[..., str],
) -> VariantSpec[Never]: ...


@overload
def make_variant[PayloadT](schema: type[PayloadT], message: str) -> VariantSpec[PayloadT]: ...


@overload
def make_variant(schema: type[str], message: Callable[[str], str]) -> VariantSpec[str]: ...


# The generic fallback remains reachable for non-str schemas; PyCharm misreads
# the narrower overload above as shadowing it.
# noinspection PyOverloads
@overload
def make_variant[PayloadT](
    schema: type[PayloadT],
    message: Callable[[PayloadT], str],
) -> VariantSpec[PayloadT]: ...


def make_variant(
    schema: type[Any] | tuple[()],
    message: str | Callable[..., str],
) -> VariantSpec[Any]:
    """Build a typed variant declaration for an error enum."""
    return VariantSpec(schema, message)


Variant = make_variant


def _make_typed_variant[PayloadT](
    variant: VariantSpec[PayloadT],
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

    variant: VariantSpec[PayloadT]
    _payload: PayloadT
    _is_unit: bool
    _owner: object | None

    def __init__(
        self,
        variant: VariantSpec[PayloadT],
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
        if not isinstance(variant, VariantSpec):
            raise TypeError(f"{self.name} is not a Variant")
        return _make_typed_variant(variant, self, *args)

    def __reduce_ex__(self, proto: object) -> tuple[Any, ...]:
        return getattr, (type(self), self.name)


def _restore_variant_error(
    member: object | None,
    variant: VariantSpec[Any] | None,
    payload: object,
    is_unit: bool,
) -> Any:
    if member is not None:
        if not isinstance(member, Enum):
            raise TypeError("the owner must be an enum member")
        owned_variant = member.value
        if not isinstance(owned_variant, VariantSpec):
            raise TypeError("the enum member is not backed by a Variant")
        if is_unit:
            return _make_typed_variant(owned_variant, member)
        return _make_typed_variant(owned_variant, member, payload)
    if variant is None:
        raise TypeError("a standalone variant error requires its Variant")
    if is_unit:
        return _make_typed_variant(variant, None)
    return _make_typed_variant(variant, None, payload)
