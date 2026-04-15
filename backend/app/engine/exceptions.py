from typing import Any

class ExecutionError(Exception):
    def __init__(self, message, line, type="RuntimeError"):
        self.message = message
        self.line = line
        self.type = type
        super().__init__(self.message)

class FunctionReturn(Exception):
    """Custom exception to signal a function return and carry its value."""
    def __init__(self, value: Any):
        self.value = value
        super().__init__()

class BreakException(Exception):
    pass

class JavaException(Exception):
    """Custom exception to signal a Java-level exception (try-catch-throw)."""
    def __init__(self, type: str, message: str, line: int):
        self.exception_type = type
        self.message = message
        self.line = line
        super().__init__(f"{type}: {message}")
