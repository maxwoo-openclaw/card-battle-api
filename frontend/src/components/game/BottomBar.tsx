import { HPBar } from './HPBar';
import { EnergyDisplay } from './EnergyDisplay';
import { useNavigate } from 'react-router-dom';

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
  const navigate = useNavigate();
  return (
    <div className="bottom-bar">
      <div className="player-info">
        <span>{playerName}</span>
        <HPBar current={playerHp} max={maxHp} />
        <EnergyDisplay current={energy} max={maxEnergy} />
      </div>
      <div className="action-buttons">
        <button className="btn-rules" onClick={() => navigate('/rules')} title="Game Rules">?</button>
        <button className="btn-end-turn" onClick={onEndTurn}>End Turn</button>
        <button className="btn-surrender" onClick={onSurrender}>Surrender</button>
      </div>
    </div>
  );
}
