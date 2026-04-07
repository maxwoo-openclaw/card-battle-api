// User types
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  wins: number;
  losses: number;
  draws: number;
  rating: number;
  created_at: string;
}

export interface UserStats {
  wins: number;
  losses: number;
  draws: number;
  rating: number;
}

export interface UserRegisterResponse {
  message: string;
  user: User;
}

// Auth types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Card types
export interface Card {
  id: number;
  name: string;
  type: 'monster' | 'spell' | 'trap';
  description?: string;
  attack?: number;
  defense?: number;
  cost?: number;
  attribute?: string;
  hp?: number;
  rarity?: string;
  is_legendary?: boolean;
  passive_ability?: string;
  active_ability?: string;
}

export interface Deck {
  id: number;
  name: string;
  owner_id: number;
  is_active: number;
  cards: { card_id: number; quantity: number; card_name?: string }[];
  created_at: string;
  updated_at: string;
}

// Game types
export interface PlayerState {
  hp: number;
  max_hp: number;
  energy: number;
  max_energy: number;
  hand: Card[];
  field_monsters: (Card | null)[];
  field_spells: (Card | null)[];
  deck_cards: Card[];
  graveyard: Card[];
}

export interface GameState {
  session_id: string;
  current_turn: 'player' | 'opponent';
  current_player_id: number;
  current_phase: string;
  is_your_turn: boolean;
  your_state: PlayerState;
  opponent_state: PlayerState; // masked - hand shows card backs
  game_over: boolean;
  winner_id?: number;
}

// WebSocket message types
export interface WSMessage {
  type: string;
  [key: string]: unknown;
}

export interface GameMessage {
  type: 'game_start' | 'state_update' | 'turn_change' | 'card_played' | 'attack_result' | 'game_over';
  state?: GameState;
  turn?: 'player' | 'opponent';
  player?: string;
  card_name?: string;
  attacker?: string;
  target?: string;
  damage?: number;
  result?: 'win' | 'lose';
}
