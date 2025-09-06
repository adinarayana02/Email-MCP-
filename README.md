# AI Communication Assistant - Frontend

A modern, responsive React-based frontend for the AI-Powered Communication Assistant that provides intelligent email management, analytics, and automated response generation.

## 🚀 Features

- **📧 Email Management Dashboard** - Comprehensive email listing with filtering and sorting
- **🤖 AI-Powered Analysis** - Sentiment analysis, priority detection, and categorization
- **📊 Advanced Analytics** - Interactive charts and real-time statistics
- **✍️ Response Editor** - AI-generated draft responses with editing capabilities
- **🎨 Modern UI/UX** - Clean, responsive design with Tailwind CSS
- **📱 Mobile-First** - Optimized for all device sizes
- **🌙 Dark Mode Support** - Automatic theme switching
- **♿ Accessibility** - WCAG compliant with ARIA support

## 🛠️ Tech Stack

- **Framework**: React 18 with Hooks
- **Styling**: Tailwind CSS with custom design system
- **Charts**: Recharts for data visualization
- **State Management**: React Query + Zustand
- **Forms**: React Hook Form with Zod validation
- **Icons**: Lucide React + React Icons
- **HTTP Client**: Axios with interceptors
- **Testing**: Jest + React Testing Library + Cypress
- **Build Tool**: Create React App with custom config

## 📋 Prerequisites

- Node.js >= 16.0.0
- npm >= 8.0.0 or yarn >= 1.22.0
- Backend API running on `http://localhost:8000`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Setup

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=AI Communication Assistant
REACT_APP_VERSION=1.0.0
```

### 3. Start Development Server

```bash
npm start
```

The application will open at `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Charts/        # Data visualization components
│   │   ├── common/        # Shared components (Header, Sidebar)
│   │   └── Dashboard/     # Dashboard-specific components
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API and external service integrations
│   ├── utils/             # Utility functions and helpers
│   ├── App.js             # Main application component
│   └── index.js           # Application entry point
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
└── package.json           # Dependencies and scripts
```

## 🎨 Design System

### Color Palette

- **Primary**: Blue (#3B82F6) - Main actions and branding
- **Success**: Green (#22C55E) - Positive states and confirmations
- **Warning**: Yellow (#F59E0B) - Caution and pending states
- **Danger**: Red (#EF4444) - Errors and destructive actions
- **Info**: Cyan (#06B6D4) - Information and neutral states

### Typography

- **Font Family**: Inter (system fallback)
- **Scale**: 12px to 72px with consistent line heights
- **Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Components

- **Cards**: Consistent elevation and border radius
- **Buttons**: Multiple variants (primary, secondary, outline, ghost)
- **Forms**: Accessible inputs with validation states
- **Tables**: Responsive data tables with sorting

## 🔧 Available Scripts

```bash
# Development
npm start              # Start development server
npm run build         # Build for production
npm run test          # Run tests in watch mode
npm run test:coverage # Run tests with coverage

# Code Quality
npm run lint          # Check for linting errors
npm run lint:fix      # Fix auto-fixable linting errors
npm run format        # Format code with Prettier
npm run type-check    # Type checking (if using TypeScript)

# Testing
npm run cypress:open  # Open Cypress test runner
npm run cypress:run   # Run Cypress tests headlessly

# Build Analysis
npm run build:analyze # Analyze bundle size
```

## 🧪 Testing

### Unit Tests

```bash
npm test
```

Tests are written using Jest and React Testing Library, focusing on component behavior and user interactions.

### E2E Tests

```bash
npm run cypress:open
```

End-to-end tests using Cypress for critical user flows and integration testing.

### Test Coverage

```bash
npm run test:coverage
```

Generates coverage reports to ensure comprehensive testing.

## 📱 Responsive Design

The application is built with a mobile-first approach:

- **Mobile**: < 640px - Single column layout
- **Tablet**: 640px - 1024px - Two column layout
- **Desktop**: > 1024px - Full multi-column layout

## ♿ Accessibility

- **WCAG 2.1 AA** compliance
- **Keyboard navigation** support
- **Screen reader** optimization
- **High contrast** mode support
- **Focus management** for modals and forms

## 🌙 Dark Mode

Automatic dark mode detection with manual toggle:

```jsx
import { useTheme } from './hooks/useTheme';

const { theme, toggleTheme } = useTheme();
```

## 📊 Performance

- **Code splitting** with React.lazy()
- **Virtual scrolling** for large lists
- **Image optimization** with lazy loading
- **Bundle analysis** and optimization
- **Service worker** for offline support

## 🔒 Security

- **XSS protection** with proper sanitization
- **CSRF protection** with token validation
- **Content Security Policy** headers
- **Input validation** on client and server
- **Secure HTTP** only in production

## 🚀 Deployment

### Production Build

```bash
npm run build
```

### Environment Variables

Set production environment variables:

```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Use Prettier for formatting
- Follow ESLint rules
- Write meaningful commit messages
- Add tests for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](../../wiki)
- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Email**: support@yourdomain.com

## 🙏 Acknowledgments

- [Tailwind CSS](https://tailwindcss.com/) for the utility-first CSS framework
- [Recharts](https://recharts.org/) for beautiful charts
- [Lucide](https://lucide.dev/) for the icon library
- [React Query](https://tanstack.com/query) for server state management
