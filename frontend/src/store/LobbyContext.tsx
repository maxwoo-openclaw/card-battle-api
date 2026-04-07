import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { deckApi, cardApi, userApi } from '../services/api';
import type { Deck, Card, UserStats } from '../types';

interface LobbyContextType {
  decks: Deck[];
  cards: Card[];
  stats: UserStats | null;
  selectedDeck: Deck | null;
  isLoading: boolean;
  loadDecks: (token: string) => Promise<void>;
  loadCards: (token: string) => Promise<void>;
  loadStats: (token: string) => Promise<void>;
  createDeck: (token: string, name: string, cardIds: number[]) => Promise<Deck>;
  setSelectedDeck: (deck: Deck | null) => void;
}

const LobbyContext = createContext<LobbyContextType | undefined>(undefined);

export function LobbyProvider({ children }: { children: React.ReactNode }) {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [cards, setCards] = useState<Card[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [selectedDeck, setSelectedDeck] = useState<Deck | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const loadDecks = useCallback(async (token: string) => {
    setIsLoading(true);
    try {
      const data = await deckApi.getAll(token);
      setDecks(data);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadCards = useCallback(async (token: string) => {
    const data = await cardApi.getAll(token);
    setCards(data);
  }, []);

  const loadStats = useCallback(async (token: string) => {
    const data = await userApi.getStats(token);
    setStats(data);
  }, []);

  const createDeck = useCallback(async (token: string, name: string, cardIds: number[]) => {
    const deck = await deckApi.create(token, name, cardIds);
    setDecks((prev) => [...prev, deck]);
    return deck;
  }, []);

  return (
    <LobbyContext.Provider
      value={{
        decks,
        cards,
        stats,
        selectedDeck,
        isLoading,
        loadDecks,
        loadCards,
        loadStats,
        createDeck,
        setSelectedDeck,
      }}
    >
      {children}
    </LobbyContext.Provider>
  );
}

export function useLobby() {
  const context = useContext(LobbyContext);
  if (context === undefined) {
    throw new Error('useLobby must be used within a LobbyProvider');
  }
  return context;
}
