const API_BASE = 'http://localhost:8000';

interface ApiOptions extends RequestInit {
  token?: string | null;
}

export async function api<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Auth API
export const authApi = {
  login: (username: string, password: string) =>
    api<{ access_token: string; refresh_token: string; token_type: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  register: (username: string, email: string, password: string) =>
    api<{ message: string; user: { id: number; username: string; email: string; is_active: boolean; wins: number; losses: number; draws: number; rating: number; created_at: string } }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    }),
};

// User API
export const userApi = {
  getStats: (token: string) =>
    api<{ wins: number; losses: number; draws: number; rating: number }>('/api/users/me/stats', { token }),
};

// Deck API
export const deckApi = {
  getAll: (token: string) =>
    api<{ id: number; name: string; owner_id: number; is_active: number; cards: { card_id: number; quantity: number; card_name?: string }[]; created_at: string; updated_at: string }[]>('/api/decks', { token }),

  create: (token: string, name: string, cardIds: number[]) =>
    api<{ id: number; name: string; owner_id: number; is_active: number; cards: { card_id: number; quantity: number }[]; created_at: string; updated_at: string }>('/api/decks', {
      method: 'POST',
      body: JSON.stringify({
        name,
        cards: cardIds.map((card_id) => ({ card_id, quantity: 1 })),
      }),
      token,
    }),
};

// Cards API
export const cardApi = {
  getAll: (token: string) =>
    api<{ id: number; name: string; type: 'monster' | 'spell' | 'trap'; description?: string; attack?: number; defense?: number; cost?: number; attribute?: string; hp?: number; rarity?: string; is_legendary?: boolean; passive_ability?: string; active_ability?: string }[]>('/api/cards', { token }),
};

// Matchmaking API
export const matchmakingApi = {
  join: (token: string) =>
    api<{ message: string }>('/api/matchmaking/queue', { method: 'POST', token }),

  leave: (token: string) =>
    api<{ message: string }>('/api/matchmaking/queue', { method: 'DELETE', token }),

  getStatus: (token: string) =>
    api<{ in_queue: boolean; session_id?: string }>('/api/matchmaking/status', { token }),
};
