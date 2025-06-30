# Newsletter AI Agent - Simple Setup Guide

## Overview

The Newsletter AI Agent is a lightweight FastAPI application that uses **FastAPI BackgroundTasks** for handling newsletter generation in the background.

## Quick Start

```bash
# Install dependencies
./env/bin/pip install -r requirements.txt

# Run the application
./env/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Trigger newsletters via API
curl -X POST http://localhost:8000/send-newsletters
```

## API Endpoints

### Core Features

- `POST /users/register` - Register a new user with interests
- `POST /users/generate-newsletter?user_id={id}` - Generate newsletter for a user
- `POST /send-newsletters` - Send newsletters to all active users
- `POST /send-newsletter/{user_id}` - Send newsletter to specific user
- `GET /` - API status

### Example Usage

```bash
# Send newsletters to all users
curl -X POST http://localhost:8000/send-newsletters

# Send newsletter to user ID 1
curl -X POST http://localhost:8000/send-newsletter/1
```

## Environment Variables

Make sure your `.env` file includes:

```env
DATABASE_URL=sqlite:///./newsletter.db
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_password
```

## How It Works

1. **User Registration**: Users register with email and interests
2. **Background Processing**: Newsletter generation runs in background using FastAPI BackgroundTasks
3. **AI Content**: Uses Google Gemini for content processing and Tavily for research
4. **Email Delivery**: Sends personalized newsletters via SMTP

## Architecture

```
FastAPI App
├── User Registration
├── Newsletter Generation (Background)
├── AI Content Processing (Gemini)
├── Content Research (Tavily)
└── Email Delivery (SMTP)
```

## Key Features

- ✅ **Lightweight**: Only essential dependencies
- ✅ **Fast**: FastAPI with async background tasks
- ✅ **AI-Powered**: Google Gemini for content generation
- ✅ **Research**: Tavily API for latest content
- ✅ **Simple**: SQLite database, no external services required
