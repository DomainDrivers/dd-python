from typing import Any, Protocol, Self, Sequence, Type, TypeVar, cast
from uuid import UUID

from pydantic import TypeAdapter
from sqlalchemy import Dialect, select, types
from sqlalchemy.orm import Session
from sqlalchemy.orm import registry as Registry

from smartschedule.shared.typing_extensions import JSON

registry = Registry()


class EmbeddableUUID(Protocol):
    def __init__(self, uuid: UUID, *args: Any, **kwargs: Any) -> None: ...

    @property
    def id(self) -> UUID: ...


class EmbeddedUUID[T: EmbeddableUUID](types.TypeDecorator[T]):
    """Manages identifiers as UUIDs in the database.

    Type is expected to have a `id` attribute that is a UUID.
    `.id` can be read-only, e.g. property.

    It must be possible for the type to be constructed with
    a single argument of UUID type.
    """

    impl = types.UUID(as_uuid=True)
    cache_ok = True

    _type: Type[T]

    def __class_getitem__(cls, type_: Type[T]) -> Self:
        specialized_class = type(
            f"EmbeddedUUID[{type_.__name__}]",
            (cls,),
            {"_type": type_, "cache_ok": True},
        )
        return cast(Self, specialized_class)

    def process_bind_param(self, value: T | None, dialect: Dialect) -> UUID | None:
        if value is not None:
            return value.id
        return value

    def process_result_value(self, value: UUID | None, dialect: Dialect) -> T | None:
        if self._type is None:
            raise RuntimeError("Type not set, use EmbeddedUUID[Type]")

        if value is not None:
            return self._type(value)
        return value


class AsJSON[T](types.TypeDecorator[T]):
    """Will serialize to JSON and back everything that TypeAdapter handles."""

    impl = types.JSON
    cache_ok = True

    _type_adapter: TypeAdapter[T]

    def __class_getitem__(cls, type_: Type[T]) -> Self:
        type_adapter = TypeAdapter(type_)
        specialized_class = type(
            f"JSONSerializable[{type_.__name__}]",
            (cls,),
            {"_type_adapter": type_adapter},
        )
        return cast(Self, specialized_class)

    def process_bind_param(self, value: T | None, dialect: Dialect) -> JSON | None:
        if self._type_adapter is None:
            raise RuntimeError(f"Type adapter not set, use {type(self).__name__}[Type]")

        if value is None:
            return value

        return cast(JSON, self._type_adapter.dump_python(value, mode="json"))

    def process_result_value(self, value: JSON | None, dialect: Dialect) -> T | None:
        if value is None:
            return value

        return self._type_adapter.validate_python(value)


TIdentity = TypeVar("TIdentity")


class SQLAlchemyRepository[TModel, TIdentity]:
    _type: Type[TModel]

    def __class_getitem__(cls, type_arg: tuple[Type[TModel], Type[TIdentity]]) -> Self:
        model_type, identity_type = type_arg

        specialized_class = type(
            f"SQLAlchemyRepository[{model_type.__name__}, {identity_type}]",
            (cls,),
            {"_type": model_type},
        )
        return cast(Self, specialized_class)

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, model: TModel) -> None:
        self._session.add(model)
        self._session.flush([model])

    def get(self, id: TIdentity) -> TModel:
        stmt = select(self._type).filter_by(id=id)
        return self._session.execute(stmt).scalar_one()

    def get_all(self, ids: list[TIdentity]) -> Sequence[TModel]:
        stmt = select(self._type).filter(getattr(self._type, "id").in_(ids))
        return self._session.execute(stmt).scalars().all()
