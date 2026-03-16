# LuminaLearn Backend

AI-Powered Adaptive Learning System API built with FastAPI, Groq AI, and
Supabase PostgreSQL.

------------------------------------------------------------------------

# 🚀 Features

-   AI-Powered Feedback -- Uses Groq LLM to generate personalized
    explanations for students
-   Adaptive Question Generation -- Creates custom quiz questions on any
    topic or difficulty
-   Real-time Analytics -- SQL-based performance tracking with
    aggregation queries
-   RESTful API -- Fast, asynchronous endpoints for student interactions
-   Database Integration -- PostgreSQL with asyncpg for high-performance
    queries

------------------------------------------------------------------------

# 📁 Project Structure

backend/ ├── main.py \# FastAPI app entry point & routes ├── config.py
\# Environment configuration (Pydantic Settings) ├── database.py \#
Database connection pool & schema ├── models.py \# Pydantic
request/response schemas ├── ai_service.py \# Groq AI integration &
prompt engineering ├── analytics.py \# SQL analytics queries & teacher
dashboard data ├── requirements.txt \# Python dependencies └── .env \#
Environment variables (not in git)

------------------------------------------------------------------------

# 🛠️ Technology Stack

  Component         Technology            Purpose
  ----------------- --------------------- ---------------------------------
  Web Framework     FastAPI               High-performance async API
  Database          Supabase PostgreSQL   Cloud-hosted PostgreSQL
  Database Driver   asyncpg               Async PostgreSQL connection
  AI Engine         Groq API              LLaMA 3.1 8B for fast inference
  Validation        Pydantic              Request/response validation
  Environment       python-dotenv         Configuration management

------------------------------------------------------------------------

# ⚙️ Installation

## Prerequisites

-   Python 3.9+
-   Supabase account (free tier works)
-   Groq API key (free tier available)

------------------------------------------------------------------------

## Setup

cd backend python -m venv venv

Windows venv`\Scripts`{=tex}`\activate`{=tex}

macOS/Linux source venv/bin/activate

pip install -r requirements.txt

------------------------------------------------------------------------

## Environment Configuration

Create a .env file:

DATABASE_URL=postgresql://postgres:\[PASSWORD\]@db.\[PROJECT-REF\].supabase.co:5432/postgres
GROQ_API_KEY=gsk_your_groq_api_key_here APP_NAME=LuminaLearn DEBUG=true

------------------------------------------------------------------------

# 🚀 Running the Server

Development

uvicorn main:app --reload --host 0.0.0.0 --port 8000

Production

uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

------------------------------------------------------------------------

# 📡 API Endpoints

Students

POST /students -- Register new student GET /students/{id} -- Get student
profile

Quiz & Learning

POST /submit-answer -- Submit answer and receive AI feedback POST
/generate-question -- Generate AI quiz question POST /get-hint -- Get
contextual hint

Progress Tracking

GET /student-progress/{id} GET /recent-mistakes/{id}

Teacher Analytics

GET /analytics/struggling GET /analytics/hardest-topic GET
/analytics/class-overview POST /analytics/ai-teaching-insights/{id}

------------------------------------------------------------------------

# 🧪 Testing

Install dependencies

pip install httpx pytest

Run tests

python test_phase2.py

------------------------------------------------------------------------

# 🔧 Troubleshooting

Database test

psql "YOUR_DATABASE_URL" -c "SELECT 1;"

Check Groq API

curl -H "Authorization: Bearer \$GROQ_API_KEY"
https://api.groq.com/openai/v1/models

------------------------------------------------------------------------

# 📄 License

MIT License

------------------------------------------------------------------------

# 🆘 Support

FastAPI Docs: https://fastapi.tiangolo.com Groq Docs:
https://console.groq.com/docs Supabase Docs: https://supabase.com/docs
