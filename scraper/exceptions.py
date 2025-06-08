class ScraperError(Exception):
    """Base exception for all scraper-related errors."""
    pass

class AuthenticationError(ScraperError):
    """Raised when login/authentication fails."""
    pass

class DataFetchError(ScraperError):
    """Raised when data fetching fails."""
    pass

class ProcessingError(ScraperError):
    """Raised when data processing fails."""
    pass