from fastapi import HTTPException, status

class SMSException(HTTPException):
    def __init__(self, status_code: int = status.HTTP_400_BAD_REQUEST, detail: str = 'Bad Request'):
        super().__init__(status_code=status_code, detail=detail)

class NotFoundException(SMSException):
    def __init__(self, detail: str = 'Resource not found'):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class UnauthorizedException(SMSException):
    def __init__(self, detail: str = 'Unauthorized'):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class APIException(SMSException):
    def __init__(
        self,
        message: str = 'API error',
        code: str = 'API_ERROR',
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code

class AuthenticationException(SMSException):
    def __init__(
        self,
        message: str = 'Authentication failed',
        code: str = 'AUTH_FAILED',
        detail: str = None,
    ):
        if detail is not None:
            message = detail
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
        self.code = code

class AuthorizationException(SMSException):
    def __init__(
        self,
        message: str = 'Insufficient permissions',
        code: str = 'ACCESS_DENIED',
        detail: str = None,
    ):
        if detail is not None:
            message = detail
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)
        self.code = code
