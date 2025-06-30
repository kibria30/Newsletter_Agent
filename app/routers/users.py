from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse
from ..agents.newsletter_agent import newsletter_agent

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = pwd_context.hash(user.password)
    
    # Create user
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        interests=user.interests
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: int, db: Session = Depends(get_db)):
    """Get current user profile"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/interests")
async def update_interests(user_id: int, interests: List[str], db: Session = Depends(get_db)):
    """Update user interests"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.interests = interests
    db.commit()
    
    return {"message": "Interests updated successfully"}

@router.post("/generate-newsletter")
async def generate_newsletter_for_user(user_id: int, db: Session = Depends(get_db)):
    """Generate and send newsletter for a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.interests:
        raise HTTPException(status_code=400, detail="User has no interests set")
    
    try:
        result = await newsletter_agent.run_newsletter_generation(
            user_email=user.email,
            user_interests=user.interests
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Newsletter generation failed: {str(e)}"
        )
