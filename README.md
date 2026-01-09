# AI Tutor – Multi-Agent Adaptive Learning System

## Overview

**AI Tutor** is an intelligent, adaptive, multi-agent learning system built with **LangGraph** and **LangChain**. It simulates a human tutor by assessing student knowledge, planning lessons, providing explanations, generating practice questions, evaluating answers, and adapting its teaching strategy based on student performance.

The system provides **personalized learning experiences** at scale while maintaining **accuracy, consistency, and stateful interactions**.

---

## Features

### Adaptive Learning
- Tailors lessons based on **student level** (beginner, intermediate, advanced).  
- Adjusts difficulty dynamically using student performance and mastery scores.  

### Multi-Agent Architecture
- **Planner Agent** – sequences lessons and decides teaching strategy.  
- **Tutor Agent** – provides explanations and analogies tailored to the student.  
- **Retriever Agent** – fetches examples, definitions, code snippets from trusted sources.  
- **Question Generator Agent** – creates adaptive practice questions.  
- **Evaluator Agent** – grades answers, detects misconceptions, and updates mastery.  
- **Critic / Reflector Agent** – monitors quality, detects errors, and triggers retries if needed.  

### Stateful Interactions
- Maintains a **shared LangGraph state** across all agents.  
- Tracks **student progress, mastery, misconceptions, and learning history**.  
- Allows **loops and retries** for topics not fully mastered.  

### Knowledge Integration
- Supports **RAG (Retrieval-Augmented Generation)** to provide accurate, grounded explanations.  
- Connects to **vector databases, documentation, or curriculum resources**.  

### Feedback & Assessment
- Provides immediate feedback on answers.  
- Generates hints or alternative explanations when needed.  
- Tracks mastery per concept for long-term learning analytics.  

---

## Architecture

The AI Tutor is organized into **layers of specialized agents** orchestrated by a central **LangGraph state machine**:


### Key Points

- **Planner Agent:** Decides lesson flow and teaching strategy.
- **Retriever Agent:** Fetches reliable examples, definitions, and context.
- **Tutor Agent:** Explains topics and generates analogies.
- **Question Generator:** Produces adaptive exercises.
- **Evaluator Agent:** Grades answers, updates mastery, detects misconceptions.
- **Critic / Reflector:** Monitors output quality and triggers retries if necessary.
- **LangGraph Core:** Orchestrates agent execution, manages state, supports loops, retries, and conditional paths.
- **Feedback & Adaptation:** Adjusts lesson plan dynamically based on student performance.

---

> This architecture enables **adaptive, stateful, and explainable tutoring**, unlike a linear chain-based system.
