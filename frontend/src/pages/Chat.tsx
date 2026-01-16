import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, LogOut, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import type { Message } from '../types';

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | undefined>(undefined);
  const [hasStudyGuide, setHasStudyGuide] = useState<boolean | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check if user has uploaded a study guide
  useEffect(() => {
    const checkStudyGuide = async () => {
      try {
        const status = await apiService.getStudyGuideStatus();
        setHasStudyGuide(status.has_study_guide);
      } catch (err) {
        setHasStudyGuide(false);
      }
    };
    checkStudyGuide();
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const questionText = input;
    setInput('');
    setLoading(true);

    try {
      const response = await apiService.sendMessage({
        question: questionText,
        conversation_id: conversationId,
      });

      setConversationId(response.conversation_id);

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleLogout = async () => {
    try {
      await apiService.logout();
    } catch (err) {
      // Still logout even if API call fails
      apiService.removeToken();
    }
    navigate('/login');
  };

  const suggestedQuestions = [
    "Explain quantum mechanics in simple terms",
    "Help me solve a calculus problem",
    "What are the main causes of World War II?",
    "Teach me about photosynthesis"
  ];

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
            <Bot className="text-white" size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">AI Tutor</h1>
            <p className="text-sm text-gray-500">Ask me anything!</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/study-guide')}
            className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors font-medium"
          >
            <FileText size={18} />
            <span>Study Guide</span>
          </button>
          <button
            onClick={() => navigate('/practice')}
            className="text-gray-600 hover:text-blue-600 transition-colors font-medium"
          >
            Practice
          </button>
          <button
            onClick={() => navigate('/progress')}
            className="text-gray-600 hover:text-blue-600 transition-colors font-medium"
          >
            Progress
          </button>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-gray-600 hover:text-red-600 transition-colors"
          >
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-full py-20"
            >
              <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl flex items-center justify-center mb-6">
                <Sparkles className="text-white" size={40} />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-3">Welcome to StudyBuddy AI</h2>
              <p className="text-gray-600 mb-8 text-center max-w-md">
                Your personal AI tutor is ready to help you learn anything. Ask a question to get started!
              </p>

              {/* Suggested Questions */}
              <div className="w-full max-w-2xl">
                <p className="text-sm font-medium text-gray-700 mb-3">Try asking:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {suggestedQuestions.map((question, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      onClick={() => setInput(question)}
                      className="text-left p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-md transition-all group"
                    >
                      <p className="text-sm text-gray-700 group-hover:text-blue-600">{question}</p>
                    </motion.button>
                  ))}
                </div>
              </div>
            </motion.div>
          ) : (
            <AnimatePresence>
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Bot className="text-white" size={18} />
                    </div>
                  )}
                  <div
                    className={`max-w-2xl rounded-2xl px-5 py-4 ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                        : 'bg-white text-gray-800 shadow-sm border border-gray-100'
                    }`}
                  >
                    <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  </div>
                  {message.role === 'user' && (
                    <div className="w-8 h-8 bg-gray-700 rounded-lg flex items-center justify-center flex-shrink-0">
                      <User className="text-white" size={18} />
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          )}

          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3 justify-start"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <Bot className="text-white" size={18} />
              </div>
              <div className="bg-white text-gray-800 shadow-sm border border-gray-100 rounded-2xl px-5 py-4">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-pink-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="border-t bg-white/80 backdrop-blur-sm p-6">
        <div className="max-w-4xl mx-auto">
          {hasStudyGuide === false && (
            <div className="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between">
              <p className="text-amber-800">
                Please upload a study guide to start chatting with the AI tutor.
              </p>
              <button
                onClick={() => navigate('/study-guide')}
                className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors font-medium"
              >
                Upload Study Guide
              </button>
            </div>
          )}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={hasStudyGuide === false ? "Upload a study guide to start..." : "Ask me anything..."}
                rows={1}
                disabled={hasStudyGuide === false}
                className={`w-full px-5 py-4 pr-12 border rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none shadow-sm ${
                  hasStudyGuide === false
                    ? 'bg-gray-100 border-gray-300 text-gray-400 cursor-not-allowed'
                    : 'bg-white border-gray-200'
                }`}
                style={{ minHeight: '56px', maxHeight: '200px' }}
              />
            </div>
            <motion.button
              whileHover={{ scale: hasStudyGuide === false ? 1 : 1.05 }}
              whileTap={{ scale: hasStudyGuide === false ? 1 : 0.95 }}
              onClick={handleSend}
              disabled={!input.trim() || loading || hasStudyGuide === false}
              className="px-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-semibold"
            >
              <Send size={20} />
              <span>Send</span>
            </motion.button>
          </div>
          <p className="text-xs text-gray-500 mt-3 text-center">
            Press Enter to send, Shift + Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}
