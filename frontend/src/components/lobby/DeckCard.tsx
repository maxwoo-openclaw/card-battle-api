import type { Deck } from '../../types';

interface DeckCardProps {
  deck: Deck;
  isSelected: boolean;
  onClick: () => void;
  onEdit: () => void;
}

export function DeckCard({ deck, isSelected, onClick, onEdit }: DeckCardProps) {
  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit();
  };

  return (
    <div className={`deck-card ${isSelected ? 'selected' : ''}`} onClick={onClick}>
      <strong>{deck.name}</strong>
      <br />
      <small>{deck.cards ? deck.cards.length : 0} cards</small>
      <button
        className="btn-secondary"
        style={{ marginTop: '0.5rem', padding: '0.25rem 0.5rem', fontSize: '0.8rem' }}
        onClick={handleEdit}
      >
        Edit
      </button>
    </div>
  );
}
