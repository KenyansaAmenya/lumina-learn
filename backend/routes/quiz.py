from fastapi import APIRouter, HTTPException, Depends
from models import AnswerSubmission, FeedbackResponse, QuestionGenerationRequest, GeneratedQuestion, HintRequest, HintResponse
from services.quiz_service import QuizService
from dependencies import get_quiz_service

router = APIRouter(tags=["quiz"])

@router.post("/submit-answer", response_model=FeedbackResponse)
async def submit_answer(
    submission: AnswerSubmission,
    service: QuizService = Depends(get_quiz_service)
):
    try:
        return await service.process_answer(
            student_id=submission.student_id,
            topic=submission.topic,
            question=submission.question,
            correct_answer=submission.correct_answer,
            student_answer=submission.student_answer,
            time_taken_seconds=submission.time_taken_seconds
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-question", response_model=GeneratedQuestion)
async def generate_question(
    request: QuestionGenerationRequest,
    service: QuizService = Depends(get_quiz_service)
):
    result = await service.generate_question(request.topic, request.difficulty)
    return GeneratedQuestion(**result)

@router.post("/get-hint", response_model=HintResponse)
async def get_hint(
    request: HintRequest,
    service: QuizService = Depends(get_quiz_service)
):
    hint = await service.get_hint(
        request.student_id, request.topic, request.question
    )
    return HintResponse(hint=hint)

@router.get("/recent-mistakes/{student_id}")
async def get_recent_mistakes(
    student_id: int,
    limit: int = 5,
    service: QuizService = Depends(get_quiz_service)
):
    return await service.get_recent_mistakes(student_id, limit)

