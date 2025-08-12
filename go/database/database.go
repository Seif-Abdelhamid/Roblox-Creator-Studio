package database

import "fmt"

// GameDB is a simple stub suitable for local dev; swap with a real DB in production
// In scaffolding, it does nothing but satisfy interfaces

type GameDB struct{}

// NewGameDB simulates creating a DB connection
func NewGameDB() (*GameDB, error) {
	// In a real implementation, connect to Postgres/Redis here
	return &GameDB{}, nil
}

// Close closes the DB connection
func (db *GameDB) Close() error { return nil }

// Example method to avoid unused warnings
func (db *GameDB) Ping() error { return fmt.Errorf("") }