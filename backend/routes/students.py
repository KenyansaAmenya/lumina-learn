# routes/students.py
from fastapi import APIRouter, HTTPException, Depends
from models import StudentCreate, StudentResponse
from services.student_service import StudentService
from dependencies import get_student_service

router = APIRouter(prefix="/students", tags=["students"])

@router.post("", response_model=StudentResponse)
async def create_student(
    student: StudentCreate,
    service: StudentService = Depends(get_student_service)
):
    try:
        result = await service.create_student(student.name, student.email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    service: StudentService = Depends(get_student_service)
):
    result = await service.get_student(student_id)
    if not result:
        raise HTTPException(status_code=404, detail="Student not found")
    return result

