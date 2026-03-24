import logging

logger = logging.getLogger(__name__)

async def create_tables(conn):
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
        
        -- Indexes for faster queries
        CREATE INDEX IF NOT EXISTS idx_quiz_results_student_id ON quiz_results(student_id);
        CREATE INDEX IF NOT EXISTS idx_quiz_results_topic ON quiz_results(topic);
        CREATE INDEX IF NOT EXISTS idx_performance_history_student_id ON performance_history(student_id);
    """)
    logger.info("Database schema created/verified")