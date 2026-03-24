from typing import Optional
from services.ai_service import AIService
from repositories.quiz_repository import QuizRepository
from database import get_connection  # Only for transaction

class QuizService:
    def __init__(
        self, 
        quiz_repo: QuizRepository, 
        ai_service: AIService
    ):
        self.quiz_repo = quiz_repo
        self.ai = ai_service
    
    async def process_answer(
        self,
        student_id: int,
        topic: str,
        question: str,
        correct_answer: str,
        student_answer: str,
        time_taken_seconds: Optional[int]
    ) -> dict:
        is_correct = student_answer.strip().lower() == correct_answer.strip().lower()
        
        ai_feedback = await self.ai.generate_feedback(
            topic, question, student_answer, correct_answer, is_correct
        )
        
        result = await self.quiz_repo.save_result(
            student_id, topic, question, correct_answer,
            student_answer, is_correct, time_taken_seconds, ai_feedback
        )
        
        await self._update_performance(student_id, topic, is_correct, time_taken_seconds or 0)
        
        return {
            "is_correct": is_correct,
            "feedback": ai_feedback,
            "saved_to_db": True
        }
    
    async def _update_performance(
        self, student_id: int, topic: str, is_correct: bool, time_taken: int
    ):
        async with get_connection() as conn:
            await conn.execute("""
                INSERT INTO performance_history 
                    (student_id, topic, total_attempts, correct_count, average_time_seconds)
                VALUES ($1, $2, 1, $3, $4)
                ON CONFLICT (student_id, topic) 
                DO UPDATE SET
                    total_attempts = performance_history.total_attempts + 1,
                    correct_count = performance_history.correct_count + $3,
                    average_time_seconds = (
                        (performance_history.average_time_seconds * performance_history.total_attempts + $4) 
                        / (performance_history.total_attempts + 1)
                    ),
                    last_updated = CURRENT_TIMESTAMP;
            """, student_id, topic, 1 if is_correct else 0, time_taken)
    
    async def generate_question(self, topic: str, difficulty: str) -> dict:
        return await self.ai.generate_question(topic, difficulty)
    
    async def get_hint(
        self, student_id: int, topic: str, question: str
    ) -> str:
        previous_attempts = await self.quiz_repo.count_attempts(student_id, question)
        return await self.ai.generate_hint(topic, question, previous_attempts)
    
    async def get_recent_mistakes(self, student_id: int, limit: int = 5):
        return await self.quiz_repo.get_recent_mistakes(student_id, limit)
