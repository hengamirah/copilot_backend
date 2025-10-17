from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SqlQueryResult(BaseModel):
    """Represents SQL query and its results"""
    query: str = Field(..., description="The SQL query that was executed")
    results: List[Dict[str, Any]] = Field(..., description="Query results as list of dictionaries")
    execution_time_ms: Optional[float] = Field(None, description="Query execution time in milliseconds")
    row_count: int = Field(..., description="Number of rows returned")


class VisualizationData(BaseModel):
    """Represents visualization information"""
    chart_url: str = Field(..., description="URL of the generated chart")
    chart_type: str = Field(..., description="Type of chart (bar, line, pie, etc.)")
    chart_title: Optional[str] = Field(None, description="Title of the chart")
    description: Optional[str] = Field(None, description="Description of what the chart shows")


class ReportData(BaseModel):
    """Complete report data structure"""
    title: str = Field(..., description="Report title")
    sql_data: Optional[SqlQueryResult] = Field(None, description="SQL query and results")
    visualization: Optional[VisualizationData] = Field(None, description="Chart visualization data")
    summary: Optional[str] = Field(None, description="Executive summary")
    insights: Optional[List[str]] = Field(None, description="Key insights from the data")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations based on findings")

# ============================================================================
# DTOs (src/agents/dto/internal/reporting.py)
# ============================================================================
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class SqlQueryResultDTO(BaseModel):
    """Represents SQL query results for reporting"""
    query: str = Field(..., min_length=1, description="SQL query that was executed")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Query results")
    row_count: int = Field(..., ge=0, description="Number of rows returned")
    execution_time_ms: Optional[float] = Field(None, ge=0, description="Execution time in milliseconds")
    
    @field_validator('query')
    @classmethod
    def validate_query_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty")
        return v


class VisualizationDataDTO(BaseModel):
    """Represents visualization data for reporting"""
    chart_url: str = Field(..., min_length=1, description="URL or path to chart image")
    chart_type: str = Field(..., min_length=1, description="Type of chart (bar, line, pie, etc.)")
    chart_title: Optional[str] = Field(None, description="Title of the chart")
    description: Optional[str] = Field(None, description="Description of the visualization")
    
    @field_validator('chart_url', 'chart_type')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v


class ReportDataDTO(BaseModel):
    """Complete report data"""
    title: str = Field(..., min_length=1, description="Report title")
    sql_data: Optional[SqlQueryResultDTO] = Field(None, description="SQL query data")
    visualization: Optional[VisualizationDataDTO] = Field(None, description="Visualization data")
    summary: Optional[str] = Field(None, description="Executive summary")
    insights: Optional[List[str]] = Field(default_factory=list, description="Key insights")
    recommendations: Optional[List[str]] = Field(default_factory=list, description="Recommendations")
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v


class GenerateReportRequestDTO(BaseModel):
    """Request to generate a report"""
    title: str = Field(..., min_length=1, description="Report title")
    sql_query: Optional[str] = Field(None, description="SQL query that was executed")
    sql_results: Optional[List[Dict[str, Any]]] = Field(None, description="Results from SQL query")
    chart_url: Optional[str] = Field(None, description="URL of generated chart")
    chart_type: Optional[str] = Field(None, description="Type of chart")
    chart_title: Optional[str] = Field(None, description="Title of chart")
    summary: Optional[str] = Field(None, description="Executive summary")
    insights: Optional[List[str]] = Field(None, description="List of key insights")
    recommendations: Optional[List[str]] = Field(None, description="List of recommendations")
    execution_time_ms: Optional[float] = Field(None, ge=0, description="Query execution time")
    
    @field_validator('title')
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v


class AnalyzeSqlResultsRequestDTO(BaseModel):
    """Request to analyze SQL results"""
    sql_results: List[Dict[str, Any]] = Field(..., description="SQL query results to analyze")
    context: str = Field("", description="Context about what the data represents")
    
    @field_validator('sql_results')
    @classmethod
    def validate_results_not_empty(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not v:
            raise ValueError("SQL results cannot be empty")
        return v


class ReportAnalysisResultDTO(BaseModel):
    """Result of SQL results analysis"""
    insights: List[str] = Field(..., description="Generated insights")
    summary: str = Field(..., description="Analysis summary")
    numeric_columns: List[str] = Field(default_factory=list, description="Numeric columns found")
    row_count: int = Field(..., ge=0, description="Number of rows analyzed")
