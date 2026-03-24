from typing import List, Optional
from database import get_connection

class AnalyticsRepository:
    async def get_struggling_students(self, threshold: float) -> List[dict]:
        async with get_connection() as conn:
            rows = await conn.fetch("""
                SELECT 
                    s.id as student_id,
                    s.name as student_name,
                    s.email,
                    AVG(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END) as avg_score
                FROM students s
                JOIN quiz_results qr ON s.id = qr.student_id
                GROUP BY s.id, s.name, s.email
                HAVING AVG(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END) < $1
                ORDER BY avg_score ASC
            """, threshold)
            return [dict(row) for row in rows]  

    async def get_student_weak_topics(self, student_id: int, threshold: float) -> List[str]:
        async with get_connection() as conn:
            rows = await conn.fetch("""
                SELECT topic FROM performance_history
                WHERE student_id = $1 
                AND (correct_count::float / NULLIF(total_attempts, 0)) < $2
            """, student_id, threshold)
            return [r['topic'] for r in rows] 

    async def get_hardest_topic(self) -> Optional[dict]:
        async with get_connection() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    topic,
                    AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as avg_accuracy,
                    COUNT(*) as total_attempts
                FROM quiz_results
                GROUP BY topic
                ORDER BY avg_accuracy ASC
                LIMIT 1
            """)
            return dict(row) if row else None  

    async def get_student_report(self, student_id: int) -> List[dict]:
        async with get_connection() as conn:
            rows = await conn.fetch("""
                SELECT 
                    topic,
                    total_attempts,
                    correct_count,
                    (correct_count::float / NULLIF(total_attempts, 0) * 100) as avg_score,
                    average_time_seconds
                FROM performance_history
                WHERE student_id = $1
                ORDER BY topic
            """, student_id)
            return [dict(row) for row in rows] 

    async def get_class_overview_stats(self) -> dict:
        async with get_connection() as conn:
            total_students = await conn.fetchval("SELECT COUNT(*) FROM students")
            total_attempts = await conn.fetchval("SELECT COUNT(*) FROM quiz_results")
            avg_accuracy = await conn.fetchval("""
                SELECT AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END)
                FROM quiz_results
            """)
            topic_stats = await conn.fetch("""
                SELECT 
                    topic,
                    AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as accuracy,
                    COUNT(DISTINCT student_id) as students_attempted
                FROM quiz_results
                GROUP BY topic
                ORDER BY accuracy ASC
            """)
            return {
                "total_students": total_students,
                "total_attempts": total_attempts,
                "avg_accuracy": avg_accuracy,
                "topic_stats": [dict(row) for row in topic_stats]  
            }

    async def get_weak_areas(self, student_id: int) -> List[dict]:
        async with get_connection() as conn:
            rows = await conn.fetch("""
                SELECT topic, total_attempts, correct_count
                FROM performance_history
                WHERE student_id = $1
                AND (correct_count::float / NULLIF(total_attempts, 0)) < 0.6
                ORDER BY (correct_count::float / NULLIF(total_attempts, 0)) ASC
            """, student_id)
            return [dict(row) for row in rows] 

    async def get_performance_history(self, student_id: int) -> List[dict]:
        async with get_connection() as conn:
            rows = await conn.fetch("""
                SELECT 
                    topic,
                    total_attempts,
                    correct_count,
                    (correct_count::float / NULLIF(total_attempts, 0) * 100) as accuracy,
                    average_time_seconds
                FROM performance_history
                WHERE student_id = $1
                ORDER BY topic
            """, student_id)
            return [dict(row) for row in rows]  