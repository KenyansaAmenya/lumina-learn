from repositories.analytics_repository import AnalyticsRepository
from repositories.student_repository import StudentRepository

class ProgressService:
    def __init__(
        self, 
        analytics_repo: AnalyticsRepository,
        student_repo: StudentRepository
    ):
        self.analytics_repo = analytics_repo
        self.student_repo = student_repo
    
    async def get_student_progress(self, student_id: int) -> dict:
        # Verifying that a student exists
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")
        
        # Getting performance data
        rows = await self.analytics_repo.get_performance_history(student_id)
        
        topics = []
        total_correct = 0
        total_attempts = 0
        
        for row in rows:
            topics.append({
                "topic": row['topic'],
                "total_attempts": row['total_attempts'],
                "correct_count": row['correct_count'],
                "accuracy_percentage": round(row['accuracy'] or 0, 2),
                "average_time_seconds": round(row['average_time_seconds'], 2)
            })
            total_correct += row['correct_count']
            total_attempts += row['total_attempts']
        
        overall_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            "student_id": student_id,
            "student_name": student['name'],
            "overall_accuracy": round(overall_accuracy, 2),
            "topics": topics
        }
