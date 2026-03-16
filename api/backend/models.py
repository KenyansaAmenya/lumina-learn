# Pyndatic models
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# Student Models
class StudentCreate(BaseModel):
    name: str
    email: EmailStr


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Quiz Models
class AnswerSubmission(BaseModel):
    student_id: int
    topic: str
    question: str
    correct_answer: str
    student_answer: str
    time_taken_seconds: Optional[int] = None


class QuizResultResponse(BaseModel):
    id: int
    is_correct: bool
    ai_explanation: Optional[str] = None
    created_at: datetime


class FeedbackResponse(BaseModel):
    is_correct: bool
    feedback: str
    saved_to_db: bool = True


# Progress Models
class TopicPerformance(BaseModel):
    topic: str
    total_attempts: int
    correct_count: int
    accuracy_percentage: float
    average_time_seconds: float


class StudentProgress(BaseModel):
    student_id: int
    student_name: str
    overall_accuracy: float
    topics: List[TopicPerformance]


# Analytics Models
class StrugglingStudent(BaseModel):
    student_id: int
    student_name: str
    email: str
    overall_accuracy: float
    topics_struggling: List[str]


class HardestTopic(BaseModel):
    topic: str
    avg_accuracy: float
    total_attempts: int
    
# models for phase 2
class QuestionGenerationRequest(BaseModel):
    topic: str
    difficulty: str = "medium"

class GeneratedQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explaination: str
    hint: str


class HintRequest(BaseModel):
    topic: str
    question: str
    student_id: int

class HintResponse(BaseModel):
    hint: str                