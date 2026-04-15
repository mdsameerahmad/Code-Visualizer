from app.engine.executor import Executor
from app.engine.exceptions import ExecutionError

class ExecutionService:
    def __init__(self):
        self.executor = Executor()

    def run(self, code: str):
        try:
            steps, normalized_code, error = self.executor.execute(code)

            # ✅ Always return in consistent shape
            return {
                "steps": steps if steps else [],
                "normalized_code": normalized_code,
                "error": error
            }

        except ExecutionError as e:
            return {
                "steps": [],
                "normalized_code": None,
                "error": {
                    "type": e.type,
                    "message": e.message,
                    "line": e.line
                }
            }

        except Exception as e:
            return {
                "steps": [],
                "normalized_code": None,
                "error": {
                    "type": "InternalError",
                    "message": str(e),
                    "line": 0
                }
            }