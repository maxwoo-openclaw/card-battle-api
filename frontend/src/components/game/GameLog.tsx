import { useEffect, useRef } from 'react';

interface GameLogProps {
  entries: string[];
}

export function GameLog({ entries }: GameLogProps) {
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = 0;
    }
  }, [entries]);

  return (
    <div className="game-log" id="game-log" ref={logRef}>
      {entries.map((entry, index) => (
        <div key={index} className="log-entry">
          {entry}
        </div>
      ))}
    </div>
  );
}
