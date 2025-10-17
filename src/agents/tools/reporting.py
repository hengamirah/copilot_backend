from typing import Optional, Dict, Any, List

from src.agents.utils.utils import global_error_handler_controller
from src.agents.dto.internal.reporting import GenerateReportRequestDTO, AnalyzeSqlResultsRequestDTO, ReportAnalysisResultDTO
from src.agents.dto.response import ResponseDTO, ResponseStatus
from src.core.interface import ReportingServiceProtocol

class ReportingTool:
    """Tool for generating comprehensive reports"""
    
    def __init__(self, service: ReportingServiceProtocol):
        self.service = service
    
    @global_error_handler_controller
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
        """
        Generate a markdown report from components.
        
        Args:
            title: Report title
            sql_query: SQL query that was executed
            sql_results: Results from SQL query
            chart_url: URL of generated chart
            chart_type: Type of chart
            chart_title: Title of chart
            summary: Executive summary
            insights: List of key insights
            recommendations: List of recommendations
            execution_time_ms: Query execution time
            
        Returns:
            ResponseDTO containing the markdown report
        """
        request = GenerateReportRequestDTO(
            title=title,
            sql_query=sql_query,
            sql_results=sql_results,
            chart_url=chart_url,
            chart_type=chart_type,
            chart_title=chart_title,
            summary=summary,
            insights=insights,
            recommendations=recommendations,
            execution_time_ms=execution_time_ms
        )
        
        markdown_report = self.service.generate_report(request)
        
        return ResponseDTO(
            status=ResponseStatus.SUCCESS,
            data={"report": markdown_report}
        ).model_dump()
    
    @global_error_handler_controller
    def analyze_results(
        self,
        sql_results: List[Dict[str, Any]],
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze SQL results to extract insights.
        
        Args:
            sql_results: SQL query results
            context: Context about what the data represents
            
        Returns:
            ResponseDTO containing analysis results
        """
        request = AnalyzeSqlResultsRequestDTO(
            sql_results=sql_results,
            context=context
        )
        
        analysis_result: ReportAnalysisResultDTO = self.service.analyze_results(request)
        
        return ResponseDTO(
            status=ResponseStatus.SUCCESS,
            data=analysis_result
        ).model_dump()