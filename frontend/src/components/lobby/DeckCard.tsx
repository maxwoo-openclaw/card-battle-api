import type { Deck } from '../../types';

interface DeckCardProps {
  deck: Deck;
  isSelected: boolean;
  onClick: () => void;
}

export function DeckCard({ deck, isSelected, onClick }: DeckCardProps) {
  return (
    <div className={`deck-card ${isSelected ? 'selected' : ''}`} onClick={onClick}>
      <strong>{deck.name}</strong>
      <br />
      <small>{deck.cards ? deck.cards.length : 0} cards</small>
    </div>
  );
}
