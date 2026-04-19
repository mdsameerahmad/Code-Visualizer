import re
import json
from typing import Any, List
from app.engine.exceptions import JavaException


class ExpressionEngine:
    def __init__(self, executor):
        self.executor = executor
        self.keywords = {
            'if', 'for', 'while', 'switch', 'return', 'new',
            'public', 'static', 'class', 'String', 'boolean',
            'int', 'char', 'float', 'double', 'long', 'byte', 'short',
            'ArrayList', 'HashMap', 'null', 'true', 'false'
        }

    def evaluate(self, expr: str, line_number: int, steps: List) -> Any:
        expr = expr.strip()
        if not expr:
            return None

        # ---------------- DIRECT SYMBOL RESOLUTION (preserve references) ----------------
        # If the expression is just a single symbol like `arr` or `obj.field`, return the
        # underlying value directly. This is critical for arrays/objects: using _safe_repr +
        # eval would materialize a *copy* (breaking pass-by-reference across stack frames).
        if re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*', expr) and expr not in self.keywords:
            try:
                val = self.executor._get_var(expr)
                if val is not None:
                    return val
            except Exception:
                # Fall through to normal evaluation for cases like unresolved members
                pass

        # ---------------- LITERALS ----------------
        decoded = self.executor.runtime_engine.string_engine.decode_literal(expr)
        if decoded is not None:
            return decoded

        if expr == 'true': return True
        if expr == 'false': return False
        if expr == 'null': return None

        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except:
            pass

        # ---------------- OBJECT CREATION ----------------
        if expr.startswith('new '):
            builtin = self.executor.runtime_engine.create_builtin_object(expr, line_number, steps)
            if builtin is not None:
                return builtin

            match = re.match(r'new\s+([\w\.]+)\s*\(([^)]*)\)', expr)
            if match:
                class_name, args_str = match.groups()

                eval_args = [
                    self.evaluate(a, line_number, steps)
                    for a in self.executor._parse_method_args(args_str)
                ]

                obj_id = self.executor.memory.create_object(class_name)

                self.executor.oop_engine.execute_constructor(
                    class_name, obj_id, eval_args, line_number, steps
                )

                return obj_id

        # ---------------- LITERAL BASE METHOD CALLS ----------------
        # Handle calls like:
        #   "ABC".equalsIgnoreCase("abc")
        #   "hello".length()
        # before generic method parsing, so dispatch uses StringExecutor.
        literal_base_method_pattern = re.compile(r'("([^"\\]|\\.)*")\s*\.\s*([\w]+)\s*\(')
        while True:
            m = literal_base_method_pattern.search(expr)
            if not m:
                break

            start = m.end() - 1
            end = self.executor._find_matching_paren(expr, start)
            if end == -1:
                break

            base_expr = m.group(1)
            method_name = m.group(3)
            args_raw = self.executor._parse_method_args(expr[start + 1:end])
            eval_args = [self.evaluate(a, line_number, steps) for a in args_raw]
            base_val = self.evaluate(base_expr, line_number, steps)

            result = self.executor.runtime_engine.handle_builtin_method(
                base_val, method_name, eval_args, line_number
            )
            if result == "NO_BUILTIN":
                raise JavaException(
                    "RuntimeException",
                    f"String method '{method_name}' not found",
                    line_number,
                )

            replacement = self._safe_repr(result)
            expr = expr[:m.start()] + replacement + expr[end + 1:]

        # ---------------- METHOD CALLS ----------------
        method_pattern = re.compile(r'\b([\w\.]+)\s*\(')

        while True:
            matches = list(method_pattern.finditer(expr))
            if not matches:
                break

            match = None
            for m in reversed(matches):
                if m.group(1) not in self.keywords:
                    match = m
                    break

            if not match:
                break

            start = match.end() - 1
            end = self.executor._find_matching_paren(expr, start)
            if end == -1:
                break

            full_name = match.group(1)
            args_raw = self.executor._parse_method_args(expr[start + 1:end])

            eval_args = [
                self.evaluate(a, line_number, steps)
                for a in args_raw
            ]

            result = self.executor.method_engine.call(
                full_name, eval_args, line_number, steps
            )

            replacement = self._safe_repr(result)
            expr = expr[:match.start()] + replacement + expr[end + 1:]

        # ---------------- ARRAY ACCESS ----------------
        array_pattern = re.compile(r'(\w+)\[([^\[\]]+)\]')

        while True:
            match = array_pattern.search(expr)
            if not match:
                break

            name, idx_expr = match.groups()
            idx = self.evaluate(idx_expr, line_number, steps)
            arr = self.executor._get_var(name)

            if arr is None:
                raise JavaException("NullPointerException", name, line_number)
            if not isinstance(arr, dict) or arr.get("type") != "array" or 'values' not in arr:
                raise JavaException("RuntimeException", f"'{name}' is not an array", line_number)

            if not (0 <= idx < len(arr['values'])):
                raise JavaException("ArrayIndexOutOfBoundsException", str(idx), line_number)

            self.executor.last_accessed_array_name = name
            self.executor.last_accessed_array_index = idx
            
            expr = expr.replace(match.group(0), self._safe_repr(arr['values'][idx]), 1)

        # ---------------- MEMBER + VARIABLE RESOLUTION ----------------
        member_pattern = re.compile(r'\b([\w]+(?:\.[\w]+)*)\b')

        while True:
            found = False

            for m in member_pattern.finditer(expr):
                name = m.group(1)

                # skip keywords
                if name in self.keywords:
                    continue

                # ---------------- this.field ----------------
                if name.startswith("this."):
                    frame = self.executor.call_stack.peek()
                    if frame and frame.this_obj_id:
                        field = name.split(".", 1)[1]
                        val = self.executor.memory.get_instance_field(frame.this_obj_id, field)
                        expr = expr.replace(name, self._safe_repr(val), 1)
                        found = True
                        break

                # ---------------- obj.field ----------------
                if "." in name:
                    base, field = name.split(".", 1)
                    
                    # skip keywords in base
                    if base in self.keywords:
                        continue

                    base_val = self.executor._get_var(base)

                    if base_val is None:
                        raise JavaException("NullPointerException", base, line_number)

                    # If base_val is a primitive (and not None), it cannot have fields
                    if not isinstance(base_val, (dict, int)): # int is for object IDs
                        raise JavaException("RuntimeException", f"'{base}' is a primitive type and does not have fields", line_number)

                    # Handle array.length for directly stored array dictionaries
                    if isinstance(base_val, dict) and base_val.get("type") == "array" and field == "length":
                        expr = expr.replace(name, self._safe_repr(len(base_val["values"])), 1)
                        found = True
                        break

                    if isinstance(base_val, int): # This is likely an object ID
                        # Check for array.length
                        if field == "length":
                            obj = self.executor.memory.objects.get(base_val)
                            if obj and obj.get("type") == "array" and "values" in obj:
                                expr = expr.replace(name, self._safe_repr(len(obj["values"])), 1)
                                found = True
                                break
                        # Original logic for instance fields
                        val = self.executor.memory.get_instance_field(base_val, field)
                        expr = expr.replace(name, self._safe_repr(val), 1)
                        found = True
                        break

                # ---------------- local variable ----------------
                val = self.executor._get_var(name)
                if val is not None:
                    expr = expr.replace(name, self._safe_repr(val), 1)
                    found = True
                    break

                # 🔥 FIX: implicit this.field (YOUR BUG FIX)
                frame = self.executor.call_stack.peek()
                if frame and frame.this_obj_id:
                    try:
                        val = self.executor.memory.get_instance_field(frame.this_obj_id, name)
                        expr = expr.replace(name, self._safe_repr(val), 1)
                        found = True
                        break
                    except:
                        pass

            if not found:
                break

        # ---------------- FINAL EVAL ----------------
        concat_result = self.executor.runtime_engine.string_engine.try_concat_expression(
            expr,
            lambda part: self.evaluate(part, line_number, steps)
        )
        if concat_result is not None:
            return concat_result

        python_expr = (
            expr.replace('&&', ' and ')
                .replace('||', ' or ')
                # Replace unary '!' only (preserve '!=').
                .replace('true', 'True')
                .replace('false', 'False')
        )
        python_expr = re.sub(r'!(?!=)', ' not ', python_expr)

        # array literal fix
        python_expr = re.sub(r'new\s+\w+\[\]\s*\{', '[', python_expr)
        python_expr = python_expr.replace('{', '[').replace('}', ']')

        try:
            return eval(python_expr, {"__builtins__": None}, {})
        except Exception as e:
            raise JavaException("RuntimeException", str(e), line_number)

    # ---------------- SAFE REPRESENTATION ----------------
    def _safe_repr(self, val: Any) -> str:
        if val is None:
            return 'None'
        if isinstance(val, str):
            return json.dumps(val)
        if isinstance(val, bool):
            return 'True' if val else 'False'
        return str(val)