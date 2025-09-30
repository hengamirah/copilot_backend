from typing import Callable, List, Dict, Any, Union
import functools
import traceback
import uuid
import json
import os
from pathlib import Path

from src.agents.dto import (
    ErrorDTO,
    ResponseDTO,
)

from src.core import (
    SearchServiceError, 
    SearchFormattingError, 
    StateValidationError,
    RuleServiceError,
    LLMResponseError,
    SearchRepositoryError,
    RuleRepositoryError,
    SessionServiceError,
    ValidationOrchestrationServiceError,
    logger
)

def global_error_handler_controller(func: Callable) -> Callable:
    """
    A decorator to catch specific known exceptions and format a standard error response.
    This decorator catches known exceptions (e.g., SearchServiceError, StateValidationError)
    and general exceptions, logging them and returning a standardized error response
    using `ResponseDTO`. This ensures that API calls from the agent always receive
    a consistent response format, even in case of failures.
    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The decorated function with error handler built in.

    Notes:
        This decorator is intended for use with methods of classes that are
        exposed as tools to the agent. It ensures that any errors are
        gracefully handled and a structured error response is returned,
        preventing the agent from receiving malformed or unhandled exceptions.
        
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Run the original function
            return func(*args, **kwargs)

        #errors for search service
        except SearchRepositoryError as e:
            logger.error(f"A general error occurred in {func.__name__}: {e}", exc_info=True)
            error_dto = ErrorDTO(code="SEARCH_REPOSITORY_ERROR", message=str(e))
            return ResponseDTO[None](status="error", error=error_dto).model_dump()
        
        except SearchFormattingError as e:
            logger.error(f"A formatting error occurred in {func.__name__}: {e}", exc_info=True)
            error_dto = ErrorDTO(code="SEARCH_FORMATTING_ERROR", message=str(e))
            return ResponseDTO[None](status="error", error=error_dto).model_dump()

        except SearchServiceError as e:
            logger.error(f"A general error occurred in {func.__name__}: {e}", exc_info=True)
            error_dto = ErrorDTO(code="SEARCH_SERVICE_ERROR", message=str(e))
            return ResponseDTO[None](status="error", error=error_dto).model_dump()
        
        #errors for rule service
        except LLMResponseError as e:
            logger.error(f"A llm parsing error occurred in {func.__name__}: {e}", exc_info=True)
            error_dto = ErrorDTO(code="LLM_RESPONSE_ERROR", message=str(e))
            return ResponseDTO[None](status="error", error=error_dto).model_dump()
        
        except RuleRepositoryError as e:
            logger.error(f"A general error occurred in {func.__name__}: {e}", exc_info=True)
            error_dto = ErrorDTO(code="RULE_REPOSITORY_ERROR", message=str(e))
            return ResponseDTO[None](status="error", error=error_dto).model_dump()

        except RuleServiceError as e:
            logger.error(f"A general error occurred in {func.__name__}: {e}", exc_info=True)
            error_dto = ErrorDTO(code="RULE_SERVICE_ERROR", message=str(e))
            return ResponseDTO[None](status="error", error=error_dto).model_dump()
        
        #errors for state service
        except StateValidationError as e:
            logger.warning(f"State validation failed in {func.__name__}: {e}", exc_info=True)
            error_dto = ErrorDTO(code="VALIDATION_ERROR", message=str(e))
            return ResponseDTO[None](status="error", error=error_dto).model_dump()
        
        except SessionServiceError as e:
            logger.error(f"A session service error occurred in {func.__name__}: {e}", exc_info=True)
            error_dto = ErrorDTO(code="SESSION_SERVICE_ERROR", message=str(e))
            return ResponseDTO[None](status="error", error=error_dto).model_dump()
        
        except ValidationOrchestrationServiceError as e:   
            logger.error(f"A validation orchestration service error occurred in {func.__name__}: {e}", exc_info=True)
            error_dto = ErrorDTO(code="VALIDATION_ORCHESTRATION_SERVICE_ERROR", message=str(e))
            return ResponseDTO[None](status="error", error=error_dto).model_dump()
            
        except (ValueError, RuntimeError) as e:
            logger.error(f"A runtime error occurred in {func.__name__}: {e}", exc_info=True)
            error_dto = ErrorDTO(code="RUNTIME_ERROR", message=str(e))
            
            return ResponseDTO[None](status="error", error=error_dto).model_dump()
        
        except Exception as e:
            # A final catch-all for any other unexpected error
            # 1. Generate a unique ID for this specific error instance.
            error_id = uuid.uuid4()
            # 2. Get the full, formatted traceback as a string.
            traceback_str = traceback.format_exc()
            logger.critical(f"An unexpected error occurred in {func.__name__}: {e}", exc_info=True)
            logger.critical(f"Unexpected error in {func.__name__} [Error ID: {error_id}]:\n{traceback_str}")
            error_dto = ErrorDTO(
                code="INTERNAL_SERVER_ERROR", 
                message=f"An unexpected internal error occurred {e} and error id {error_id}."
                )
            return ResponseDTO[None](status="error", error=error_dto).model_dump()

    return wrapper


def list_json_files_pathlib(directory_path: str) -> List[Path]:
    folder = Path(directory_path)
    json_files = list(folder.glob('*.json'))
    return json_files


def parse_json_file_to_dict(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Reads a file containing JSON data and parses it into a Python dictionary.

    Args:
        file_path: The full path (string or Path object) to the JSON file. 
        
    Returns:
        A Python dictionary created from the file content, 
        or an empty dictionary if the file cannot be read or parsing fails.
    """

    try:
        # Ensure file_path is treated as a string for open() if it was a Path object
        path_str = str(file_path)
        
        with open(path_str, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)
            return data_dict
    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file_path}: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred with file {file_path}: {e}")
        return {}

