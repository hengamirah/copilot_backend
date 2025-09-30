#these are non pydantic error classes
#used by service and repository for raising proper errors to be catched by tools
class StateValidationError(Exception):
    """Raised when session state validation fails."""
    pass

class SearchFormattingError(Exception):
    """Custom exception for errors during search result processing."""
    pass

class SearchServiceError(Exception):
    """Custom exception for general errors within the SearchService."""
    pass


class SearchRepositoryError(Exception):
    """Custom exception for general errors within the SearchRepository."""
    pass

class RuleRepositoryError(Exception):
    """Custom exception for general errors within the RuleRepository."""
    pass

class SessionServiceError(Exception):
    """Custom exception for general errors within the SessionService."""
    pass

class SessionRepositoryError(Exception):
    """Custom exception for general errors within the SessionRepository."""
    pass

class ValidationOrchestrationServiceError(Exception):
    """Custom exception for general errors within the ValidationOrchestrationService."""
    pass

class CacheRepositoryError(Exception):
    """Custom exception for general errors within the CacheRepository."""
    pass

class RuleServiceError(Exception):
    """Custom exception for general errors within the RuleService."""
    pass

class ExampleServiceError(Exception):
    """Custom exception for errors related to the ExampleStore service."""
    pass

class ExampleRepositoryError(Exception):
    """Custom exception for errors related to the ExampleStore repository."""
    pass

class LLMResponseError(Exception):
    """Raised when the LLM response cannot be parsed or is invalid."""
    def __init__(self, message: str, text: str = ""):
        super().__init__(message)
        self.text = text # Store the raw response text for logging

    def __str__(self):
        return f"{super().__str__()} | Response Text: '{self.text[:100]}...'"