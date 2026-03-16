import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings, Settings
from database import init_db, close_db, get_connection, update_performance_history
from models import (
    StudentCreate, StudentResponse, AnswerSubmission, 
    FeedbackResponse, StudentProgress, QuestionGenerationRequest,
    GeneratedQuestion, HintRequest, HintResponse
)
import ai_service
import analytics
  
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    settings = get_settings()
    await init_db(settings.database_url)
    yield
    await close_db()

app = FastAPI(
    title="LuminaLearn API",
    description="AI-Powered Adaptive Learning System",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "https://127.0.0.1:3000",
        "https://lumina-learn-five.vercel.app",
        "https://lumina-app-mauve.vercel.app/"
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to LuminaLearn API", 
        "status": "operational",
        "ai_status": "Groq integrated"
    }


@app.post("/students", response_model=StudentResponse)
async def create_student(student: StudentCreate):
    """Registering a new student in the system."""
    async with get_connection() as conn:
        try:
            # 
            row = await conn.fetchrow(
                "INSERT INTO students (name, email) VALUES ($1, $2) RETURNING *",
                student.name, student.email
            )
            return dict(row)
        except asyncpg.UniqueViolationError:
            raise HTTPException(status_code=400, detail="Email already registered")


@app.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int):
    """Get student by ID."""
    async with get_connection() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM students WHERE id = $1", student_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Student not found")
        return dict(row)


@app.post("/submit-answer", response_model=FeedbackResponse)
async def submit_answer(
    submission: AnswerSubmission,
    background_tasks: BackgroundTasks
):
    # Validate student exists
    async with get_connection() as conn:
        student = await conn.fetchrow(
            "SELECT id, name FROM students WHERE id = $1", submission.student_id
        )
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Check correctness
        is_correct = submission.student_answer.strip().lower() == submission.correct_answer.strip().lower()
        
        # Generating AI feedback
        ai_feedback = await ai_service.groq_service.generate_feedback(
            topic=submission.topic,
            question=submission.question,
            student_answer=submission.student_answer,
            correct_answer=submission.correct_answer,
            is_correct=is_correct
        )
        
        # Saving to database with AI explanation
        try:
            result_row = await conn.fetchrow("""
                INSERT INTO quiz_results 
                (student_id, topic, question, correct_answer, student_answer, 
                 is_correct, time_taken_seconds, ai_explanation)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id, is_correct, ai_explanation, created_at
            """, 
                submission.student_id, submission.topic, submission.question,
                submission.correct_answer, submission.student_answer,
                is_correct, submission.time_taken_seconds, ai_feedback
            )
            
            # Update performance history 
            await update_performance_history(
                conn, submission.student_id, submission.topic,
                is_correct, submission.time_taken_seconds or 0
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        return FeedbackResponse(
            is_correct=is_correct,
            feedback=ai_feedback,
            saved_to_db=True
        )


@app.post("/generate-question", response_model=GeneratedQuestion)
async def generate_question(request: QuestionGenerationRequest):
    """
    Generate a new AI-powered quiz question on any topic.
    """
    question_data = await ai_service.groq_service.generate_question(
        topic=request.topic,
        difficulty=request.difficulty
    )
    return GeneratedQuestion(**question_data)


@app.post("/get-hint", response_model=HintResponse)
async def get_hint(request: HintRequest):
    """
    Get a contextual hint for a question without revealing the answer.
    """
    # Check previous attempts for this question pattern
    async with get_connection() as conn:
        previous_attempts = await conn.fetchval("""
            SELECT COUNT(*) FROM quiz_results
            WHERE student_id = $1 AND question = $2
        """, request.student_id, request.question)
    
    hint = await ai_service.groq_service.generate_hint(
        topic=request.topic,
        question=request.question,
        student_previous_attempts=previous_attempts
    )
    
    return HintResponse(hint=hint)


@app.get("/student-progress/{student_id}", response_model=StudentProgress)
async def get_student_progress(student_id: int):
    """Get detailed progress for a student."""
    async with get_connection() as conn:
        # Verify student exists
        student = await conn.fetchrow(
            "SELECT id, name FROM students WHERE id = $1", student_id
        )
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get topic breakdown
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
        
        return StudentProgress(
            student_id=student_id,
            student_name=student['name'],
            overall_accuracy=round(overall_accuracy, 2),
            topics=topics
        )


@app.get("/recent-mistakes/{student_id}")
async def get_recent_mistakes(student_id: int, limit: int = 5):
    """
    Get recent wrong answers with AI explanations for review.
    """
    async with get_connection() as conn:
        rows = await conn.fetch("""
            SELECT 
                topic,
                question,
                student_answer,
                correct_answer,
                ai_explanation,
                created_at
            FROM quiz_results
            WHERE student_id = $1 AND is_correct = false
            ORDER BY created_at DESC
            LIMIT $2
        """, student_id, limit)
        
        return [dict(row) for row in rows]


# analytics routes
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

if __name__ != "__main__":
    app = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)