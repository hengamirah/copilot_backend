from typing import Dict, Optional, Protocol, Any, List
from datetime import datetime
from pandas import DataFrame
from plotly.graph_objs import Figure

from src.agents.dto.response import ResponseDTO, ErrorDTO, ErrorType, ResponseStatus

from src.agents.dto.internal.database import (
    DatabaseQueryRequestDTO,
    QueryRequestDTO,
    RunSQLRequestDTO, 
    GeneratePlotlyCodeRequestDTO,
    GetPlotlyFigureRequestDTO,

    QueryResultDTO,
    GenerateSQLResultDTO,
    RunSQLResultDTO,
    GeneratePlotlyCodeResultDTO,
    GetPlotlyFigureResultDTO

    )

from src.agents.dto.internal.reporting import (
    GenerateReportRequestDTO,
    AnalyzeSqlResultsRequestDTO,
    ReportAnalysisResultDTO
)

class ExampleServiceProtocol(Protocol):
    """
    Protocol for a service that manages examples.
    """
    def save_example_data(self, data: str) -> None:
        """
        Saves example data.
        """   
        ...

    def get_example_data(self) -> str:
        """
        Retrieves example data.
        """
        ...

class ExampleRepositoryProtocol(Protocol):
    """
    Protocol for a repository that manages examples.
    """
    def save_example_data(self, data: str) -> None:
        """
        Saves example data.
        """   
        ...

    def get_example_data(self) -> str:
        """
        Retrieves example data.
        """
        ... 

class ExampleToolProtocol(Protocol):
    """
    Protocol for a tool that manages examples.
    """
    def save_example_data(self, data: str) -> None:
        """
        Saves example data.
        """   
        ...

    def get_example_data(self) -> str:
        """
        Retrieves example data.
        """
        ...

class VannaToolProtocol(Protocol):
    """
    Protocol for a tool that manages vanna.
    """
    def generate_sql_query(self):
        ...
    def execute_sql_query(self):
        ...
    def generate_plot_code(self):
        ...
    def create_plotly_figure(self):
        ...

class VannaRepositoryProtocol(Protocol):
    """
    Protocol for a tool that manages vanna.
    """
    def generate_sql(self, question: str, allow_llm_to_see_data: bool = False) -> str:
        ...

    def run_sql(self, sql: str) -> DataFrame:
        ...

    def generate_plotly_code(self, question: str, sql: str, df_metadata: str = None) -> str:
        ...

    def get_plotly_figure(self, plotly_code: str, df: DataFrame, dark_mode: bool)-> Figure:
        ...

class VannaServiceProtocol(Protocol):
    """
    Protocol for a tool that manages vanna.
    """
    def generate_sql(self, request: QueryRequestDTO) -> ResponseDTO[GenerateSQLResultDTO]:
        ...

    def run_sql(self, request: RunSQLRequestDTO) -> ResponseDTO[RunSQLResultDTO]:
        ...

    def generate_plotly_code(self, request: GeneratePlotlyCodeRequestDTO) -> ResponseDTO[GeneratePlotlyCodeResultDTO]:
        ...

    def get_plotly_figure(self, request: GetPlotlyFigureRequestDTO) -> ResponseDTO[GetPlotlyFigureResultDTO]:
        ...

class HistorianDatabaseRepositoryProtocol(Protocol):
    """
    Protocol for data access operations using DTOs.
    """
    def execute_query(self, query:str, parameters: Dict[str, str]) -> Dict[str, Any]:
        """
        Executes a raw SQL query and returns the results wrapped in a ResponseDTO.
        """
        ...

class HistorianDatabaseServiceProtocol(Protocol):
    def execute_query(self, request: DatabaseQueryRequestDTO) -> QueryResultDTO:
        """
        Executes a raw SQL query using DTOs.
        """
        ...
        
class DatabaseToolProtocol(Protocol):
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Executes a raw SQL query using DTOs.
        """
        ...

class CommunicationServiceProtocol(Protocol):
    def send_message(self, message: str) -> None:
        ...

from typing import Protocol, runtime_checkable


@runtime_checkable
class ReportingRepositoryProtocol(Protocol):
    """Protocol for reporting repository"""
    
    def generate_markdown(
        self,
        title: str,
        generated_at: datetime,
        summary: Optional[str] = None,
        sql_query: Optional[str] = None,
        sql_results: Optional[List[Dict[str, Any]]] = None,
        sql_row_count: Optional[int] = None,
        execution_time_ms: Optional[float] = None,
        chart_url: Optional[str] = None,
        chart_type: Optional[str] = None,
        chart_title: Optional[str] = None,
        chart_description: Optional[str] = None,
        insights: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None
    ) -> str:
        """Generate markdown from report data"""
        ...
    
    def analyze_data(self, sql_results: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """Analyze SQL results"""
        ...

@runtime_checkable
class ReportingServiceProtocol(Protocol):
    """Protocol for reporting service"""
    
    def generate_report(self, request: GenerateReportRequestDTO) -> str:
        """Generate markdown report"""
        ...
    
    def analyze_results(self, request: AnalyzeSqlResultsRequestDTO) -> ReportAnalysisResultDTO:
        """Analyze SQL results"""
        ...

class ReportingToolProtocol(Protocol):
    """Protocol for reporting tool"""
    def generate_report(
        self,
        title: str,
        sql_query: Optional[str] = None,
        sql_results: Optional[List[Dict[str, Any]]] = None,
        chart_url: Optional[str] = None,
        chart_type: Optional[str] = None,
        chart_title: Optional[str] = None,
        summary: Optional[str] = None,
        insights: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
        execution_time_ms: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate a markdown report from components."""
        ...
    
    def analyze_results(
        self,
        sql_results: List[Dict[str, Any]],
        context: str = ""
    ) -> Dict[str, Any]:
        """Analyze SQL results to extract insights."""
        ...
        