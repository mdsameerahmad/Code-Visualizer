from typing import Any, List

from app.engine.exceptions import JavaException


class StringExecutor:
    """Execution layer for Java-like String methods."""

    def __init__(self, string_engine):
        self.string_engine = string_engine

    def is_string_like(self, value: Any) -> bool:
        return isinstance(value, str) or (
            isinstance(value, dict) and value.get("type") == "string"
        )

    def normalize_string(self, value: Any, line_number: int) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and value.get("type") == "string":
            return str(value.get("value", ""))
        if value is None:
            raise JavaException("RuntimeException", "Null string access", line_number)
        raise JavaException("RuntimeException", "Target is not a String", line_number)

    def execute(self, base_val: Any, method_name: str, args: List[Any], line_number: int):
        s = self.normalize_string(base_val, line_number)

        if method_name == "length":
            self._expect_arity(method_name, args, [0], line_number)
            return len(s)

        if method_name == "charAt":
            self._expect_arity(method_name, args, [1], line_number)
            idx = int(args[0])
            if 0 <= idx < len(s):
                return s[idx]
            raise JavaException("RuntimeException", f"charAt index out of bounds: {idx}", line_number)

        if method_name == "toUpperCase":
            self._expect_arity(method_name, args, [0], line_number)
            return s.upper()

        if method_name == "toLowerCase":
            self._expect_arity(method_name, args, [0], line_number)
            return s.lower()

        if method_name == "equals":
            self._expect_arity(method_name, args, [1], line_number)
            return s == self._coerce_to_str(args[0])

        if method_name == "equalsIgnoreCase":
            self._expect_arity(method_name, args, [1], line_number)
            return s.lower() == self._coerce_to_str(args[0]).lower()

        if method_name == "substring":
            self._expect_arity(method_name, args, [1, 2], line_number)
            start = int(args[0])
            end = int(args[1]) if len(args) == 2 else len(s)
            if start < 0 or end < start or end > len(s):
                raise JavaException("RuntimeException", f"substring invalid range: {start}, {end}", line_number)
            return s[start:end]

        if method_name == "indexOf":
            self._expect_arity(method_name, args, [1], line_number)
            needle = self._coerce_to_str(args[0])
            return s.find(needle)

        if method_name == "concat":
            self._expect_arity(method_name, args, [1], line_number)
            return s + self._coerce_to_str(args[0])

        if method_name == "replace":
            self._expect_arity(method_name, args, [2], line_number)
            return s.replace(self._coerce_to_str(args[0]), self._coerce_to_str(args[1]))

        return "NO_BUILTIN"

    def _coerce_to_str(self, value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, dict) and value.get("type") == "string":
            return str(value.get("value", ""))
        return str(value)

    def _expect_arity(self, method_name: str, args: List[Any], allowed, line_number: int):
        if len(args) not in allowed:
            msg = f"String.{method_name} expected {allowed} args, got {len(args)}"
            raise JavaException("RuntimeException", msg, line_number)
