from fastapi import APIRouter, HTTPException, Depends
from models import StudentProgress
from services.progress_service import ProgressService
from dependencies import get_progress_service

router = APIRouter(tags=["progress"])

@router.get("/student-progress/{student_id}", response_model=StudentProgress)
async def get_student_progress(
    student_id: int,
    service: ProgressService = Depends(get_progress_service)
):
    try:
        return await service.get_student_progress(student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

