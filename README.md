# AI Tutor – Multi-Agent Adaptive Learning System

## Overview

**AI Tutor** is an intelligent, adaptive, multi-agent learning system built with **LangGraph** and **LangChain**. It simulates a human tutor by assessing student knowledge, providing explanations, generating practice questions, evaluating answers, tracking mastery, and adapting its teaching strategy based on student performance.

The system provides **personalized learning experiences** at scale while maintaining **accuracy, consistency, and stateful interactions**.

---

## Implementation Status

### ✅ Phase 1 & 2: Core Tutoring System
- Q&A Mode with RAG-powered explanations
- Practice question generation
- Answer evaluation with feedback
- Conversation memory management

### ✅ Phase 3: Mastery Tracking
- Topic extraction and identification
- Performance-based score tracking
- Visual progress monitoring

---

## Features

### Current Features (Implemented)

#### Q&A Mode
- Ask questions about your study material
- Get detailed explanations with analogies
- Context pulled from your personal study guide using RAG
- Maintains conversation history for contextual responses

#### Practice Mode
- Auto-generated practice questions from study material
- Intelligent answer evaluation (handles paraphrasing and synonyms)
- Immediate feedback with correct answer explanations
- Topic-based mastery tracking

#### Mastery Tracking System
- **Automatic topic identification** - Extracts key concepts from questions
- **Performance scoring** - Tracks mastery per topic (0-100%)
- **Visual progress bars** - See your strengths and weak areas
- **Adaptive tracking** - Correct answers +10%, incorrect -15%
- **Progress command** - Type `progress` to view all topic scores

### Multi-Agent Architecture (Current)

#### 1. **Retriever Agent**
Performs semantic search in FAISS vector database to fetch relevant study material chunks.

#### 2. **Tutor Agent**
Provides clear explanations with analogies based on retrieved context. Uses conversational AI to maintain engagement.

#### 3. **Question Generator Agent**
Creates practice questions from study material. Generates both question and correct answer in structured format.

#### 4. **Evaluator Agent**
Grades student answers intelligently, accounting for paraphrasing and synonyms. Provides constructive feedback.

#### 5. **Topic Extractor Agent** *(New in Phase 3)*
Uses LLM to identify the main concept/topic from questions and context. Returns clean, short topic names for tracking.

#### 6. **Mastery Tracker Agent** *(New in Phase 3)*
Updates performance scores based on evaluation results. Adjusts scores by topic for granular progress tracking.

### Stateful Interactions
- Maintains **shared LangGraph state** across all agents
- Tracks **chat history, retrieved documents, mastery scores**
- **Persistent mastery tracking** across practice sessions
- Supports **conditional routing** based on mode (Q&A, Practice, Evaluate)

### Knowledge Integration
- **RAG (Retrieval-Augmented Generation)** using FAISS vector store
- OpenAI embeddings for semantic search
- Custom study guide (currently: Computer Science fundamentals)
- 500-character chunks with 50-character overlap for optimal retrieval

---

## Architecture

The AI Tutor uses a **LangGraph state machine** with conditional routing:

```
┌─────────────────────────────────────────────────────────────┐
│                         User Input                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Retriever   │ (Always first)
                    │     Agent     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Router/Decide │ (Based on mode)
                    │     Node      │
                    └───┬───┬───┬───┘
                        │   │   │
        ┌───────────────┘   │   └───────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────��────┐   ┌───────────────┐   ┌───────────────┐
│  Tutor Agent  │   │  Question Gen │   │  Evaluator    │
│  (Q&A Mode)   │   │ (Practice)    │   │  Agent        │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        ▼                   │                   ▼
      [END]                 │           ┌───────────────┐
                            │           │ Topic Extract │
                            │           └───────┬───────┘
                            │                   │
                            │                   ▼
                            │           ┌───────────────┐
                            │           │   Mastery     │
                            │           │   Tracker     │
                            │           └───────┬───────┘
                            │                   │
                            └───────────────────┴────────► [END]
```

### Execution Flows

#### Q&A Mode:
```
User question → Retriever → Router → Tutor → END
```

#### Practice Mode:
```
1. Generation: "practice" → Retriever → Router → Question Generator → END
2. Evaluation: Student answer → Retriever → Router → Evaluator → Topic Extractor → Mastery Tracker → END
```

---

## Commands

| Command | Description |
|---------|-------------|
| `<question>` | Ask any question about your study material (Q&A mode) |
| `practice` | Get a randomly generated practice question |
| `progress` | View your mastery levels for all topics |
| `exit` or `quit` | Exit the tutor |

---

## Example Usage

```bash
$ python multiAgentTutor.py

Welcome to your Multi-Agent AI Tutor!
Commands:
 - Ask any question for the Q&A mode
 - Type 'practice' to get a practice question
 - Type 'progress' to see your mastery levels
 - Type 'exit' to quit

You: What is polymorphism?
[Retriever Agent] Searching for What is polymorphism?

Tutor: Polymorphism is the ability of objects to take on multiple forms...

You: practice
[Retriever Agent] Searching for Generate a practice question from study guide
[Router] Practice mode -> Question Generator
Practice Question: What is the time complexity of binary search?

Your answer: O(log n)
[Retriever Agent] Searching for What is the time complexity of binary search?
[Router] Evaluate mode -> Evaluator
[Evaluator Agent] Checking your answer...
[Topic Extractor] Identified topic: binary search
[Mastery Tracker] ✅ binary search: 50% → 60%

✅ Correct! Excellent! Binary search indeed has O(log n) time complexity...

You: progress

📊 Your Mastery Levels:

  ⚠️  polymorphism       : █████░░░░░ 50%
  ✅ binary search      : ██████░░░░ 60%

You: exit
Goodbye! Happy Studying!
```

---

## State Schema

```python
class TutorState(TypedDict):
    question: str                    # Current question/query
    chat_history: List[BaseMessage]  # Conversation history (accumulates)
    retrieved_docs: List             # FAISS search results
    answer: str                      # Agent responses
    mode: str                        # "qa" | "practice" | "evaluate"
    generated_question: str          # Practice question
    correct_answer: str              # Ground truth answer
    student_answer: str              # User's response
    is_correct: bool                 # Evaluation result
    current_topic: str               # Identified topic/concept
    mastery_scores: Dict[str, float] # Topic → score (0.0-1.0)
    user_feedback: str               # Reserved for future phases
```

---

## Technology Stack

- **LangGraph** - State machine orchestration, conditional routing
- **LangChain** - LLM chains, prompt templates, message handling
- **OpenAI GPT** - Language model for all agents
- **FAISS** - Vector database for semantic search
- **OpenAI Embeddings** - Text embeddings for RAG
- **Python 3.x** - Core implementation

---

> This architecture enables **adaptive, stateful, and explainable tutoring** with granular progress tracking, unlike simple chain-based systems.
