# api/main.py
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from main import app

# Local imports (same folder, no 'backend.' prefix)
from config import get_settings, Settings
from database import init_db, close_db, get_connection, update_performance_history
from models import (
    StudentCreate, StudentResponse, AnswerSubmission, 
    FeedbackResponse, StudentProgress, QuestionGenerationRequest,
    GeneratedQuestion, HintRequest, HintResponse
)
import ai_service
import analytics

handler = Mangum(app)

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "LuminaLearn API", "status": "running on Vercel"}

@app.get("/health")
async def health():
    return {"status": "healthy", "deployment": "vercel"}

# ... (copy all your other routes here) ...

# CRITICAL: Expose for Vercel
app = app
