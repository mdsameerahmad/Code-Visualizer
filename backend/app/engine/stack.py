import copy
from typing import List, Dict, Any, Optional

class FieldDefinition:
    def __init__(self, type: str, name: str, is_static: bool = False):
        self.type = type
        self.name = name
        self.is_static = is_static
    def __repr__(self):
        return f"FieldDefinition({self.type} {self.name}, static={self.is_static})"

class MethodDefinition:
    def __init__(self, access_modifier: str, is_static: bool, return_type: str, name: str, parameters: List[Dict[str, str]], body: List[str], start_line: int, is_constructor: bool = False):
        self.access_modifier = access_modifier
        self.is_static = is_static
        self.return_type = return_type
        self.name = name
        self.parameters = parameters  # [{'type': 'int', 'name': 'a'}, ...]
        self.body = body              # List of code lines
        self.start_line = start_line   # Line number in the source code where the method body starts
        self.is_constructor = is_constructor

class ClassDefinition:
    def __init__(self, name: str, parent_class: Optional[str] = None):
        self.name = name
        self.parent_class = parent_class
        self.methods: Dict[str, MethodDefinition] = {}
        self.fields: Dict[str, FieldDefinition] = {}
        self.constructors: List[MethodDefinition] = []

class StackFrame:
    def __init__(self, class_name: str, method_name: str, return_address: int, local_variables: Dict[str, Any], parameters: Dict[str, Any], this_obj_id: Optional[int] = None):
        self.class_name = class_name
        self.method_name = method_name
        self.return_address = return_address # Line number to return to in the caller
        self.local_variables = local_variables
        self.parameters = parameters
        self.this_obj_id = this_obj_id # ID of the 'this' object if instance method
        self.return_value: Optional[Any] = None
        self.current_line_pointer: int = 0 # Index into the function body

class CallStack:
    def __init__(self):
        self.frames: List[StackFrame] = []

    def push(self, frame: StackFrame):
        self.frames.append(frame)

    def pop(self) -> StackFrame:
        if not self.frames:
            raise IndexError("Pop from empty call stack")
        return self.frames.pop()

    def peek(self) -> Optional[StackFrame]:
        if not self.frames:
            return None
        return self.frames[-1]

    def is_empty(self) -> bool:
        return len(self.frames) == 0

    def size(self) -> int:
        return len(self.frames)
    
    def get_frames_info(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionaries, each representing a frame's info for visualization."""
        frames_info = []
        for frame in reversed(self.frames): # Show top of stack last
            frames_info.append({
                "class_name": frame.class_name,
                "method_name": frame.method_name,
                "local_variables": copy.deepcopy(frame.local_variables),
                "parameters": copy.deepcopy(frame.parameters),
                "this_obj_id": frame.this_obj_id,
                "current_line_pointer": frame.current_line_pointer,
                "return_value": frame.return_value
            })
        return frames_info
