# LuminaLearn -- AI Adaptive Learning System

LuminaLearn is an AI-powered adaptive learning platform that generates
personalized quiz questions, provides intelligent feedback, and gives
teachers real-time analytics on student performance.

The system combines FastAPI, Groq LLMs, PostgreSQL, and a modern web
interface to create a dynamic learning experience that adapts to each
student's progress.

------------------------------------------------------------------------

# 🎯 Project Goals

LuminaLearn demonstrates how AI can improve digital education by:

-   Providing instant AI explanations for student answers
-   Generating adaptive questions based on topic and difficulty
-   Helping teachers identify struggling students early
-   Delivering data-driven teaching insights
-   Tracking student learning progress over time

------------------------------------------------------------------------

# 🧠 System Architecture

Student UI (HTML + Tailwind)
        │
        ▼
FastAPI Backend (Routes/Controllers)
        │
   ┌────┴─────┬─────────────┐
   ▼          ▼             ▼
Services  Repositories   Groq LLM
(Business   (SQL/Data    (AI Engine)
 Logic)     Access)
   │          │
   └────┬─────┘
        ▼
   PostgreSQL
   (Supabase DB)

   ------------------------------------------------------------------------

# 🏗️ Backend Architecture (Controller-Service-Repository Pattern)

The backend follows clean architecture principles with clear separation
of concerns:

## Layers

| Layer | Responsibility | Example Files |
|-------|---------------|---------------|
| **Routes** (Controllers) | HTTP handling, input validation, JSON responses | `routes/students.py`, `routes/quiz.py` |
| **Services** | Business logic, orchestration, AI interactions | `services/quiz_service.py`, `services/ai_service.py` |
| **Repositories** | Database access, SQL queries | `repositories/student_repository.py` |
| **Database** | Connection management | `database.py`, `schema.py` |

## Data Flow

HTTP Request → Routes → Services → Repositories → Database
↓         ↓            ↓
Validate   Business    SQL Queries
& Parse    Logic       & Execution


## Benefits

-   **Testability**: Mock repositories to test business logic in isolation
-   **Maintainability**: Change database schema without touching business logic
-   **Reusability**: Same services usable by CLI, admin scripts, or other interfaces
-   **Single Responsibility**: Each file has one reason to change

------------------------------------------------------------------------

# 🚀 Key Features

## Student Features

-   AI-generated quiz questions
-   Instant AI feedback
-   Concept explanations for mistakes
-   Contextual hints
-   Topic selection
-   Progress tracking
-   Accuracy statistics
-   Review of recent mistakes

## Teacher Features

-   Class performance dashboard
-   Student accuracy tracking
-   Topic difficulty analysis
-   Identification of struggling students
-   AI-generated teaching recommendations
-   Visual analytics charts

------------------------------------------------------------------------

# 🧩 Project Structure
```
lumina-learn/
├── backend/
│   ├── .env                    # SUPABASE_URL, GROQ_API_KEY
│   ├── main.py                 # FastAPI app, lifespan management, wires layers together
│   ├── config.py               # Pydantic settings, environment variable loader
│   ├── database.py             # asyncpg connection pool ONLY (no SQL, no schema)
│   ├── schema.py               # Database DDL: CREATE TABLE, CREATE INDEX statements
│   ├── models.py               # Pydantic schemas for request/response validation
│   ├── dependencies.py         # FastAPI dependency injection wiring
│   │
│   ├── repositories/           # DATA ACCESS LAYER: SQL queries only
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract base class for repositories
│   │   ├── student_repository.py    # Student SQL: get_by_id, get_by_email, create
│   │   ├── quiz_repository.py       # Quiz SQL: save_results, get_recent_mistakes
│   │   └── analytics_repository.py  # Analytics SQL: struggling students, reports
│   │
│   ├── services/               # BUSINESS LOGIC LAYER: Orchestration, calculations, AI
│   │   ├── __init__.py
│   │   ├── ai_service.py       # Groq client wrapper: generate_feedback, questions, hints
│   │   ├── student_service.py  # Student business logic: duplicate checking
│   │   ├── quiz_service.py     # Quiz logic: answer evaluation, AI feedback, performance updates
│   │   ├── progress_service.py # Progress logic: accuracy calculations, topic breakdowns
│   │   └── analytics_service.py # Analytics logic: enrich data, build AI prompts
│   │
│   └── routes/                 # CONTROLLER LAYER: HTTP handling only (thin)
│       ├── __init__.py
│       ├── students.py         # POST /students, GET /students/{id}
│       ├── quiz.py             # POST /submit-answer, POST /generate-question, etc.
│       ├── progress.py         # GET /student-progress/{id}
│       └── analytics.py        # GET /analytics/* endpoints
│
└── frontend/
    ├── index.html              # Student quiz interface
    ├── teacher-dashboard.html  # Analytics view
    ├── css/styles.css
    └── js/
        ├── api.js              # Fetch wrappers
        ├── quiz.js             # Student interaction
        └── dashboard.js        # Charts/reports
```
------------------------------------------------------------------------

# ⚙️ Technology Stack

## Backend

-   FastAPI
-   Groq LLM API
-   Supabase PostgreSQL
-   asyncpg
-   Pydantic

## Frontend

-   HTML5
-   Tailwind CSS
-   Chart.js
-   Fetch API
-   Phosphor Icons

------------------------------------------------------------------------

# 🧠 AI Capabilities

## AI Question Generation

Generate a multiple-choice quiz question including: - question - 4
options - correct answer - explanation - hint

## AI Feedback

Correct answer: - congratulate student - reinforce concept - suggest
advanced challenge

Wrong answer: - explain concept clearly - identify mistake - provide
example - encourage learning

------------------------------------------------------------------------

# 🔄 Learning Workflow

1.  Student selects topic
2.  AI generates question (via services/ai_service.py)
3.  Student submits answer
4.  Backend evaluates response (services/quiz_service.py)
5.  AI generates feedback (via services/ai_service.py)
6.  Database stores attempt (repositories/quiz_repository.py)
7.  Performance history updated (services/quiz_service.py)
8.  Teacher dashboard updates analytics (services/analytics_service.py)

------------------------------------------------------------------------

# 🚀 Running the System
**Prerequisites**
- Python 3.9+
- PostgreSQL database (local or Supabase)
- Groq API key

**Environment Setup**
Create backend/.env:
```env
DATABASE_URL=postgresql://user:password@host:port/database
GROQ_API_KEY=your_groq_api_key_here
```

## Start Backend

cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload

- Backend runs at: http://localhost:8000

- API Docs: http://localhost:8000/docs

------------------------------------------------------------------------

## Start Frontend

cd frontend

python -m http.server 3000

Student Interface http://localhost:3000/index.html

Teacher Dashboard http://localhost:3000/teacher-dashboard.html

------------------------------------------------------------------------

🔐 Security Notes
For production:
-   Add authentication (JWT/OAuth2)
-   Protect API endpoints
-   Use HTTPS
-   Restrict CORS origins
-   Store secrets in environment variables
-   Add rate limiting
-   Validate all inputs

------------------------------------------------------------------------

# 🚀 Future Improvements

-   Student authentication
-   Adaptive ML difficulty system
-   Personalized learning paths
-   RAG-based explanations
-   Mobile application
-   Classroom management tools
-   Multi-language support
-   WebSocket real-time updates
-   Export reports (PDF/CSV)


------------------------------------------------------------------------

# 🆘 Resources

FastAPI\
https://fastapi.tiangolo.com

Groq AI\
https://console.groq.com/docs

Supabase\
https://supabase.com/docs

Chart.js\
https://www.chartjs.org/docs/

Tailwind CSS\
https://tailwindcss.com/docs

Controller-Service-Repository Pattern:
https://matthewdavis.io/controller-service-repository-pattern/
