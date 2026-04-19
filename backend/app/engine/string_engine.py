import re
from typing import Any, Callable, List, Optional


class StringEngine:
    """Parsing/resolution helpers for Java-like String expressions."""

    def decode_literal(self, expr: str) -> Optional[str]:
        expr = expr.strip()
        if len(expr) >= 2 and expr[0] == '"' and expr[-1] == '"':
            raw = expr[1:-1]
            return bytes(raw, "utf-8").decode("unicode_escape")
        return None

    def split_top_level_plus(self, expr: str) -> List[str]:
        parts: List[str] = []
        current = []
        paren = bracket = brace = 0
        in_string = False
        escaped = False

        for ch in expr:
            if in_string:
                current.append(ch)
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
                current.append(ch)
                continue
            if ch == "(":
                paren += 1
            elif ch == ")":
                paren -= 1
            elif ch == "[":
                bracket += 1
            elif ch == "]":
                bracket -= 1
            elif ch == "{":
                brace += 1
            elif ch == "}":
                brace -= 1

            if ch == "+" and paren == 0 and bracket == 0 and brace == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(ch)

        parts.append("".join(current).strip())
        return [p for p in parts if p != ""]

    def try_concat_expression(
        self, expr: str, value_resolver: Callable[[str], Any]
    ) -> Optional[str]:
        parts = self.split_top_level_plus(expr)
        if len(parts) < 2:
            return None

        values = [value_resolver(part) for part in parts]
        if not any(isinstance(v, str) for v in values):
            return None

        # Java '+' semantics are left-associative:
        # 1 + 2 + "A" => (1 + 2) + "A" => "3A"
        acc: Any = values[0]
        used_string_concat = isinstance(acc, str)

        for nxt in values[1:]:
            if isinstance(acc, str) or isinstance(nxt, str):
                used_string_concat = True
                acc = self._java_stringify(acc) + self._java_stringify(nxt)
            else:
                acc = acc + nxt

        return self._java_stringify(acc) if used_string_concat else None

    def _java_stringify(self, value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, dict) and value.get("type") == "array":
            return str(value.get("values", []))
        return str(value)

    def parse_operation_hints(self, line_content: str) -> dict:
        """Best-effort operation hints for string-specific visualization."""
        hints = {"charAt": None, "substring": None}
        char_at = re.search(r"(\w+)\.charAt\(([^)]+)\)", line_content or "")
        if char_at:
            hints["charAt"] = {"name": char_at.group(1), "index": char_at.group(2).strip()}
        substring = re.search(r"(\w+)\.substring\(([^)]+)\)", line_content or "")
        if substring:
            args = [a.strip() for a in substring.group(2).split(",")]
            hints["substring"] = {"name": substring.group(1), "args": args}
        return hints
