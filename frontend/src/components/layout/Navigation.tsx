import { Link, useNavigate, useLocation } from 'react-router-dom';
import { apiService } from '../../services/api';

export default function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    apiService.removeToken();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link to="/chat" className="text-xl font-bold text-indigo-600">
              StudyBuddy
            </Link>

            <div className="flex space-x-4">
              <Link
                to="/chat"
                className={`px-3 py-2 rounded-lg font-medium transition ${
                  isActive('/chat')
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Chat
              </Link>

              <Link
                to="/practice"
                className={`px-3 py-2 rounded-lg font-medium transition ${
                  isActive('/practice')
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Practice
              </Link>

              <Link
                to="/progress"
                className={`px-3 py-2 rounded-lg font-medium transition ${
                  isActive('/progress')
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Progress
              </Link>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}