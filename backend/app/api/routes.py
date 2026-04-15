from fastapi import APIRouter
from app.models.request_model import CodeExecutionRequest
from app.models.response_model import CodeExecutionResponse
from app.services.execution_service import ExecutionService

router = APIRouter()

@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    try:
        service = ExecutionService()
        result = service.run(request.code)

        return CodeExecutionResponse(
            steps=result["steps"],
            normalized_code=result["normalized_code"],
            error=result["error"]
        )

    except Exception as e:
        return CodeExecutionResponse(
            steps=[],
            normalized_code=None,
            error={
                "type": "InternalError",
                "message": str(e),
                "line": 0
            }
        )