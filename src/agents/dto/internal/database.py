from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Any, Optional
import re

from pandas import DataFrame
# # Import pandas and plotly for type hints and validation
# try:
#     from plotly.graph_objs import Figure
#     PANDAS_AVAILABLE = True
#     PLOTLY_AVAILABLE = True
# except ImportError:
#     # Fallback to Any if libraries not available
#     pd = Any  # type: ignore
#     Figure = Any  # type: ignore
#     PANDAS_AVAILABLE = False
#     PLOTLY_AVAILABLE = False

# === Query Result DTOs ===
class QueryResultRowDTO(BaseModel):
    """Represents a single row from a database query result"""
    data: Dict[str, Any] = Field(..., description="Key-value pairs representing column names and values")
    
    @field_validator('data')
    @classmethod
    def validate_data_not_empty(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure data dictionary is not empty"""
        if not v:
            raise ValueError("Data dictionary cannot be empty")
        return v

class QueryResultDTO(BaseModel):
    """Represents the complete result of a database query"""
    rows: List[QueryResultRowDTO] = Field(default_factory=list, description="List of query result rows")
    row_count: int = Field(..., ge=0, description="Total number of rows returned")
    execution_time_ms: Optional[float] = Field(None, ge=0, description="Query execution time in milliseconds")
    
    @model_validator(mode='after')
    def validate_row_count_matches(self):
        """Ensure row_count matches the actual number of rows"""
        if self.row_count != len(self.rows):
            raise ValueError(
                f"row_count ({self.row_count}) does not match actual number of rows ({len(self.rows)})"
            )
        return self

class DatabaseQueryRequestDTO(BaseModel):
    """Represents a database query request"""
    query: str = Field(..., min_length=1, description="SQL query to execute")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Query parameters for parameterized queries")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate SQL query is not empty and contains valid SQL keywords"""
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty or only whitespace")
        
        # Check for basic SQL keywords
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'WITH']
        upper_query = v.upper()
        if not any(keyword in upper_query for keyword in sql_keywords):
            raise ValueError("Query must contain valid SQL keywords")

        # Check for dangerous operations
        dangerous_patterns = [
            r'\bDROP\s+DATABASE\b',
            r'\bDROP\s+SCHEMA\b',
            r'\bTRUNCATE\b',
        ]
        upper_sql = v.upper()
        for pattern in dangerous_patterns:
            if re.search(pattern, upper_sql):
                # Changed to PermissionError for security violations
                raise PermissionError(f"Dangerous SQL operation not allowed: {pattern}")
        
        return v

# === Vanna Data Agent Request DTOs ===
class QueryRequestDTO(BaseModel):
    """Request to generate and optionally execute SQL from a natural language question"""
    question: str = Field(..., min_length=1, description="Natural language question to convert to SQL")
    allow_llm_to_see_data: bool = Field(True, description="Whether to allow LLM to see actual data results")
    
    @field_validator('question')
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate question is meaningful"""
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty or only whitespace")
        if len(v) < 3:
            raise ValueError("Question must be at least 3 characters long")
        return v

class RunSQLRequestDTO(BaseModel):
    """Request to execute a SQL query"""
    sql: str = Field(..., min_length=1, description="SQL query to execute")
    
    @field_validator('sql')
    @classmethod
    def validate_sql(cls, v: str) -> str:
        """Validate SQL query"""
        v = v.strip()
        if not v:
            raise ValueError("SQL query cannot be empty or only whitespace")
        
        # Check for dangerous operations
        dangerous_patterns = [
            r'\bDROP\s+DATABASE\b',
            r'\bDROP\s+SCHEMA\b',
            r'\bTRUNCATE\b',
        ]
        upper_sql = v.upper()
        for pattern in dangerous_patterns:
            if re.search(pattern, upper_sql):
                # Changed to PermissionError for security violations
                raise PermissionError(f"Dangerous SQL operation not allowed: {pattern}")
        
        return v

class GeneratePlotlyCodeRequestDTO(BaseModel):
    """Request to generate Plotly visualization code"""
    question: str = Field(..., min_length=1, description="Natural language question about the visualization")
    sql: str = Field(..., min_length=1, description="SQL query that generated the data")
    df_metadata: Optional[str] = Field(None, description="Metadata about the DataFrame structure")
    
    @field_validator('question', 'sql')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure fields are not empty or whitespace"""
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty or only whitespace")
        return v

class GetPlotlyFigureRequestDTO(BaseModel):
    """Request to create a Plotly figure from generated code"""
    plotly_code: str = Field(..., min_length=1, description="Python code to generate the Plotly figure")
    df: DataFrame = Field(..., description="DataFrame containing the data to visualize")
    dark_mode: bool = Field(False, description="Whether to apply dark mode styling")
    
    class Config:
        arbitrary_types_allowed = True
    
    @field_validator('plotly_code')
    @classmethod
    def validate_plotly_code(cls, v: str) -> str:
        """Validate Plotly code is not empty and looks like Python code"""
        v = v.strip()
        if not v:
            raise ValueError("Plotly code cannot be empty")
        
        # Basic check for Python/Plotly indicators
        if 'fig' not in v.lower() and 'figure' not in v.lower():
            raise ValueError("Plotly code should contain 'fig' or 'figure' reference")
        
        return v
    
    @field_validator('df')
    @classmethod
    def validate_dataframe(cls, v: Any) -> Any:
        """Validate that df is a pandas DataFrame"""
        try:
            import pandas as pd
            if not isinstance(v, pd.DataFrame):
                # Changed to TypeError for type mismatch
                raise TypeError("df must be a pandas DataFrame")
            if v.empty:
                raise ValueError("DataFrame cannot be empty")
        except ImportError:
            pass  # Skip validation if pandas not available
        return v

# === Vanna Data Agent Response DTOs ===
class GenerateSQLResultDTO(BaseModel):
    """Response containing generated SQL query"""
    result: str = Field(..., description="Generated SQL query")

    @field_validator('result')
    @classmethod
    def validate_result(cls, v: str) -> str:
        """Ensure result is not empty"""
        if not v or not v.strip():
            raise ValueError("SQL result cannot be empty")
        return v.strip()

class RunSQLResultDTO(BaseModel):
    """Response containing SQL query execution results"""
    result: Any = Field(..., description="DataFrame containing query results")
    row_count: Optional[int] = Field(None, ge=0, description="Number of rows returned")
    execution_time_ms: Optional[float] = Field(None, ge=0, description="Execution time in milliseconds")
    
    class Config:
        arbitrary_types_allowed = True
    
    @field_validator('result')
    @classmethod
    def validate_result_dataframe(cls, v: Any) -> Any:
        """Validate that result is a DataFrame"""
        try:
            import pandas as pd
            if not isinstance(v, pd.DataFrame):
                # Changed to TypeError for type mismatch
                raise TypeError("Result must be a pandas DataFrame")
        except ImportError:
            pass
        return v
    
    @model_validator(mode='after')
    def validate_row_count_if_present(self):
        """Validate row_count matches DataFrame if both are present"""
        if self.row_count is not None:
            try:
                import pandas as pd
                if isinstance(self.result, pd.DataFrame):
                    actual_count = len(self.result)
                    if self.row_count != actual_count:
                        raise ValueError(
                            f"row_count ({self.row_count}) does not match DataFrame length ({actual_count})"
                        )
            except ImportError:
                pass
        return self

class GeneratePlotlyCodeResultDTO(BaseModel):
    """Response containing generated Plotly code"""
    result: str = Field(..., description="Generated Plotly visualization code")
    
    @field_validator('result')
    @classmethod
    def validate_plotly_code_result(cls, v: str) -> str:
        """Validate generated Plotly code"""
        if not v or not v.strip():
            raise ValueError("Plotly code result cannot be empty")
        
        v = v.strip()
        # Check for basic Plotly indicators
        plotly_indicators = ['plotly', 'go.', 'px.', 'graph_objects', 'express']
        if not any(indicator in v.lower() for indicator in plotly_indicators):
            raise ValueError("Result does not appear to contain Plotly code")
        
        return v

class GetPlotlyFigureResultDTO(BaseModel):
    """Response containing Plotly figure"""
    result: Any = Field(..., description="Plotly Figure object")
    
    class Config:
        arbitrary_types_allowed = True
    
    @field_validator('result')
    @classmethod
    def validate_figure(cls, v: Any) -> Any:
        """Validate that result is a Plotly Figure"""
        try:
            from plotly.graph_objs import Figure
            if not isinstance(v, Figure):
                # Changed to TypeError for type mismatch
                raise TypeError("Result must be a Plotly Figure object")
        except ImportError:
            pass
        return v

