from typing import List, Optional
from database import get_connection

class QuizRepository:
    async def save_result(
        self, 
        student_id: int,
        topic: str,
        question: str,
        correct_answer: str,
        student_answer: str,
        is_correct: bool,
        time_taken_seconds: Optional[int],
        ai_explanation: Optional[str] 
    ) -> dict:
        async with get_connection() as conn:
            row = await conn.fetchrow("""
                INSERT INTO quiz_results
                (student_id, topic, question, correct_answer, student_answer, is_correct, time_taken_seconds, ai_explanation)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id, is_correct, ai_explanation, created_at
            """, student_id, topic, question, correct_answer, student_answer, is_correct, time_taken_seconds, ai_explanation)
            return dict(row) if row else None  # Also added null check

    async def get_recent_mistakes(self, student_id: int, limit: int = 5) -> List[dict]:
        async with get_connection() as conn:
            rows = await conn.fetch("""
                SELECT topic, question, student_answer, correct_answer, ai_explanation, created_at
                FROM quiz_results
                WHERE student_id = $1 AND is_correct = false
                ORDER BY created_at DESC
                LIMIT $2
            """, student_id, limit)
            return [dict(row) for row in rows]

    async def count_attempts(self, student_id: int, question: str) -> int:
        async with get_connection() as conn:
            return await conn.fetchval("""
                SELECT COUNT(*) FROM quiz_results
                WHERE student_id = $1 AND question = $2
            """, student_id, question)