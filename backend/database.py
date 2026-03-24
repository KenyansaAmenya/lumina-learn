import asyncpg
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pool: Optional[asyncpg.Pool] = None

async def init_db(database_url: str):
    """Initialize connection pool only."""
    global pool
    if not database_url:
        raise ValueError("DATABASE_URL not set")
    
    pool = await asyncpg.create_pool(
        database_url,
        min_size=1,
        max_size=10,
        command_timeout=60,
        ssl="require" if "supabase" in database_url else None
    )
    logger.info("Database pool initialized")

async def close_db():
    global pool
    if pool:
        await pool.close()
        pool = None
        logger.info("Database connection closed")

@asynccontextmanager
async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    if not pool:
        raise RuntimeError("Database not initialized")
    async with pool.acquire() as conn:
        yield conn