import type { UserStats } from '../../types';

interface StatsBoxProps {
  stats: UserStats | null;
}

export function StatsBox({ stats }: StatsBoxProps) {
  return (
    <div className="stats-box">
      <h3>Your Stats</h3>
      <p>
        {stats
          ? `Wins: ${stats.wins} | Losses: ${stats.losses} | Draws: ${stats.draws} | Rating: ${stats.rating}`
          : 'Loading...'}
      </p>
    </div>
  );
}
