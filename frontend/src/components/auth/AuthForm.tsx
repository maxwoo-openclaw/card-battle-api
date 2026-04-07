import React, { useState } from 'react';
import { useAuth } from '../../store/AuthContext';

interface AuthFormProps {
  onSuccess?: () => void;
}

export function AuthForm({ onSuccess }: AuthFormProps) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const { login, register, isLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (isRegistering) {
        const response = await register(username, email, password);
        setSuccess(response.message);
        // Switch to login mode after 2 seconds
        setTimeout(() => {
          setIsRegistering(false);
          setEmail('');
          setPassword('');
          setSuccess('');
        }, 2000);
      } else {
        await login(username, password);
        onSuccess?.();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const toggleMode = () => {
    setIsRegistering(!isRegistering);
    setError('');
    setSuccess('');
  };

  return (
    <div className="auth-box">
      <h2 id="auth-title">{isRegistering ? 'Register' : 'Login'}</h2>

      {error && <div className="auth-error">{error}</div>}
      {success && <div className="auth-success">{success}</div>}

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          id="username"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          id="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {isRegistering && (
          <input
            type="email"
            id="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        )}
        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? 'Loading...' : isRegistering ? 'Register' : 'Login'}
        </button>
      </form>

      <button type="button" className="btn-secondary auth-switch" onClick={toggleMode}>
        {isRegistering ? 'Have an account? Login' : 'Need an account? Register'}
      </button>
    </div>
  );
}
