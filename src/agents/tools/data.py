from typing import Dict, Any, Optional

from src.agents.utils.utils import global_error_handler_controller
from src.core.interface import HistorianDatabaseServiceProtocol
from src.agents.dto import (
    ResponseDTO,
    ResponseStatus, 
    DatabaseQueryRequestDTO, 
    QueryResultDTO
)

class DatabaseTool:

    def __init__(self, service: HistorianDatabaseServiceProtocol):
        self.service = service

    @global_error_handler_controller
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a raw SQL query against the database and returns the results wrapped in ResponseDTO.
        
        Args:
            query: The full SQL query string.
            parameters: (Optional) A dictionary of bind parameters to safely pass into the query.
        
        Returns:
            A ResponseDTO containing either successful QueryResultDTO or error information.
        """
        request = DatabaseQueryRequestDTO(
            query=query, 
            parameters=parameters
        )
        
        queryResultDTO: QueryResultDTO = self.service.execute_query(request)

        return ResponseDTO(status=ResponseStatus.SUCCESS, data=queryResultDTO).model_dump()

