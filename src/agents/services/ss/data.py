from datetime import datetime
import functools

from src.agents.dto.internal.database import DatabaseQueryRequestDTO, QueryResultDTO
from src.agents.dto.response import ResponseDTO, ErrorDTO, ErrorType    
from src.core import (
    logger, 
    HistorianDatabaseRepositoryProtocol,
    StateValidationError,
    DataAgentServiceError,
    DataAgentRepositoryError,
)

# Updated Service Implementation
class HistorianDatabaseService:
    def __init__(self, repository: HistorianDatabaseRepositoryProtocol):
        self.repository = repository
    
    @staticmethod
    def _local_error_handler(func):
        """
        A static decorator to wrap service methods that call the SearchRepository, providing
        centralized error handling and logging.
        """
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                # Call the original decorated method (e.g., analyze_analysis_rule)
                # 'self' is passed to the wrapper because it's decorating an instance method
                return func(self, *args, **kwargs)
            
            except DataAgentRepositoryError as e:
                # WARNING is better for a caught and re-raised exception.
                logger.warning(f"A general error occured in SearchRepository, propagating up: {e}")
                raise 

            except Exception as e:
                # ERROR is correct for a new, unexpected failure.
                logger.error(f"A general error occurred in SearchService: {e}", exc_info=True)
                raise DataAgentServiceError("A general failure occurred in the data agent service.") from e
                
        return wrapper
    
    @_local_error_handler
    def execute_query(self, request: DatabaseQueryRequestDTO) -> QueryResultDTO:
        # Add service-level validation if needed
        
        data = self.repository.execute_query(
            query = request.query, 
            parameters = request.parameters
        )

        queryResultDTO = QueryResultDTO(
            rows= data['rows'], 
            row_count=data['row_count']
            )
        
        return queryResultDTO

