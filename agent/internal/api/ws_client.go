package api

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"time"

	"github.com/gorilla/websocket"
)

// WSClient handles WebSocket communication with the ChatOps API
type WSClient struct {
	baseURL      string
	apiKey       string
	serverID     string
	conn         *websocket.Conn
	done         chan struct{}
	messageChan  chan map[string]interface{}
	metricsAck   chan map[string]interface{}
}

// NewWSClient creates a new WebSocket client
func NewWSClient(baseURL, apiKey string) (*WSClient, error) {
	// First, fetch server ID via HTTP
	httpClient := &Client{
		baseURL: baseURL,
		apiKey:  apiKey,
		client:  &http.Client{Timeout: 30 * time.Second},
	}

	ctx := context.Background()
	serverID, err := httpClient.fetchServerID(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch server ID: %w", err)
	}

	return &WSClient{
		baseURL:     baseURL,
		apiKey:      apiKey,
		serverID:    serverID,
		done:        make(chan struct{}),
		messageChan: make(chan map[string]interface{}, 100),
		metricsAck:  make(chan map[string]interface{}, 1),
	}, nil
}

// Connect establishes a WebSocket connection to the API
func (c *WSClient) Connect(ctx context.Context) error {
	// Build WebSocket URL with API key in query parameter
	u, err := url.Parse(c.baseURL)
	if err != nil {
		return fmt.Errorf("invalid base URL: %w", err)
	}

	// Convert http/https to ws/wss
	scheme := "ws"
	if u.Scheme == "https" {
		scheme = "wss"
	} else if u.Scheme == "http" {
		scheme = "ws"
	}

	wsURL := fmt.Sprintf("%s://%s/api/v1/agents/ws", scheme, u.Host)

	// Connect to WebSocket
	dialer := websocket.Dialer{
		HandshakeTimeout: 10 * time.Second,
	}

	conn, _, err := dialer.DialContext(ctx, wsURL, nil)
	if err != nil {
		return fmt.Errorf("failed to connect to WebSocket: %w", err)
	}

	c.conn = conn

	// Send authentication message
	authMsg := map[string]string{
		"type":    "auth",
		"api_key": c.apiKey,
	}
	if err := conn.WriteJSON(authMsg); err != nil {
		conn.Close()
		return fmt.Errorf("failed to send auth message: %w", err)
	}

	// Wait for auth success message
	var authResponse map[string]interface{}
	if err := conn.ReadJSON(&authResponse); err != nil {
		conn.Close()
		return fmt.Errorf("failed to read auth response: %w", err)
	}

	if authResponse["type"] != "auth_success" {
		conn.Close()
		return fmt.Errorf("authentication failed: %v", authResponse)
	}

	log.Printf("WebSocket connected successfully for server %s", c.serverID)

	// Start message reader goroutine
	go c.readMessages()

	// Start ping goroutine
	go c.pingLoop()

	return nil
}

// readMessages reads all messages from the WebSocket and routes them
func (c *WSClient) readMessages() {
	for {
		if c.conn == nil {
			return
		}
		
		var message map[string]interface{}
		if err := c.conn.ReadJSON(&message); err != nil {
			log.Printf("Error reading WebSocket message: %v", err)
			return
		}

		msgType, _ := message["type"].(string)
		
		// Route metrics acknowledgments to metricsAck channel
		if msgType == "metrics_received" {
			select {
			case c.metricsAck <- message:
			default:
				// Channel full, skip (shouldn't happen with buffered channel)
			}
			continue
		}

		// Route all other messages to messageChan
		select {
		case c.messageChan <- message:
		default:
			log.Printf("Message channel full, dropping message: %v", msgType)
		}
	}
}

// pingLoop sends periodic ping messages to keep connection alive
func (c *WSClient) pingLoop() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-c.done:
			return
		case <-ticker.C:
			if c.conn == nil {
				return
			}
			if err := c.conn.WriteJSON(map[string]string{"type": "ping"}); err != nil {
				log.Printf("Error sending ping: %v", err)
				return
			}
		}
	}
}


// SendMetrics sends metrics via WebSocket
func (c *WSClient) SendMetrics(ctx context.Context, metrics *Metrics) error {
	if c.conn == nil {
		return fmt.Errorf("WebSocket not connected")
	}

	// Format metrics message
	message := map[string]interface{}{
		"type": "metrics",
		"data": map[string]interface{}{
			"server_id":  metrics.ServerID,
			"timestamp":  metrics.Timestamp.Format(time.RFC3339),
			"cpu":        metrics.CPU,
			"memory":     metrics.Memory,
			"disk":       metrics.Disk,
			"network":    metrics.Network,
			"containers": metrics.Containers,
			"processes":   metrics.Processes,
		},
	}

	// Send message
	if err := c.conn.WriteJSON(message); err != nil {
		return fmt.Errorf("failed to send metrics: %w", err)
	}

	// Wait for acknowledgment via channel (with timeout)
	select {
	case ack := <-c.metricsAck:
		if ack["type"] != "metrics_received" {
			return fmt.Errorf("unexpected acknowledgment: %v", ack)
		}
		return nil
	case <-time.After(5 * time.Second):
		return fmt.Errorf("timeout waiting for metrics acknowledgment")
	case <-ctx.Done():
		return ctx.Err()
	}
}

// Close closes the WebSocket connection
func (c *WSClient) Close() error {
	close(c.done)
	if c.conn != nil {
		return c.conn.Close()
	}
	return nil
}

// GetServerID returns the server ID
func (c *WSClient) GetServerID() string {
	return c.serverID
}

// GetConn returns the WebSocket connection (for reading messages)
func (c *WSClient) GetConn() *websocket.Conn {
	return c.conn
}

// GetMessageChan returns the channel for receiving messages
func (c *WSClient) GetMessageChan() <-chan map[string]interface{} {
	return c.messageChan
}

// SendResponse sends a response message
func (c *WSClient) SendResponse(originalMessage map[string]interface{}, response map[string]interface{}) error {
	if c.conn == nil {
		return fmt.Errorf("WebSocket not connected")
	}

	// Include request ID if present
	if reqID, ok := originalMessage["request_id"]; ok {
		response["request_id"] = reqID
	}

	return c.conn.WriteJSON(response)
}

