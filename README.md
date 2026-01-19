# StudyBuddy - AI-Powered Multi-Agent Tutoring System

An intelligent, adaptive learning platform that uses **LangGraph** to orchestrate multiple AI agents for personalized tutoring. Upload your study materials and get explanations, practice questions, and track your mastery across topics.

## Features

- **Q&A Mode** - Ask questions about your study material and get detailed explanations with analogies
- **Practice Mode** - Auto-generated quiz questions with intelligent answer evaluation
- **Mastery Tracking** - Track your progress per topic with adaptive scoring
- **Personal Study Guides** - Upload your own materials for customized learning
- **Multi-Agent AI** - Six specialized agents working together via LangGraph

## Tech Stack

### Backend
- **FastAPI** - Python web framework
- **LangGraph** - Multi-agent orchestration
- **LangChain** - LLM framework
- **OpenAI GPT-4o-mini** - Language model
- **PostgreSQL + pgvector** - Database with vector search
- **Supabase** - Database hosting & file storage
- **SQLAlchemy** - ORM
- **JWT** - Authentication

### Frontend
- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations

### Deployment
- **Vercel** - Frontend hosting
- **Railway** - Backend hosting
- **Supabase** - PostgreSQL database & file storage

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                          │
│   Login • Chat • Practice • Progress • Study Guide Upload    │
│                      (Vercel)                                │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│              JWT Auth • Routes • Database                    │
│                      (Railway)                               │
└───────────────────────────┬─────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Supabase    │  │   Supabase    │  │   LangGraph   │
│   PostgreSQL  │  │    Storage    │  │  State Machine│
│   + pgvector  │  │ (Study Guides)│  │  (AI Agents)  │
└───────────────┘  └───────────────┘  └───────────────┘
```

### Agent Responsibilities

| Agent | Purpose |
|-------|---------|
| **Retriever** | Semantic search on user's vectorized study guide |
| **Tutor** | Provides explanations with analogies and examples |
| **Question Generator** | Creates practice questions from study material |
| **Evaluator** | Grades answers (handles paraphrasing/synonyms) |
| **Topic Extractor** | Identifies main concept from questions |
| **Mastery Tracker** | Updates scores: correct +10%, incorrect -15% |

## Project Structure

```
StudyBuddy/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── auth.py              # JWT authentication
│   │   ├── storage.py           # Supabase Storage manager
│   │   ├── vectorstore.py       # pgvector store manager
│   │   ├── graph.py             # LangGraph multi-agent system
│   │   ├── models/
│   │   │   ├── database_models.py   # SQLAlchemy models
│   │   │   └── schemas.py           # Pydantic schemas
│   │   └── routes/
│   │       ├── auth.py          # Login, register, API key
│   │       ├── chat.py          # Q&A mode endpoint
│   │       ├── practice.py      # Practice question & grading
│   │       ├── progress.py      # Mastery score retrieval
│   │       └── study_guide.py   # File upload & vectorization
│   ├── Dockerfile
│   ├── railway.json
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/               # React page components
│   │   ├── components/          # Reusable UI components
│   │   ├── services/api.ts      # Axios HTTP client
│   │   └── App.tsx              # Router setup
│   ├── vercel.json
│   ├── package.json
│   └── .env.example
└── README.md
```

## Deployment Guide

### Prerequisites

- GitHub repository with the code
- Accounts on: [Supabase](https://supabase.com), [Railway](https://railway.app), [Vercel](https://vercel.com)

### 1. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Enable the **pgvector** extension:
   - Go to **Database → Extensions**
   - Search for `vector` and enable it
3. Create a storage bucket:
   - Go to **Storage → New bucket**
   - Name it `study-guides`
   - Keep it **Private**
4. Get your credentials from **Settings → API**:
   - Project URL
   - service_role key (click Reveal)
5. Get your database connection string from **Settings → Database**:
   - Use the "Connection string" under "Connection Pooling"

### 2. Railway Backend Deployment

1. Create a new project at [railway.app](https://railway.app)
2. **Deploy from GitHub repo** → Select this repository
3. Set **Root Directory** to `backend`
4. Add these environment variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Generate a secure 32+ char string |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `DATABASE_URL` | Your Supabase connection string |
| `CORS_ORIGINS` | `https://your-app.vercel.app` |
| `SUPABASE_URL` | `https://your-project.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Your service_role key |
| `SUPABASE_BUCKET` | `study-guides` |

5. Deploy and copy your Railway URL (e.g., `https://studybuddy-production-xxxx.up.railway.app`)

### 3. Vercel Frontend Deployment

1. Create a new project at [vercel.com](https://vercel.com)
2. **Import from GitHub** → Select this repository
3. Set **Root Directory** to `frontend`
4. Add environment variable:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Your Railway backend URL |

5. Deploy

### 4. Update CORS

After Vercel deploys, go back to Railway and update `CORS_ORIGINS` with your Vercel URL.

---

## Local Development

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if your backend is not at localhost:8000

# Run development server
npm run dev
```

The app will be available at `http://localhost:5173`

## Environment Variables

### Backend (.env)

```env
# JWT Configuration
SECRET_KEY=your-secure-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase PostgreSQL Database
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

# CORS Origins
CORS_ORIGINS=http://localhost:5173,https://your-app.vercel.app

# Supabase Storage
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_BUCKET=study-guides
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new user |
| POST | `/auth/login` | Get JWT token |
| GET | `/auth/me` | Current user info |
| POST | `/auth/api-key` | Set OpenAI API key |
| GET | `/auth/api-key/status` | Check if API key is set |

### Chat (Q&A Mode)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send question, get tutor response |

### Practice
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/practice/generate` | Generate a practice question |
| POST | `/practice/submit` | Submit answer for grading |

### Progress
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/progress` | Get mastery scores by topic |

### Study Guide
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/study-guide/upload` | Upload .txt study material |
| GET | `/study-guide/status` | Check upload status |

## Database Schema

| Table | Fields |
|-------|--------|
| **users** | id, email, hashed_password, full_name, has_study_guide, encrypted_openai_key |
| **conversations** | id, user_id, created_at |
| **messages** | id, conversation_id, role, content, timestamp |
| **mastery_scores** | id, user_id, topic, score, updated_at |
| **practice_questions** | id, user_id, question, correct_answer, student_answer, is_correct, topic |

## How It Works

### 1. Upload Study Guide
User uploads a `.txt` file which gets:
- Stored in Supabase Storage
- Split into 500-character chunks (50 overlap)
- Converted to embeddings via OpenAI
- Stored in PostgreSQL with pgvector

### 2. Q&A Mode
```
User Question → Retriever (pgvector search) → Tutor Agent → Response
```

### 3. Practice Mode
```
Generate: Retriever → Question Generator → Question + Answer
Submit:   Retriever → Evaluator → Topic Extractor → Mastery Tracker → Feedback
```

### 4. Mastery Scoring
- Correct answer: +10% (max 100%)
- Incorrect answer: -15% (min 0%)
- New topics start at 50%

## License

MIT
