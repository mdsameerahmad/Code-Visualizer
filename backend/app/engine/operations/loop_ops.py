from typing import List, Dict, Any
from app.engine.operations.condition_ops import ConditionEngine
from app.engine.exceptions import ExecutionError, BreakException

class LoopEngine:
    def __init__(self, condition_engine: ConditionEngine):
        self.condition_engine = condition_engine

    def execute_for_loop(self, header_data: Dict[str, str], body_lines: List[str], 
                         executor, memory, step_builder, steps, base_line_number, is_function_body=False):
        """
        header_data contains: init (e.g., 'int i = 0'), condition (e.g., 'i < 3'), increment (e.g., 'i++')
        body_lines: lines inside the { }
        executor: current executor instance to process body lines
        """
        init_line = header_data['init'] + ";"
        condition = header_data['condition']
        increment = header_data['increment']
        if not increment.endswith(';'):
            increment += ";"
        
        # 1. Initialize (Step for initialization)
        executor.execute_line(init_line, base_line_number, steps)
        
        # 2. Loop: while condition is true
        iteration = 0
        iteration_cap = 1000
        while True:
            snapshot = executor._get_full_snapshot()
            is_true = self.condition_engine.evaluate(condition, snapshot, base_line_number, steps)
            
            # a. Condition check step
            steps.append(step_builder.build(
                step_number=len(steps) + 1,
                line_number=base_line_number,
                line_content=f"for(...; {condition}; ...)",
                explanation=f"Loop condition '{condition}' is {'TRUE' if is_true else 'FALSE'}",
                memory_snapshot=snapshot,
                call_stack_frames=executor.call_stack.get_frames_info()
            ))

            if not is_true:
                break

            iteration += 1
            if iteration > iteration_cap:
                raise ExecutionError("Possible infinite loop detected: exceeded 1000 iterations", base_line_number)
                
            # b. Execute each line inside body
            # The lines inside body start at base_line_number + 1
            try:
                executor.execute_lines(body_lines, base_line_number + 1, steps, is_function_body=is_function_body)
            except BreakException:
                break

            # d. Apply increment (i++) and record step
            executor.execute_line(increment, base_line_number, steps)
            # Removed redundant iteration += 1 from the end of body to prevent double increment in step count

    def execute_while_loop(self, condition: str, body_lines: List[str], 
                           executor, memory, step_builder, steps, base_line_number, is_function_body=False):
        """
        condition: e.g., 'i < 3' or 'true'
        body_lines: lines inside the { }
        """
        iteration = 0
        iteration_cap = 1000
        while True:
            snapshot = executor._get_full_snapshot()
            is_true = executor.evaluate_expression(condition, base_line_number, steps)
            
            steps.append(step_builder.build(
                step_number=len(steps) + 1,
                line_number=base_line_number,
                line_content=f"while({condition})",
                explanation=f"Loop condition '{condition}' is {'TRUE' if is_true else 'FALSE'}",
                memory_snapshot=snapshot,
                call_stack_frames=executor.call_stack.get_frames_info()
            ))

            if not is_true:
                break

            iteration += 1
            if iteration > iteration_cap:
                raise ExecutionError("Possible infinite loop detected: exceeded 1000 iterations", base_line_number)
                
            try:
                executor.execute_lines(body_lines, base_line_number + 1, steps, is_function_body=is_function_body)
            except BreakException:
                break
