from sqlalchemy.future import select
from typing import Type, Generic, TypeVar, List, Optional
from enum import Enum

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, session, id: int) -> Optional[ModelType]:
        result = session.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    def get_all(self, session) -> List[ModelType]:
        result = session.execute(select(self.model))
        return result.scalars().all()

    def create(self, session, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.dict()
        for key, value in obj_data.items():
            if isinstance(value, Enum):
                obj_data[key] = value.value
        obj = self.model(**obj_data)
        session.add(obj)
        session.flush()
        return obj

    def update(self, session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        session.flush()
        return db_obj

    def delete(self, session, id: int) -> None:
        obj = self.get(session, id)
        if obj:
            session.delete(obj)
            session.flush()
