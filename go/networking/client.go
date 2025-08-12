package networking

import (
	"encoding/json"
	"log"

	"github.com/Seif-Abdelhamid/roblox-creator-studio/models"
	"github.com/gorilla/websocket"
	"github.com/google/uuid"
)

// Client represents a connected player
// Minimal implementation for scaffolding

type Client struct {
	ID           string
	Conn         *websocket.Conn
	MessageQueue chan models.GameMessage
	CloseFunc    func(*Client)
}

// NewClient creates a new client instance
func NewClient(conn *websocket.Conn, _ interface{}) *Client {
	return &Client{
		ID:           uuid.NewString(),
		Conn:         conn,
		MessageQueue: make(chan models.GameMessage, 100),
	}
}

// Start begins reading messages from the websocket and enqueues them
func (c *Client) Start() {
	go func() {
		defer func() {
			if c.CloseFunc != nil {
				c.CloseFunc(c)
			}
		}()
		for {
			var msg models.GameMessage
			_, raw, err := c.Conn.ReadMessage()
			if err != nil {
				log.Printf("client %s read error: %v", c.ID, err)
				return
			}
			if err := json.Unmarshal(raw, &msg); err != nil {
				log.Printf("client %s json error: %v", c.ID, err)
				continue
			}
			select {
			case c.MessageQueue <- msg:
			default:
				log.Printf("client %s message queue full, dropping msg", c.ID)
			}
		}
	}()
}

// Send enqueues a message to be sent to this client and attempts immediate write
func (c *Client) Send(msg models.GameMessage) {
	select {
	case c.MessageQueue <- msg:
		// ok
	default:
		log.Printf("client %s message queue full, dropping message", c.ID)
	}
	_ = c.Conn.WriteJSON(msg)
}