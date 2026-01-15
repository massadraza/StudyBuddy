import { Navigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Upload, X } from 'lucide-react';
import { apiService } from '../../services/api';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const token = apiService.getToken();
  const location = useLocation();
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkStudyGuideStatus = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const status = await apiService.getStudyGuideStatus();

        // Show modal if user doesn't have a study guide and is not on study-guide page
        if (!status.has_study_guide && location.pathname !== '/study-guide') {
          setShowModal(true);
        }
      } catch (error) {
        console.error('Failed to check study guide status:', error);
      } finally {
        setLoading(false);
      }
    };

    checkStudyGuideStatus();
  }, [token, location.pathname]);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <>
      {children}

      {/* Study Guide Required Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative"
            >
              {/* Close button */}
              <button
                onClick={() => setShowModal(false)}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X size={24} />
              </button>

              {/* Icon */}
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <FileText className="text-white" size={32} />
              </div>

              {/* Content */}
              <h2 className="text-2xl font-bold text-gray-900 text-center mb-3">
                Study Guide Required
              </h2>
              <p className="text-gray-600 text-center mb-6">
                To use the chat and practice features, you need to upload a study guide first.
                This allows the AI to help you learn from your own materials.
              </p>

              {/* Features list */}
              <div className="bg-blue-50 rounded-xl p-4 mb-6">
                <p className="text-sm font-medium text-blue-900 mb-2">After uploading, you can:</p>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>Chat with AI about your study materials</li>
                  <li>Get personalized practice questions</li>
                  <li>Track your mastery progress</li>
                </ul>
              </div>

              {/* Action button */}
              <motion.a
                href="/study-guide"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center justify-center gap-2"
              >
                <Upload size={20} />
                <span>Upload Study Guide</span>
              </motion.a>

              <p className="text-xs text-gray-500 text-center mt-4">
                Only .txt files are supported
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
