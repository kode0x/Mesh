"""
Custom exception classes for the Mesh application.

Provides domain-specific exceptions for better error handling and differentiation.
"""


class MeshException(Exception):
    """Base exception for all Mesh application errors."""
    
    pass


class ValidationError(MeshException):
    """Raised when user input validation fails."""
    
    pass


class ConfigurationError(MeshException):
    """Raised when configuration is invalid or missing."""
    
    pass


class APIError(MeshException):
    """Raised when API calls fail."""
    
    def __init__(self, code: int, reason: str, details: str = ""):
        self.code = code
        self.reason = reason
        self.details = details
        super().__init__(f"API Error {code}: {reason}")


class FileNotFoundError(MeshException):
    """Raised when required files are not found."""
    
    pass


class ProjectError(MeshException):
    """Raised when project operations fail."""
    
    pass
