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

Student UI (HTML + Tailwind) │ ▼ FastAPI Backend │ ┌────┴─────┐ ▼ ▼ Groq
LLM PostgreSQL (AI Engine) (Supabase DB)

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

LuminaLearn/ │ ├── backend/ │ ├── main.py │ ├── database.py │ ├──
ai_service.py │ ├── analytics.py │ ├── models.py │ ├── config.py │ └──
requirements.txt │ ├── frontend/ │ ├── index.html │ ├──
teacher-dashboard.html │ ├── css/ │ │ └── styles.css │ └── js/ │ ├──
api.js │ ├── student.js │ └── dashboard.js │ └── README.md

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
2.  AI generates question
3.  Student submits answer
4.  Backend evaluates response
5.  AI generates feedback
6.  Database stores attempt
7.  Teacher dashboard updates analytics

------------------------------------------------------------------------

# 🚀 Running the System

## Start Backend

cd backend

python -m venv venv venv`\Scripts`{=tex}`\activate`{=tex}

pip install -r requirements.txt

uvicorn main:app --reload

Backend runs at: http://localhost:8000

API Docs: http://localhost:8000/docs

------------------------------------------------------------------------

## Start Frontend

cd frontend

python -m http.server 3000

Student Interface http://localhost:3000/index.html

Teacher Dashboard http://localhost:3000/teacher-dashboard.html

------------------------------------------------------------------------

# 🔐 Security Notes

For production:

-   Add authentication
-   Protect API endpoints
-   Use HTTPS
-   Restrict CORS
-   Store secrets in environment variables

------------------------------------------------------------------------

# 🚀 Future Improvements

-   Student authentication
-   Adaptive ML difficulty system
-   Personalized learning paths
-   RAG-based explanations
-   Mobile application
-   Classroom management tools
-   Multi-language support

------------------------------------------------------------------------

# 📄 License

MIT License

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
