import { HPBar } from './HPBar';
import { EnergyDisplay } from './EnergyDisplay';

interface TopBarProps {
  opponentName: string;
  opponentHp: number;
  maxHp: number;
  energy: number;
  maxEnergy: number;
  isMyTurn: boolean;
}

export function TopBar({ opponentName, opponentHp, maxHp, energy, maxEnergy, isMyTurn }: TopBarProps) {
  return (
    <div className="top-bar">
      <div className="opponent-info">
        <span>{opponentName}</span>
        <HPBar current={opponentHp} max={maxHp} />
      </div>
      <EnergyDisplay current={energy} max={maxEnergy} />
      <div className={`turn-indicator ${isMyTurn ? 'opponent-turn' : 'your-turn'}`}>
        {isMyTurn ? "Opponent's Turn" : 'Your Turn'}
      </div>
    </div>
  );
}
