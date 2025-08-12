package models

// GameMessage represents a generic message exchanged between server and clients
// Data can be any JSON-serializable payload
// Keep minimal for scaffolding

type GameMessage struct {
	Type string      `json:"type"`
	Data interface{} `json:"data"`
}