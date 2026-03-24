from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List
from models import StrugglingStudent, HardestTopic
from services.analytics_service import AnalyticsService
from dependencies import get_analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/struggling", response_model=List[StrugglingStudent])
async def get_struggling_students(
    threshold: float = Query(0.6, ge=0, le=1),
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        return await service.get_struggling_students(threshold)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hardest-topic", response_model=HardestTopic)
async def get_hardest_topic(
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        return await service.get_hardest_topic()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/student-report/{student_id}")
async def get_individual_report(
    student_id: int,
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        return await service.get_student_report(student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/class-overview")
async def get_class_overview(
    service: AnalyticsService = Depends(get_analytics_service)
):
    return await service.get_class_overview()

@router.post("/ai-teaching-insights/{student_id}")
async def get_ai_teaching_insights(
    student_id: int,
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        return await service.get_ai_teaching_insights(student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))