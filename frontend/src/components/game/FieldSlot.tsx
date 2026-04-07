import type { Card as CardType } from '../../types';
import { Card } from './Card';

interface FieldSlotProps {
  card: CardType | null;
  slotType: 'monster' | 'spell';
  index: number;
  owner: 'player' | 'opponent';
  isSelected?: boolean;
  isTarget?: boolean;
  onCardClick?: (index: number, card: CardType) => void;
  onSlotClick?: (index: number) => void;
}

export function FieldSlot({
  card,
  slotType,
  index,
  owner,
  isSelected,
  isTarget,
  onCardClick,
  onSlotClick,
}: FieldSlotProps) {
  const slotKey = `${owner}-${slotType}-${index}`;

  return (
    <div
      className={`field-slot ${card ? 'occupied' : ''} ${isSelected ? 'selected' : ''} ${isTarget ? 'target' : ''}`}
      data-slot={slotKey}
      onClick={() => onSlotClick?.(index)}
    >
      {card && (
        <Card
          card={card}
          onClick={() => onCardClick?.(index, card)}
        />
      )}
    </div>
  );
}
