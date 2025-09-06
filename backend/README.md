# AI Communication Assistant Backend

A powerful, AI-driven backend system for automated email management and customer support using FastAPI, OpenAI, and advanced NLP techniques.

## 🚀 Features

- **AI-Powered Email Analysis**: Automatic sentiment analysis, priority determination, and categorization
- **Smart Response Generation**: Context-aware AI responses using OpenAI GPT models
- **Email Processing Pipeline**: Automated email fetching, processing, and response management
- **Real-time Analytics**: Comprehensive metrics and insights into email operations
- **Scalable Architecture**: Built with FastAPI and SQLAlchemy for high performance
- **Background Task Processing**: Asynchronous email processing with scheduled jobs
- **RESTful API**: Clean, documented API endpoints for frontend integration

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: SQLite (configurable for PostgreSQL/MySQL)
- **ORM**: SQLAlchemy 2.0+
- **AI/ML**: OpenAI GPT, Transformers, scikit-learn
- **Authentication**: JWT with bcrypt
- **Background Tasks**: Schedule library with threading
- **Validation**: Pydantic 2.0+

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Email service credentials (Gmail, Outlook, etc.)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Or install with extras for development
pip install -e ".[dev]"
```

### 3. Environment Configuration

Create a `.env` file in the backend directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Email Service Configuration
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
IMAP_USERNAME=your_email@gmail.com
IMAP_PASSWORD=your_app_password

# Optional: Environment
ENVIRONMENT=development
SECRET_KEY=your_secret_key_here
```

### 4. Run the Application

```bash
# Development mode
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:

- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🔧 Configuration

### Environment Variables

| Variable         | Description                    | Default        |
| ---------------- | ------------------------------ | -------------- |
| `OPENAI_API_KEY` | OpenAI API key for AI services | Required       |
| `EMAIL_USERNAME` | Email service username         | Required       |
| `EMAIL_PASSWORD` | Email service password         | Required       |
| `IMAP_USERNAME`  | IMAP server username           | Required       |
| `IMAP_PASSWORD`  | IMAP server password           | Required       |
| `ENVIRONMENT`    | Environment (dev/prod)         | `development`  |
| `SECRET_KEY`     | JWT secret key                 | Auto-generated |
| `DATABASE_URL`   | Database connection string     | SQLite local   |

### Database Configuration

The system uses SQLite by default. For production, consider PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database models and connection
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── email.py         # Email-related models
│   │   └── response.py      # Response models
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── emails.py        # Email management endpoints
│   │   └── analytics.py     # Analytics endpoints
│   ├── services/            # Business logic services
│   │   ├── __init__.py
│   │   ├── ai_service.py    # AI and ML services
│   │   ├── email_service.py # Email processing
│   │   ├── priority_service.py # Priority determination
│   │   └── sentiment_service.py # Sentiment analysis
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── email_utils.py   # Email processing utilities
│       └── text_processing.py # Text analysis utilities
├── data/                    # Data storage directory
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── requirements-prod.txt     # Production-specific dependencies
├── setup.py                 # Package setup
├── pyproject.toml           # Modern Python packaging
└── README.md                # This file
```

## 🔌 API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with API info
- `GET /api/v1/health` - Health check
- `GET /api/v1/system/status` - System status and configuration

### Email Management

- `GET /api/v1/emails/` - List all emails with filtering
- `GET /api/v1/emails/{email_id}` - Get specific email
- `GET /api/v1/emails/priority-queue` - Get priority-sorted emails
- `POST /api/v1/process-emails` - Trigger email processing

### Analytics

- `GET /api/v1/analytics/` - Get analytics data
- `GET /api/v1/analytics/dashboard` - Dashboard metrics
- `GET /api/v1/analytics/trends` - Trend analysis

## 🧪 Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Type checking
mypy app/

# Linting
flake8 app/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🚀 Production Deployment

### Using Gunicorn

```bash
# Install production dependencies
pip install -r requirements-prod.txt

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

```bash
# Build image
docker build -t ai-communication-assistant-backend .

# Run container
docker run -p 8000:8000 --env-file .env ai-communication-assistant-backend
```

## 📊 Monitoring and Logging

The system includes comprehensive logging and monitoring:

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Performance Metrics**: Response times, throughput, error rates
- **Health Checks**: Database connectivity, service status
- **Error Tracking**: Detailed error logs with stack traces

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Pydantic models for request validation
- **CORS Protection**: Configurable cross-origin resource sharing
- **Rate Limiting**: Configurable API rate limiting
- **Secure Headers**: Security headers middleware

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the logs for debugging information

## 🔄 Changelog

### Version 1.0.0

- Initial release
- Core email processing functionality
- AI-powered analysis and response generation
- RESTful API with FastAPI
- Background task processing
- Comprehensive analytics

---

**Note**: This is a production-ready backend system. Ensure proper security measures and monitoring are in place before deploying to production environments.
