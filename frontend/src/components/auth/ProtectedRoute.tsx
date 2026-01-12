import { Navigate } from 'react-router-dom';
import { apiService } from '../../services/api';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const token = apiService.getToken();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}