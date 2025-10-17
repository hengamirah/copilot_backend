import functools
from datetime import datetime
from src.core import (
    logger,
    ReportingRepositoryProtocol,
    ReportingServiceError,
    ReportingRepositoryError,
)

from src.agents.dto.internal.reporting import (
    GenerateReportRequestDTO,
    AnalyzeSqlResultsRequestDTO,
    ReportAnalysisResultDTO
)

# Service converts DTOs to primitives for repository
class ReportingService:
    """Service layer for report generation"""
    
    def __init__(self, repository: ReportingRepositoryProtocol):
        self.repository = repository
    
    @staticmethod
    def _local_error_handler(func):
        """Decorator for centralized error handling"""
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except ReportingRepositoryError as e:
                logger.warning(f"Repository error in ReportingService: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in ReportingService: {e}", exc_info=True)
                raise ReportingServiceError("Report generation service failed") from e
        return wrapper
    
    @_local_error_handler
    def generate_report(self, request: GenerateReportRequestDTO) -> str:
        """
        Generate a markdown report from request data.
        
        Args:
            request: Report generation request
            
        Returns:
            Formatted markdown report string
        """
        # Service extracts primitives from DTO and passes to repository
        return self.repository.generate_markdown(
            title=request.title,
            generated_at=datetime.now(),
            summary=request.summary,
            sql_query=request.sql_query,
            sql_results=request.sql_results,
            sql_row_count=len(request.sql_results) if request.sql_results else None,
            execution_time_ms=request.execution_time_ms,
            chart_url=request.chart_url,
            chart_type=request.chart_type,
            chart_title=request.chart_title,
            chart_description=f"Visual representation showing {request.chart_type or 'chart'}" if request.chart_url else None,
            insights=request.insights,
            recommendations=request.recommendations
        )
    
    @_local_error_handler
    def analyze_results(self, request: AnalyzeSqlResultsRequestDTO) -> ReportAnalysisResultDTO:
        """Analyze SQL results"""
        # Call repository with primitives
        analysis_data = self.repository.analyze_data(
            sql_results=request.sql_results,
            context=request.context
        )
        
        # Convert raw dict to DTO for response
        return ReportAnalysisResultDTO(
            insights=analysis_data["insights"],
            summary=analysis_data["summary"],
            numeric_columns=analysis_data["numeric_columns"],
            row_count=analysis_data["row_count"]
        )