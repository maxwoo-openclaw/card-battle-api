import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthForm } from '../components/auth/AuthForm';
import { useAuth } from '../store/AuthContext';

export function AuthPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/lobby');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div id="auth-screen">
      <AuthForm onSuccess={() => navigate('/lobby')} />
    </div>
  );
}
