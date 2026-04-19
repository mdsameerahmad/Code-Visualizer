from typing import Any, List, Dict, Optional
from app.engine.exceptions import JavaException, ExecutionError
from app.engine.string_engine import StringEngine
from app.engine.string_executor import StringExecutor

class RuntimeEngine:
    def __init__(self, executor):
        self.executor = executor
        self.virtual_files = {"test.txt": "line1\nline2\nline3"}
        self.string_engine = StringEngine()
        self.string_executor = StringExecutor(self.string_engine)

    def handle_builtin_method(self, base_val: Any, method_name: str, args: List[Any], line_number: int) -> Any:
        if self.string_executor.is_string_like(base_val):
            result = self.string_executor.execute(base_val, method_name, args, line_number)
            if result != "NO_BUILTIN":
                return result
            # String methods must not fall through to Global/user-method lookup.
            raise JavaException(
                "RuntimeException",
                f"String method '{method_name}' not found",
                line_number,
            )
        
        elif isinstance(base_val, dict):
            b_type = base_val.get("type")
            if b_type == "ArrayList":
                if method_name == "add": base_val["values"].append(args[0]); return None
                if method_name == "get": return base_val["values"][args[0]]
                if method_name == "size": return len(base_val["values"])
            elif b_type == "HashMap":
                if method_name == "put": base_val["map"][str(args[0])] = args[1]; return None
                if method_name == "get": return base_val["map"].get(str(args[0]))
                if method_name == "size": return len(base_val["map"])
            elif b_type == "Scanner":
                if method_name == "nextLine":
                    lines = base_val["content"].split("\n")
                    res = lines[base_val["pos"]] if base_val["pos"] < len(lines) else None
                    base_val["pos"] += 1
                    return res
            elif b_type == "Thread":
                if method_name == "start": base_val["started"] = True; return None
        
        return self._handle_object_builtin(base_val, method_name, line_number)

    def _handle_object_builtin(self, obj_id: Any, method_name: str, line_number: int) -> Any:
        if not isinstance(obj_id, int) or obj_id not in self.executor.memory.objects:
            return "NO_BUILTIN"
        
        obj = self.executor.memory.objects[obj_id]
        class_def = self.executor.classes.get(obj["class"])
        
        if method_name == "start" and self._is_subclass(class_def, "Thread"):
            obj["started"] = True
            return None
            
        return "NO_BUILTIN"

    def _is_subclass(self, class_def, target: str) -> bool:
        if not class_def: return False
        if class_def.name == target or class_def.parent_class == target: return True
        return self._is_subclass(self.executor.classes.get(class_def.parent_class), target)

    def create_builtin_object(self, expr: str, line_number: int, steps: List) -> Any:
        if 'ArrayList' in expr: return {"type": "ArrayList", "values": []}
        if 'HashMap' in expr: return {"type": "HashMap", "map": {}}
        if 'File' in expr:
            import re
            fname = re.search(r'\((.*)\)', expr).group(1).strip('"')
            return {"type": "File", "name": fname}
        if 'Scanner' in expr:
            import re
            arg = re.search(r'\((.*)\)', expr).group(1)
            f_obj = self.executor.expression_engine.evaluate(arg, line_number, steps)
            return {"type": "Scanner", "content": self.virtual_files.get(f_obj.get("name", ""), ""), "pos": 0}
        if 'Thread' in expr: return {"type": "Thread", "started": False}
        return None
