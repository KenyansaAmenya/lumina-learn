from typing import List
from repositories.analytics_repository import AnalyticsRepository
from services.ai_service import AIService
from models import StrugglingStudent, HardestTopic

class AnalyticsService:
    def __init__(
        self, 
        repository: AnalyticsRepository, 
        ai_service: AIService
    ):
        self.repo = repository
        self.ai = ai_service

    async def get_struggling_students(self, threshold: float) -> List[StrugglingStudent]:
        rows = await self.repo.get_struggling_students(threshold)
        
        result = []
        for row in rows:
            weak_topics = await self.repo.get_student_weak_topics(
                row['student_id'], threshold
            )
            result.append(StrugglingStudent(
                student_id=row['student_id'],
                student_name=row['student_name'],
                email=row['email'],
                overall_accuracy=round(row['avg_score'] * 100, 2),
                topics_struggling=weak_topics
            ))
        return result

    async def get_hardest_topic(self) -> HardestTopic:
        row = await self.repo.get_hardest_topic()
        if not row:
            raise ValueError("No quiz data available")
        
        return HardestTopic(
            topic=row['topic'],
            avg_accuracy=round(row['avg_accuracy'] * 100, 2),
            total_attempts=row['total_attempts']
        )

    async def get_student_report(self, student_id: int) -> List[dict]:
        rows = await self.repo.get_student_report(student_id)
        if not rows:
            raise ValueError("No data for this student")
        return [dict(row) for row in rows]

    async def get_class_overview(self) -> dict:
        stats = await self.repo.get_class_overview_stats()
        
        return {
            "total_students": stats['total_students'],
            "total_attempts": stats['total_attempts'],
            "overall_accuracy": round((stats['avg_accuracy'] or 0) * 100, 2),
            "topic_breakdown": [
                {
                    "topic": row['topic'],
                    "accuracy": round(row['accuracy'] * 100, 2),
                    "students_attempted": row['students_attempted']
                }
                for row in stats['topic_stats']
            ]
        }

    async def get_ai_teaching_insights(self, student_id: int) -> dict:
        weak_areas = await self.repo.get_weak_areas(student_id)
        
        if not weak_areas:
            return {
                "student_id": student_id,
                "weak_areas": [],
                "ai_recommendations": "Student is performing well across all topics!"
            }
        
        insights = await self.ai.generate_teaching_insights(weak_areas)
        
        return {
            "student_id": student_id,
            "weak_areas": [dict(row) for row in weak_areas],
            "ai_recommendations": insights
        }