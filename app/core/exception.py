 # Custom Exceptions for the application
 
class DevsphereException(Exception):
     """Base class for all exceptions in the Devsphere application."""
     pass
 

class NotFoundException(DevsphereException):
    """Exception raised when a requested resource is not found."""
    def __init__(self, resource: str = "Resource"):
        self.resource = resource
        super().__init__(f"{resource} not found")
        

class PermissionDeniedException(DevsphereException):
    """Exception raised when a user does not have permission to perform an action."""
    def __init__(self, message: str = "Permission denied"):
        self.message = message
        super().__init__(message)


class ValidationException(DevsphereException):
    """Exception raised for validation errors."""
    def __init__(self, message: str = "Validation error"):
        self.message = message
        super().__init__(message)
        
class AuthenticationException(DevsphereException):
    """Exception raised for authentication errors."""
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(message)