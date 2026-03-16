import asyncpg
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

pool: Optional[asyncpg.Pool] = None

async def init_db(database_url: str = None):
   
    global pool
    url = database_url or DATABASE_URL
    
    if not url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    try:
        # Create connection pool
        pool = await asyncpg.create_pool(
            url,
            min_size=1,
            max_size=10,
            command_timeout=60,
            ssl="require" if "supabase" in url else None
        )
        
        # Create tables if they don't exist
        async with pool.acquire() as conn:
            await create_tables(conn)
            
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def create_tables(conn: asyncpg.Connection):
    """Create database tables if they don't exist."""
    await conn.execute("""
        -- Students table
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Quiz results with AI feedback
        CREATE TABLE IF NOT EXISTS quiz_results (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            topic VARCHAR(100) NOT NULL,
            question TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            student_answer TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            time_taken_seconds INTEGER,
            ai_explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Aggregated performance history
        CREATE TABLE IF NOT EXISTS performance_history (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            topic VARCHAR(100) NOT NULL,
            total_attempts INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            average_time_seconds FLOAT DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, topic)
        );
        
        -- Index for faster queries
        CREATE INDEX IF NOT EXISTS idx_quiz_results_student_id ON quiz_results(student_id);
        CREATE INDEX IF NOT EXISTS idx_quiz_results_topic ON quiz_results(topic);
        CREATE INDEX IF NOT EXISTS idx_performance_history_student_id ON performance_history(student_id);
    """)


async def close_db():
    global pool
    if pool:
        await pool.close()
        pool = None
        logger.info("Database connection closed")


@asynccontextmanager
async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    if pool:
        async with pool.acquire() as conn:
            yield conn
        return
    
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable not set")
    
    conn = None
    try:
        conn = await asyncpg.connect(
            DATABASE_URL,
            ssl="require" if "supabase" in DATABASE_URL else None,
            command_timeout=60
        )
        yield conn
    finally:
        if conn:
            await conn.close()


async def update_performance_history(
    conn: asyncpg.Connection,
    student_id: int,
    topic: str,
    is_correct: bool,
    time_taken: int
):

    await conn.execute("""
        INSERT INTO performance_history 
            (student_id, topic, total_attempts, correct_count, average_time_seconds, last_updated)
        VALUES 
            ($1, $2, 1, $3, $4, CURRENT_TIMESTAMP)
        ON CONFLICT (student_id, topic) 
        DO UPDATE SET
            total_attempts = performance_history.total_attempts + 1,
            correct_count = performance_history.correct_count + $3,
            average_time_seconds = (
                (performance_history.average_time_seconds * performance_history.total_attempts + $4) 
                / (performance_history.total_attempts + 1)
            ),
            last_updated = CURRENT_TIMESTAMP;
    """, student_id, topic, 1 if is_correct else 0, time_taken)


async def get_student_by_id(student_id: int):
    async with get_connection() as conn:
        return await conn.fetchrow(
            "SELECT * FROM students WHERE id = $1", 
            student_id
        )

async def create_student(name: str, email: str):
    async with get_connection() as conn:
        try:
            return await conn.fetchrow(
                "INSERT INTO students (name, email) VALUES ($1, $2) RETURNING *",
                name, email
            )
        except asyncpg.UniqueViolationError:
            raise ValueError(f"Email {email} already registered")

async def save_quiz_result(
    student_id: int,
    topic: str,
    question: str,
    correct_answer: str,
    student_answer: str,
    is_correct: bool,
    time_taken_seconds: Optional[int],
    ai_explanation: Optional[str]
):
    async with get_connection() as conn:
        async with conn.transaction():
            # Insert quiz result
            result = await conn.fetchrow("""
                INSERT INTO quiz_results 
                (student_id, topic, question, correct_answer, student_answer, 
                 is_correct, time_taken_seconds, ai_explanation)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id, is_correct, ai_explanation, created_at
            """, 
                student_id, topic, question,
                correct_answer, student_answer,
                is_correct, time_taken_seconds, ai_explanation
            )
            
            # Update performance history
            await update_performance_history(
                conn, student_id, topic,
                is_correct, time_taken_seconds or 0
            )
            
            return result


async def health_check():
    try:
        async with get_connection() as conn:
            result = await conn.fetchval("SELECT 1")
            return {"status": "healthy", "database": "connected", "result": result}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}