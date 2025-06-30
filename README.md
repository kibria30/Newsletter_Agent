# Newsletter AI Agent - Lightweight Version

A simple, lightweight AI-powered newsletter generation system using FastAPI and Google Gemini.

## Quick Start

```bash
# 1. Activate virtual environment
source env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Features

- ✅ **User Registration** with interests
- ✅ **AI Content Generation** using Google Gemini
- ✅ **Content Research** via Tavily API
- ✅ **Background Processing** with FastAPI BackgroundTasks
- ✅ **Email Delivery** via SMTP
- ✅ **SQLite Database** for simplicity
- ✅ **Web Interface** for easy testing

## API Usage

### Register User & Generate Newsletter
```bash
# Via web interface: http://localhost:8000/static/index.html

# Or via API:
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password", "interests": ["AI", "Tech"]}'
```

### Manual Newsletter Triggers
```bash
# Send to all users
curl -X POST http://localhost:8000/send-newsletters

# Send to specific user
curl -X POST http://localhost:8000/send-newsletter/1
```

## Environment Setup

Create a `.env` file:
```env
DATABASE_URL=sqlite:///./newsletter.db
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_password
```

## Architecture

```
FastAPI App
├── 📧 User Management (SQLAlchemy + SQLite)
├── 🤖 AI Content Generation (Google Gemini)
├── 🔍 Content Research (Tavily API)
├── ⚡ Background Tasks (FastAPI BackgroundTasks)
└── 📨 Email Delivery (SMTP)
```

## Project Structure

```
app/
├── main.py              # FastAPI application
├── models.py            # Database models
├── database.py          # Database configuration
├── agents/              # AI newsletter agent
├── services/            # Content, email, vector services
├── routers/             # API route handlers
└── static/              # Web interface
```

That's it! Simple and lightweight. 🚀
