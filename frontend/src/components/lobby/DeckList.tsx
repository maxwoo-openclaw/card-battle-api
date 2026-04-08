import type { Deck } from '../../types';
import { DeckCard } from './DeckCard';

interface DeckListProps {
  decks: Deck[];
  selectedDeck: Deck | null;
  onSelectDeck: (deck: Deck) => void;
  onEditDeck: (deck: Deck) => void;
}

export function DeckList({ decks, selectedDeck, onSelectDeck, onEditDeck }: DeckListProps) {
  return (
    <div className="decks-grid">
      {decks.length === 0 ? (
        <p>No decks yet. Create one!</p>
      ) : (
        decks.map((deck) => (
          <DeckCard
            key={deck.id}
            deck={deck}
            isSelected={selectedDeck?.id === deck.id}
            onClick={() => onSelectDeck(deck)}
            onEdit={() => onEditDeck(deck)}
          />
        ))
      )}
    </div>
  );
}
