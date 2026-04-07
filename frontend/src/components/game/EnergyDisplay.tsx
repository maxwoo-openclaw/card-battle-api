interface EnergyDisplayProps {
  current: number;
  max: number;
}

export function EnergyDisplay({ current, max }: EnergyDisplayProps) {
  return (
    <div className="energy-display">
      ⚡ {current}/{max}
    </div>
  );
}
