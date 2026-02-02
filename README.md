# Resummate

> Transform your resume into a Top 1% application with AI-powered career coaching

## Overview

Resummate is an intelligent resume review platform that combines modern hiring standards, ATS optimization, and personalized coaching to help job seekers create exceptional applications. By leveraging advanced AI analysis, Resummate provides actionable feedback on resume content, formatting, keyword alignment, and overall effectiveness.

## Product Features

### AI Career Strategist
- **Comprehensive Resume Analysis**: Deep evaluation of content, structure, and presentation
- **ATS Optimization**: Ensures resumes pass Applicant Tracking Systems with proper formatting and keyword usage
- **Interactive Coaching**: Real-time, personalized guidance tailored to your target role and industry
- **Action Verb Enhancement**: Identifies weak language and suggests powerful alternatives
- **Keyword Alignment**: Matches resume content with job description requirements
- **Modern Standards**: Feedback based on current hiring best practices and recruiter expectations

### User Experience
1. **Upload Resume**: Support for PDF, DOCX, and TXT formats
2. **Instant Analysis**: AI-powered review of resume content and structure
3. **Detailed Feedback**: Section-by-section recommendations with specific examples
4. **Iterative Improvement**: Continuous coaching to refine and optimize applications

## Technical Architecture

### Technology Stack

**Frontend**
- **Framework**: Next.js 16
- **Language**: TypeScript
- **Deployment**: Vercel
- **Features**: Server-side rendering, API routes, optimized performance

**Backend**
- **Framework**: FastAPI
- **Language**: Python
- **Deployment**: Vercel (Serverless Functions)
- **Features**: High-performance REST API, async request handling

**Authentication**
- **Provider**: [Stack Auth](https://stack-auth.com/)
- **Features**: Open-source authentication, user management, password/SSO/2FA, organizations & teams, permissions & RBAC
- **Benefits**: Seamless integration, beautiful pre-built components, headless SDK option

**AI & Machine Learning**
- **Provider**: Google Gemini API
- **Capabilities**: Natural language understanding, resume parsing, content generation, personalized recommendations

**Database**
- **Platform**: Supabase PostgreSQL
- **Features**: Persistent storage, real-time capabilities, row-level security
- **Data**: User profiles, resume versions, analysis history, feedback cache

---

## API Documentation

### Project Structure

```
api/
├── chat/                    # Chat domain
│   ├── __init__.py
│   └── router.py           # Chat endpoints
├── resume/                  # Resume domain
│   ├── __init__.py
│   └── router.py           # Resume endpoints
├── job_description/         # Job description domain
│   ├── __init__.py
│   └── router.py           # Job description endpoints
├── core/                    # Core application modules
│   ├── __init__.py
│   ├── config.py           # Configuration using pydantic-settings
│   ├── dependencies.py     # Dependency injection providers
│   ├── logging.py          # Structured logging setup
│   └── schemas.py          # Shared Pydantic models
├── db/                      # Database layer
│   ├── __init__.py
│   └── service.py          # Supabase database operations
├── services/                # Business logic layer
│   ├── __init__.py
│   ├── gemini.py           # Gemini AI service
│   ├── prompts.py          # System prompts and utilities
│   └── tools.py            # AI function calling tools
├── main.py                  # Main application entry point
└── index.py                 # Legacy compatibility wrapper
```

### Architecture Principles

This codebase follows FastAPI best practices:

#### 1. Domain-Driven Organization
- Code is organized by domain (chat, resume, job_description) rather than by file type
- Each domain has its own router
- Shared code lives in `core/`, `db/`, and `services/`

#### 2. Type Safety
- All functions have complete type hints
- Pydantic models are used for all request/response validation
- Type aliases (`SupabaseClient`, `GeminiClient`) simplify dependency injection

#### 3. Dependency Injection
- Database and AI clients are injected via FastAPI's `Depends`
- No global state or direct instantiation in routers
- Makes code testable and modular

#### 4. Consistent API Structure
- All endpoints follow REST conventions under `/api/`
- Organized by domain (chat, resume, job-description)

#### 5. Error Handling
- Consistent use of `HTTPException` with appropriate status codes
- Structured error responses
- Comprehensive error logging with traceback

#### 6. Structured Logging
- Centralized logging configuration in `core/logging.py`
- Context-aware logging with extra fields
- Easy integration with log aggregation services

#### 7. Configuration Management
- All configuration in `core/config.py` using `pydantic-settings`
- Environment variables loaded from `.env.local`
- Type-safe access to configuration values

#### 8. Service Layer Pattern
- Business logic separated from HTTP layer
- Routers are thin and focused on HTTP concerns
- Services in `services/` handle complex operations
- Database operations isolated in `db/service.py`

### Environment Variables

Required environment variables (set in `.env.local`):

```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_PUBLISHABLE_DEFAULT_KEY=your_supabase_key

# Google Gemini AI
GOOGLE_GENERATIVE_AI_API_KEY=your_gemini_api_key

# Optional Configuration
GEMINI_MODEL=gemini-2.5-flash-lite
MAX_OUTPUT_TOKENS=512
DEFAULT_TEMPERATURE=0.5
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
LOG_LEVEL=INFO
```

### API Endpoints

#### Health Check
- `GET /api/health` - Health check endpoint

#### Chat
- `POST /api/chat` - Stream chat responses
- `POST /api/generate` - Generate non-streaming responses
- `GET /api/chat/history/{thread_id}` - Get message history

#### Resume
- `POST /api/resume/upload` - Upload resume file
- `GET /api/resume/{thread_id}` - Get resume info
- `DELETE /api/resume/{thread_id}` - Delete resume

#### Job Description
- `POST /api/job-description/upload` - Upload job description
- `GET /api/job-description/{thread_id}` - Get job description info
- `DELETE /api/job-description/{thread_id}` - Delete job description

### Development

#### Installation

```bash
pip install -r requirements.txt
```

#### Running Locally

```bash
uvicorn api.main:app --reload --port 8000
```

#### Production Deployment

The application is deployed on Vercel. The `api/index.py` file serves as a compatibility wrapper for Vercel's serverless functions.

### Code Quality

- All functions have docstrings with Args, Returns, and Raises sections
- Type hints on all function signatures
- Consistent error handling patterns
- Comprehensive logging for debugging

### Testing

To add tests, create a `tests/` directory with pytest:

```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

---

## License

MIT License

## Contact

For technical questions or support, contact dan.deng.wei@gmail.com

---

Built with ❤️ to help job seekers succeed