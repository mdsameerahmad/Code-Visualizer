from typing import Any, List, Dict, Optional
from app.engine.stack import StackFrame
from app.engine.exceptions import ExecutionError, FunctionReturn, JavaException

class MethodEngine:
    def __init__(self, executor):
        self.executor = executor
        self.MAX_RECURSION_DEPTH = 100

    def call(self, full_method_name: str, args: List[Any], line_number: int, steps: List) -> Any:
        obj_id, method_name, class_def = None, full_method_name, self.executor.current_class
        
        if "." in full_method_name:
            parts = full_method_name.split(".")
            base_name, method_name = parts[0], parts[1]
            
            if base_name == "this":
                frame = self.executor.call_stack.peek()
                if frame and frame.this_obj_id: obj_id = frame.this_obj_id
                else: raise ExecutionError("'this' is not available in static context", line_number)
            else:
                base_val = self.executor._get_var(base_name)
                
                # Check runtime engine for built-in methods
                builtin = self.executor.runtime_engine.handle_builtin_method(base_val, method_name, args, line_number)
                if builtin != "NO_BUILTIN": return builtin
                
                # Check object-based method calls
                if isinstance(base_val, int) and base_val in self.executor.memory.objects:
                    obj_id = base_val
                    class_def = self.executor.classes.get(self.executor.memory.objects[obj_id]["class"])
                elif base_name in self.executor.classes:
                    class_def, obj_id = self.executor.classes[base_name], None
                else:
                    raise ExecutionError(f"Cannot call method '{method_name}' on undefined object '{base_name}'", line_number)

        def find_method(c_def, m_name):
            if not c_def: return None
            if m_name in c_def.methods: return c_def.methods[m_name]
            if c_def.parent_class and c_def.parent_class in self.executor.classes:
                return find_method(self.executor.classes[c_def.parent_class], m_name)
            return None

        method_def = find_method(class_def, method_name)
        
        # Fallback for implicit instance method call
        if not method_def:
            frame = self.executor.call_stack.peek()
            if frame and frame.this_obj_id:
                obj_id = frame.this_obj_id
                class_def = self.executor.classes.get(self.executor.memory.objects[obj_id]["class"])
                method_def = find_method(class_def, method_name)
        
        # Fallback for standalone/global methods
        if not method_def and "Global" in self.executor.classes:
            method_def = find_method(self.executor.classes["Global"], method_name)
            if method_def:
                class_def = self.executor.classes["Global"]
                obj_id = None
        
        if not method_def:
            raise ExecutionError(f"Method '{method_name}' not found in class '{class_def.name if class_def else 'Unknown'}'", line_number)
        
        if not method_def.is_static and obj_id is None:
             raise ExecutionError(f"Non-static method '{method_name}' cannot be called from static context", line_number)

        if len(args) != len(method_def.parameters):
            raise ExecutionError(f"Method {method_name} expected {len(method_def.parameters)} arguments, but got {len(args)}", line_number)

        if self.executor.call_stack.size() >= self.MAX_RECURSION_DEPTH:
            raise ExecutionError("Stack Overflow", line_number)

        frame_params = {}
        for i, param_def in enumerate(method_def.parameters):
            val = args[i]
            if param_def['type'] == 'int[]':
                if isinstance(val, list): frame_params[param_def['name']] = {'values': val, 'lastUpdatedIndex': None}
                elif isinstance(val, dict) and 'values' in val: frame_params[param_def['name']] = val
                else: raise ExecutionError(f"Type mismatch: expected int[] for {param_def['name']}", line_number)
            else: frame_params[param_def['name']] = val

        frame = StackFrame(class_def.name, method_name, line_number, {}, frame_params, this_obj_id=obj_id)
        self.executor.call_stack.push(frame)
        
        try:
            self.executor.execute_lines(method_def.body, method_def.start_line, steps, True)
            if method_def.return_type != 'void': raise ExecutionError(f"Method {method_name} must return {method_def.return_type}", line_number)
            
            # ✅ NORMAL RETURN → POP
            self.executor.call_stack.pop()
            return None
        except FunctionReturn as fr:
            # ✅ NORMAL RETURN → POP
            self.executor.call_stack.pop()
            return fr.value
        except JavaException:
            # 🔥 DO NOT POP → PRESERVE STACK
            raise
