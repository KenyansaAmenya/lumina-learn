import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

pool: Optional[asyncpg.Pool] = None


async def init_db(database_url: str):
    """Initialize connection pool and create tables."""
    global pool
    pool = await asyncpg.create_pool(
        database_url,
        min_size=5,
        max_size=20,
        command_timeout=60
    )
    
    async with pool.acquire() as conn:
        # Create tables
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
    print(" Database initialized successfully")


async def close_db():
    """Close connection pool."""
    global pool
    if pool:
        await pool.close()
        print(" Database connection closed")


@asynccontextmanager
async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get database connection from pool."""
    if not pool:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with pool.acquire() as conn:
        yield conn


async def update_performance_history(
    conn: asyncpg.Connection,
    student_id: int,
    topic: str,
    is_correct: bool,
    time_taken: int
):
    """Update or insert performance summary."""
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