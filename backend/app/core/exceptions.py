from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.response import error_response

class APIException(Exception):
    """
    Base class for custom API exceptions.
    """
    def __init__(self, message: str, code: str = "API_ERROR", status_code: int = 400, details: Exception = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

class NotFoundException(APIException):
    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(message, code, status_code=status.HTTP_404_NOT_FOUND)

class AuthenticationException(APIException):
    def __init__(self, message: str = "Could not authenticate user", code: str = "AUTHENTICATION_FAILED"):
        super().__init__(message, code, status_code=status.HTTP_401_UNAUTHORIZED)

class AuthorizationException(APIException):
    def __init__(self, message: str = "Not authorized to access resource", code: str = "FORBIDDEN"):
        super().__init__(message, code, status_code=status.HTTP_403_FORBIDDEN)

def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers custom exception handlers to map raw exceptions to standardized responses.
    """
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
        return error_response(
            message=exc.message,
            code=exc.code,
            status_code=exc.status_code,
            details=exc.details
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Standardize standard HTTPExceptions from FastAPI
        code = "HTTP_ERROR"
        if exc.status_code == 404:
            code = "NOT_FOUND"
        elif exc.status_code == 401:
            code = "UNAUTHORIZED"
        elif exc.status_code == 403:
            code = "FORBIDDEN"
        
        return error_response(
            message=str(exc.detail),
            code=code,
            status_code=exc.status_code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Standardize pydantic validation errors
        errors = exc.errors()
        details = []
        for error in errors:
            loc = " -> ".join(str(l) for l in error.get("loc", []))
            details.append({
                "field": loc,
                "type": error.get("type"),
                "message": error.get("msg")
            })
            
        return error_response(
            message="Validation failed",
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Handle unhandled system errors safely without exposing internal details in production
        return error_response(
            message="An unexpected system error occurred",
            code="INTERNAL_SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(exc) if exc.__class__.__name__ != "Exception" else None
        )
