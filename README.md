# LinkedIn Agent

<div align="center">

![LinkedIn Agent](https://img.shields.io/badge/LinkedIn-Agent-blue)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![React](https://img.shields.io/badge/React-18+-61DAFB)
![License](https://img.shields.io/badge/License-MIT-green)

A powerful automation and management tool for LinkedIn interactions.

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

## Features

- 🤖 **Automated Interactions**: Schedule and automate LinkedIn activities
- 👥 **Connection Management**: Smart tools for managing your network
- 📊 **Analytics Dashboard**: Track your LinkedIn performance
- 🔄 **Task Scheduling**: Set up recurring tasks and campaigns
- 🔒 **Secure Authentication**: Safe and reliable LinkedIn integration

## Tech Stack

### Frontend
- React 18+
- TypeScript
- Vite
- Modern CSS with CSS Modules

### Backend
- Python 3.8+
- FastAPI
- Celery
- PostgreSQL
- Redis

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/linkedin-agent.git
cd linkedin-agent
```

2. **Backend Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Database Setup**
```bash
cd backend
alembic upgrade head
```

## Usage

1. **Start Backend**
```bash
cd backend
python run.py
```

2. **Start Frontend**
```bash
cd frontend
npm run dev
```

3. **Start Celery Worker**
```bash
celery -A celery_worker worker --loglevel=info
```

Visit `http://localhost:3000` to access the application.

## Documentation

- [Frontend Guide](./frontend/README.md)
- [Backend Guide](./backend/README.md)
- [API Documentation](./backend/docs/api.md)
- [Development Guide](./docs/development.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Support

- 📚 [Documentation](https://github.com/yourusername/linkedin-agent/wiki)
- 💬 [Discussions](https://github.com/yourusername/linkedin-agent/discussions)
- 🐛 [Issues](https://github.com/yourusername/linkedin-agent/issues)

## Acknowledgments

- LinkedIn API
- FastAPI
- React
- Celery
- All our contributors

---

<div align="center">
Made with ❤️ by [Sahil Patil]
</div> 
