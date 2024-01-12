from typing import TypeVar
from sqlalchemy.ext.declarative import DeclarativeMeta
from pydantic import BaseModel


ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
SerializerType = TypeVar("SerializerType", bound=BaseModel)
