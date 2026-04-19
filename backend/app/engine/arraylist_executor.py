import copy
from typing import Any, List, Optional

from app.engine.arraylist_engine import ArrayListEngine
from app.engine.exceptions import JavaException


class ArrayListExecutor:
    """Execution layer for ArrayList method calls."""

    def __init__(self, engine: ArrayListEngine, executor):
        self.engine = engine
        self.executor = executor

    def can_handle(self, base_val: Any) -> bool:
        return isinstance(base_val, dict) and base_val.get("type") in ("arraylist", "ArrayList")

    def execute(
        self,
        base_val: Any,
        method_name: str,
        args: List[Any],
        line_number: int,
        steps: Optional[List] = None,
        target_name: Optional[str] = None,
    ):
        arr_list = self.engine.ensure_structure(base_val, line_number)
        before = copy.deepcopy(arr_list.get("elements", []))
        arg0 = args[0] if args else None

        try:
            if method_name == "add":
                if len(args) != 1:
                    raise JavaException("RuntimeException", "ArrayList.add expects 1 argument", line_number)
                self.engine.ensure_capacity_for_add(arr_list)
                arr_list["elements"].append(args[0])
                arr_list["size"] = len(arr_list["elements"])
                arr_list["lastUpdatedIndex"] = arr_list["size"] - 1
                self._log_step(
                    steps,
                    line_number,
                    target_name or "<arraylist>",
                    "add",
                    before,
                    arr_list["elements"],
                    index=arr_list["lastUpdatedIndex"],
                    value=args[0],
                )
                return True

            if method_name == "get":
                if len(args) != 1:
                    raise JavaException("RuntimeException", "ArrayList.get expects 1 argument", line_number)
                idx = self._coerce_index(args[0])
                self.engine.validate_index(arr_list, idx, line_number)
                value = arr_list["elements"][idx]
                self._log_step(
                    steps,
                    line_number,
                    target_name or "<arraylist>",
                    "get",
                    before,
                    arr_list["elements"],
                    index=idx,
                    value=value,
                )
                return value

            if method_name == "set":
                if len(args) != 2:
                    raise JavaException("RuntimeException", "ArrayList.set expects 2 arguments", line_number)
                idx = self._coerce_index(args[0])
                self.engine.validate_index(arr_list, idx, line_number)
                old = arr_list["elements"][idx]
                arr_list["elements"][idx] = args[1]
                arr_list["lastUpdatedIndex"] = idx
                self._log_step(
                    steps,
                    line_number,
                    target_name or "<arraylist>",
                    "set",
                    before,
                    arr_list["elements"],
                    index=idx,
                    value=args[1],
                )
                return old

            if method_name == "remove":
                if len(args) != 1:
                    raise JavaException("RuntimeException", "ArrayList.remove expects 1 argument", line_number)
                arg = args[0]
                removed = None
                removed_index = None
                # Java-like strict behavior: integer argument is remove(index) and must validate.
                if isinstance(arg, int):
                    removed_index = int(arg)
                    self.engine.validate_index(arr_list, removed_index, line_number)
                    removed = arr_list["elements"].pop(removed_index)
                elif isinstance(arg, dict) and arg.get("type") == "Integer":
                    # Boxed Integer => remove(value) semantics
                    needle = int(arg.get("value", 0))
                    for i, val in enumerate(arr_list["elements"]):
                        if val == needle:
                            removed_index = i
                            removed = arr_list["elements"].pop(i)
                            break
                else:
                    for i, val in enumerate(arr_list["elements"]):
                        if val == arg:
                            removed_index = i
                            removed = arr_list["elements"].pop(i)
                            break

                arr_list["size"] = len(arr_list["elements"])
                arr_list["lastUpdatedIndex"] = (
                    None if removed_index is None else min(removed_index, max(arr_list["size"] - 1, 0))
                )
                self._log_step(
                    steps,
                    line_number,
                    target_name or "<arraylist>",
                    "remove",
                    before,
                    arr_list["elements"],
                    index=removed_index,
                    value=arg if removed_index is None else removed,
                )
                return removed

            if method_name == "size":
                if len(args) != 0:
                    raise JavaException("RuntimeException", "ArrayList.size expects 0 arguments", line_number)
                self._log_step(
                    steps,
                    line_number,
                    target_name or "<arraylist>",
                    "size",
                    before,
                    arr_list["elements"],
                    index=None,
                    value=arr_list["size"],
                )
                return arr_list["size"]

            return "NO_BUILTIN"
        except JavaException as je:
            self._log_error_step(steps, line_number, target_name or "<arraylist>", je.message)
            raise

    def _coerce_index(self, value: Any) -> int:
        if isinstance(value, dict) and value.get("type") == "Integer":
            return int(value.get("value", 0))
        return int(value)

    def _log_step(
        self,
        steps: Optional[List],
        line_number: int,
        target: str,
        operation: str,
        before: List[Any],
        after: List[Any],
        index: Optional[int],
        value: Any,
    ):
        if steps is None:
            return
        explanation = (
            f"ArrayList op={operation} target={target} before={before} after={list(after)} "
            f"meta(index={index}, value={value})"
        )
        steps.append(
            self.executor.step_builder.build(
                len(steps) + 1,
                line_number,
                f"{target}.{operation}(...)",
                explanation,
                self.executor._get_full_snapshot(),
                self.executor.call_stack.get_frames_info(),
            )
        )

    def _log_error_step(self, steps: Optional[List], line_number: int, target: str, message: str):
        if steps is None:
            return
        before = []
        current = self.executor._get_var(target) if target and target != "<arraylist>" else None
        if isinstance(current, dict) and current.get("type") in ("arraylist", "ArrayList"):
            before = list(current.get("elements", []))
        steps.append(
            self.executor.step_builder.build(
                len(steps) + 1,
                line_number,
                f"{target}.error",
                f"ArrayList error: {message} | state_before={before} | state_after=None | executionStopped=true",
                self.executor._get_full_snapshot(),
                self.executor.call_stack.get_frames_info(),
                type="error",
            )
        )
