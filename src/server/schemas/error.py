from pydantic import BaseModel
from typing import Optional, Any


class ErrorResponse(BaseModel):
    error: str
    error_code: Optional[str] = None
    details: Optional[Any] = None
