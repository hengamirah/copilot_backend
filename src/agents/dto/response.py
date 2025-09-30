# DTOs for Response Handling
from pydantic import BaseModel
from typing import Dict, Any, Optional, Generic, TypeVar
from enum import Enum

T = TypeVar('T')

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"

class ErrorType(str, Enum):
    DATABASE_ERROR = "database_error"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    INTERNAL_ERROR = "internal_error"
    EXAMPLE_ERROR = "example_error"


class ErrorDTO(BaseModel):
    type: ErrorType
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class ResponseDTO(BaseModel, Generic[T]):
    status: ResponseStatus
    data: Optional[T] = None
    error: Optional[ErrorDTO] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def success(cls, data: T, metadata: Optional[Dict[str, Any]] = None) -> "ResponseDTO[T]":
        return cls(status=ResponseStatus.SUCCESS, data=data, metadata=metadata)
    
    @classmethod
    def error(cls, error: ErrorDTO, metadata: Optional[Dict[str, Any]] = None) -> "ResponseDTO[T]":
        return cls(status=ResponseStatus.ERROR, error=error, metadata=metadata)

