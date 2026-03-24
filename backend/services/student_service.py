from typing import Optional
from repositories.student_repository import StudentRepository

class StudentService:
    def __init__(self, repository: StudentRepository):
        self.repo = repository
    
    async def get_student(self, student_id: int) -> Optional[dict]:
        return await self.repo.get_by_id(student_id)
    
    async def create_student(self, name: str, email: str) -> dict:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")
        return await self.repo.create(name, email)

