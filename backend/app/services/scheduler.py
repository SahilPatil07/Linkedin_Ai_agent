from celery import Celery
from datetime import datetime
from sqlalchemy.orm import Session
from ..db.models import Post, ScheduledPost, PostStatus
from .linkedin_service import LinkedInService
import logging

# Configure Celery
celery_app = Celery('linkedin_scheduler',
                    broker='redis://localhost:6379/0',
                    backend='redis://localhost:6379/0')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self, db: Session):
        self.db = db
        self.linkedin_service = LinkedInService()

    def schedule_post(self, post_id: int, scheduled_time: datetime) -> bool:
        """Schedule a post for later publishing"""
        try:
            post = self.db.query(Post).filter(Post.id == post_id).first()
            if not post:
                logger.error(f"Post {post_id} not found")
                return False

            # Create scheduled post entry
            scheduled_post = ScheduledPost(
                post_id=post_id,
                scheduled_time=scheduled_time,
                status=PostStatus.SCHEDULED
            )
            self.db.add(scheduled_post)
            
            # Update post status
            post.status = PostStatus.SCHEDULED
            post.scheduled_time = scheduled_time
            
            self.db.commit()
            
            # Schedule the task
            job = publish_post.apply_async(
                args=[post_id],
                eta=scheduled_time
            )
            
            # Update job ID
            scheduled_post.job_id = job.id
            self.db.commit()
            
            logger.info(f"Post {post_id} scheduled for {scheduled_time}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling post {post_id}: {str(e)}")
            self.db.rollback()
            return False

    def cancel_scheduled_post(self, post_id: int) -> bool:
        """Cancel a scheduled post"""
        try:
            scheduled_post = self.db.query(ScheduledPost).filter(
                ScheduledPost.post_id == post_id
            ).first()
            
            if not scheduled_post:
                logger.error(f"Scheduled post {post_id} not found")
                return False

            # Revoke the Celery task
            if scheduled_post.job_id:
                celery_app.control.revoke(scheduled_post.job_id, terminate=True)

            # Update statuses
            scheduled_post.status = PostStatus.CANCELLED
            scheduled_post.post.status = PostStatus.CANCELLED
            
            self.db.commit()
            logger.info(f"Post {post_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling post {post_id}: {str(e)}")
            self.db.rollback()
            return False

@celery_app.task
def publish_post(post_id: int):
    """Celery task to publish a post to LinkedIn"""
    from ..db.session import SessionLocal
    
    db = SessionLocal()
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            logger.error(f"Post {post_id} not found")
            return False

        # Get LinkedIn service
        linkedin_service = LinkedInService()
        
        # Attempt to post
        success = linkedin_service.create_post(
            user_id=post.user_id,
            content=post.content,
            visibility=post.visibility,
            media_category=post.media_category,
            media_url=post.media_url
        )

        if success:
            post.status = PostStatus.POSTED
            post.posted_at = datetime.utcnow()
            if post.scheduled_post:
                post.scheduled_post.status = PostStatus.POSTED
        else:
            post.status = PostStatus.FAILED
            post.error_message = "Failed to post to LinkedIn"
            if post.retry_count < post.max_retries:
                # Reschedule with exponential backoff
                post.retry_count += 1
                delay = 2 ** post.retry_count  # 2, 4, 8 minutes
                publish_post.apply_async(
                    args=[post_id],
                    countdown=delay * 60
                )

        db.commit()
        return success

    except Exception as e:
        logger.error(f"Error publishing post {post_id}: {str(e)}")
        if post:
            post.status = PostStatus.FAILED
            post.error_message = str(e)
            db.commit()
        return False
    finally:
        db.close() 