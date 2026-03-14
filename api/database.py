import asyncpg
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

DATABASE_URL = os.getenv("DATABASE_URL")
pool = None

async def init_db(database_url: str = None):
    global pool
    url = database_url or DATABASE_URL
    
    if not url:
        raise ValueError("DATABASE_URL not set")
    
    pool = await asyncpg.create_pool(
        url,
        min_size=1,
        max_size=10,
        command_timeout=60,
        ssl="require" if "supabase" in url else None
    )
    
    async with pool.acquire() as conn:
        await create_tables(conn)

async def create_tables(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
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
    """)

async def close_db():
    global pool
    if pool:
        await pool.close()

@asynccontextmanager
async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    if pool:
        async with pool.acquire() as conn:
            yield conn
    else:
        # Serverless fallback
        conn = await asyncpg.connect(
            DATABASE_URL,
            ssl="require" if "supabase" in DATABASE_URL else None
        )
        try:
            yield conn
        finally:
            await conn.close()

async def update_performance_history(conn, student_id, topic, is_correct, time_taken):
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