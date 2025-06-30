# Newsletter AI Agent

A simple, lightweight AI-powered newsletter generation system using **LangGraph** for workflow orchestration, **FastAPI** for the web framework, **Google Gemini** for AI content generation, and **Tavily API** for intelligent research and content discovery.

## Key Technologies

- 🔗 **LangGraph** - Orchestrates the entire newsletter generation workflow
- 🚀 **FastAPI** - High-performance web framework with async support
- 🤖 **Google Gemini** - AI model for content generation and summarization
- 🔍 **Tavily API** - Real-time content research and web scraping
- 🧠 **FAISS** - Vector similarity search for content deduplication and ranking
- 🍲 **BeautifulSoup** - HTML parsing and content formation
- 📧 **SMTP** - Email delivery system
- 💾 **SQLite** - Lightweight database for user management

## Quick Start

```bash
# 1. Activate virtual environment
source env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## LangGraph Workflow

The newsletter generation follows a structured **LangGraph** workflow with the following nodes:

1. **🔍 Generate Search Queries** - Creates optimized search queries based on user interests
2. **📰 Collect Content** - Gathers articles using Tavily API and web scraping
3. **⚙️ Process Content** - Filters, deduplicates, and ranks articles using FAISS vector similarity
4. **✍️ Compose Newsletter** - Uses Gemini AI to create personalized newsletter content
5. **📨 Send Email** - Delivers the final newsletter via SMTP

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
SMTP_USERNAME=some_email@gmail.com
SMTP_PASSWORD=a_password
```

That's it! **LangGraph** + **Gemini** + **Tavily** + **FastAPI** = Powerful AI Newsletter Agent 🚀
