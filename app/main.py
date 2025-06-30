from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, get_db
from .models import Base, User
from .routers import users, newsletters
from .agents.newsletter_agent import newsletter_agent
from .services.content_service import content_service

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Newsletter AI Agent",
    description="AI-powered newsletter generation system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(newsletters.router)

@app.get("/")
async def root():
    return {"message": "Newsletter AI Agent API is running!"}

# Background task function
async def send_newsletters_background():
    """Send newsletters to all active users using FastAPI BackgroundTasks"""
    print("Running newsletter generation...")
    
    try:
        from .database import SessionLocal
        db = SessionLocal()
        
        users = db.query(User).filter(User.is_active == True).all()
        
        for user in users:
            if user.interests:
                try:
                    result = await newsletter_agent.run_newsletter_generation(
                        user_email=user.email,
                        user_interests=user.interests
                    )
                    print(f"Newsletter sent to {user.email}: {result['status']}")
                except Exception as e:
                    print(f"Failed to send newsletter to {user.email}: {e}")
        
        db.close()
        
    except Exception as e:
        print(f"Newsletter task failed: {e}")

async def send_single_newsletter_background(user_email: str, user_interests: list):
    """Send newsletter to a single user"""
    try:
        result = await newsletter_agent.run_newsletter_generation(
            user_email=user_email,
            user_interests=user_interests
        )
        print(f"Newsletter sent to {user_email}: {result['status']}")
    except Exception as e:
        print(f"Failed to send newsletter to {user_email}: {e}")

@app.post("/send-newsletters")
async def trigger_newsletters(background_tasks: BackgroundTasks):
    """Send newsletters to all users"""
    background_tasks.add_task(send_newsletters_background)
    return {"message": "Newsletter generation started"}

@app.post("/send-newsletter/{user_id}")
async def trigger_single_newsletter(user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Send newsletter to a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.interests:
        raise HTTPException(status_code=400, detail="User has no interests set")
    
    background_tasks.add_task(send_single_newsletter_background, user.email, user.interests)
    return {"message": "Newsletter generation started"}

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await content_service.close()
