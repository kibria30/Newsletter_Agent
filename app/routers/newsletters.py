from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User, Newsletter, Article
from ..schemas import NewsletterResponse, ArticleResponse
from ..services.vector_service import vector_service
from ..services.content_service import content_service

router = APIRouter(prefix="/newsletters", tags=["newsletters"])

@router.get("/", response_model=List[NewsletterResponse])
async def get_user_newsletters(user_id: int, db: Session = Depends(get_db)):
    """Get all newsletters for a user"""
    newsletters = db.query(Newsletter).filter(Newsletter.user_id == user_id).order_by(Newsletter.sent_at.desc()).all()
    return newsletters

@router.get("/{newsletter_id}", response_model=NewsletterResponse)
async def get_newsletter(newsletter_id: int, db: Session = Depends(get_db)):
    """Get a specific newsletter"""
    newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")
    return newsletter

@router.get("/articles/search")
async def search_articles(query: str, interests: List[str] = None, limit: int = 10):
    """Search articles using vector similarity"""
    try:
        results = vector_service.search_similar_articles(
            query=query,
            k=limit,
            interests=interests
        )
        return {"articles": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/trending/topics")
async def get_trending_topics(interests: List[str] = None):
    """Get trending topics"""
    try:
        trending = vector_service.get_trending_topics(interests=interests)
        return {"trending_topics": trending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending topics: {str(e)}")

@router.post("/collect-content")
async def collect_content_for_interests(interests: List[str], background_tasks: BackgroundTasks):
    """Collect and process content for given interests"""
    async def collect_and_store():
        try:
            articles = await content_service.search_content_tavily(interests, max_results=50)
            articles = await content_service.enhance_articles_with_scraping(articles)
            vector_service.add_articles(articles)
        except Exception as e:
            print(f"Background content collection failed: {e}")
    
    background_tasks.add_task(collect_and_store)
    return {"message": "Content collection started in background"}