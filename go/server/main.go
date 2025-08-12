package main

/*
Roblox Creator Studio - Go Networking Server
High-performance WebSocket server for real-time multiplayer communication

Author: Seif Abdelhamid
GitHub: https://github.com/Seif-Abdelhamid
*/

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/websocket"
	"github.com/Seif-Abdelhamid/roblox-creator-studio/networking"
	"github.com/Seif-Abdelhamid/roblox-creator-studio/database"
	"github.com/Seif-Abdelhamid/roblox-creator-studio/models"
	"github.com/google/uuid"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	metricMsgsRx = prometheus.NewCounter(prometheus.CounterOpts{Name: "rcs_msgs_rx_total"})
	metricMsgsTx = prometheus.NewCounter(prometheus.CounterOpts{Name: "rcs_msgs_tx_total"})
)

func init() {
	prometheus.MustRegister(metricMsgsRx, metricMsgsTx)
}

// GameServer represents the main game server
type GameServer struct {
	clients    map[string]*networking.Client
	broadcast  chan models.GameMessage
	register   chan *networking.Client
	unregister chan *networking.Client
	mutex      sync.RWMutex
	db         *database.GameDB
	config     *ServerConfig
}

// ServerConfig holds server configuration
type ServerConfig struct {
	Port         string
	MaxPlayers   int
	TickRate     int
	WorldSize    int
	DebugMode    bool
}

// NewGameServer creates a new game server instance
func NewGameServer(config *ServerConfig) *GameServer {
	return &GameServer{
		clients:    make(map[string]*networking.Client),
		broadcast:  make(chan models.GameMessage, 1000),
		register:   make(chan *networking.Client, 100),
		unregister: make(chan *networking.Client, 100),
		config:     config,
	}
}

// Start initializes and starts the game server
func (gs *GameServer) Start() error {
	log.Printf("🎮 Starting Roblox Creator Studio Server...")
	log.Printf("📡 Server Port: %s", gs.config.Port)
	log.Printf("👥 Max Players: %d", gs.config.MaxPlayers)
	log.Printf("⚡ Tick Rate: %d Hz", gs.config.TickRate)

	// Initialize database connection
	db, err := database.NewGameDB()
	if err != nil {
		return fmt.Errorf("failed to connect to database: %v", err)
	}
	gs.db = db

	// Start server goroutines
	go gs.run()
	go gs.gameLoop()

	// Setup WebSocket upgrader
	upgrader := websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true // Allow all origins for development
		},
		ReadBufferSize:  1024,
		WriteBufferSize: 1024,
	}

	// Setup HTTP routes
	http.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
		gs.handleWebSocket(upgrader, w, r)
	})

	http.Handle("/metrics", promhttp.Handler())

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("Server is healthy!"))
	})

	// Start HTTP server
	log.Printf("🚀 Server starting on port %s", gs.config.Port)
	return http.ListenAndServe(":"+gs.config.Port, nil)
}

// handleWebSocket handles WebSocket connections
func (gs *GameServer) handleWebSocket(upgrader websocket.Upgrader, w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("❌ WebSocket upgrade failed: %v", err)
		return
	}

	// Check if server is full
	gs.mutex.RLock()
	if len(gs.clients) >= gs.config.MaxPlayers {
		gs.mutex.RUnlock()
		conn.WriteJSON(models.GameMessage{
			Type: "error",
			Data: map[string]interface{}{
				"message": "Server is full",
			},
		})
		conn.Close()
		return
	}
	gs.mutex.RUnlock()

	// Demonstrate uuid usage to ensure module resolution
	_ = uuid.NewString()

	// Create new client
	client := networking.NewClient(conn, gs)
	client.CloseFunc = func(c *networking.Client) {
		gs.unregister <- c
	}
	gs.register <- client
	client.Start()

	log.Printf("👤 New player connected: %s", client.ID)
}

// run handles server events
func (gs *GameServer) run() {
	for {
		select {
		case client := <-gs.register:
			gs.mutex.Lock()
			gs.clients[client.ID] = client
			gs.mutex.Unlock()

			// Send welcome message
			client.Send(models.GameMessage{
				Type: "welcome",
				Data: map[string]interface{}{
					"playerId": client.ID,
					"serverInfo": map[string]interface{}{
						"maxPlayers": gs.config.MaxPlayers,
						"tickRate":   gs.config.TickRate,
						"worldSize":  gs.config.WorldSize,
					},
				},
			})

			// Broadcast player joined
			gs.broadcastToOthers(client.ID, models.GameMessage{
				Type: "playerJoined",
				Data: map[string]interface{}{
					"playerId": client.ID,
					"position": map[string]float64{"x": 0, "y": 2, "z": 0},
				},
			})

		case client := <-gs.unregister:
			gs.mutex.Lock()
			if _, ok := gs.clients[client.ID]; ok {
				delete(gs.clients, client.ID)
				client.Conn.Close()
			}
			gs.mutex.Unlock()

			// Broadcast player left
			gs.broadcastToAll(models.GameMessage{
				Type: "playerLeft",
				Data: map[string]interface{}{
					"playerId": client.ID,
				},
			})

			log.Printf("👋 Player disconnected: %s", client.ID)

		case message := <-gs.broadcast:
			gs.broadcastToAll(message)
		}
	}
}

// gameLoop runs the main game loop
func (gs *GameServer) gameLoop() {
	ticker := time.NewTicker(time.Duration(1000/gs.config.TickRate) * time.Millisecond)
	defer ticker.Stop()

	for range ticker.C {
		gs.update()
	}
}

// update processes game logic
func (gs *GameServer) update() {
	gs.mutex.RLock()
	clients := make([]*networking.Client, 0, len(gs.clients))
	for _, client := range gs.clients {
		clients = append(clients, client)
	}
	gs.mutex.RUnlock()

	// Process player updates
	for _, client := range clients {
		select {
		case msg := <-client.MessageQueue:
			gs.handleMessage(client, msg)
		default:
			// No message to process
		}
	}

	// Broadcast game state updates
	gs.broadcastGameState()
}

// handleMessage processes incoming messages
func (gs *GameServer) handleMessage(client *networking.Client, message models.GameMessage) {
	switch message.Type {
	case "playerUpdate":
		gs.handlePlayerUpdate(client, message)
	case "chat":
		gs.handleChat(client, message)
	case "build":
		gs.handleBuild(client, message)
	case "interact":
		gs.handleInteraction(client, message)
	default:
		log.Printf("⚠️ Unknown message type: %s", message.Type)
	}
}

// handlePlayerUpdate processes player movement and state updates
func (gs *GameServer) handlePlayerUpdate(client *networking.Client, message models.GameMessage) {
	// Validate player data
	playerData, ok := message.Data.(map[string]interface{})
	if !ok {
		return
	}

	// Update player state in database
	err := gs.db.UpdatePlayerState(client.ID, playerData)
	if err != nil {
		log.Printf("❌ Failed to update player state: %v", err)
		return
	}

	// Broadcast to other players
	gs.broadcastToOthers(client.ID, models.GameMessage{
		Type: "playerUpdate",
		Data: map[string]interface{}{
			"playerId": client.ID,
			"position": playerData["position"],
			"rotation": playerData["rotation"],
			"health":   playerData["health"],
			"energy":   playerData["energy"],
		},
	})
}

// handleChat processes chat messages
func (gs *GameServer) handleChat(client *networking.Client, message models.GameMessage) {
	chatData, ok := message.Data.(map[string]interface{})
	if !ok {
		return
	}
	// Basic anti-abuse: rate-limit and naive moderation
	if !gs.allowChat(client) {
		return
	}
	text, _ := chatData["message"].(string)
	if gs.isBannedText(text) {
		return
	}
	metricMsgsRx.Inc()
	log.Printf("💬 [%s]: %s", client.ID, text)
	gs.broadcastToAll(models.GameMessage{
		Type: "chat",
		Data: map[string]interface{}{
			"playerId":  client.ID,
			"message":   text,
			"timestamp": time.Now().Unix(),
		},
	})
	metricMsgsTx.Inc()
}

func (gs *GameServer) allowChat(client *networking.Client) bool {
	// Rate limit placeholder: replace with token bucket per client
	return true
}

func (gs *GameServer) isBannedText(s string) bool {
	if s == "" { return false }
	lower := strings.ToLower(s)
	for _, w := range []string{"spam", "abuse"} {
		if strings.Contains(lower, w) { return true }
	}
	return false
}

// handleBuild processes building actions
func (gs *GameServer) handleBuild(client *networking.Client, message models.GameMessage) {
	buildData, ok := message.Data.(map[string]interface{})
	if !ok {
		return
	}

	// Validate build permissions and world limits
	if gs.validateBuild(buildData) {
		// Save build data to database
		err := gs.db.SaveBuildAction(client.ID, buildData)
		if err != nil {
			log.Printf("❌ Failed to save build action: %v", err)
			return
		}

		// Broadcast build action to all players
		gs.broadcastToAll(models.GameMessage{
			Type: "build",
			Data: map[string]interface{}{
				"playerId": client.ID,
				"position": buildData["position"],
				"blockType": buildData["blockType"],
				"action":    buildData["action"], // place/remove
			},
		})
	}
}

// handleInteraction processes player interactions
func (gs *GameServer) handleInteraction(client *networking.Client, message models.GameMessage) {
	interactionData, ok := message.Data.(map[string]interface{})
	if !ok {
		return
	}

	// Process interaction logic
	response := gs.processInteraction(client.ID, interactionData)

	// Send response to client
	client.Send(models.GameMessage{
		Type: "interactionResponse",
		Data: response,
	})
}

// validateBuild validates building actions
func (gs *GameServer) validateBuild(buildData map[string]interface{}) bool {
	// Check world boundaries
	position, ok := buildData["position"].(map[string]interface{})
	if !ok {
		return false
	}

	x, _ := position["x"].(float64)
	y, _ := position["y"].(float64)
	z, _ := position["z"].(float64)

	// Check if within world bounds
	if x < -float64(gs.config.WorldSize) || x > float64(gs.config.WorldSize) ||
		y < 0 || y > 256 ||
		z < -float64(gs.config.WorldSize) || z > float64(gs.config.WorldSize) {
		return false
	}

	return true
}

// processInteraction processes player interactions with objects
func (gs *GameServer) processInteraction(playerID string, interactionData map[string]interface{}) map[string]interface{} {
	// Example interaction logic
	objectType, _ := interactionData["objectType"].(string)
	
	switch objectType {
	case "chest":
		return map[string]interface{}{
			"type": "inventory",
			"items": []string{"sword", "shield", "potion"},
		}
	case "npc":
		return map[string]interface{}{
			"type": "dialogue",
			"message": "Welcome to Roblox Creator Studio!",
		}
	default:
		return map[string]interface{}{
			"type": "error",
			"message": "Cannot interact with this object",
		}
	}
}

// broadcastGameState broadcasts current game state to all players
func (gs *GameServer) broadcastGameState() {
	gs.mutex.RLock()
	playerCount := len(gs.clients)
	gs.mutex.RUnlock()

	// Broadcast server stats periodically
	if time.Now().Unix()%10 == 0 { // Every 10 seconds
		gs.broadcastToAll(models.GameMessage{
			Type: "serverStats",
			Data: map[string]interface{}{
				"playerCount": playerCount,
				"maxPlayers":  gs.config.MaxPlayers,
				"uptime":      time.Now().Unix(),
			},
		})
	}
}

// broadcastToAll sends a message to all connected clients
func (gs *GameServer) broadcastToAll(message models.GameMessage) {
	gs.mutex.RLock()
	defer gs.mutex.RUnlock()

	for _, client := range gs.clients {
		select {
		case client.SendQueue <- message:
		default:
			// Client's send queue is full, skip this message
		}
	}
}

// broadcastToOthers sends a message to all clients except the specified one
func (gs *GameServer) broadcastToOthers(excludeID string, message models.GameMessage) {
	gs.mutex.RLock()
	defer gs.mutex.RUnlock()

	for id, client := range gs.clients {
		if id != excludeID {
			select {
			case client.SendQueue <- message:
			default:
				// Client's send queue is full, skip this message
			}
		}
	}
}

// GetPlayerCount returns the current number of connected players
func (gs *GameServer) GetPlayerCount() int {
	gs.mutex.RLock()
	defer gs.mutex.RUnlock()
	return len(gs.clients)
}

// GetServerStats returns server statistics
func (gs *GameServer) GetServerStats() map[string]interface{} {
	return map[string]interface{}{
		"playerCount": gs.GetPlayerCount(),
		"maxPlayers":  gs.config.MaxPlayers,
		"uptime":      time.Now().Unix(),
		"version":     "1.0.0",
		"author":      "Seif Abdelhamid",
	}
}

func main() {
	// Server configuration
	config := &ServerConfig{
		Port:       "8080",
		MaxPlayers: 50,
		TickRate:   20,
		WorldSize:  1000,
		DebugMode:  true,
	}

	// Create and start server
	server := NewGameServer(config)
	
	log.Printf("🎮 Roblox Creator Studio Server")
	log.Printf("👨‍💻 Author: Seif Abdelhamid")
	log.Printf("🌐 GitHub: https://github.com/Seif-Abdelhamid")
	
	if err := server.Start(); err != nil {
		log.Fatalf("❌ Server failed to start: %v", err)
	}
}
