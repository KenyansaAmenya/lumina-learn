# LuminaLearn Frontend

Student quiz interface and teacher analytics dashboard for the
AI-Powered Adaptive Learning System.

## 🎨 Features

-   Student Quiz Interface with AI-generated questions and real-time
    feedback
-   Adaptive learning questions based on student performance
-   AI explanations for correct and incorrect answers
-   Contextual hint system
-   Teacher analytics dashboard
-   Chart.js performance visualizations
-   AI-generated teaching insights for struggling students

------------------------------------------------------------------------

## 📁 Project Structure

frontend/ ├── index.html ├── teacher-dashboard.html ├── css/ │ └──
styles.css └── js/ ├── api.js ├── student.js └── dashboard.js

------------------------------------------------------------------------

## 🛠️ Technology Stack

  Component     Technology       Purpose
  ------------- ---------------- -------------------------------------
  Styling       Tailwind CSS     Utility-first CSS framework
  Icons         Phosphor Icons   Consistent iconography
  Charts        Chart.js         Performance analytics visualization
  Fonts         Google Fonts     Typography
  HTTP Client   Fetch API        Backend communication

------------------------------------------------------------------------

## 🚀 Quick Start

### Setup

No build step required. Pure HTML, JavaScript and CDN dependencies.

### Configure API Endpoint

Edit js/api.js

const API_BASE_URL = "http://localhost:8000";

### Serve Files

Python

python -m http.server 3000

Node

npx serve .

PHP

php -S localhost:3000

------------------------------------------------------------------------

## Access Application

Student Interface\
http://localhost:3000/index.html

Teacher Dashboard\
http://localhost:3000/teacher-dashboard.html

------------------------------------------------------------------------

## 🔌 API Integration

Example

const result = await api.submitAnswer({ student_id: 1, topic:
"Mathematics", question: "What is 2+2?", correct_answer: "4",
student_answer: "4", time_taken_seconds: 5 });

------------------------------------------------------------------------

## 🎨 Customization

Primary Color: #019863\
Primary Light: #e6f4ef\
Primary Dark: #0c1c17\
Danger: #dc2626\
Warning: #f59e0b

Modify colors in HTML classes or CSS.

------------------------------------------------------------------------

## 🐛 Troubleshooting

Check backend

curl http://localhost:8000/

If CORS errors occur update backend CORS settings.

Ensure API_BASE_URL matches backend port.

------------------------------------------------------------------------

## 🔒 Security Notes

Demo version has no authentication.\
Do not expose API keys in frontend.\
Use HTTPS in production.

------------------------------------------------------------------------

## 🚀 Deployment

Deploy on static hosting platforms:

Netlify\
Vercel\
GitHub Pages

Update API endpoint for production.

------------------------------------------------------------------------

## 📄 License

MIT License

------------------------------------------------------------------------

## 🆘 Support

Tailwind CSS Docs\
https://tailwindcss.com/docs

Chart.js Docs\
https://www.chartjs.org/docs/

FastAPI Docs\
https://fastapi.tiangolo.com
