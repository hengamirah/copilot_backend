from src.core.interface import HistorianDatabaseRepositoryProtocol
from datetime import datetime
from src.agents.dto.internal.database import DatabaseQueryRequestDTO, QueryResultDTO
from src.agents.dto.response import ResponseDTO, ErrorDTO, ErrorType    

# Updated Service Implementation
class HistorianDatabaseService:
    def __init__(self, repository: HistorianDatabaseRepositoryProtocol):
        self.repository = repository
    
    def execute_query(self, request: DatabaseQueryRequestDTO) -> ResponseDTO[QueryResultDTO]:
        # Add service-level validation if needed
        if not request.query.strip():
            error = ErrorDTO(
                type=ErrorType.VALIDATION_ERROR,
                message="Query cannot be empty",
                timestamp=datetime.utcnow().isoformat()
            )
            return ResponseDTO.error(error)
        
        # Forward to repository
        return self.repository.execute_query(request)