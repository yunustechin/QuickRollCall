from fastapi import HTTPException, status

class SessionNotFoundOrClosedError(HTTPException):
    """Raised when an operation is attempted on a session that does not exist or has already been closed."""
    def __init__(self, session_id: str):
        super().__init__(
            status_code=status.HTTP_410_GONE , 
            detail=f"Session '{session_id}' is closed or does not exist."
        )

class TokenInvalidError(HTTPException):
    """Raised when a provided one-time access token is invalid, expired, or has already been used."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access token is invalid, expired, or has already been used."
        )

class TokenMismatchError(HTTPException):
    """Raised when a valid token is used for a session it does not belong to."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Token does not match the session."
        )

class DuplicateAttendanceError(HTTPException):
    """Raised when a student attempts to submit attendance more than once for the same session."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Attendance already submitted for this student in this session."
        )

class APIServiceError(HTTPException):
    """A generic exception for internal service failures, such as a database operation failing."""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(
            status_code=status_code, 
            detail=detail
        )

