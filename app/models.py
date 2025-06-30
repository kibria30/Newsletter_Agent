from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    interests = Column(JSON)  # ["AI", "IoT", "EV", etc.]
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscriptions = relationship("Newsletter", back_populates="user")

class Newsletter(Base):
    __tablename__ = "newsletters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    content = Column(Text)
    html_content = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="draft")  # draft, sent, failed
    
    user = relationship("User", back_populates="subscriptions")

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    url = Column(String)
    source = Column(String)
    category = Column(String)
    published_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    embedding_id = Column(String)  # Reference to FAISS vector