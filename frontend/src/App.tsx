import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './store/AuthContext';
import { GameProvider } from './store/GameContext';
import { LobbyProvider } from './store/LobbyContext';
import { AuthPage } from './pages/Auth';
import { LobbyPage } from './pages/Lobby';
import { GamePage } from './pages/Game';
import './index.css';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/auth" />;
}

function App() {
  return (
    <AuthProvider>
      <LobbyProvider>
        <GameProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/auth" element={<AuthPage />} />
              <Route
                path="/lobby"
                element={
                  <ProtectedRoute>
                    <LobbyPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/game/:sessionId"
                element={
                  <ProtectedRoute>
                    <GamePage />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<Navigate to="/auth" />} />
            </Routes>
          </BrowserRouter>
        </GameProvider>
      </LobbyProvider>
    </AuthProvider>
  );
}

export default App;
