interface HPBarProps {
  current: number;
  max: number;
  showText?: boolean;
}

export function HPBar({ current, max, showText = true }: HPBarProps) {
  const percentage = (current / max) * 100;

  return (
    <div className="hp-bar-container">
      {showText && <div className="hp-bar-label">HP: {current}</div>}
      <div className="hp-bar">
        <div className="hp-bar-fill" style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}
