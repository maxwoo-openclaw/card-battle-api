import { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../store/AuthContext';
import { useGame } from '../store/GameContext';
import { useWebSocket } from '../hooks/useWebSocket';
import { TopBar } from '../components/game/TopBar';
import { BottomBar } from '../components/game/BottomBar';
import { Hand } from '../components/game/Hand';
import { FieldSlot } from '../components/game/FieldSlot';
import { GameLog } from '../components/game/GameLog';
import { GameOverOverlay } from '../components/game/GameOverOverlay';
import type { GameMessage, Card } from '../types';

export function GamePage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { token, isAuthenticated } = useAuth();
  const { gameState, setGameState, setIsMyTurn, selectedCard, setSelectedCard, selectedMonster, setSelectedMonster } = useGame();

  const [gameLogs, setGameLogs] = useState<string[]>([]);
  const [gameOverResult, setGameOverResult] = useState<'win' | 'lose' | null>(null);
  const [highlightedSlots, setHighlightedSlots] = useState<string[]>([]);

  useEffect(() => {
    if (!isAuthenticated || !token) {
      navigate('/auth');
    }
  }, [isAuthenticated, token, navigate]);

  const addLog = useCallback((entry: string) => {
    setGameLogs((prev) => [entry, ...prev]);
  }, []);

  const handleMessage = useCallback((message: unknown) => {
    const msg = message as GameMessage;
    console.log('Game message:', msg);

    switch (msg.type) {
      case 'game_start':
      case 'state_update':
        if (msg.state) {
          setGameState(msg.state);
          setIsMyTurn(msg.state.current_turn === 'player');
        }
        break;
      case 'turn_change':
        setIsMyTurn(msg.turn === 'player');
        addLog(msg.turn === 'player' ? 'Your turn!' : "Opponent's turn");
        break;
      case 'card_played':
        if (msg.player && msg.card_name) {
          addLog(`${msg.player} played ${msg.card_name}`);
        }
        break;
      case 'attack_result':
        if (msg.attacker && msg.target && msg.damage) {
          addLog(`${msg.attacker} attacked ${msg.target} for ${msg.damage} damage`);
        }
        break;
      case 'game_over':
        setGameOverResult(msg.result === 'win' ? 'win' : 'lose');
        if (msg.result === 'win') {
          addLog('You won!');
        } else {
          addLog('You lost.');
        }
        break;
    }
  }, [setGameState, setIsMyTurn, addLog]);

  const { send } = useWebSocket({
    sessionId: sessionId || '',
    token: token || '',
    onMessage: handleMessage,
    onConnect: () => addLog('Connected to game'),
    onDisconnect: () => addLog('Disconnected from game'),
  });

  const handleCardClick = useCallback((index: number, card: Card) => {
    if (!gameState) return;

    // Clear selections
    setSelectedMonster(null);
    setHighlightedSlots([]);

    if (card.type === 'monster') {
      setSelectedCard({ card, index });
      // Highlight empty monster slots
      const slots: string[] = [];
      gameState.your_state.field_monsters.forEach((_, i) => {
        if (!gameState.your_state.field_monsters[i]) {
          slots.push(`player-monster-${i}`);
        }
      });
      setHighlightedSlots(slots);
    } else {
      setSelectedCard({ card, index });
      // Highlight empty spell slots
      const slots: string[] = [];
      gameState.your_state.field_spells.forEach((_, i) => {
        if (!gameState.your_state.field_spells[i]) {
          slots.push(`player-spell-${i}`);
        }
      });
      setHighlightedSlots(slots);
    }
  }, [gameState, setSelectedCard, setSelectedMonster]);

  const handleSlotClick = useCallback((index: number) => {
    if (selectedCard) {
      const slotType = selectedCard.card.type === 'monster' ? 'monster' : 'spell';
      send({
        type: 'play_card',
        card_index: selectedCard.index,
        slot_index: index,
        slot_type: slotType,
      });
      setSelectedCard(null);
      setHighlightedSlots([]);
    } else if (selectedMonster) {
      send({
        type: 'attack',
        attacker_index: selectedMonster.index,
        target_index: index,
      });
      setSelectedMonster(null);
      setHighlightedSlots([]);
    }
  }, [selectedCard, selectedMonster, send, setSelectedCard, setSelectedMonster]);

  const handleEndTurn = useCallback(() => {
    send({ type: 'end_turn' });
  }, [send]);

  const handleSurrender = useCallback(() => {
    if (confirm('Are you sure you want to surrender?')) {
      send({ type: 'surrender' });
    }
  }, [send]);

  const handleBackToLobby = useCallback(() => {
    navigate('/lobby');
  }, [navigate]);

  const isMyTurn = gameState?.current_turn === 'player';

  if (!gameState) {
    return (
      <div id="game-screen">
        <div className="matchmaking-status active">
          <div className="spinner" />
          <p>Loading game...</p>
        </div>
      </div>
    );
  }

  return (
    <div id="game-screen">
      <TopBar
        opponentName="Opponent"
        opponentHp={gameState.opponent_state.hp}
        maxHp={gameState.opponent_state.max_hp}
        energy={gameState.opponent_state.energy}
        maxEnergy={gameState.opponent_state.max_energy}
        isMyTurn={isMyTurn}
      />

      <div className="field-area">
        <div className="opponent-area">
          <Hand cards={gameState.opponent_state.hand} isPlayer={false} />
          <div className="field-row">
            {[0, 1, 2, 3, 4].map((i) => (
              <FieldSlot
                key={`opp-monster-${i}`}
                card={gameState.opponent_state.field_monsters[i]}
                slotType="monster"
                index={i}
                owner="opponent"
              />
            ))}
          </div>
          <div className="field-row">
            {[0, 1, 2, 3, 4].map((i) => (
              <FieldSlot
                key={`opp-spell-${i}`}
                card={gameState.opponent_state.field_spells[i]}
                slotType="spell"
                index={i}
                owner="opponent"
              />
            ))}
          </div>
        </div>

        <div className="divider" />

        <div className="player-area">
          <div className="field-row">
            {[0, 1, 2, 3, 4].map((i) => (
              <FieldSlot
                key={`player-monster-${i}`}
                card={gameState.your_state.field_monsters[i]}
                slotType="monster"
                index={i}
                owner="player"
                isTarget={highlightedSlots.includes(`player-monster-${i}`)}
                onSlotClick={handleSlotClick}
              />
            ))}
          </div>
          <div className="field-row">
            {[0, 1, 2, 3, 4].map((i) => (
              <FieldSlot
                key={`player-spell-${i}`}
                card={gameState.your_state.field_spells[i]}
                slotType="spell"
                index={i}
                owner="player"
                isTarget={highlightedSlots.includes(`player-spell-${i}`)}
                onSlotClick={handleSlotClick}
              />
            ))}
          </div>
          <Hand
            cards={gameState.your_state.hand}
            isPlayer={true}
            isPlayable={isMyTurn}
            maxEnergy={gameState.your_state.energy}
            onCardClick={handleCardClick}
          />
        </div>
      </div>

      <BottomBar
        playerName="You"
        playerHp={gameState.your_state.hp}
        maxHp={gameState.your_state.max_hp}
        energy={gameState.your_state.energy}
        maxEnergy={gameState.your_state.max_energy}
        onEndTurn={handleEndTurn}
        onSurrender={handleSurrender}
      />

      <GameLog entries={gameLogs} />

      <GameOverOverlay
        isVisible={!!gameOverResult}
        result={gameOverResult}
        onBackToLobby={handleBackToLobby}
      />
    </div>
  );
}
