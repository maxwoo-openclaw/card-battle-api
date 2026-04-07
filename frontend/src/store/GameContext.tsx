import React, { createContext, useContext, useState, useCallback } from 'react';
import type { GameState, Card } from '../types';

interface GameContextType {
  gameState: GameState | null;
  sessionId: string | null;
  isMyTurn: boolean;
  selectedCard: { card: Card; index: number } | null;
  selectedMonster: { card: Card; index: number } | null;
  setGameState: (state: GameState | null) => void;
  setSessionId: (id: string | null) => void;
  setIsMyTurn: (turn: boolean) => void;
  setSelectedCard: (selection: { card: Card; index: number } | null) => void;
  setSelectedMonster: (selection: { card: Card; index: number } | null) => void;
  resetGame: () => void;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

export function GameProvider({ children }: { children: React.ReactNode }) {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isMyTurn, setIsMyTurn] = useState(false);
  const [selectedCard, setSelectedCard] = useState<{ card: Card; index: number } | null>(null);
  const [selectedMonster, setSelectedMonster] = useState<{ card: Card; index: number } | null>(null);

  const resetGame = useCallback(() => {
    setGameState(null);
    setSessionId(null);
    setIsMyTurn(false);
    setSelectedCard(null);
    setSelectedMonster(null);
  }, []);

  return (
    <GameContext.Provider
      value={{
        gameState,
        sessionId,
        isMyTurn,
        selectedCard,
        selectedMonster,
        setGameState,
        setSessionId,
        setIsMyTurn,
        setSelectedCard,
        setSelectedMonster,
        resetGame,
      }}
    >
      {children}
    </GameContext.Provider>
  );
}

export function useGame() {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
}
