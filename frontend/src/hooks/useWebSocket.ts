import { useEffect, useRef, useCallback, useState } from 'react';
import { wsService, WebSocketService } from '../services/websocket';
import type { GameMessage } from '../types';

interface UseWebSocketOptions {
  sessionId: string;
  token: string;
  onMessage?: (message: GameMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export function useWebSocket({ sessionId, token, onMessage, onConnect, onDisconnect }: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const serviceRef = useRef<WebSocketService | null>(null);

  useEffect(() => {
    if (!sessionId || !token) return;

    // Create new service instance for this connection
    const ws = new WebSocketService();
    serviceRef.current = ws;

    ws.connect(sessionId, token);

    ws.onConnect(() => {
      setIsConnected(true);
      onConnect?.();
    });

    ws.onDisconnect(() => {
      setIsConnected(false);
      onDisconnect?.();
    });

    if (onMessage) {
      const unsubscribe = ws.onMessage(onMessage as (message: unknown) => void);
      return () => {
        unsubscribe();
        ws.disconnect();
      };
    }

    return () => {
      ws.disconnect();
    };
  }, [sessionId, token, onMessage, onConnect, onDisconnect]);

  const send = useCallback((message: Record<string, unknown>) => {
    serviceRef.current?.send(message);
  }, []);

  return { isConnected, send };
}

export { wsService };
