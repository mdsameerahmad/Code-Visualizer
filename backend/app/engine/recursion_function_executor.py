"""
Dedicated execution path for method invocations, recursion, and return propagation.

All stack-frame lifecycle for normal Java method calls (push → execute body → pop / return)
lives here so the main Executor stays focused on line-level control flow.
"""
from typing import Any, List, Dict, Optional

from app.engine.stack import StackFrame
from app.engine.exceptions import ExecutionError, FunctionReturn, JavaException


class RecursionFunctionExecutor:
    """Single place for call-stack semantics around function/method execution."""

    MAX_RECURSION_DEPTH = 100

    def __init__(self, executor):
        self.executor = executor

    def execute_invocation(
        self, full_method_name: str, args: List[Any], line_number: int, steps: List
    ) -> Any:
        """
        Resolve and run a method: push frame, execute body step-by-step via executor.execute_lines,
        handle return/exception, pop frame, propagate return value.
        """
        obj_id, method_name, class_def = None, full_method_name, self.executor.current_class

        if "." in full_method_name:
            parts = full_method_name.split(".")
            base_name, method_name = parts[0], parts[1]

            if base_name == "this":
                frame = self.executor.call_stack.peek()
                if frame and frame.this_obj_id:
                    obj_id = frame.this_obj_id
                else:
                    raise ExecutionError("'this' is not available in static context", line_number)
            else:
                base_val = self.executor._get_var(base_name)

                builtin = self.executor.runtime_engine.handle_builtin_method(
                    base_val, method_name, args, line_number
                )
                if builtin != "NO_BUILTIN":
                    return builtin

                if isinstance(base_val, int) and base_val in self.executor.memory.objects:
                    obj_id = base_val
                    class_def = self.executor.classes.get(
                        self.executor.memory.objects[obj_id]["class"]
                    )
                elif base_name in self.executor.classes:
                    class_def, obj_id = self.executor.classes[base_name], None
                else:
                    raise ExecutionError(
                        f"Cannot call method '{method_name}' on undefined object '{base_name}'",
                        line_number,
                    )

        def find_method(c_def: Optional[object], m_name: str):
            if not c_def:
                return None
            if m_name in c_def.methods:
                return c_def.methods[m_name]
            if c_def.parent_class and c_def.parent_class in self.executor.classes:
                return find_method(self.executor.classes[c_def.parent_class], m_name)
            return None

        method_def = find_method(class_def, method_name)

        if not method_def:
            frame = self.executor.call_stack.peek()
            if frame and frame.this_obj_id:
                obj_id = frame.this_obj_id
                class_def = self.executor.classes.get(
                    self.executor.memory.objects[obj_id]["class"]
                )
                method_def = find_method(class_def, method_name)

        if not method_def and "Global" in self.executor.classes:
            method_def = find_method(self.executor.classes["Global"], method_name)
            if method_def:
                class_def = self.executor.classes["Global"]
                obj_id = None

        if not method_def:
            raise ExecutionError(
                f"Method '{method_name}' not found in class '{class_def.name if class_def else 'Unknown'}'",
                line_number,
            )

        if not method_def.is_static and obj_id is None:
            raise ExecutionError(
                f"Non-static method '{method_name}' cannot be called from static context",
                line_number,
            )

        if len(args) != len(method_def.parameters):
            raise ExecutionError(
                f"Method {method_name} expected {len(method_def.parameters)} arguments, but got {len(args)}",
                line_number,
            )

        if self.executor.call_stack.size() >= self.MAX_RECURSION_DEPTH:
            raise ExecutionError("Stack Overflow", line_number)

        frame_params: Dict[str, Any] = {}
        for i, param_def in enumerate(method_def.parameters):
            val = args[i]
            if param_def["type"] == "int[]":
                if isinstance(val, list):
                    frame_params[param_def["name"]] = {
                        "values": val,
                        "lastUpdatedIndex": None,
                    }
                elif isinstance(val, dict) and "values" in val:
                    frame_params[param_def["name"]] = val
                else:
                    raise ExecutionError(
                        f"Type mismatch: expected int[] for {param_def['name']}", line_number
                    )
            else:
                frame_params[param_def["name"]] = val

        frame = StackFrame(
            class_def.name,
            method_name,
            line_number,
            {},
            frame_params,
            this_obj_id=obj_id,
        )
        self.executor.call_stack.push(frame)

        # Emit a step for frame push / call entry (visual stack growth)
        steps.append(self.executor.step_builder.build(
            len(steps) + 1,
            line_number,
            f"{full_method_name}({', '.join(map(str, args))})",
            f"Call -> enter {class_def.name}.{method_name}",
            self.executor._get_full_snapshot(),
            self.executor.call_stack.get_frames_info(),
        ))

        try:
            self.executor.execute_lines(method_def.body, method_def.start_line, steps, True)
            if method_def.return_type != "void":
                raise ExecutionError(
                    f"Method {method_name} must return {method_def.return_type}", line_number
                )
            # Emit a step for implicit void return
            steps.append(self.executor.step_builder.build(
                len(steps) + 1,
                line_number,
                f"{class_def.name}.{method_name}()",
                f"Return from {class_def.name}.{method_name} (void)",
                self.executor._get_full_snapshot(),
                self.executor.call_stack.get_frames_info(),
            ))
            self.executor.call_stack.pop()
            return None
        except FunctionReturn as fr:
            # Emit a step for explicit return value before popping (visual stack shrink)
            steps.append(self.executor.step_builder.build(
                len(steps) + 1,
                line_number,
                f"{class_def.name}.{method_name}()",
                f"Return from {class_def.name}.{method_name} -> {fr.value}",
                self.executor._get_full_snapshot(),
                self.executor.call_stack.get_frames_info(),
            ))
            self.executor.call_stack.pop()
            return fr.value
        except JavaException:
            raise
