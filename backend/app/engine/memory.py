import copy
from typing import Dict, Any, List, Optional
from app.engine.exceptions import ExecutionError

class Memory:
    def __init__(self):
        self.variables = {}
        self.arrays = {}
        self.objects = {}
        self._next_obj_id = 1

    def set_variable(self, name, value):
        self.variables[name] = value

    def get_variable(self, name):
        return self.variables.get(name)

    def create_array(self, name, size):
        self.arrays[name] = {
            "values": [0] * size,
            "lastUpdatedIndex": None
        }

    def set_array_value(self, name, index, value):
        if name not in self.arrays:
            raise ExecutionError(f"Array '{name}' is not defined", 0)

        if not isinstance(index, int):
            raise ExecutionError(f"Array index must be an integer, got {type(index).__name__}", 0)

        if not (0 <= index < len(self.arrays[name]["values"])):
            raise ExecutionError(f"Array index out of bounds: index {index} for size {len(self.arrays[name]['values'])}", 0)
        
        # Enforce integer type for array values, converting None to 0
        if value is None:
            value = 0
        elif not isinstance(value, int):
            raise ExecutionError(f"Array values must be integers, got {type(value).__name__}", 0)

        self.arrays[name]["values"][index] = value
        self.arrays[name]["lastUpdatedIndex"] = index

    def create_object(self, class_name: str) -> int:
        obj_id = self._next_obj_id
        self.objects[obj_id] = {
            "class": class_name,
            "fields": {},
            "id": obj_id
        }
        self._next_obj_id += 1
        return obj_id

    def set_instance_field(self, obj_id: int, field_name: str, value: Any):
        if obj_id not in self.objects:
            raise ExecutionError(f"Object with ID {obj_id} not found", 0)
        self.objects[obj_id]["fields"][field_name] = value

    def get_instance_field(self, obj_id: int, field_name: str) -> Any:
        if obj_id not in self.objects:
            raise ExecutionError(f"Object with ID {obj_id} not found", 0)
        return self.objects[obj_id]["fields"].get(field_name)

    def get_snapshot(self):
        # Deep copy to avoid reference issues between steps
        snapshot = {
            "variables": copy.deepcopy(self.variables),
            "arrays": copy.deepcopy(self.arrays),
            "objects": copy.deepcopy(self.objects)
        }
        
        # Validate arrays for null values before returning snapshot
        for name, array_data in snapshot["arrays"].items():
            for i, value in enumerate(array_data["values"]):
                if value is None:
                    array_data["values"][i] = 0
        
        return snapshot
