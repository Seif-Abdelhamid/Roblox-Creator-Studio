package networking

import (
	"log"
	"github.com/gorilla/websocket"
	"github.com/Seif-Abdelhamid/roblox-creator-studio/models"
	"github.com/google/uuid"
)

// Client represents a connected player
// Minimal implementation for scaffolding

type Client struct {
	ID           string
	Conn         *websocket.Conn
	MessageQueue chan models.GameMessage
}

// NewClient creates a new client instance
func NewClient(conn *websocket.Conn, _ interface{}) *Client {
	return &Client{
		ID:           uuid.NewString(),
		Conn:         conn,
		MessageQueue: make(chan models.GameMessage, 100),
	}
}

// Send enqueues a message to be sent to this client
func (c *Client) Send(msg models.GameMessage) {
	select {
	case c.MessageQueue <- msg:
		// ok
	default:
		log.Printf("client %s message queue full, dropping message", c.ID)
	}
	// Best-effort immediate send as well
	_ = c.Conn.WriteJSON(msg)
}