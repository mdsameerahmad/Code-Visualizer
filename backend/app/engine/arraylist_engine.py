from typing import Any, Dict

from app.engine.exceptions import JavaException


class ArrayListEngine:
    """State/validation helpers for Java-like ArrayList behavior."""

    DEFAULT_CAPACITY = 10

    def create(self, initial_capacity: int = DEFAULT_CAPACITY) -> Dict[str, Any]:
        cap = max(1, int(initial_capacity))
        return {
            "type": "arraylist",
            "elements": [],
            "size": 0,
            "capacity": cap,
            "lastUpdatedIndex": None,
        }

    def ensure_structure(self, value: Any, line_number: int) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise JavaException("RuntimeException", "Target is not an ArrayList", line_number)

        list_type = value.get("type")
        if list_type not in ("arraylist", "ArrayList"):
            raise JavaException("RuntimeException", "Target is not an ArrayList", line_number)

        # Normalize legacy shape: {"type":"ArrayList","values":[...]}
        if "elements" not in value and "values" in value:
            value["elements"] = list(value.get("values", []))
        value["size"] = int(value.get("size", len(value.get("elements", []))))
        value["capacity"] = int(value.get("capacity", max(self.DEFAULT_CAPACITY, value["size"])))
        value["lastUpdatedIndex"] = value.get("lastUpdatedIndex")
        value["type"] = "arraylist"
        value["elements"] = list(value.get("elements", []))
        value["size"] = len(value["elements"])
        value["capacity"] = max(value["capacity"], value["size"], 1)
        return value

    def validate_index(self, arr_list: Dict[str, Any], idx: int, line_number: int):
        if idx < 0 or idx >= arr_list["size"]:
            raise JavaException(
                "IndexOutOfBoundsException",
                f"Index {idx} out of bounds for size {arr_list['size']}",
                line_number,
            )

    def ensure_capacity_for_add(self, arr_list: Dict[str, Any]):
        if arr_list["size"] < arr_list["capacity"]:
            return
        arr_list["capacity"] *= 2
