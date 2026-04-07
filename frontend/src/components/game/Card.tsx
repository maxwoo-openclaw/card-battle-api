import type { Card as CardType } from '../../types';

interface CardProps {
  card: CardType;
  onClick?: () => void;
  isPlayable?: boolean;
  showStats?: boolean;
}

export function Card({ card, onClick, isPlayable, showStats = true }: CardProps) {
  const getStatsHtml = () => {
    if (card.type === 'monster' && showStats) {
      return <div className="card-stats">⚔️{card.attack} 🛡️{card.defense}</div>;
    }
    return null;
  };

  return (
    <div
      className={`card ${card.type} ${isPlayable ? 'playable' : ''}`}
      onClick={onClick}
    >
      <div className="card-name">{card.name}</div>
      <div className="card-type">{card.type}</div>
      {getStatsHtml()}
    </div>
  );
}

export function CardBack() {
  return <div className="card" style={{ background: 'linear-gradient(135deg, #2c3e50, #1a252f)', border: '2px solid #34495e' }} />;
}
