from typing import Any, List, Dict, Optional
from app.engine.stack import StackFrame
from app.engine.exceptions import ExecutionError, FunctionReturn

class OOPEngine:
    def __init__(self, executor):
        self.executor = executor

    def execute_constructor(self, class_name: str, obj_id: int, args: List[Any], line_number: int, steps: List):
        search_name = class_name.split(".")[-1] if "." in class_name else class_name
        if search_name not in self.executor.classes:
            raise ExecutionError(f"Class '{class_name}' not defined", line_number)
        
        class_def = self.executor.classes[search_name]
        
        def init_fields(c_def):
            if c_def.parent_class and c_def.parent_class in self.executor.classes:
                init_fields(self.executor.classes[c_def.parent_class])
            for field_name, field_def in c_def.fields.items():
                if not field_def.is_static:
                    default_val = 0 if field_def.type in ['int', 'boolean'] else None
                    self.executor.memory.set_instance_field(obj_id, field_name, default_val)
        
        init_fields(class_def)

        # Find matching constructor
        constructor = None
        for c in class_def.constructors:
            if len(c.parameters) == len(args):
                constructor = c; break
        
        if not constructor:
            if not args: return # Default no-arg constructor
            raise ExecutionError(f"No constructor found for class '{class_name}' with {len(args)} arguments", line_number)

        frame_params = {p['name']: args[i] for i, p in enumerate(constructor.parameters)}
        frame = StackFrame(class_name, "<init>", line_number, {}, frame_params, this_obj_id=obj_id)
        self.executor.call_stack.push(frame)
        
        try:
            self.executor.execute_lines(constructor.body, constructor.start_line, steps, True)
        except FunctionReturn: pass
        finally: self.executor.call_stack.pop()
