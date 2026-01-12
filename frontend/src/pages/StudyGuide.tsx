import { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, CheckCircle, XCircle, Loader, Brain, LogOut, MessageSquare, Target, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

export default function StudyGuide() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const navigate = useNavigate();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'text/plain' || droppedFile.name.endsWith('.txt')) {
        setFile(droppedFile);
        setError('');
      } else {
        setError('Please upload a .txt file');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'text/plain' || selectedFile.name.endsWith('.txt')) {
        setFile(selectedFile);
        setError('');
      } else {
        setError('Please upload a .txt file');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError('');
    setSuccess(false);

    try {
      const formData = new FormData();
      formData.append('file', file);

      await apiService.uploadStudyGuide(formData);

      setUploading(false);
      setProcessing(true);

      // Simulate processing time (in reality, this would be handled by the backend)
      setTimeout(() => {
        setProcessing(false);
        setSuccess(true);
      }, 2000);
    } catch (err: any) {
      setUploading(false);
      setProcessing(false);
      setError(err.response?.data?.detail || 'Failed to upload study guide. Please try again.');
    }
  };

  const handleLogout = () => {
    apiService.setToken('');
    navigate('/login');
  };

  const resetUpload = () => {
    setFile(null);
    setSuccess(false);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
            <FileText className="text-white" size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Study Guide</h1>
            <p className="text-sm text-gray-500">Upload your materials</p>
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
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-xl p-8"
          >
            {!success ? (
              <>
                <div className="text-center mb-8">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Upload className="text-white" size={32} />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Study Guide</h2>
                  <p className="text-gray-600">Upload a .txt file containing your study materials</p>
                </div>

                {/* Upload Area */}
                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
                    dragActive
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="file"
                    id="file-upload"
                    accept=".txt,text/plain"
                    onChange={handleFileChange}
                    className="hidden"
                  />

                  {!file ? (
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <div className="flex flex-col items-center">
                        <FileText className="text-gray-400 mb-4" size={48} />
                        <p className="text-gray-700 font-medium mb-2">
                          Drop your study guide here, or click to browse
                        </p>
                        <p className="text-sm text-gray-500">Only .txt files are supported</p>
                      </div>
                    </label>
                  ) : (
                    <div className="flex flex-col items-center">
                      <FileText className="text-blue-600 mb-4" size={48} />
                      <p className="text-gray-900 font-semibold mb-1">{file.name}</p>
                      <p className="text-sm text-gray-500 mb-4">
                        {(file.size / 1024).toFixed(2)} KB
                      </p>
                      <button
                        onClick={resetUpload}
                        className="text-sm text-red-600 hover:text-red-700 font-medium"
                      >
                        Remove file
                      </button>
                    </div>
                  )}
                </div>

                {/* Error Message */}
                {error && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm flex items-center gap-2"
                  >
                    <XCircle size={20} />
                    <span>{error}</span>
                  </motion.div>
                )}

                {/* Upload Button */}
                {file && !uploading && !processing && (
                  <motion.button
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleUpload}
                    className="w-full mt-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center justify-center gap-2"
                  >
                    <Upload size={20} />
                    <span>Upload and Process</span>
                  </motion.button>
                )}

                {/* Processing States */}
                {uploading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-6 p-6 bg-blue-50 border border-blue-200 rounded-xl"
                  >
                    <div className="flex items-center gap-3">
                      <Loader className="text-blue-600 animate-spin" size={24} />
                      <div>
                        <p className="font-semibold text-blue-900">Uploading...</p>
                        <p className="text-sm text-blue-700">Sending your study guide to the server</p>
                      </div>
                    </div>
                  </motion.div>
                )}

                {processing && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-6 p-6 bg-purple-50 border border-purple-200 rounded-xl"
                  >
                    <div className="flex items-center gap-3">
                      <Brain className="text-purple-600 animate-pulse" size={24} />
                      <div>
                        <p className="font-semibold text-purple-900">Processing & Vectorizing...</p>
                        <p className="text-sm text-purple-700">Creating AI-ready embeddings from your study guide</p>
                      </div>
                    </div>
                    <div className="mt-4 w-full bg-purple-200 rounded-full h-2">
                      <div className="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full animate-pulse" style={{ width: '70%' }}></div>
                    </div>
                  </motion.div>
                )}

                {/* Info Card */}
                <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <div className="flex gap-3">
                    <FileText className="text-blue-600 flex-shrink-0" size={20} />
                    <div>
                      <p className="font-semibold text-blue-900 mb-1">What happens next?</p>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>• Your study guide will be uploaded securely</li>
                        <li>• AI will process and vectorize the content</li>
                        <li>• You can then chat with your study guide and practice questions</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-8"
              >
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle className="text-green-600" size={48} />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-3">Study Guide Uploaded!</h2>
                <p className="text-gray-600 mb-8">
                  Your study guide has been successfully processed and vectorized. You can now chat with it or practice questions.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => navigate('/chat')}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center justify-center gap-2"
                  >
                    <MessageSquare size={20} />
                    <span>Start Chatting</span>
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => navigate('/practice')}
                    className="bg-white border-2 border-blue-600 text-blue-600 py-4 rounded-xl font-semibold hover:bg-blue-50 transition-all flex items-center justify-center gap-2"
                  >
                    <Target size={20} />
                    <span>Practice Questions</span>
                  </motion.button>
                </div>

                <button
                  onClick={resetUpload}
                  className="mt-6 text-sm text-gray-600 hover:text-gray-800"
                >
                  Upload another study guide
                </button>
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}