#these are non pydantic error classes
#used by service and repository for raising proper errors to be catched by tools


class StateValidationError(Exception):
    """Raised when session state validation fails."""
    pass

class DataAgentServiceError(Exception):
    """Custom exception for general errors within the DataAgentService."""
    pass

class DataAgentRepositoryError(Exception):
    """Custom exception for general errors within the DataAgentRepository."""
    pass

class ReportingServiceError(Exception):
    """Custom exception for general errors within the ReportingService."""
    pass

class ReportingRepositoryError(Exception):
    """Custom exception for general errors within the ReportingRepository."""
    pass

class CommunicationServiceError(Exception):
    """Custom exception for general errors within the CommunicationService."""
    pass

class CommunicationRepositoryError(Exception):
    """Custom exception for general errors within the CommunicationRepository."""
    pass

class ExampleServiceError(Exception):
    """Custom exception for errors related to the ExampleStore service."""
    pass

class ExampleRepositoryError(Exception):
    """Custom exception for errors related to the ExampleStore repository."""
    pass



# class SearchFormattingError(Exception):
#     """Custom exception for errors during search result processing."""
#     pass

# class SearchServiceError(Exception):
#     """Custom exception for general errors within the SearchService."""
#     pass

# class SearchRepositoryError(Exception):
#     """Custom exception for general errors within the SearchRepository."""
#     pass


# class SessionServiceError(Exception):
#     """Custom exception for general errors within the SessionService."""
#     pass

# class SessionRepositoryError(Exception):
#     """Custom exception for general errors within the SessionRepository."""
#     pass


# class CacheRepositoryError(Exception):
#     """Custom exception for general errors within the CacheRepository."""
#     pass



