import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../store/AuthContext';
import { useLobby } from '../store/LobbyContext';
import { StatsBox } from '../components/lobby/StatsBox';
import { DeckList } from '../components/lobby/DeckList';
import { DeckModal } from '../components/lobby/DeckModal';
import { matchmakingApi } from '../services/api';

export function LobbyPage() {
  const navigate = useNavigate();
  const { token, logout, isAuthenticated } = useAuth();
  const { decks, cards, stats, selectedDeck, loadDecks, loadCards, loadStats, createDeck, setSelectedDeck } = useLobby();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isMatchmaking, setIsMatchmaking] = useState(false);

  useEffect(() => {
    if (!isAuthenticated || !token) {
      navigate('/auth');
      return;
    }

    loadDecks(token);
    loadCards(token);
    loadStats(token);
  }, [isAuthenticated, token, navigate, loadDecks, loadCards, loadStats]);

  const handleCreateDeck = async (name: string, cardIds: number[]) => {
    if (!token) return;
    try {
      await createDeck(token, name, cardIds);
      alert('Deck saved successfully!');
    } catch (err) {
      console.error('Failed to create deck:', err);
      alert('Failed to save deck: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handleJoinMatchmaking = async () => {
    if (!selectedDeck || !token) {
      alert('Please select a deck first');
      return;
    }

    setIsMatchmaking(true);
    try {
      await matchmakingApi.join(token);
      // Poll for match or wait for redirect
      pollMatchmaking();
    } catch (err) {
      alert('Failed to join matchmaking');
      setIsMatchmaking(false);
    }
  };

  const pollMatchmaking = async () => {
    if (!token) return;

    const checkStatus = async () => {
      try {
        const status = await matchmakingApi.getStatus(token);
        if (status.session_id) {
          navigate(`/game/${status.session_id}`);
          return;
        }
        if (!isMatchmaking) return;
        setTimeout(checkStatus, 1000);
      } catch {
        setTimeout(checkStatus, 1000);
      }
    };

    checkStatus();
  };

  const handleCancelMatchmaking = async () => {
    if (!token) return;
    await matchmakingApi.leave(token);
    setIsMatchmaking(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  return (
    <div id="lobby-screen">
      <div className="lobby-header">
        <h1>Card Battle</h1>
        <div className="lobby-actions">
          <button className="btn-primary" onClick={() => setIsModalOpen(true)}>Create Deck</button>
          <button className="btn-secondary" onClick={handleJoinMatchmaking} disabled={!selectedDeck || isMatchmaking}>
            Join Matchmaking
          </button>
          <button className="btn-secondary" onClick={handleLogout}>Logout</button>
        </div>
      </div>

      <StatsBox stats={stats} />

      <h3>Your Decks</h3>
      <DeckList decks={decks} selectedDeck={selectedDeck} onSelectDeck={setSelectedDeck} />

      {isMatchmaking && (
        <div className="matchmaking-status active">
          <div className="spinner" />
          <p>Searching for opponent...</p>
          <button className="btn-surrender" onClick={handleCancelMatchmaking}>Cancel</button>
        </div>
      )}

      <DeckModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        cards={cards}
        onSave={handleCreateDeck}
      />
    </div>
  );
}
