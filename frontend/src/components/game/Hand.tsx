import type { Card as CardType } from '../../types';
import { Card, CardBack } from './Card';

interface HandProps {
  cards: CardType[];
  isPlayer: boolean;
  onCardClick?: (index: number, card: CardType) => void;
  isPlayable?: boolean;
  maxEnergy?: number;
}

export function Hand({ cards, isPlayer, onCardClick, isPlayable = false, maxEnergy = 0 }: HandProps) {
  if (isPlayer) {
    return (
      <div className="hand-area player-hand">
        {cards.map((card, index) => (
          <Card
            key={index}
            card={card}
            isPlayable={isPlayable && (card.cost || 0) <= maxEnergy}
            onClick={() => onCardClick?.(index, card)}
          />
        ))}
      </div>
    );
  }

  // Opponent hand - show card backs
  return (
    <div className="hand-area opponent-hand">
      {cards.map((_, index) => (
        <CardBack key={index} />
      ))}
    </div>
  );
}
