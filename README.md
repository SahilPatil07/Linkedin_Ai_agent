# Hotel Management System

A comprehensive enterprise-level hotel billing and management system with analytics dashboard.

## Features

- **Table Management**
  - Real-time table status tracking
  - Table reservation system
  - Multiple seating areas support

- **Menu Management**
  - Food item categorization
  - Price management
  - Inventory tracking
  - Special offers and combos

- **Billing System**
  - Real-time order tracking
  - GST calculation
  - Split billing support
  - Multiple payment methods
  - Bill history

- **Analytics Dashboard**
  - Daily sales reports
  - Popular dishes analysis
  - Revenue trends
  - Monthly performance metrics
  - GST reports

- **User Management**
  - Role-based access control
  - Staff performance tracking
  - Shift management

## Tech Stack

### Frontend
- React.js with Vite
- TailwindCSS for styling
- Redux for state management
- Chart.js for analytics visualization

### Backend
- FastAPI (Python)
- PostgreSQL database
- Redis for caching
- JWT authentication

## Getting Started

1. Clone the repository
2. Install dependencies for frontend and backend
3. Set up environment variables
4. Run database migrations
5. Start development servers

## Project Structure

```
hotel-management/
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── pages/      # Page components
│   │   ├── store/      # Redux store
│   │   └── api/        # API integration
│   
└── backend/           # FastAPI backend application
    ├── app/
    │   ├── api/       # API endpoints
    │   ├── core/      # Core functionality
    │   ├── models/    # Database models
    │   └── services/  # Business logic
    └── tests/         # Test cases
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
