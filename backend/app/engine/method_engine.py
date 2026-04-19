"""
Thin facade: method calls are implemented in RecursionFunctionExecutor (single source of truth).
"""
from typing import Any, List

from app.engine.recursion_function_executor import RecursionFunctionExecutor


class MethodEngine:
    def __init__(self, executor):
        self._invoker = RecursionFunctionExecutor(executor)

    def call(self, full_method_name: str, args: List[Any], line_number: int, steps: List) -> Any:
        return self._invoker.execute_invocation(full_method_name, args, line_number, steps)
