# Contributing to LinkedIn Agent

Thank you for your interest in contributing to LinkedIn Agent! This document provides guidelines and instructions for contributing.

## Quick Links

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## Getting Started

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/yourusername/linkedin-agent.git
cd linkedin-agent
```

3. Set up development environment:
```bash
# Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Frontend
cd frontend
npm install
```

## Development Process

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
3. Run tests:
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

4. Commit your changes:
```bash
git commit -m "feat: add new feature"
```

5. Push to your fork:
```bash
git push origin feature/your-feature-name
```

## Pull Request Process

1. Update documentation for any new features
2. Add tests for new functionality
3. Ensure all tests pass
4. Update the README.md if needed
5. Submit your pull request

## Style Guide

### Python
- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions focused

### JavaScript/TypeScript
- Follow Airbnb style guide
- Use TypeScript
- Write meaningful names
- Add JSDoc comments

### Git Commit Messages
- Use conventional commits
- Be clear and concise
- Reference issues when relevant

## Need Help?

- Open an issue
- Join our discussions
- Check the documentation

Thank you for contributing! 🚀 