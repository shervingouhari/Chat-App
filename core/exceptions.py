from fastapi import HTTPException, status

from .logging import log


class ChatAppAPIError(HTTPException):
    """The base class for all ChatApp exceptions."""

    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An unexpected error occurred."
    default_resolution = "Try again later or report the bug."

    def __init__(self, status_code: int = None, detail: str = None, resolution: str = None):
        self.status_code = status_code or self.default_status_code
        self.detail = detail or self.default_detail
        self.resolution = resolution or self.default_resolution
        log.error(
            f"{self.__class__.__name__} | {self.status_code} | {self.detail}"
        )
        super().__init__(
            status_code=self.status_code,
            detail={
                "type": self.__class__.__name__,
                "message": self.detail,
                "resolution": self.resolution,
            })


class EntityDoesNotExistError(ChatAppAPIError):
    """Raised when a requested entity does not exist in the database."""

    default_status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Document does not exist in the database."
    default_resolution = "Ensure the entity ID or query parameters are correct, and the entity exists before attempting to retrieve it."


class EntityAlreadyExistsError(ChatAppAPIError):
    """Raised when an attempt is made to create an entity that already exists in the database."""

    default_status_code = status.HTTP_409_CONFLICT
    default_detail = "Document already exists in the database."
    default_resolution = "Try creating a record with unique identifiers or modify the existing entity instead."


class AuthenticationFailedError(ChatAppAPIError):
    """Raised when user authentication fails due to incorrect credentials."""

    default_status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication failed."
    default_resolution = "Ensure that your username and password are correct and try again."
