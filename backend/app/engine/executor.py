import re
import copy
from typing import List, Tuple, Dict, Any, Optional, Set

from app.engine.memory import Memory
from app.utils.step_builder import StepBuilder
from app.engine.operations.condition_ops import ConditionEngine
from app.engine.operations.loop_ops import LoopEngine
from app.engine.stack import MethodDefinition, ClassDefinition, FieldDefinition, StackFrame, CallStack
from app.engine.exceptions import ExecutionError, FunctionReturn, JavaException, BreakException

from app.engine.runtime_engine import RuntimeEngine
from app.engine.expression_engine import ExpressionEngine
from app.engine.method_engine import MethodEngine
from app.engine.oop_engine import OOPEngine
from app.engine.exception_engine import ExceptionEngine


class Executor:
    def __init__(self):
        self._exception_active = False
        self.memory = Memory()
        self.step_builder = StepBuilder()
        self.condition_engine = ConditionEngine(self)
        self.loop_engine = LoopEngine(self.condition_engine)
        self.call_stack = CallStack()
        self.classes: Dict[str, ClassDefinition] = {}
        self.current_class: Optional[ClassDefinition] = None
        self.imported_libraries: Set[str] = set()

        self.runtime_engine = RuntimeEngine(self)
        self.expression_engine = ExpressionEngine(self)
        self.method_engine = MethodEngine(self)
        self.oop_engine = OOPEngine(self)
        self.exception_engine = ExceptionEngine(self)

        self.breakpoints = set()
        self.is_paused = False
        self.debug_mode = True
        self.current_line = 0
        self.execution_pointer = None

        self.patterns = {
            'import_stmt': re.compile(r'import\s+([a-zA-Z0-9_.*]+)\s*;'),
            'class_def': re.compile(r'(public|private|static)?\s*(static)?\s*class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'),
            'field_def': re.compile(r'(public|private)?\s*(static)?\s*(int|String|boolean|char|byte|short|long|float|double|ArrayList|File|Scanner|Thread|[\w<>\.]+)\s+(\w+)\s*;'),
            'constructor_def': re.compile(r'(public|private)?\s*(\w+)\s*\(([^)]*)\)\s*\{'),
            'method_def': re.compile(r'(public|private)?\s*(static)?\s*(int|void|boolean|char|byte|short|long|float|double|String|ArrayList|File|Scanner|Thread|[\w<>\.]+)\s+(\w+)\s*\(([^)]*)\)\s*\{'),
            'method_call': re.compile(r'([\w\.]+)\s*\('),
            'return_stmt': re.compile(r'return\s*([^;]*)\s*;'),
            'throw_stmt': re.compile(r'throw\s+new\s+(\w+)\s*\(([^)]*)\)\s*;'),
            'try_header': re.compile(r'try\s*\{'),
            'catch_header': re.compile(r'\}\s*catch\s*\(([^)]+)\)\s*\{|catch\s*\(([^)]+)\)\s*\{'),
            'array_decl': re.compile(r'(int|boolean|char|byte|short|long|float|double|String)\[\]\s+(\w+)\s*=\s*new\s+\1\[(\d+)\]\s*;'),
            'array_assign': re.compile(r'(\w+)\[([^\]]+)\]\s*=\s*([^;]+)\s*;'),
            'var_decl_assign': re.compile(r'(char|byte|short|long|float|double|int|boolean|String|var|[\w<>\.]+)\s+(\w+)\s*=\s*([^;]+)\s*;'),
            'var_assign': re.compile(r'^([\w\.]+)\s*=\s*([^;]+)\s*;'),
            'increment': re.compile(r'([\w\.]+)(\+\+|--)\s*;?'),
            'break_stmt': re.compile(r'break\s*;'),
            'for_header': re.compile(r'for\s*\(\s*([\w<>\s]+\w+\s*=\s*[^;]*|int\s+\w+\s*=\s*\d+)\s*;\s*([^;]*)\s*;\s*([^)]*)\s*\)\s*(\{)?'),
            'while_header': re.compile(r'while\s*\(([^)]+)\)\s*(\{)?'),
            'if_header': re.compile(r'if\s*\(([^)]+)\)\s*(\{)?'),
            'else_line': re.compile(r'\}\s*else\s*\{'),
            'print_stmt': re.compile(r'System\.out\.println\s*\((.*)\)\s*;')
        }

    def _find_matching_paren(self, s: str, start: int) -> int:
        count = 0
        for i in range(start, len(s)):
            if s[i] == '(': count += 1
            elif s[i] == ')':
                count -= 1
                if count == 0: return i
        return -1

    def _parse_classes_recursive(self, lines: List[str], base_line: int):
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if m := self.patterns['class_def'].match(line):
                class_name = m.group(3)
                parent_name = m.group(4)
                class_def = ClassDefinition(class_name, parent_name)
                self.classes[class_name] = class_def
                body, end = self.extract_block(lines, i + 1)
                self._parse_classes_recursive(body, base_line + i + 1)
                j = 0
                while j < len(body):
                    l = body[j].strip()
                    if mm := self.patterns['method_def'].match(l):
                        acc, stat, ret, name, params_raw = mm.groups()
                        params = []
                        for p in params_raw.split(','):
                            p = p.strip()
                            if p:
                                parts = p.rsplit(None, 1)
                                if len(parts) == 2:
                                    params.append({"type": parts[0], "name": parts[1]})
                        m_body, me = self.extract_block(body, j + 1)
                        class_def.methods[name] = MethodDefinition(
                            acc or "default", bool(stat), ret, name, params, m_body, base_line + i + j + 3
                        )
                        j = me + 1
                        continue
                    elif cm := self.patterns['constructor_def'].match(l):
                        acc, name, params_raw = cm.groups()
                        if name == class_def.name:
                            params = []
                            for p in params_raw.split(','):
                                p = p.strip()
                                if p:
                                    parts = p.rsplit(None, 1)
                                    if len(parts) == 2:
                                        params.append({"type": parts[0], "name": parts[1]})
                            c_body, ce = self.extract_block(body, j + 1)
                            class_def.constructors.append(MethodDefinition(
                                acc or "default", False, "void", name, params, c_body, base_line + i + j + 2, is_constructor=True
                            ))
                            j = ce + 1
                            continue
                    elif fm := self.patterns['field_def'].match(l):
                        acc, stat, ftype, fname = fm.groups()
                        class_def.fields[fname] = FieldDefinition(ftype, fname, bool(stat))
                        j += 1
                        continue
                    j += 1
                i = end + 1
            elif m := self.patterns['method_def'].match(line):
                acc, stat, ret, name, params_raw = m.groups()
                params = []
                for p in params_raw.split(','):
                    p = p.strip()
                    if p:
                        parts = p.rsplit(None, 1)
                        if len(parts) == 2:
                            params.append({"type": parts[0], "name": parts[1]})
                m_body, me = self.extract_block(lines, i + 1)
                
                if "Global" not in self.classes:
                    self.classes["Global"] = ClassDefinition("Global")
                
                self.classes["Global"].methods[name] = MethodDefinition(
                    acc or "default", True, ret, name, params, m_body, base_line + i + 2
                )
                i = me + 1
            else:
                i += 1

    def _normalize_code(self, code: str) -> List[str]:
        lines = []
        for l in code.split('\n'):
             cleaned = re.sub(r'//.*', '', l)
             lines.append(cleaned.rstrip())
        return lines

    def _parse_method_args(self, args_str: str) -> List[str]:
        args, current, paren_depth = [], "", 0
        for ch in args_str:
            if ch == '(': paren_depth += 1; current += ch
            elif ch == ')': paren_depth -= 1; current += ch
            elif ch == ',' and paren_depth == 0:
                args.append(current.strip()); current = ""
            else: current += ch
        if current.strip(): args.append(current.strip())
        return args

    def evaluate_expression(self, expr, line, steps):
        return self.expression_engine.evaluate(expr, line, steps)

    def _get_var(self, name: str) -> Any:
        frame = self.call_stack.peek()
        if "." in name:
            parts = name.split(".", 1)
            base_name, field_name = parts[0], parts[1]
            if base_name == "this":
                if frame and frame.this_obj_id:
                    return self.memory.get_instance_field(frame.this_obj_id, field_name)
                raise ExecutionError("'this' is not available in static context", 0)
            base_val = self._get_var(base_name)
            if isinstance(base_val, int) and base_val in self.memory.objects:
                return self.memory.get_instance_field(base_val, field_name)
        if frame:
            if name in frame.local_variables: return frame.local_variables[name]
            if name in frame.parameters: return frame.parameters[name]
        if name in self.memory.variables: return self.memory.get_variable(name)
        if name in self.memory.arrays: return self.memory.arrays[name]
        return None

    def _set_var(self, name: str, value: Any, is_decl: bool = False, line_number: int = 0):
        frame = self.call_stack.peek()
        if "." in name:
            parts = name.split(".", 1)
            base_name, field_name = parts[0], parts[1]
            if base_name == "this":
                if frame and frame.this_obj_id:
                    self.memory.set_instance_field(frame.this_obj_id, field_name, value)
                    return
                raise ExecutionError("'this' is not available in static context", line_number)
            base_val = self._get_var(base_name)
            if isinstance(base_val, int) and base_val in self.memory.objects:
                self.memory.set_instance_field(base_val, field_name, value)
                return
        if frame:
            if is_decl:
                frame.local_variables[name] = value
                return
            if name in frame.local_variables:
                frame.local_variables[name] = value
                return
            if name in frame.parameters:
                frame.parameters[name] = value
                return
        if not is_decl and name not in self.memory.variables:
            raise ExecutionError(f"Variable '{name}' is not declared", line_number)
        self.memory.set_variable(name, value)

    def execute_line(self, line: str, line_number: int, steps: List):
        line = line.strip()
        if not line or line in ["{", "}", ";"]: return

        # 🔥 Use updated full snapshot
        snapshot = self._get_full_snapshot()

        steps.append(self.step_builder.build(
            len(steps) + 1, 
            line_number, 
            line, 
            "Executing",
            snapshot,
            self.call_stack.get_frames_info()
        ))

        if re.match(r'^(public|private|protected|static|final)\s', line) and '=' not in line and '(' not in line:
            return

        if m := self.patterns['return_stmt'].match(line):
            val = self.evaluate_expression(m.group(1), line_number, steps)
            raise FunctionReturn(val)

        elif m := self.patterns['throw_stmt'].match(line):
            ex_type = m.group(1)
            msg = self.evaluate_expression(m.group(2), line_number, steps)
            raise JavaException(ex_type, str(msg), line_number)

        elif m := self.patterns['array_decl'].match(line):
            name, size_val = m.group(2), int(m.group(3))
            arr_obj = {"values": [0] * size_val, "lastUpdatedIndex": None}
            if self.call_stack.peek(): 
                self.call_stack.peek().local_variables[name] = arr_obj
            else: 
                self.memory.arrays[name] = arr_obj

        elif m := self.patterns['array_assign'].match(line):
            name, idx_expr, val_expr = m.groups()
            idx = self.evaluate_expression(idx_expr, line_number, steps)
            val = self.evaluate_expression(val_expr, line_number, steps)
            arr = self._get_var(name)
            if not arr or 'values' not in arr: 
                raise ExecutionError(f"Array '{name}' not defined", line_number)
            if not (0 <= idx < len(arr['values'])): 
                raise JavaException("ArrayIndexOutOfBoundsException", str(idx), line_number)
            arr['values'][idx] = val
            arr['lastUpdatedIndex'] = idx

        elif m := self.patterns['print_stmt'].match(line):
            expr = m.group(1)
            val = self.evaluate_expression(expr, line_number, steps)
            
            if val is True: formatted = "true"
            elif val is False: formatted = "false"
            elif isinstance(val, dict) and 'values' in val: formatted = str(val['values'])
            elif isinstance(val, int) and val in self.memory.objects:
                obj = self.memory.objects[val]
                formatted = f"{obj['class_name']} {obj['fields']}"
            elif isinstance(val, dict) and val.get("type") == "HashMap":
                formatted = str(val["map"])
            else: 
                formatted = str(val)
            
            steps.append(self.step_builder.build(
                len(steps) + 1, 
                line_number, 
                line, 
                f"Print: {formatted}",
                self._get_full_snapshot(),
                self.call_stack.get_frames_info(),
                type="print", 
                output=formatted
            ))

        elif "=" in line and not any(op in line for op in ["==", ">=", "<=", "!="]):
            parts = line.split("=", 1)
            left, right = parts[0].strip(), parts[1].strip().rstrip(";")
            
            tokens = left.split()
            var_path = tokens[-1]
            is_decl = len(tokens) > 1
            
            val = self.evaluate_expression(right, line_number, steps)
            if isinstance(val, list):
                val = {"values": val, "lastUpdatedIndex": None}
            
            if "." in var_path:
                base_name, field_name = var_path.split(".", 1)
                obj_id = None
                if base_name == "this":
                    frame = self.call_stack.peek()
                    if frame: obj_id = frame.this_obj_id
                else:
                    obj_id = self._get_var(base_name)
                
                if isinstance(obj_id, int) and obj_id in self.memory.objects:
                    self.memory.set_instance_field(obj_id, field_name, val)
                else:
                    self._set_var(var_path, val, is_decl, line_number)
            else:
                self._set_var(var_path, val, is_decl, line_number)

        elif m := self.patterns['increment'].match(line):
            name, op = m.group(1), m.group(2)
            current = self._get_var(name) or 0
            self._set_var(name, current + (1 if op == '++' else -1), False, line_number)

        elif m := self.patterns['break_stmt'].match(line):
            steps.append(self.step_builder.build(
                len(steps) + 1, 
                line_number, 
                line, 
                "Breaking loop",
                self._get_full_snapshot(),
                self.call_stack.get_frames_info()
            ))
            raise BreakException()

        elif m := self.patterns['method_call'].match(line):
            if not any(line.startswith(kw) for kw in ['if', 'for', 'while', 'return', 'throw', 'try', 'catch']):
                start = m.end() - 1
                end = self._find_matching_paren(line, start)
                if end != -1:
                    args_str = line[start + 1:end]
                    arg_strs = self._parse_method_args(args_str)
                    args = [self.evaluate_expression(a, line_number, steps) for a in arg_strs]
                    self._execute_method_call(m.group(1), args, line_number, steps)

    # 🔥 UPDATED _get_full_snapshot AS PER YOUR REQUEST
    def _get_full_snapshot(self) -> Dict[str, Any]:
        snapshot = self.memory.get_snapshot()

        # ✅ FIXED VERSION - Convert object keys to string
        snapshot["heap"] = {
            str(k): v for k, v in self.memory.objects.items()
        }

        return snapshot

    def execute_lines(self, lines: List[str], base_line: int, steps: List, is_function_body: bool = False):
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith('//') or line in ["}", ";"]:
                i += 1
                continue

            line_no = base_line + i
            frame = self.call_stack.peek()
            if frame:
                frame.current_line_pointer = line_no

            if self.debug_mode and line_no in self.breakpoints:
                self.is_paused = True
                self.execution_pointer = (lines, i, base_line)
                return

            try:
                if line.startswith("try"):
                    i = self.exception_engine.execute_try_catch(
                        lines, i, base_line, steps, is_function_body
                    )
                    continue

                elif m := self.patterns['for_header'].match(line):
                    header = {'init': m.group(1), 'condition': m.group(2), 'increment': m.group(3)}
                    has_brace = m.group(4) == '{'
                    body, end = self.extract_block(lines, i + 1) if has_brace else (([line[m.end():].strip() or lines[i+1]], i + (0 if line[m.end():].strip() else 1)))
                    self.loop_engine.execute_for_loop(header, body, self, self.memory, self.step_builder, steps, base_line + i, is_function_body)
                    i = end + 1

                elif m := self.patterns['while_header'].match(line):
                    has_brace = m.group(2) == '{'
                    body, end = self.extract_block(lines, i + 1) if has_brace else (([line[m.end():].strip() or lines[i+1]], i + (0 if line[m.end():].strip() else 1)))
                    self.loop_engine.execute_while_loop(m.group(1), body, self, self.memory, self.step_builder, steps, base_line + i, is_function_body)
                    i = end + 1

                elif m := self.patterns['if_header'].match(line):
                    header_line = base_line + i
                    if m.group(2) == '{':
                        true_b, i = self.extract_block(lines, i + 1); i += 1
                    else:
                        rest = line[m.end():].strip()
                        true_b, i = ([rest], i + 1) if rest else ([lines[i+1]], i + 2)
                    
                    false_b = []
                    if i < len(lines) and self.patterns['else_line'].match(lines[i].strip()):
                        if '{' in lines[i]:
                            false_b, end_else = self.extract_block(lines, i + 1); i = end_else + 1
                        else:
                            rest = lines[i].split('else', 1)[1].strip()
                            false_b, i = ([rest], i + 1) if rest else ([lines[i+1]], i + 2)
                    self.condition_engine.execute_if(m.group(1), true_b, false_b, self, self.memory, self.step_builder, steps, header_line, is_function_body)

                else:
                    self.execute_line(line, base_line + i, steps)
                    i += 1

            except JavaException as je:
                raise je
            except BreakException:
                if not is_function_body: raise
                return
            except FunctionReturn:
                if is_function_body: raise
                return

    def _execute_method_call(self, full_method_name: str, args: List[Any], line_number: int, steps: List) -> Any:
        return self.method_engine.call(full_method_name, args, line_number, steps)

    def add_breakpoint(self, line):
        self.breakpoints.add(line)

    def remove_breakpoint(self, line):
        self.breakpoints.discard(line)

    def resume(self, steps):
        if not self.execution_pointer:
            return
        lines, i, base_line = self.execution_pointer
        self.is_paused = False
        self.execute_lines(lines[i:], base_line + i, steps, True)

    def step(self, steps):
        if not self.execution_pointer:
            return
        lines, i, base_line = self.execution_pointer
        self.is_paused = False
        self.execute_lines(lines[i:i+1], base_line + i, steps, True)

    def build_stack_trace(self, exception):
        trace = []
        for frame in reversed(self.call_stack.frames):
            trace.append({
                "class": frame.class_name,
                "method": frame.method_name,
                "line": frame.current_line_pointer
            })
        return {
            "type": exception.exception_type,
            "message": exception.message,
            "trace": trace
        }

    def extract_block(self, lines: List[str], start: int) -> Tuple[List[str], int]:
        block, count, i = [], 1, start
        while i < len(lines):
            line = lines[i]
            for char in line:
                if char == '{': count += 1
                elif char == '}':
                    count -= 1
                    if count == 0:
                        return block, i
            block.append(line)
            i += 1
        return block, i

    def execute(self, code: str):
        self._exception_active = False
        self.memory, self.call_stack, self.classes, self.imported_libraries = Memory(), CallStack(), {}, set()
        steps = []
        try:
            for line in code.split('\n'):
                if m := self.patterns['import_stmt'].match(line.strip()):
                    self.imported_libraries.add(m.group(1))

            lines = self._normalize_code(code)
            normalized_code = "\n".join(lines)
            
            self._parse_classes_recursive(lines, 0)
            
            implicit_main_body = []
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line or line.startswith('import') or line.startswith('//'):
                    i += 1
                elif self.patterns['class_def'].match(line):
                    _, end = self.extract_block(lines, i + 1)
                    i = end + 1
                elif self.patterns['method_def'].match(line):
                    _, end = self.extract_block(lines, i + 1)
                    i = end + 1
                else:
                    implicit_main_body.append(lines[i])
                    i += 1
            
            if implicit_main_body:
                if "Global" not in self.classes:
                    self.classes["Global"] = ClassDefinition("Global")
                self.classes["Global"].methods["main"] = MethodDefinition(
                    "public", True, "void", "main", [{"type": "String[]", "name": "args"}], implicit_main_body, 0
                )

            main_class = None
            public_class = next((c for c in self.classes.values() if "public" in c.name), None)
            if public_class and "main" in public_class.methods:
                main_class = public_class
            else:
                if "Global" in self.classes and "main" in self.classes["Global"].methods:
                    main_class = self.classes["Global"]
                else:
                    for c in self.classes.values():
                        if "main" in c.methods:
                            main_class = c
                            break
            
            if main_class and "main" in main_class.methods:
                self.current_class = main_class
                self.call_stack.push(StackFrame(main_class.name, "main", 0, {}, {"args": []}))
                try:
                    self.execute_lines(main_class.methods["main"].body, main_class.methods["main"].start_line, steps, True)
                except (FunctionReturn, BreakException): pass
                except JavaException as je:
                    self._exception_active = True
                    return steps, normalized_code, self.build_stack_trace(je)
                self.call_stack.pop()
            return steps, normalized_code, None

        except JavaException as je:
            self._exception_active = True
            return steps, normalized_code, self.build_stack_trace(je)
        except ExecutionError as e:
            return steps, normalized_code, {"type": e.type, "message": e.message, "line": e.line}
        except Exception as e:
            return steps, "\n".join(lines), {"type": "InternalError", "message": str(e), "line": 0}