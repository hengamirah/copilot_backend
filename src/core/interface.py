from typing import Dict, Optional, Protocol
from src.agents.dto.internal.database import QueryResultDTO, DatabaseQueryRequestDTO
from src.agents.dto.response import ResponseDTO

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
    
class HistorianDatabaseRepositoryProtocol(Protocol):
    """
    Protocol for data access operations using DTOs.
    """
    def execute_query(self, request: DatabaseQueryRequestDTO) -> ResponseDTO[QueryResultDTO]:
        """
        Executes a raw SQL query and returns the results wrapped in a ResponseDTO.
        """
        ...

class HistorianDatabaseServiceProtocol(Protocol):
    def execute_query(self, request: DatabaseQueryRequestDTO) -> ResponseDTO[QueryResultDTO]:
        """
        Executes a raw SQL query using DTOs.
        """
        ...
        
class DatabaseToolProtocol(Protocol):
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> ResponseDTO[QueryResultDTO]:
        """
        Executes a raw SQL query using DTOs.
        """
        ...