// User types
export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

// Chat types
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  question: string;
  conversation_id?: number;
}

export interface ChatResponse {
  answer: string;
  conversation_id: number;
  retrieved_docs: string[];
}

// Practice Quiz types
export interface PracticeQuestionRequest {
  topic?: string;
}

export interface PracticeQuestionResponse {
  question_id: number;
  question: string;
}

export interface PracticeAnswerRequest {
  question_id: number;
  student_answer: string;
}

export interface PracticeAnswerResponse {
  is_correct: boolean;
  feedback: string;
  correct_answer: string;
  topic: string;
  new_mastery_score: number;
}

// Progress types
export interface TopicMastery {
  topic: string;
  score: number;
}

export interface ProgressResponse {
  mastery_scores: TopicMastery[];
}

// Study session types
export interface StudySession {
  id: string;
  user_id: string;
  topic: string;
  start_time: string;
  end_time?: string;
  questions_attempted: number;
  questions_correct: number;
}