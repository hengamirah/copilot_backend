from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Specific DTOs for your use case
class QueryResultRowDTO(BaseModel):
    """Represents a single row from a database query result"""
    data: Dict[str, Any]

class QueryResultDTO(BaseModel):
    """Represents the complete result of a database query"""
    rows: List[QueryResultRowDTO]
    row_count: int
    execution_time_ms: Optional[float] = None

class DatabaseQueryRequestDTO(BaseModel):
    """Represents a database query request"""
    query: str
    parameters: Optional[Dict[str, Any]] = None
    