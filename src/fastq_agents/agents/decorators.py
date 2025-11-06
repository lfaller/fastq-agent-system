"""Decorators for agent process methods."""

from functools import wraps
from typing import Any, Callable, Dict


def handle_agent_errors(func: Callable) -> Callable:
    """
    Decorator to standardize error handling for agent process methods.

    Catches exceptions, logs them, and returns standardized error response.
    Supports different error types with appropriate categorization.

    Usage:
        @handle_agent_errors
        async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            # Your agent logic here
            pass

    Args:
        func: The async process method to wrap

    Returns:
        Wrapped function with standardized error handling
    """

    @wraps(func)
    async def wrapper(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result: Dict[str, Any] = await func(self, input_data)
            return result
        except ValueError as e:
            # Validation errors (e.g., missing required fields)
            self.log(f"Validation error in {func.__name__}: {e}", "ERROR")
            return {
                "status": "error",
                "error_type": "validation",
                "error_message": str(e),
            }
        except FileNotFoundError as e:
            # File I/O errors
            self.log(f"File not found in {func.__name__}: {e}", "ERROR")
            return {
                "status": "error",
                "error_type": "file_not_found",
                "error_message": str(e),
            }
        except PermissionError as e:
            # Permission errors
            self.log(f"Permission error in {func.__name__}: {e}", "ERROR")
            return {
                "status": "error",
                "error_type": "permission",
                "error_message": str(e),
            }
        except Exception as e:
            # Catch-all for unexpected errors
            self.log(
                f"Unexpected error in {func.__name__}: {type(e).__name__}: {e}",
                "ERROR",
            )
            return {
                "status": "error",
                "error_type": "internal",
                "error_message": str(e),
            }

    return wrapper
