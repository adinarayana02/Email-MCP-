# AI-Powered Communication Assistant

A comprehensive email management system that uses artificial intelligence to automatically analyze, categorize, prioritize, and generate responses to customer support emails.

## 🚀 Features

### Core Functionality

- **Email Retrieval & Filtering**: Automatically fetch and filter support-related emails
- **AI-Powered Analysis**: Sentiment analysis, priority detection, and email categorization
- **Smart Prioritization**: Urgent emails are automatically flagged and prioritized
- **Context-Aware Responses**: AI-generated responses using RAG (Retrieval-Augmented Generation)
- **Comprehensive Dashboard**: Real-time analytics and email management interface

### Advanced Capabilities

- **Multi-Priority Levels**: Urgent, High, Normal, and Low priority classification
- **Enhanced Categorization**: Technical support, billing, complaints, feature requests, etc.
- **Information Extraction**: Automatic extraction of contact details, customer requirements, and metadata
- **Response Templates**: Pre-built templates for common scenarios
- **Bulk Operations**: Mass email management and updates
- **Performance Analytics**: Detailed metrics and insights

## 🏗️ Architecture

### Backend (Python/FastAPI)

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping
- **SQLite**: Lightweight database for development and production
- **OpenAI GPT**: AI-powered response generation
- **Transformers**: Advanced sentiment analysis and NLP
- **Background Tasks**: Automated email processing and analytics

### Frontend (React)

- **React 18**: Modern React with hooks and functional components
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Recharts**: Beautiful and composable charts for analytics
- **Lucide React**: Beautiful & consistent icon toolkit
- **React Toastify**: Toast notifications for user feedback

### AI Services

- **Sentiment Analysis**: Multi-label sentiment classification
- **Priority Detection**: Keyword-based urgency assessment
- **Email Categorization**: Intelligent topic classification
- **Response Generation**: Context-aware AI responses with RAG
- **Information Extraction**: Named entity recognition and data extraction

## 📋 Requirements

### Backend Dependencies

- Python 3.8+
- FastAPI 0.104.1+
- SQLAlchemy 2.0.23+
- OpenAI API key
- Transformers 4.36.2+
- PyTorch 2.1.1+

### Frontend Dependencies

- Node.js 16+
- React 18.2.0+
- Tailwind CSS 3.3.6+
- Recharts 2.8.0+

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Hackthon
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and other configurations

# Initialize database
python -m app.main
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 4. Environment Configuration

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./data/email_database.db
PROJECT_NAME=AI Communication Assistant
ENVIRONMENT=development
```

## 🚀 Usage

### Starting the Application

1. **Start Backend Server**

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start Frontend Development Server**

```bash
cd frontend
npm start
```

3. **Access the Application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Key Features Usage

#### Email Management

- **Priority Queue**: View emails sorted by urgency and importance
- **Filtering**: Filter by priority, sentiment, category, and status
- **Search**: Full-text search across email content
- **Bulk Actions**: Mass update, assign, or resolve emails

#### Response Management

- **AI Generation**: Automatically generate contextual responses
- **Template System**: Use pre-built response templates
- **Manual Editing**: Edit and customize AI-generated responses
- **Response Tracking**: Monitor response status and metrics

#### Analytics Dashboard

- **Real-time Metrics**: Live email statistics and performance indicators
- **Trend Analysis**: Historical data and pattern recognition
- **Performance Insights**: AI accuracy and response quality metrics
- **Export Options**: Download reports in PDF or CSV format

## 🔧 Configuration

### AI Service Configuration

The AI service can be configured through environment variables and the knowledge base:

```python
# Backend configuration
OPENAI_API_KEY=your_api_key
AI_MODEL=gpt-3.5-turbo
SENTIMENT_MODEL=cardiffnlp/twitter-roberta-base-sentiment-latest
```

### Knowledge Base

Customize the knowledge base in `backend/data/knowledge_base.json`:

```json
{
  "technical_issues": {
    "login_problems": "Custom response for login issues...",
    "connectivity": "Custom response for connectivity problems..."
  },
  "billing": {
    "payment_failed": "Custom response for payment issues..."
  }
}
```

### Email Filtering

Configure email filtering criteria in the backend:

```python
SUPPORT_KEYWORDS = [
    "support", "query", "request", "help", "issue", "problem"
]

URGENT_KEYWORDS = [
    "urgent", "critical", "emergency", "immediately", "asap"
]
```

## 📊 API Endpoints

### Email Management

- `GET /api/v1/emails/` - Get all emails with filtering
- `GET /api/v1/emails/priority-queue` - Get priority-sorted emails
- `POST /api/v1/emails/filter` - Advanced email filtering
- `PUT /api/v1/emails/{id}` - Update email metadata
- `POST /api/v1/emails/bulk-update` - Bulk email operations

### Analytics

- `GET /api/v1/analytics/dashboard` - Dashboard statistics
- `GET /api/v1/analytics/sentiment-analysis` - Sentiment trends
- `GET /api/v1/analytics/priority-analysis` - Priority distribution
- `GET /api/v1/analytics/performance-metrics` - AI performance data

### Response Management

- `POST /api/v1/emails/{id}/send-response` - Send email response
- `PUT /api/v1/emails/{id}/response` - Update generated response

## 🧪 Testing

### Backend Testing

```bash
cd backend
pytest tests/
```

### Frontend Testing

```bash
cd frontend
npm test
```

### API Testing

Use the interactive API documentation at http://localhost:8000/docs

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Production Deployment

1. **Backend**: Deploy to cloud platform (AWS, GCP, Azure)
2. **Frontend**: Build and deploy to CDN or hosting service
3. **Database**: Use production database (PostgreSQL, MySQL)
4. **Environment**: Set production environment variables

## 🔒 Security Considerations

- **API Key Management**: Secure storage of OpenAI API keys
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: API rate limiting to prevent abuse
- **CORS Configuration**: Proper CORS settings for production
- **Database Security**: Secure database connections and queries

## 📈 Performance Optimization

- **Background Processing**: Asynchronous email processing
- **Database Indexing**: Optimized database queries
- **Caching**: Response caching for improved performance
- **Connection Pooling**: Efficient database connection management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation
- Review the code examples

## 🔮 Future Enhancements

- **Multi-language Support**: Internationalization and localization
- **Advanced AI Models**: Integration with newer AI models
- **Mobile Application**: React Native mobile app
- **Integration APIs**: Connect with popular email services
- **Machine Learning**: Continuous learning from user feedback
- **Advanced Analytics**: Predictive analytics and insights

## 📊 Project Status

- ✅ Core email management functionality
- ✅ AI-powered analysis and categorization
- ✅ Response generation and management
- ✅ Comprehensive analytics dashboard
- ✅ Modern, responsive UI
- 🔄 Advanced filtering and search
- 🔄 Bulk operations and automation
- 🔄 Performance optimization
- 🔄 Testing and documentation

---

**Built with ❤️ for efficient customer support management**
