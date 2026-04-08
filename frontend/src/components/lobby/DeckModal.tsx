import { useState, useEffect } from 'react';
import type { Card, Deck } from '../../types';
import { Card as CardComponent } from '../game/Card';

interface DeckModalProps {
  isOpen: boolean;
  onClose: () => void;
  cards: Card[];
  onSave: (name: string, cardIds: number[]) => void;
  onDelete?: (deckId: number) => void;
  editingDeck?: Deck | null;
}

export function DeckModal({ isOpen, onClose, cards, onSave, onDelete, editingDeck }: DeckModalProps) {
  const [name, setName] = useState('');
  const [selectedCardIds, setSelectedCardIds] = useState<number[]>([]);

  useEffect(() => {
    if (editingDeck) {
      setName(editingDeck.name);
      setSelectedCardIds(editingDeck.cards.map((c) => c.card_id));
    } else {
      setName('');
      setSelectedCardIds([]);
    }
  }, [editingDeck, isOpen]);

  const toggleCard = (cardId: number) => {
    setSelectedCardIds((prev) => {
      if (prev.includes(cardId)) {
        return prev.filter((id) => id !== cardId);
      }
      if (prev.length < 60) {
        return [...prev, cardId];
      }
      return prev;
    });
  };

  const handleSave = () => {
    if (!name.trim()) {
      alert('Please enter a deck name');
      return;
    }
    if (selectedCardIds.length < 1) {
      alert(`Deck needs at least 1 card (currently ${selectedCardIds.length})`);
      return;
    }
    if (selectedCardIds.length > 60) {
      alert(`Deck can have at most 60 cards (currently ${selectedCardIds.length})`);
      return;
    }
    onSave(name, selectedCardIds);
    setName('');
    setSelectedCardIds([]);
    onClose();
  };

  const handleDelete = () => {
    if (editingDeck && onDelete && confirm(`Delete deck "${editingDeck.name}"?`)) {
      onDelete(editingDeck.id);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal active" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{editingDeck ? 'Edit Deck' : 'Create Deck'}</h2>
          <button className="modal-close" onClick={onClose}>
            &times;
          </button>
        </div>

        <input
          type="text"
          className="deck-name-input"
          placeholder="Deck Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <h4>Available Cards</h4>
        <div className="available-cards">
          {cards.map((card) => (
            <div
              key={card.id}
              onClick={() => toggleCard(card.id)}
              style={{ opacity: selectedCardIds.includes(card.id) ? 0.5 : 1 }}
            >
              <CardComponent card={card} />
            </div>
          ))}
        </div>

        <h4>
          Deck Preview ({selectedCardIds.length}/60)
        </h4>
        <div className="deck-preview">
          {selectedCardIds.map((id) => {
            const card = cards.find((c) => c.id === id);
            return card ? (
              <div key={id} onClick={() => toggleCard(id)}>
                <CardComponent card={card} />
              </div>
            ) : null;
          })}
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn-primary" onClick={handleSave}>
            {editingDeck ? 'Update Deck' : 'Save Deck'}
          </button>
          {editingDeck && onDelete && (
            <button className="btn-surrender" onClick={handleDelete}>
              Delete Deck
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
