import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type {
  UserCreate,
  UserLogin,
  Token,
  ChatRequest,
  ChatResponse,
  PracticeQuestionRequest,
  PracticeQuestionResponse,
  PracticeAnswerRequest,
  PracticeAnswerResponse,
  ProgressResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add token to requests if available
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle 401 errors (unauthorized)
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async register(userData: UserCreate): Promise<Token> {
    const response = await this.api.post<Token>('/auth/register', userData);
    return response.data;
  }

  async login(credentials: UserLogin): Promise<Token> {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await this.api.post<Token>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.api.get('/auth/me');
    return response.data;
  }

  async logout(): Promise<{ message: string }> {
    const response = await this.api.post('/auth/logout');
    this.removeToken();
    return response.data;
  }

  // API Key endpoints
  async getApiKeyStatus(): Promise<{ has_api_key: boolean }> {
    const response = await this.api.get('/auth/api-key/status');
    return response.data;
  }

  async setApiKey(apiKey: string): Promise<{ message: string }> {
    const response = await this.api.post('/auth/api-key', { api_key: apiKey });
    return response.data;
  }

  async deleteApiKey(): Promise<{ message: string }> {
    const response = await this.api.delete('/auth/api-key');
    return response.data;
  }

  // Chat endpoints
  async sendMessage(chatRequest: ChatRequest): Promise<ChatResponse> {
    const response = await this.api.post<ChatResponse>('/chat', chatRequest);
    return response.data;
  }

  // Practice endpoints
  async generatePractice(request: PracticeQuestionRequest): Promise<PracticeQuestionResponse> {
    const response = await this.api.post<PracticeQuestionResponse>('/practice/generate', request);
    return response.data;
  }

  async submitAnswer(submission: PracticeAnswerRequest): Promise<PracticeAnswerResponse> {
    const response = await this.api.post<PracticeAnswerResponse>('/practice/submit', submission);
    return response.data;
  }

  // Progress endpoints
  async getProgress(): Promise<ProgressResponse> {
    const response = await this.api.get<ProgressResponse>('/progress');
    return response.data;
  }

  // Study Guide endpoints
  async uploadStudyGuide(formData: FormData): Promise<{ message: string }> {
    const response = await this.api.post<{ message: string }>('/study-guide/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getStudyGuideStatus(): Promise<{
    has_study_guide: boolean;
    user_id: number;
    filename: string | null;
    file_size: number | null;
    word_count: number | null;
  }> {
    const response = await this.api.get('/study-guide/status');
    return response.data;
  }

  // Utility methods
  setToken(token: string) {
    localStorage.setItem('access_token', token);
  }

  removeToken() {
    localStorage.removeItem('access_token');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }
}

export const apiService = new ApiService();