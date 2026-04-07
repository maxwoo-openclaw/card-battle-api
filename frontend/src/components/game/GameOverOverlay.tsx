interface GameOverOverlayProps {
  isVisible: boolean;
  result: 'win' | 'lose' | null;
  onBackToLobby: () => void;
}

export function GameOverOverlay({ isVisible, result, onBackToLobby }: GameOverOverlayProps) {
  if (!isVisible) return null;

  return (
    <div className={`game-over-overlay active ${result === 'win' ? 'victory' : 'defeat'}`}>
      <h1>{result === 'win' ? 'Victory!' : 'Defeat'}</h1>
      <button onClick={onBackToLobby}>Back to Lobby</button>
    </div>
  );
}
