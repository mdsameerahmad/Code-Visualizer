from typing import List
import re

from app.engine.exceptions import JavaException


EXCEPTION_HIERARCHY = {
    "ArithmeticException": ["RuntimeException", "Exception", "Throwable"],
    "NullPointerException": ["RuntimeException", "Exception", "Throwable"],
    "ArrayIndexOutOfBoundsException": ["RuntimeException", "Exception", "Throwable"],
    "RuntimeException": ["Exception", "Throwable"],
    "Exception": ["Throwable"],
    "Throwable": []
}


class ExceptionEngine:
    def __init__(self, executor):
        self.executor = executor

    def execute_try_catch(self, lines: List[str], i: int, base_line: int, steps: List, is_function_body: bool) -> int:

        try_body, end_try = self.executor.extract_block(lines, i + 1)
        catch_re = re.compile(r'^\}?\s*catch\s*\(')
        catch_start = end_try if catch_re.match(lines[end_try].strip() if end_try < len(lines) else "") else end_try + 1

        # ✅ PRE-SCAN: Find finally block and skip catches to get final return index
        idx = catch_start
        while idx < len(lines):
            line = lines[idx].strip()
            if catch_re.match(line):
                _, end_catch = self.executor.extract_block(lines, idx + 1)
                idx = end_catch if (end_catch < len(lines) and catch_re.match(lines[end_catch].strip())) else end_catch + 1
            else:
                break

        finally_body = []
        finally_start_idx = -1
        if idx < len(lines) and lines[idx].strip().startswith("finally"):
            finally_body, finally_end = self.executor.extract_block(lines, idx + 1)
            finally_start_idx = idx
            final_return_idx = finally_end + 1
        else:
            final_return_idx = idx

        try:
            # ✅ run try block
            self.executor.execute_lines(
                try_body,
                base_line + i + 1,
                steps,
                is_function_body
            )

            # ✅ skip all catches
            idx = catch_start
            while idx < len(lines):
                line = lines[idx].strip()
                if catch_re.match(line):
                    _, end_catch = self.executor.extract_block(lines, idx + 1)
                    idx = end_catch if (end_catch < len(lines) and catch_re.match(lines[end_catch].strip())) else end_catch + 1
                else:
                    break

            return final_return_idx

        except JavaException as je:
            idx = catch_start
            matched_catch = False

            while idx < len(lines):
                line = lines[idx].strip()

                if not line:
                    idx += 1
                    continue

                if not catch_re.match(line):
                    break

                # parse catch(Exception ex)
                inside = line[line.find("(")+1:line.find(")")]
                parts = inside.strip().split()

                catch_type = parts[0]
                catch_var = parts[1] if len(parts) > 1 else "e"

                catch_body, end_catch = self.executor.extract_block(lines, idx + 1)

                # 🔥 MATCH LOGIC (JAVA STYLE)
                if catch_type == je.exception_type or catch_type in EXCEPTION_HIERARCHY.get(je.exception_type, []):
                    matched_catch = True
                    self.executor._set_var(
                        catch_var,
                        {
                            "type": je.exception_type,
                            "message": je.message,
                            "line": je.line
                        },
                        True,
                        base_line + idx
                    )

                    self.executor.execute_lines(
                        catch_body,
                        base_line + idx + 1,
                        steps,
                        is_function_body
                    )

                    # After executing a matching catch, skip remaining catches
                    next_idx = end_catch if (end_catch < len(lines) and catch_re.match(lines[end_catch].strip())) else end_catch + 1
                    while next_idx < len(lines):
                        nxt = lines[next_idx].strip()
                        if catch_re.match(nxt):
                            _, next_end = self.executor.extract_block(lines, next_idx + 1)
                            next_idx = next_end if (next_end < len(lines) and catch_re.match(lines[next_end].strip())) else next_end + 1
                        else:
                            break
                    idx = next_idx # Update idx to point after all catches
                    break # Exit the while loop after finding a match and skipping others

                else:
                    idx = end_catch if (end_catch < len(lines) and catch_re.match(lines[end_catch].strip())) else end_catch + 1

            # ❌ no match → throw
            if not matched_catch:
                raise je
            return final_return_idx
        finally:
            if finally_body:
                self.executor.execute_lines(
                    finally_body,
                    base_line + finally_start_idx + 1,
                    steps,
                    is_function_body
                )