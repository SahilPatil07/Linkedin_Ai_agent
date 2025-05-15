from app.core.config import settings

# Celery Configuration
broker_url = settings.CELERY_BROKER_URL
result_backend = settings.CELERY_RESULT_BACKEND

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Worker settings
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000
worker_max_memory_per_child = 200000  # 200MB

# Beat settings
beat_schedule = {
    'cleanup-expired-tokens': {
        'task': 'app.services.tasks.cleanup_expired_tokens',
        'schedule': 3600.0,  # Run every hour
    },
} 