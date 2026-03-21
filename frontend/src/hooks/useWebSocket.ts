/**
 * useWebSocket.ts - Custom React Hook for WebSocket Connections
 * Manages real-time OSCE AI patient simulation connections
 *
 * SECURITY:
 * - JWT authentication via query parameter
 * - Auto-reconnection with exponential backoff
 * - No PHI/token logging
 *
 * PERFORMANCE:
 * - <100ms message latency target
 * - Exponential backoff (1s, 2s, 4s, 8s, max 30s)
 * - Automatic cleanup on unmount
 */

import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * WebSocket message types from backend
 * Matches backend FastAPI WebSocket implementation
 */
export interface WebSocketMessage {
  type: 'message' | 'response' | 'timer' | 'emotional_state' | 'session_ended' | 'error';
  content?: string;
  emotional_state?: 'COOPERATIVE' | 'ANXIOUS_GUARDED' | 'RESISTANT' | 'EMOTIONAL_DISTRESS' | 'CRISIS';
  remaining_seconds?: number;
  timestamp: string;
  score?: {
    overall: number;
    communication: number;
    clinical_reasoning: number;
    professionalism: number;
  };
  error?: string;
}

/**
 * Hook configuration options
 */
export interface UseWebSocketOptions {
  url: string;                          // WebSocket endpoint (ws://localhost:8001/ws/osce/{attempt_id})
  token: string;                        // JWT access token for authentication
  onMessage: (message: WebSocketMessage) => void;  // Message handler
  onError?: () => void;                 // Error handler
  onClose?: (event: CloseEvent) => void; // Close handler
  reconnectAttempts?: number;           // Max reconnection attempts (default: 5)
  reconnectInterval?: number;           // Initial reconnection interval in ms (default: 1000)
  enabled?: boolean;                    // Enable/disable connection (default: true)
}

/**
 * Hook return value
 */
export interface UseWebSocketReturn {
  sendMessage: (content: string) => void;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  reconnecting: boolean;
  lastError: string | null;
}

/**
 * Custom React hook for WebSocket connection management
 *
 * @param options - Configuration options
 * @returns WebSocket connection state and methods
 *
 * @example
 * ```typescript
 * const { sendMessage, connectionState } = useWebSocket({
 *   url: `ws://localhost:8001/ws/osce/${attemptId}`,
 *   token: jwtToken,
 *   onMessage: (msg) => console.log(msg),
 *   reconnectAttempts: 5,
 *   reconnectInterval: 1000
 * });
 *
 * // Send message to AI patient
 * sendMessage("What brings you here today?");
 * ```
 */
export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    url,
    token,
    onMessage,
    onError,
    onClose,
    reconnectAttempts = 5,
    reconnectInterval = 1000,
    enabled = true,
  } = options;

  // State
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('connecting');
  const [reconnecting, setReconnecting] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);

  // Refs (persist across re-renders)
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const intentionalDisconnectRef = useRef(false);

  /**
   * Calculate exponential backoff delay
   * 1s -> 2s -> 4s -> 8s -> 16s -> 30s (max)
   */
  const getReconnectDelay = useCallback((attemptNumber: number): number => {
    const delay = Math.min(reconnectInterval * Math.pow(2, attemptNumber), 30000);
    return delay;
  }, [reconnectInterval]);

  /**
   * Connect to WebSocket server
   */
  const connect = useCallback(() => {
    // Don't connect if disabled or already connected
    if (!enabled || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    // Clear any pending reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    try {
      // Construct WebSocket URL with JWT token as query parameter
      const wsUrl = `${url}?token=${token}`;

      // SECURITY: Don't log the full URL (contains JWT token)
      console.log('[WebSocket] Connecting to OSCE session...');

      // Create WebSocket connection
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      // Set connection state to connecting
      setConnectionState('connecting');
      setLastError(null);

      /**
       * WebSocket onopen handler
       * Called when connection is successfully established
       */
      ws.onopen = () => {
        console.log('[WebSocket] Connected successfully');
        setConnectionState('connected');
        setReconnecting(false);
        reconnectCountRef.current = 0; // Reset reconnection counter
      };

      /**
       * WebSocket onmessage handler
       * Processes incoming messages from AI patient simulation
       */
      ws.onmessage = (event: MessageEvent) => {
        try {
          // Parse JSON message from server
          const message: WebSocketMessage = JSON.parse(event.data);

          // SECURITY: Don't log message content (may contain PHI)
          console.log('[WebSocket] Message received:', message.type);

          // Call user-provided message handler
          onMessage(message);
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
          setLastError('Failed to parse server message');
        }
      };

      /**
       * WebSocket onerror handler
       * Handles connection errors
       */
      ws.onerror = () => {
        console.error('[WebSocket] Connection error');
        setConnectionState('error');
        setLastError('WebSocket connection error');

        // Call user-provided error handler
        if (onError) {
          onError();
        }
      };

      /**
       * WebSocket onclose handler
       * Handles connection closure and triggers reconnection
       */
      ws.onclose = (event: CloseEvent) => {
        console.log('[WebSocket] Connection closed', {
          code: event.code,
          reason: event.reason || 'No reason provided',
          wasClean: event.wasClean,
        });

        wsRef.current = null;

        // Call user-provided close handler
        if (onClose) {
          onClose(event);
        }

        // Don't reconnect if intentional disconnect
        if (intentionalDisconnectRef.current) {
          setConnectionState('disconnected');
          return;
        }

        // Handle reconnection
        if (reconnectCountRef.current < reconnectAttempts) {
          // Increment reconnection counter
          reconnectCountRef.current += 1;

          // Calculate backoff delay
          const delay = getReconnectDelay(reconnectCountRef.current - 1);

          console.log(
            `[WebSocket] Reconnecting (attempt ${reconnectCountRef.current}/${reconnectAttempts}) in ${delay}ms...`
          );

          setReconnecting(true);
          setConnectionState('connecting');

          // Schedule reconnection
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else {
          // Max reconnection attempts reached
          console.error('[WebSocket] Max reconnection attempts reached');
          setConnectionState('error');
          setReconnecting(false);
          setLastError('Failed to reconnect after multiple attempts');
        }
      };
    } catch (error) {
      console.error('[WebSocket] Failed to create connection:', error);
      setConnectionState('error');
      setLastError('Failed to create WebSocket connection');
    }
  }, [url, token, enabled, onMessage, onError, onClose, reconnectAttempts, getReconnectDelay]);

  /**
   * Disconnect from WebSocket server
   */
  const disconnect = useCallback(() => {
    console.log('[WebSocket] Disconnecting...');

    // Set intentional disconnect flag (prevents auto-reconnection)
    intentionalDisconnectRef.current = true;

    // Clear reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Close WebSocket connection
    if (wsRef.current) {
      wsRef.current.close(1000, 'Client initiated disconnect');
      wsRef.current = null;
    }

    setConnectionState('disconnected');
    setReconnecting(false);
  }, []);

  /**
   * Send message to WebSocket server
   * @param content - Message content to send to AI patient
   */
  const sendMessage = useCallback((content: string) => {
    // Validate WebSocket is connected
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('[WebSocket] Cannot send message: not connected');
      setLastError('Cannot send message: not connected');
      return;
    }

    // Validate message content
    if (!content || content.trim().length === 0) {
      console.error('[WebSocket] Cannot send empty message');
      return;
    }

    try {
      // Create message object
      const message = {
        type: 'message',
        content: content.trim(),
        timestamp: new Date().toISOString(),
      };

      // Send message to server
      wsRef.current.send(JSON.stringify(message));

      // SECURITY: Don't log message content (may contain PHI)
      console.log('[WebSocket] Message sent');
    } catch (error) {
      console.error('[WebSocket] Failed to send message:', error);
      setLastError('Failed to send message');
    }
  }, []);

  /**
   * Effect: Connect on mount, disconnect on unmount
   */
  useEffect(() => {
    if (enabled) {
      // Reset intentional disconnect flag
      intentionalDisconnectRef.current = false;

      // Connect to WebSocket
      connect();
    }

    // Cleanup on unmount
    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled]);

  return {
    sendMessage,
    connectionState,
    reconnecting,
    lastError,
  };
}

export default useWebSocket;
