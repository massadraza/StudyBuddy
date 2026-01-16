import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain, Sparkles, CheckCircle, XCircle, ArrowRight, LogOut, MessageSquare, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

export default function Practice() {
  const [topic, setTopic] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState<{ id: number; text: string } | null>(null);
  const [studentAnswer, setStudentAnswer] = useState('');
  const [result, setResult] = useState<{
    is_correct: boolean;
    feedback: string;
    correct_answer: string;
    topic: string;
    new_mastery_score: number;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [hasStudyGuide, setHasStudyGuide] = useState<boolean | null>(null);
  const navigate = useNavigate();

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

  const handleGenerateQuestion = async () => {
    if (!topic.trim()) return;

    setLoading(true);
    setResult(null);
    setShowResult(false);
    setStudentAnswer('');

    try {
      const response = await apiService.generatePractice({ topic });
      setCurrentQuestion({ id: response.question_id, text: response.question });
    } catch (err) {
      console.error('Failed to generate question:', err);
      alert('Failed to generate question. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!currentQuestion || !studentAnswer.trim()) return;

    setLoading(true);
    try {
      const response = await apiService.submitAnswer({
        question_id: currentQuestion.id,
        student_answer: studentAnswer,
      });
      setResult(response);
      setShowResult(true);
    } catch (err) {
      console.error('Failed to submit answer:', err);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNewQuestion = () => {
    setCurrentQuestion(null);
    setStudentAnswer('');
    setResult(null);
    setShowResult(false);
  };

  const handleLogout = () => {
    apiService.setToken('');
    navigate('/login');
  };

  if (!currentQuestion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <Brain className="text-white" size={20} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Practice Quiz</h1>
              <p className="text-sm text-gray-500">Test your knowledge</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/study-guide')}
              className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors font-medium"
            >
              <Brain size={18} />
              <span>Study Guide</span>
            </button>
            <button
              onClick={() => navigate('/chat')}
              className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors font-medium"
            >
              <MessageSquare size={18} />
              <span>Chat</span>
            </button>
            <button
              onClick={() => navigate('/progress')}
              className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors font-medium"
            >
              <TrendingUp size={18} />
              <span>Progress</span>
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

        {/* Content */}
        <div className="p-8">
          <div className="max-w-2xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-xl p-8 space-y-6"
            >
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="text-white" size={32} />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Start Practicing</h2>
                <p className="text-gray-600">Choose a topic and test your understanding with AI-generated questions</p>
              </div>

              {hasStudyGuide === false && (
                <div className="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between">
                  <p className="text-amber-800">
                    Please upload a study guide to start practicing.
                  </p>
                  <button
                    onClick={() => navigate('/study-guide')}
                    className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors font-medium"
                  >
                    Upload Study Guide
                  </button>
                </div>
              )}

              <div>
                <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-2">
                  What topic would you like to practice?
                </label>
                <input
                  id="topic"
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && hasStudyGuide !== false && handleGenerateQuestion()}
                  placeholder={hasStudyGuide === false ? "Upload a study guide to start..." : "e.g., Python, Calculus, World History"}
                  disabled={hasStudyGuide === false}
                  className={`w-full px-5 py-4 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm ${
                    hasStudyGuide === false
                      ? 'bg-gray-100 border-gray-300 text-gray-400 cursor-not-allowed'
                      : 'border-gray-200'
                  }`}
                />
              </div>

              <motion.button
                whileHover={{ scale: hasStudyGuide === false ? 1 : 1.02 }}
                whileTap={{ scale: hasStudyGuide === false ? 1 : 0.98 }}
                onClick={handleGenerateQuestion}
                disabled={!topic.trim() || loading || hasStudyGuide === false}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Generating Question...</span>
                  </>
                ) : (
                  <>
                    <span>Generate Practice Question</span>
                    <ArrowRight size={20} />
                  </>
                )}
              </motion.button>

              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex gap-3">
                  <Sparkles className="text-blue-600 flex-shrink-0" size={20} />
                  <div>
                    <p className="font-semibold text-blue-900 mb-1">How it works:</p>
                    <p className="text-sm text-blue-800">
                      AI will generate an open-ended question about your chosen topic. Answer in your own words to test your understanding and get personalized feedback!
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
            <Brain className="text-white" size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Practice Quiz</h1>
            <p className="text-sm text-gray-500">Test your knowledge</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={handleNewQuestion}
            className="px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition"
          >
            New Question
          </button>
          <button
            onClick={() => navigate('/chat')}
            className="text-gray-600 hover:text-blue-600 transition-colors font-medium"
          >
            Chat
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
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-xl p-8 space-y-6"
          >
            {/* Question */}
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
              <h2 className="text-sm font-semibold text-blue-600 mb-3 uppercase tracking-wide">Question</h2>
              <p className="text-gray-900 text-lg font-medium leading-relaxed">{currentQuestion.text}</p>
            </div>

            {!showResult ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-4"
              >
                <div>
                  <label htmlFor="answer" className="block text-sm font-medium text-gray-700 mb-2">
                    Your Answer:
                  </label>
                  <textarea
                    id="answer"
                    value={studentAnswer}
                    onChange={(e) => setStudentAnswer(e.target.value)}
                    placeholder="Type your answer here... Explain in your own words."
                    rows={8}
                    className="w-full px-5 py-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none shadow-sm"
                  />
                </div>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSubmitAnswer}
                  disabled={!studentAnswer.trim() || loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Evaluating...</span>
                    </>
                  ) : (
                    <>
                      <span>Submit Answer</span>
                      <ArrowRight size={20} />
                    </>
                  )}
                </motion.button>
              </motion.div>
            ) : (
              result && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-6"
                >
                  {/* Result Card */}
                  <div
                    className={`p-6 rounded-xl border-2 ${
                      result.is_correct
                        ? 'bg-green-50 border-green-500'
                        : 'bg-red-50 border-red-500'
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-4">
                      {result.is_correct ? (
                        <CheckCircle className="text-green-600" size={32} />
                      ) : (
                        <XCircle className="text-red-600" size={32} />
                      )}
                      <h3 className="text-2xl font-bold text-gray-900">
                        {result.is_correct ? 'Excellent Work!' : 'Keep Learning!'}
                      </h3>
                    </div>
                    <p className="text-gray-700 mb-4 text-lg">{result.feedback}</p>
                    {!result.is_correct && (
                      <div className="bg-white/60 p-4 rounded-lg">
                        <p className="font-semibold text-sm text-gray-600 mb-2">Correct Answer:</p>
                        <p className="text-gray-800 leading-relaxed">{result.correct_answer}</p>
                      </div>
                    )}
                  </div>

                  {/* Your Answer */}
                  <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-600 mb-3 uppercase tracking-wide">Your Answer</h3>
                    <p className="text-gray-700 leading-relaxed">{studentAnswer}</p>
                  </div>

                  {/* Stats */}
                  <div className="bg-gradient-to-br from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-100">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Topic</p>
                        <p className="font-bold text-gray-900">{result.topic}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Mastery Score</p>
                        <p className="font-bold text-2xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                          {Math.round(result.new_mastery_score * 100)}%
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Action Button */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleNewQuestion}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-xl hover:shadow-lg transition-all font-semibold flex items-center justify-center gap-2"
                  >
                    <span>Try Another Question</span>
                    <ArrowRight size={20} />
                  </motion.button>
                </motion.div>
              )
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}