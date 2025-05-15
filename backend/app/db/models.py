from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    linkedin_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # LinkedIn credentials
    linkedin_access_token = Column(String, nullable=True)
    linkedin_refresh_token = Column(String, nullable=True)
    linkedin_token_expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    posts = relationship("LinkedInPost", back_populates="user")
    scheduled_posts = relationship("ScheduledPost", back_populates="user")

class PostStatus(enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    POSTED = "POSTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class LinkedInPost(Base):
    __tablename__ = "linkedin_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    linkedin_post_id = Column(String, unique=True, index=True)
    content = Column(Text)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    status = Column(String, default="published")  # published, deleted, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="posts")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    visibility = Column(String, default="PUBLIC")
    media_category = Column(String, nullable=True)
    media_url = Column(String, nullable=True)
    scheduled_time = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    analytics = relationship("PostAnalytics", back_populates="post")
    scheduled_post = relationship("ScheduledPost", back_populates="post", uselist=False)

class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    scheduled_time = Column(DateTime)
    status = Column(String, default="scheduled")  # scheduled, posted, failed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="scheduled_posts")

class PostAnalytics(Base):
    __tablename__ = "post_analytics"

    id = Column(Integer, primary_key=True, index=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    analytics_data = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    post_id = Column(Integer, ForeignKey("posts.id"))
    
    # Relationships
    post = relationship("Post", back_populates="analytics") 