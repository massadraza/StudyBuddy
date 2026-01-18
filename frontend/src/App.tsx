import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Chat from './pages/Chat';
import Practice from './pages/Practice';
import Progress from './pages/Progress';
import StudyGuide from './pages/StudyGuide';
import Settings from './pages/Settings';
import Navigation from './components/layout/Navigation';
import ProtectedRoute from './components/auth/ProtectedRoute';

/* Public Routes: No authentication required */
/* Protected Routes: Authentication required */

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes */}
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <>
                <Navigation />
                <Chat />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/practice"
          element={
            <ProtectedRoute>
              <>
                <Navigation />
                <Practice />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/progress"
          element={
            <ProtectedRoute>
              <>
                <Navigation />
                <Progress />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/study-guide"
          element={
            <ProtectedRoute>
              <>
                <Navigation />
                <StudyGuide />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <>
                <Navigation />
                <Settings />
              </>
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/study-guide" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;