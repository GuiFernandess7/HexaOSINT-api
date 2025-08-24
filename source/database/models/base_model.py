from dataclasses import dataclass
from sqlalchemy.orm import DeclarativeBase, registry
from datetime import datetime, date
from sqlalchemy.inspection import inspect

table_registry = registry()


class Base(DeclarativeBase):
    registry = table_registry


@dataclass
class BaseModel(Base):
    __abstract__ = True

    def as_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            c.key: serialize_values(getattr(self, c.key))
            for c in inspect(self).mapper.column_attrs
        }

    def __init__(self, **kwargs):
        """Initialize the model with keyword arguments."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        super().__init__(**kwargs)


def serialize_values(value):
    """Serialize values for JSON compatibility."""
    if isinstance(value, (list, tuple)):
        return [serialize_values(v) for v in value]
    elif isinstance(value, dict):
        return {k: serialize_values(v) for k, v in value.items()}
    elif hasattr(value, "isoformat"):
        return value.isoformat()
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    return value
