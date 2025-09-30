from src.core.interface import ExampleDatabaseServiceProtocol
from typing import Dict, Any, Optional
from src.agents.dto.internal.example import ExampleQueryRequestDTO, ExampleQueryResultDTO
from src.agents.dto.response import ResponseDTO
from src.agents.utils.utils import global_error_handler_controller


class Communications:
    def __init__(self, service: ExampleDatabaseServiceProtocol):
        self.service = service