from typing import Optional
from database import get_connection

class StudentRepository:
    async def get_by_id(self, student_id: int) -> Optional[dict]:
        async with get_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM students WHERE id = $1", student_id
            )
            return dict(row) if row else None

    async def get_by_email(self, email: str) -> Optional[dict]:
        async with get_connection() as conn:
            row = await conn.fetchrow(  
                "SELECT * FROM students WHERE email = $1", email
            )
            return dict(row) if row else None 

    async def create(self, name: str, email: str) -> dict:
        async with get_connection() as conn:
            row = await conn.fetchrow(  
                "INSERT INTO students (name, email) VALUES ($1, $2) RETURNING *",
                name, email
            )
            return dict(row) 