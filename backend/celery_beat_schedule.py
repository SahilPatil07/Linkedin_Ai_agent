from celery.schedules import crontab
from app.core.config import settings

# Celery Beat Schedule
beat_schedule = {
    'cleanup-expired-tokens': {
        'task': 'app.services.tasks.cleanup_expired_tokens',
        'schedule': crontab(minute=0, hour='*/1'),  # Run every hour
    },
    'refresh-linkedin-tokens': {
        'task': 'app.services.tasks.refresh_linkedin_tokens',
        'schedule': crontab(minute=0, hour='*/12'),  # Run every 12 hours
    },
} 