from typing import Any, Sequence

from pydantic import BaseModel


class GenericResponse(BaseModel):
    status_code: int
    detail: str

class GenericResponseWithData(GenericResponse):
    data: Any

class GenericResponseWithSequenceData(GenericResponseWithData):
    data: Sequence[Any]