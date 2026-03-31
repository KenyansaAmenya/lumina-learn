import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import init_db, close_db, get_connection 
from schema import create_tables  

# Import routers
from routes import students, quiz, progress, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    settings = get_settings()
    
    await init_db(settings.database_url)
    
    async with get_connection() as conn:
        await create_tables(conn)
    
    yield
    
    # Cleanup
    await close_db()

app = FastAPI(
    title="LuminaLearn API",
    description="AI-Powered Adaptive Learning System",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Frontend dev server
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "https://127.0.0.1:3000", 
        "https://lumina-learn-five.vercel.app", 
        "https://lumina-ui-topaz.vercel.app",
        "lumin-wheat-ten.vercel.app" 
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
        "version": "3.0.0",
        "architecture": "Controller-Service-Repository"
    }

app.include_router(students.router)
app.include_router(quiz.router)
app.include_router(progress.router)
app.include_router(analytics.router)

if __name__ != "__main__":
    app = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)