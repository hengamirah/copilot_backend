from src.core.interface import ExampleRepositoryProtocol
from datetime import datetime
from src.agents.dto.internal.example import ExampleQueryRequestDTO, ExampleQueryResultDTO
from src.agents.dto.response import ResponseDTO, ErrorDTO, ErrorType    

# Updated Service Implementation
class ExampleStoreService:
    def __init__(self, repository: ExampleRepositoryProtocol):
        self.repository = repository
    
    def get_example_data(self, request: ExampleQueryRequestDTO) -> ResponseDTO[ExampleQueryResultDTO]:
        # Add service-level validation if needed
        if not request.query.strip():
            error = ErrorDTO(
                type=ErrorType.EXAMPLE_ERROR,
                message="Query cannot be empty",
                timestamp=datetime.utcnow().isoformat()
            )
            return ResponseDTO.error(error)
        
        # Forward to repository
        return self.repository.get_example_data(request)

    def save_example_data(self, data) -> str:
        return self.repository.save_example_data(data)
        