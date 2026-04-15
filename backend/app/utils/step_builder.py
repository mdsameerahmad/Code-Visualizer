from typing import Dict, Any, List, Optional
from app.models.response_model import ExecutionStep, ArrayData, StackFrameData


class StepBuilder:
    def build(
        self,
        step_number: int,
        line_number: int,
        line_content: str,
        explanation: str,
        memory_snapshot: Dict[str, Any],
        call_stack_frames: List[Dict[str, Any]],
        type: str = "execution",
        output: Optional[str] = None
    ) -> ExecutionStep:

        return ExecutionStep(
            step_number=step_number,
            line_number=line_number,
            line_content=line_content,
            explanation=explanation,

            # ✅ VARIABLES
            variables=memory_snapshot.get("variables", {}),

            # ✅ ARRAYS
            arrays={
                name: ArrayData(
                    values=data["values"],
                    lastUpdatedIndex=data.get("lastUpdatedIndex")
                )
                for name, data in memory_snapshot.get("arrays", {}).items()
                if isinstance(data, dict) and "values" in data
            },

            # 🔥🔥🔥 THIS IS THE FIX (ADD HEAP)
            heap=memory_snapshot.get("heap", {}),

            # ✅ CALL STACK
            call_stack=[
                StackFrameData(**frame_data)
                for frame_data in call_stack_frames
            ],

            type=type,
            output=output
        )