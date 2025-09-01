from typing import Optional

from pydantic import BaseModel


class ErrorOut(BaseModel):
    status_code: Optional[int]
    detail: str
