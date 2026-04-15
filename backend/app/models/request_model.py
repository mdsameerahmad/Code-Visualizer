from pydantic import BaseModel

class CodeExecutionRequest(BaseModel):
    code: str