from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    interests: List[str]

class UserResponse(BaseModel):
    id: int
    email: str
    interests: List[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class NewsletterCreate(BaseModel):
    interests: List[str]
    frequency: str = "weekly"  # daily, weekly

class NewsletterResponse(BaseModel):
    id: int
    title: str
    content: str
    sent_at: datetime
    status: str
    
    class Config:
        from_attributes = True

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    url: str
    source: str
    category: str
    published_at: Optional[datetime]
    
    class Config:
        from_attributes = True