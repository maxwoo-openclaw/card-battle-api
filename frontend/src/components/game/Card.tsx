import { useState } from 'react';
import type { Card as CardType } from '../../types';

interface CardProps {
  card: CardType;
  onClick?: () => void;
  isPlayable?: boolean;
  showStats?: boolean;
}

const ATTRIBUTE_ICONS: Record<string, string> = {
  Fire: '🔥',
  Water: '💧',
  Wind: '🌪️',
  Earth: '🌍',
  Light: '☀️',
  Dark: '🌑',
};

const RARITY_COLORS: Record<string, string> = {
  Common: '#9ca3af',
  Rare: '#3b82f6',
  Epic: '#a855f7',
  Legendary: '#f59e0b',
};

export function Card({ card, onClick, isPlayable, showStats = true }: CardProps) {
  const [showDetails, setShowDetails] = useState(false);

  const rarityClass = card.rarity?.toLowerCase() ?? 'common';
  const attributeIcon = card.attribute ? ATTRIBUTE_ICONS[card.attribute] ?? '✨' : null;
  const rarityColor = card.rarity ? RARITY_COLORS[card.rarity] ?? '#9ca3af' : '#9ca3af';

  return (
    <div
      className={`card ${card.type} ${isPlayable ? 'playable' : ''} card-rarity-${rarityClass}`}
      onClick={onClick}
      onMouseEnter={() => setShowDetails(true)}
      onMouseLeave={() => setShowDetails(false)}
      style={card.rarity ? { '--rarity-color': rarityColor } as React.CSSProperties : undefined}
    >
      {card.rarity && (
        <div
          className="card-rarity-badge"
          style={{ color: rarityColor, borderColor: rarityColor }}
        >
          {card.rarity}
        </div>
      )}

      {attributeIcon && (
        <div className="card-attribute">{attributeIcon}</div>
      )}

      <div className="card-name">{card.name}</div>
      <div className="card-type">{card.type}</div>

      {card.type === 'monster' && showStats && (
        <div className="card-stats">
          ⚔️{card.attack} 🛡️{card.defense}
        </div>
      )}

      {card.cost !== undefined && (
        <div className="card-cost">
          ⚡{card.cost}
        </div>
      )}

      {showDetails && (
        <div className="card-tooltip">
          <div className="card-tooltip-header">
            <span className="card-tooltip-name">{card.name}</span>
            {card.rarity && (
              <span
                className="card-tooltip-rarity"
                style={{ color: rarityColor }}
              >
                {card.rarity}
              </span>
            )}
          </div>

          <div className="card-tooltip-meta">
            <span className="card-tooltip-type">{card.type}</span>
            {attributeIcon && (
              <span className="card-tooltip-attribute">
                {attributeIcon} {card.attribute}
              </span>
            )}
            {card.cost !== undefined && (
              <span className="card-tooltip-cost">
                ⚡ Cost: {card.cost}
              </span>
            )}
          </div>

          {card.type === 'monster' && showStats && (
            <div className="card-tooltip-stats">
              ⚔️ ATK: {card.attack} | 🛡️ DEF: {card.defense}
            </div>
          )}

          {card.description && (
            <div className="card-tooltip-description">
              {card.description}
            </div>
          )}

          {card.passive_ability && (
            <div className="card-tooltip-ability card-tooltip-passive">
              <span className="ability-label">🔗 Passive:</span>
              <span className="ability-text">{card.passive_ability}</span>
            </div>
          )}

          {card.active_ability && (
            <div className="card-tooltip-ability card-tooltip-active">
              <span className="ability-label">⚡ Active:</span>
              <span className="ability-text">{card.active_ability}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function CardBack() {
  return (
    <div
      className="card"
      style={{ background: 'linear-gradient(135deg, #2c3e50, #1a252f)', border: '2px solid #34495e' }}
    />
  );
}
