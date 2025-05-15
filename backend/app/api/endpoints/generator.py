from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ...core.security import get_current_user
from ...db.session import get_db
from ...db.models import User, Post
from ...models.schemas import PostCreate, PostResponse
from ...services.post_generator import generate_posts

router = APIRouter()

@router.post("/generate", response_model=List[PostResponse])
async def create_posts(
    topic: str,
    num_posts: Optional[int] = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        generated_posts = await generate_posts(topic, num_posts)
        
        # Save posts to database
        posts = []
        for content in generated_posts:
            post = Post(
                content=content,
                status="draft",
                user_id=current_user.id
            )
            db.add(post)
            posts.append(post)
        
        db.commit()
        for post in posts:
            db.refresh(post)
        
        return posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/posts", response_model=List[PostResponse])
async def get_user_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    posts = db.query(Post).filter(Post.user_id == current_user.id).all()
    return posts 