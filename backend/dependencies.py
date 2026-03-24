from fastapi import Depends
from groq import AsyncGroq
from config import get_settings

from repositories.student_repository import StudentRepository
from repositories.quiz_repository import QuizRepository
from repositories.analytics_repository import AnalyticsRepository

from services.ai_service import AIService
from services.student_service import StudentService
from services.quiz_service import QuizService
from services.progress_service import ProgressService
from services.analytics_service import AnalyticsService

_ai_service = None
_student_repo = None
_quiz_repo = None
_analytics_repo = None

def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        settings = get_settings()
        client = AsyncGroq(api_key=settings.groq_api_key)
        _ai_service = AIService(groq_client=client)
    return _ai_service

def get_student_repository() -> StudentRepository:
    global _student_repo
    if _student_repo is None:
        _student_repo = StudentRepository()
    return _student_repo

def get_quiz_repository() -> QuizRepository:
    global _quiz_repo
    if _quiz_repo is None:
        _quiz_repo = QuizRepository()
    return _quiz_repo

def get_analytics_repository() -> AnalyticsRepository:
    global _analytics_repo
    if _analytics_repo is None:
        _analytics_repo = AnalyticsRepository()
    return _analytics_repo

def get_student_service(
    repo: StudentRepository = Depends(get_student_repository)
) -> StudentService:
    return StudentService(repository=repo)

def get_quiz_service(
    quiz_repo: QuizRepository = Depends(get_quiz_repository),
    ai: AIService = Depends(get_ai_service)
) -> QuizService:
    return QuizService(quiz_repo=quiz_repo, ai_service=ai)

def get_progress_service(
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository),
    student_repo: StudentRepository = Depends(get_student_repository)
) -> ProgressService:
    return ProgressService(analytics_repo=analytics_repo, student_repo=student_repo)

def get_analytics_service(
    repo: AnalyticsRepository = Depends(get_analytics_repository),
    ai: AIService = Depends(get_ai_service)
) -> AnalyticsService:
    return AnalyticsService(repository=repo, ai_service=ai)