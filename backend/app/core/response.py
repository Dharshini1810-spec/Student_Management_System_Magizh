from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success_response(
    data: Any = None, 
    message: str = "Operation completed successfully", 
    status_code: int = 200
) -> JSONResponse:
    """
    Returns a standardized JSON response for successful operations.
    """
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({
            "success": True,
            "message": message,
            "data": data
        })
    )

def error_response(
    message: str, 
    code: str = "BAD_REQUEST", 
    status_code: int = 400, 
    details: Optional[Any] = None
) -> JSONResponse:
    """
    Returns a standardized JSON response for error states.
    """
    content = {
        "success": False,
        "message": message,
        "error": {
            "code": code
        }
    }
    if details is not None:
        content["error"]["details"] = details
        
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(content)
    )
