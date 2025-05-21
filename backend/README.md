# Backend Documentation

## Overview

The backend of the LinkedIn Agent is built with Python, FastAPI, and Celery, providing a robust API for LinkedIn automation and management tasks.

## Tech Stack

- Python 3.8+
- FastAPI
- Celery
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis (for Celery)

## Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Core functionality
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── utils/         # Utility functions
├── tests/             # Test suite
├── scripts/           # Utility scripts
├── alembic/           # Database migrations
├── config.py          # Configuration
├── main.py           # Application entry point
└── requirements.txt   # Dependencies
```

## Development

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- LinkedIn Developer Account

### Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Database Setup

1. Create PostgreSQL database
2. Run migrations:
```bash
alembic upgrade head
```

### Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Start Celery worker:
```bash
celery -A celery_worker worker --loglevel=info
```

3. Start Celery beat (for scheduled tasks):
```bash
celery -A celery_worker beat --loglevel=info
```

## API Documentation

The API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

1. **Authentication**
   - POST `/api/auth/login`
   - POST `/api/auth/refresh`
   - POST `/api/auth/logout`

2. **LinkedIn Operations**
   - GET `/api/linkedin/profile`
   - POST `/api/linkedin/connect`
   - GET `/api/linkedin/connections`

3. **Automation Tasks**
   - POST `/api/tasks/create`
   - GET `/api/tasks/status`
   - DELETE `/api/tasks/cancel`

## Database Models

Key models include:
- User
- LinkedInProfile
- AutomationTask
- Connection
- Message

## Celery Tasks

The application uses Celery for asynchronous task processing:

1. **Scheduled Tasks**
   - Profile updates
   - Connection management
   - Analytics collection

2. **Background Jobs**
   - Message sending
   - Profile scraping
   - Data synchronization

## Testing

Run tests with:
```bash
pytest
```

## Security

The application implements several security measures:
- JWT authentication
- Rate limiting
- Input validation
- CORS protection
- Secure password hashing

## Monitoring

The application includes:
- Logging configuration
- Error tracking
- Performance monitoring
- Task queue monitoring

## Deployment

### Production Setup

1. Set up production environment variables
2. Configure SSL/TLS
3. Set up proper logging
4. Configure database backups
5. Set up monitoring

### Docker Deployment

A Dockerfile is provided for containerized deployment:
```bash
docker build -t linkedin-agent-backend .
docker run -p 8000:8000 linkedin-agent-backend
```

## Troubleshooting

Common issues and solutions:

1. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check connection string
   - Ensure database exists

2. **Celery Worker Issues**
   - Check Redis connection
   - Verify task routing
   - Check worker logs

3. **API Issues**
   - Check authentication
   - Verify request format
   - Check rate limits

## Contributing

Please refer to the main project's CONTRIBUTING.md for guidelines on contributing to the backend.

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/) 