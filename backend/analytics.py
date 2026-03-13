from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from database import get_connection
from models import StrugglingStudent, HardestTopic, TopicPerformance
import ai_service

router = APIRouter()


@router.get("/struggling", response_model=List[StrugglingStudent])
async def get_struggling_students(threshold: float = Query(0.6, ge=0, le=1)):
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
        
        result = []
        for row in rows:
            topic_rows = await conn.fetch("""
                SELECT topic
                FROM performance_history
                WHERE student_id = $1 
                AND (correct_count::float / NULLIF(total_attempts, 0)) < $2
            """, row['student_id'], threshold)
            
            result.append({
                "student_id": row['student_id'],
                "student_name": row['student_name'],
                "email": row['email'],
                "overall_accuracy": round(row['avg_score'] * 100, 2),
                "topics_struggling": [t['topic'] for t in topic_rows]
            })
        
        return result


@router.get("/hardest-topic", response_model=HardestTopic)
async def get_hardest_topic():
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
        
        if not row:
            raise HTTPException(status_code=404, detail="No quiz data available")
        
        return {
            "topic": row['topic'],
            "avg_accuracy": round(row['avg_accuracy'] * 100, 2),
            "total_attempts": row['total_attempts']
        }


@router.get("/student-report/{student_id}")
async def get_individual_report(student_id: int):
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
        
        if not rows:
            raise HTTPException(status_code=404, detail="No data for this student")
        
        return [dict(row) for row in rows]


@router.get("/class-overview")
async def get_class_overview():
    async with get_connection() as conn:
        total_students = await conn.fetchval("SELECT COUNT(*) FROM students")
        total_attempts = await conn.fetchval("SELECT COUNT(*) FROM quiz_results")
        avg_accuracy = await conn.fetchval("""
            SELECT AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END)
            FROM quiz_results
        """)
        
        # Topic difficulty ranking
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
            "overall_accuracy": round((avg_accuracy or 0) * 100, 2),
            "topic_breakdown": [
                {
                    "topic": row['topic'],
                    "accuracy": round(row['accuracy'] * 100, 2),
                    "students_attempted": row['students_attempted']
                }
                for row in topic_stats
            ]
        }


@router.post("/ai-teaching-insights/{student_id}")
async def get_ai_teaching_insights(student_id: int):
    async with get_connection() as conn:
        # Get student's weak areas
        weak_areas = await conn.fetch("""
            SELECT topic, total_attempts, correct_count
            FROM performance_history
            WHERE student_id = $1
            AND (correct_count::float / NULLIF(total_attempts, 0)) < 0.6
            ORDER BY (correct_count::float / NULLIF(total_attempts, 0)) ASC
        """, student_id)
        
        if not weak_areas:
            return {"message": "Student is performing well across all topics!"}
        
        # Building context for AI
        context = "Student performance data:\n"
        for area in weak_areas:
            accuracy = (area['correct_count'] / area['total_attempts'] * 100) if area['total_attempts'] > 0 else 0
            context += f"- {area['topic']}: {accuracy:.1f}% accuracy ({area['correct_count']}/{area['total_attempts']} correct)\n"
        
        prompt = f"""As an expert educator, analyze this student's weak areas and provide 3 specific, actionable teaching strategies:

{context}

Provide:
1. Root cause analysis (why they might be struggling)
2. 3 concrete intervention strategies
3. Recommended resources or practice types
4. Timeline for improvement check

Keep response under 300 words, encouraging and professional."""

        try:
            insights = await ai_service.groq_service.client.chat.completions.create(
                model=ai_service.groq_service.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            
            return {
                "student_id": student_id,
                "weak_areas": [dict(row) for row in weak_areas],
                "ai_recommendations": insights.choices[0].message.content
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")