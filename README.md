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
- **FAISS** - Vector database for semantic search
- **SQLAlchemy** - ORM with SQLite
- **JWT** - Authentication

### Frontend
- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                          │
│   Login • Chat • Practice • Progress • Study Guide Upload    │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│              JWT Auth • Routes • Database                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph State Machine                     │
│                                                              │
│  ┌──────────┐                                                │
│  │Retriever │ ──► Searches FAISS vector store                │
│  └────┬─────┘                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────┐     ┌─────────────┐     ┌───────────┐          │
│  │  Tutor   │     │  Question   │     │ Evaluator │          │
│  │  Agent   │     │  Generator  │     │   Agent   │          │
│  └────┬─────┘     └──────┬──────┘     └─────┬─────┘          │
│       │                  │                  │                │
│       ▼                  ▼                  ▼                │
│     [END]              [END]         ┌───────────┐           │
│                                      │  Topic    │           │
│                                      │ Extractor │           │
│                                      └─────┬─────┘           │
│                                            ▼                 │
│                                      ┌───────────┐           │
│                                      │  Mastery  │           │
│                                      │  Tracker  │           │
│                                      └─────┬─────┘           │
│                                            ▼                 │
│                                          [END]               │
└─────────────────────────────────────────────────────────────┘
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
│   │   ├── vectorstore.py       # FAISS vector store manager
│   │   ├── graph.py             # LangGraph multi-agent system
│   │   ├── models/
│   │   │   ├── database_models.py   # SQLAlchemy models
│   │   │   └── schemas.py           # Pydantic schemas
│   │   └── routes/
│   │       ├── auth.py          # Login, register, user info
│   │       ├── chat.py          # Q&A mode endpoint
│   │       ├── practice.py      # Practice question & grading
│   │       ├── progress.py      # Mastery score retrieval
│   │       └── study_guide.py   # File upload & vectorization
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/               # React page components
│   │   ├── components/          # Reusable UI components
│   │   ├── services/api.ts      # Axios HTTP client
│   │   └── App.tsx              # Router setup
│   ├── package.json
│   └── .env
├── multiAgentTutor.py           # Standalone CLI version
└── study_guide.txt              # Sample study material
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API key

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
# Edit .env and add your OPENAI_API_KEY

# Run the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (optional)
cp .env.example .env
# Edit .env if your backend is not at localhost:8000

# Run development server
npm run dev
```

The app will be available at `http://localhost:5173`

### CLI Version (Standalone)

For a quick demo without the web interface:

```bash
# From project root
python multiAgentTutor.py
```

## Environment Variables

### Backend (.env)

```env
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./tutor.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
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
| **User** | id, email, hashed_password, full_name, has_study_guide |
| **Conversation** | id, user_id, created_at |
| **Message** | id, conversation_id, role, content, timestamp |
| **MasteryScore** | id, user_id, topic, score |
| **PracticeQuestion** | id, user_id, question, correct_answer, student_answer, is_correct |

## How It Works

### 1. Upload Study Guide
User uploads a `.txt` file which gets:
- Split into 1000-character chunks (200 overlap)
- Converted to embeddings via OpenAI
- Stored in FAISS vector database

### 2. Q&A Mode
```
User Question → Retriever (FAISS search) → Tutor Agent → Response
```

### 3. Practice Mode
```
Generate: Retriever → Question Generator → Question + Answer
Submit:   Retriever → Evaluator → Topic Extractor → Mastery Tracker → Feedback
```

### 4. State Management
LangGraph maintains a `TutorState` that flows between agents:

```python
class TutorState(TypedDict):
    mode: str                    # "qa" | "practice" | "evaluate"
    question: str
    student_answer: Optional[str]
    user_id: int
    vectorstore: Any
    db: Session
    retrieved_docs: List[Document]
    current_topic: str
    generated_question: str
    correct_answer: str
    answer: str
    is_correct: bool
    feedback: str
    new_mastery_score: float
    chat_history: Annotated[List[BaseMessage], operator.add]
```

## License

MIT
