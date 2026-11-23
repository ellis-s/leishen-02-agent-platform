from typing import Optional, TypeVar
from pydantic import BaseModel


T = TypeVar("T")

class ResponseSchema[T](BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

