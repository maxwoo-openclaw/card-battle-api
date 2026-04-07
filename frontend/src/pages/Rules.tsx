import { useNavigate } from 'react-router-dom';

export function RulesPage() {
  const navigate = useNavigate();

  return (
    <div id="rules-screen">
      <div className="rules-container">
        <div className="rules-header">
          <h1>📜 Game Rules</h1>
          <button className="btn-secondary" onClick={() => navigate('/lobby')}>
            ← Back to Lobby
          </button>
        </div>

        <div className="rules-content">
          <section className="rules-section">
            <h2>🎯 Objective</h2>
            <p>Reduce your opponent's HP to 0 before they do the same to you. Each player starts with 100 HP.</p>
          </section>

          <section className="rules-section">
            <h2>🃏 Card Types</h2>
            <ul>
              <li><strong>Monster</strong> — Place on the field to attack or defend. They have ATK/DEF stats.</li>
              <li><strong>Spell</strong> — Instant effects like dealing damage or healing. Discarded after use.</li>
              <li><strong>Trap</strong> — Hidden cards that trigger automatically when opponent takes action.</li>
            </ul>
          </section>

          <section className="rules-section">
            <h2>⚡ Energy System</h2>
            <p>Playing cards costs energy. You start each turn with 1 more max energy (max 10). Energy refills at the start of your turn.</p>
            <ul>
              <li>Turn 1: 1 energy</li>
              <li>Turn 2: 2 energy</li>
              <li>Turn 10+: 10 energy (max)</li>
            </ul>
          </section>

          <section className="rules-section">
            <h2>🔄 Turn Structure</h2>
            <ol>
              <li><strong>Draw Phase</strong> — Draw 1 card from your deck.</li>
              <li><strong>Main Phase</strong> — Play monsters or spells to your field. Use active abilities.</li>
              <li><strong>Battle Phase</strong> — Your monsters can attack opponent's monsters or directly attack the opponent.</li>
              <li><strong>End Phase</strong> — Click "End Turn" to pass to opponent.</li>
            </ol>
          </section>

          <section className="rules-section">
            <h2>⚔️ Combat</h2>
            <p>When a monster attacks another monster: the ATK of each monster deals damage to the other's HP. Monsters with higher ATK survive.</p>
            <p>When a monster attacks the opponent directly: deal damage equal to the monster's ATK.</p>
          </section>

          <section className="rules-section">
            <h2>💎 Rarity</h2>
            <ul>
              <li><span className="rarity-common">● Common</span> — Standard cards</li>
              <li><span className="rarity-rare">● Rare</span> — Stronger than common</li>
              <li><span className="rarity-epic">● Epic</span> — Powerful effects</li>
              <li><span className="rarity-legendary">● Legendary</span> — Ultimate cards, limited to 1 per deck</li>
            </ul>
          </section>

          <section className="rules-section">
            <h2>🔥🌊🌪️🌍☀️🌑 Attributes</h2>
            <p>Each monster has an attribute. Some abilities have bonuses against certain attributes:</p>
            <ul>
              <li><strong>Fire</strong> 🔥 — Strong vs Wind</li>
              <li><strong>Water</strong> 💧 — Strong vs Fire</li>
              <li><strong>Wind</strong> 🌪️ — Strong vs Earth</li>
              <li><strong>Earth</strong> 🌍 — Strong vs Lightning</li>
              <li><strong>Light</strong> ☀️ — Strong vs Dark</li>
              <li><strong>Dark</strong> 🌑 — Strong vs Light</li>
            </ul>
          </section>

          <section className="rules-section">
            <h2>✨ Abilities</h2>
            <ul>
              <li><strong>Passive Ability</strong> — Always active. Triggers automatically (e.g., heal at turn start).</li>
              <li><strong>Active Ability</strong> — Use during Main Phase if you have enough energy (shown on card).</li>
            </ul>
          </section>

          <section className="rules-section">
            <h2>🏆 Winning & Losing</h2>
            <ul>
              <li><strong>Win</strong> — Reduce opponent HP to 0</li>
              <li><strong>Lose</strong> — Your HP reaches 0</li>
              <li><strong>Draw</strong> — Both players run out of cards in deck at the same time</li>
            </ul>
          </section>

          <section className="rules-section">
            <h2>📋 Deck Rules</h2>
            <ul>
              <li>Minimum 1 card per deck</li>
              <li>Maximum 60 cards per deck</li>
              <li>Legendary cards limited to 1 copy per deck</li>
              <li>You can only use cards you own</li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
}
