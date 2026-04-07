import { HPBar } from './HPBar';
import { EnergyDisplay } from './EnergyDisplay';

interface BottomBarProps {
  playerName: string;
  playerHp: number;
  maxHp: number;
  energy: number;
  maxEnergy: number;
  onEndTurn: () => void;
  onSurrender: () => void;
}

export function BottomBar({ playerName, playerHp, maxHp, energy, maxEnergy, onEndTurn, onSurrender }: BottomBarProps) {
  return (
    <div className="bottom-bar">
      <div className="player-info">
        <span>{playerName}</span>
        <HPBar current={playerHp} max={maxHp} />
        <EnergyDisplay current={energy} max={maxEnergy} />
      </div>
      <div className="action-buttons">
        <button className="btn-end-turn" onClick={onEndTurn}>End Turn</button>
        <button className="btn-surrender" onClick={onSurrender}>Surrender</button>
      </div>
    </div>
  );
}
