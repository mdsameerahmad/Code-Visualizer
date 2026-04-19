from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ArrayData(BaseModel):
    values: List[Any]
    lastUpdatedIndex: Optional[int] = None


class StackFrameData(BaseModel):
    class_name: Optional[str] = None
    method_name: str
    local_variables: Dict[str, Any]
    parameters: Dict[str, Any]
    this_obj_id: Optional[int] = None
    current_line_pointer: int
    return_value: Optional[Any] = None


class ExecutionStep(BaseModel):
    step_number: int
    line_number: int
    line_content: str
    explanation: str

    variables: Dict[str, Any]
    arrays: Dict[str, ArrayData]

    # 🔥🔥🔥 ADD THIS (CRITICAL FIX)
    heap: Dict[str, Any] = {}

    call_stack: List[StackFrameData] = []
    type: str = "execution"
    output: Optional[str] = None
    accessed_array_name: Optional[str] = None
    accessed_array_index: Optional[int] = None


class CodeExecutionResponse(BaseModel):
    steps: List[ExecutionStep]
    normalized_code: Optional[str] = None
    error: Optional[Dict[str, Any]] = None


class ExecutionError(BaseModel):
    type: str  # RuntimeError | SyntaxError | UnsupportedError
    message: str
    line: int


class ExecutionResponse(BaseModel):
    steps: List[ExecutionStep]
    error: Optional[ExecutionError] = None