import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain, TrendingUp, Award, BarChart3, RefreshCw, LogOut, MessageSquare, Target } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import type { ProgressResponse } from '../types';

export default function Progress() {
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getProgress();
      console.log('Progress data:', data);
      setProgress(data);
    } catch (err: any) {
      console.error('Failed to load progress:', err);
      setError(err?.response?.data?.detail || err?.message || 'Failed to load progress');
    } finally {
      setLoading(false);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 font-medium">Loading your progress...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md text-center">
          <p className="text-red-600 font-medium mb-4">Error: {error}</p>
          <button
            onClick={loadProgress}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!progress || progress.mastery_scores.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <BarChart3 className="text-white" size={20} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Your Progress</h1>
              <p className="text-sm text-gray-500">Track your learning journey</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/chat')}
              className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors font-medium"
            >
              <MessageSquare size={18} />
              <span>Chat</span>
            </button>
            <button
              onClick={() => navigate('/practice')}
              className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors font-medium"
            >
              <Target size={18} />
              <span>Practice</span>
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

        {/* Empty State */}
        <div className="p-8">
          <div className="max-w-2xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-xl p-12 text-center"
            >
              <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <BarChart3 className="text-blue-600" size={48} />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">No Progress Yet</h2>
              <p className="text-gray-600 mb-8">Start practicing to track your learning journey and see your mastery scores grow!</p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/practice')}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-xl font-semibold hover:shadow-lg transition-all"
              >
                Start Practicing
              </motion.button>
            </motion.div>
          </div>
        </div>
      </div>
    );
  }

  // Calculate overall stats
  const averageScore = progress.mastery_scores.length > 0
    ? progress.mastery_scores.reduce((sum, topic) => sum + topic.score, 0) / progress.mastery_scores.length
    : 0;

  const topicsCount = progress.mastery_scores.length;
  const expertTopics = progress.mastery_scores.filter(t => t.score >= 0.8).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
            <BarChart3 className="text-white" size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Your Progress</h1>
            <p className="text-sm text-gray-500">Track your learning journey</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/study-guide')}
            className="text-gray-600 hover:text-blue-600 transition-colors font-medium"
          >
            Study Guide
          </button>
          <button
            onClick={() => navigate('/chat')}
            className="text-gray-600 hover:text-blue-600 transition-colors font-medium"
          >
            Chat
          </button>
          <button
            onClick={() => navigate('/practice')}
            className="text-gray-600 hover:text-blue-600 transition-colors font-medium"
          >
            Practice
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
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                  <TrendingUp className="text-blue-600" size={24} />
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 mb-1">Average Mastery</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {Math.round(averageScore * 100)}%
                  </p>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${Math.round(averageScore * 100)}%` }}
                />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <div className="flex items-center justify-between">
                <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                  <Brain className="text-purple-600" size={24} />
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 mb-1">Topics Practiced</p>
                  <p className="text-3xl font-bold text-gray-900">{topicsCount}</p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <div className="flex items-center justify-between">
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                  <Award className="text-green-600" size={24} />
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 mb-1">Expert Topics</p>
                  <p className="text-3xl font-bold text-gray-900">{expertTopics}</p>
                  <p className="text-xs text-gray-500">80%+ mastery</p>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Topic Progress */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-2xl shadow-xl p-8"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Topic Breakdown</h2>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={loadProgress}
                className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-xl hover:bg-blue-100 transition-colors font-medium"
              >
                <RefreshCw size={16} />
                <span>Refresh</span>
              </motion.button>
            </div>

            <div className="space-y-6">
              {progress.mastery_scores.map((topic, idx) => {
                const masteryPercentage = Math.round(topic.score * 100);
                const masteryColor =
                  masteryPercentage >= 80 ? 'text-green-600' :
                  masteryPercentage >= 60 ? 'text-blue-600' :
                  masteryPercentage >= 40 ? 'text-yellow-600' :
                  'text-red-600';

                const progressBarColor =
                  masteryPercentage >= 80 ? 'from-green-500 to-green-600' :
                  masteryPercentage >= 60 ? 'from-blue-500 to-blue-600' :
                  masteryPercentage >= 40 ? 'from-yellow-500 to-yellow-600' :
                  'from-red-500 to-red-600';

                const bgColor =
                  masteryPercentage >= 80 ? 'bg-green-50' :
                  masteryPercentage >= 60 ? 'bg-blue-50' :
                  masteryPercentage >= 40 ? 'bg-yellow-50' :
                  'bg-red-50';

                return (
                  <motion.div
                    key={`${topic.topic}-${idx}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + idx * 0.1 }}
                    className={`${bgColor} border-l-4 ${masteryColor.replace('text-', 'border-')} rounded-xl p-6`}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-bold text-lg text-gray-900 capitalize">{topic.topic}</h3>
                        <p className="text-sm text-gray-600 mt-1">Keep practicing to improve!</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-600 mb-1">Mastery Level</p>
                        <p className={`text-2xl font-bold ${masteryColor}`}>{masteryPercentage}%</p>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${masteryPercentage}%` }}
                        transition={{ duration: 1, delay: 0.6 + idx * 0.1 }}
                        className={`bg-gradient-to-r ${progressBarColor} h-4 rounded-full flex items-center justify-end pr-2`}
                      >
                        {masteryPercentage >= 15 && (
                          <span className="text-xs font-bold text-white">{masteryPercentage}%</span>
                        )}
                      </motion.div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>

          {/* Info Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-blue-50 border border-blue-200 rounded-xl p-6"
          >
            <div className="flex gap-3">
              <Award className="text-blue-600 flex-shrink-0" size={24} />
              <div>
                <p className="font-semibold text-blue-900 mb-2">How Mastery Works</p>
                <p className="text-sm text-blue-800">
                  Your mastery score increases when you answer questions correctly and decreases when you answer incorrectly. Scores of 80% or higher indicate expert-level understanding. Keep practicing to improve your scores!
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
