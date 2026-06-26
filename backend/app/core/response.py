from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None

class SuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None

def success_response(data=None, message: str = "Success") -> SuccessResponse:
    """Helper function to return standardized success responses."""
    return SuccessResponse(success=True, message=message, data=data)
