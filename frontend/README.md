# Frontend Documentation

## Overview

The frontend of the LinkedIn Agent is built with React and Vite, providing a modern, responsive user interface for managing LinkedIn interactions and automation tasks.

## Tech Stack

- React 18+
- Vite
- Node.js
- TypeScript
- Modern CSS (with CSS Modules)

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page components
│   ├── hooks/         # Custom React hooks
│   ├── services/      # API service calls
│   ├── utils/         # Utility functions
│   ├── types/         # TypeScript type definitions
│   ├── styles/        # Global styles and themes
│   └── App.tsx        # Root component
├── public/            # Static assets
└── package.json       # Dependencies and scripts
```

## Development

### Prerequisites

- Node.js 14+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run test` - Run tests

### Environment Variables

Create a `.env` file in the frontend directory with the following variables:

```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Component Documentation

### Key Components

1. **Dashboard**
   - Main interface for monitoring LinkedIn activities
   - Displays statistics and recent actions

2. **Automation Controls**
   - Interface for managing automated tasks
   - Configuration options for LinkedIn interactions

3. **Profile Management**
   - Tools for managing LinkedIn profiles
   - Connection and network management

## State Management

The application uses React Context and custom hooks for state management. Key state containers include:

- Authentication state
- User preferences
- LinkedIn connection status
- Task queue status

## API Integration

The frontend communicates with the backend through RESTful APIs and WebSocket connections. API services are organized in the `services` directory.

## Styling

The application uses CSS Modules for component-specific styling and a global theme system. Key features:

- Responsive design
- Dark/Light mode support
- Consistent component styling
- Accessibility compliance

## Testing

The project uses Jest and React Testing Library for testing. Run tests with:

```bash
npm run test
```

## Building for Production

```bash
npm run build
```

The build output will be in the `dist` directory.

## Contributing

Please refer to the main project's CONTRIBUTING.md for guidelines on contributing to the frontend.

## Troubleshooting

Common issues and solutions:

1. **Build Failures**
   - Clear node_modules and reinstall dependencies
   - Check for TypeScript errors
   - Verify environment variables

2. **API Connection Issues**
   - Verify backend server is running
   - Check API URL configuration
   - Ensure CORS is properly configured

## Additional Resources

- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Vite Documentation](https://vitejs.dev/guide/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/) 