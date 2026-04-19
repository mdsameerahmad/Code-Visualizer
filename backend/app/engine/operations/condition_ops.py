import re
from typing import Dict, Any, List

from app.engine.exceptions import ExecutionError

class ConditionEngine:
    def __init__(self, executor):
        self.executor = executor
        # Support i < 3, i <= 3, i > 3, i >= 3, i == 3
        self.pattern = re.compile(r'(\w+)\s*(<|<=|>|>=|==)\s*(\d+)')

    def evaluate(self, condition: str, memory_snapshot: Dict[str, Any], line_number: int, steps: List) -> bool:
        condition = condition.strip()
        if not condition:
            return True # Empty condition is true in for loop
            
        # Use the executor's evaluate_expression to handle complex conditions
        try:
            result = self.executor.evaluate_expression(condition, line_number, steps)
            return bool(result)
        except ExecutionError as e:
            raise e
        except Exception as e:
            raise ExecutionError(f"Invalid condition expression: '{condition}' - {str(e)}", line_number)

    def execute_if(self, condition: str, true_block: List[str], false_block: List[str], 
                   executor, memory, step_builder, steps, base_line_number, is_function_body=False, else_start_line=None):
        is_true = self.evaluate(condition, memory.get_snapshot(), base_line_number, steps)
        
        # 1. Condition check step
        steps.append(step_builder.build(
            step_number=len(steps) + 1,
            line_number=base_line_number,
            line_content=f"if({condition})",
            explanation=f"Condition '{condition}' is {str(is_true).upper()}",
            memory_snapshot=executor._get_full_snapshot(),
            call_stack_frames=executor.call_stack.get_frames_info(),
            accessed_array_name=executor.last_accessed_array_name,
            accessed_array_index=executor.last_accessed_array_index
        ))
        
        # 2. Execute corresponding block
        if is_true:
            executor.execute_lines(true_block, base_line_number + 1, steps, is_function_body=is_function_body)
        elif false_block:
            # If we have an else block, we need its correct starting line
            start_line = else_start_line if else_start_line else base_line_number + len(true_block) + 2
            executor.execute_lines(false_block, start_line, steps, is_function_body=is_function_body)
