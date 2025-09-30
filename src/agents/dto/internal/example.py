from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Specific DTOs for your use case
class ExampleQueryResultRowDTO(BaseModel):
    """Represents a single row from a example query result"""
    data: Dict[str, Any]

class ExampleQueryResultDTO(BaseModel):
    """Represents the complete result of a example query"""
    rows: List[ExampleQueryResultRowDTO]
    row_count: int
    execution_time_ms: Optional[float] = None

class ExampleQueryRequestDTO(BaseModel):
    """Represents a example query request"""
    query: str
    filter: Optional[Dict[str, Any]] = None
    