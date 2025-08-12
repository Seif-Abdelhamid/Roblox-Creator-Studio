--[[
Roblox Creator Studio - Lua Scripting System
Game logic and modding support for the 3D multiplayer game engine

Author: Seif Abdelhamid
GitHub: https://github.com/Seif-Abdelhamid
Version: 1.0.0
--]]

-- Global game state
local GameState = {
    players = {},
    world = {},
    events = {},
    time = 0,
    dayNightCycle = 0
}

-- Event system
local EventSystem = {
    listeners = {}
}

-- Register event listener
function EventSystem:on(eventName, callback)
    if not self.listeners[eventName] then
        self.listeners[eventName] = {}
    end
    table.insert(self.listeners[eventName], callback)
end

-- Trigger event
function EventSystem:trigger(eventName, ...)
    if self.listeners[eventName] then
        for _, callback in ipairs(self.listeners[eventName]) do
            callback(...)
        end
    end
end

-- Player management
local PlayerManager = {}

function PlayerManager:createPlayer(playerId, username)
    local player = {
        id = playerId,
        username = username,
        position = {x = 0, y = 2, z = 0},
        rotation = {x = 0, y = 0, z = 0},
        health = 100,
        maxHealth = 100,
        energy = 100,
        maxEnergy = 100,
        level = 1,
        experience = 0,
        inventory = {},
        permissions = {"build", "chat", "move"},
        joinTime = os.time()
    }
    
    GameState.players[playerId] = player
    EventSystem:trigger("playerJoined", player)
    
    return player
end

function PlayerManager:removePlayer(playerId)
    local player = GameState.players[playerId]
    if player then
        EventSystem:trigger("playerLeft", player)
        GameState.players[playerId] = nil
    end
end

function PlayerManager:updatePlayer(playerId, data)
    local player = GameState.players[playerId]
    if player then
        for key, value in pairs(data) do
            player[key] = value
        end
        EventSystem:trigger("playerUpdated", player)
    end
end

function PlayerManager:getPlayer(playerId)
    return GameState.players[playerId]
end

function PlayerManager:getAllPlayers()
    return GameState.players
end

-- World management
local WorldManager = {}

function WorldManager:placeBlock(position, blockType, playerId)
    local block = {
        position = position,
        type = blockType,
        placedBy = playerId,
        placedAt = os.time(),
        health = 100
    }
    
    local key = string.format("%d,%d,%d", position.x, position.y, position.z)
    GameState.world[key] = block
    
    EventSystem:trigger("blockPlaced", block, playerId)
    return block
end

function WorldManager:removeBlock(position, playerId)
    local key = string.format("%d,%d,%d", position.x, position.y, position.z)
    local block = GameState.world[key]
    
    if block then
        GameState.world[key] = nil
        EventSystem:trigger("blockRemoved", block, playerId)
        return true
    end
    
    return false
end

function WorldManager:getBlock(position)
    local key = string.format("%d,%d,%d", position.x, position.y, position.z)
    return GameState.world[key]
end

function WorldManager:getWorldData()
    return GameState.world
end

-- Chat system
local ChatSystem = {}

function ChatSystem:sendMessage(playerId, message)
    local player = PlayerManager:getPlayer(playerId)
    if player then
        local chatMessage = {
            playerId = playerId,
            username = player.username,
            message = message,
            timestamp = os.time()
        }
        
        EventSystem:trigger("chatMessage", chatMessage)
        return chatMessage
    end
    return nil
end

function ChatSystem:broadcastMessage(message, senderId)
    local chatMessage = {
        playerId = senderId or "SYSTEM",
        username = senderId and PlayerManager:getPlayer(senderId).username or "System",
        message = message,
        timestamp = os.time(),
        isSystem = not senderId
    }
    
    EventSystem:trigger("chatMessage", chatMessage)
    return chatMessage
end

-- Building system
local BuildingSystem = {}

function BuildingSystem:canBuild(playerId, position)
    local player = PlayerManager:getPlayer(playerId)
    if not player then return false end
    
    -- Check permissions
    if not self:hasPermission(player, "build") then
        return false, "No build permission"
    end
    
    -- Check world boundaries
    if position.x < -1000 or position.x > 1000 or
       position.y < 0 or position.y > 256 or
       position.z < -1000 or position.z > 1000 then
        return false, "Outside world boundaries"
    end
    
    -- Check if position is already occupied
    if WorldManager:getBlock(position) then
        return false, "Position already occupied"
    end
    
    return true
end

function BuildingSystem:hasPermission(player, permission)
    for _, perm in ipairs(player.permissions) do
        if perm == permission then
            return true
        end
    end
    return false
end

function BuildingSystem:placeBlock(playerId, position, blockType)
    local canBuild, reason = self:canBuild(playerId, position)
    if not canBuild then
        return false, reason
    end
    
    local block = WorldManager:placeBlock(position, blockType, playerId)
    return true, block
end

-- Combat system
local CombatSystem = {}

function CombatSystem:damagePlayer(playerId, damage, sourceId)
    local player = PlayerManager:getPlayer(playerId)
    if not player then return false end
    
    player.health = math.max(0, player.health - damage)
    
    EventSystem:trigger("playerDamaged", player, damage, sourceId)
    
    if player.health <= 0 then
        EventSystem:trigger("playerDied", player, sourceId)
        self:respawnPlayer(playerId)
    end
    
    return true
end

function CombatSystem:healPlayer(playerId, amount)
    local player = PlayerManager:getPlayer(playerId)
    if not player then return false end
    
    player.health = math.min(player.maxHealth, player.health + amount)
    EventSystem:trigger("playerHealed", player, amount)
    
    return true
end

function CombatSystem:respawnPlayer(playerId)
    local player = PlayerManager:getPlayer(playerId)
    if player then
        player.position = {x = 0, y = 2, z = 0}
        player.health = player.maxHealth
        player.energy = player.maxEnergy
        
        EventSystem:trigger("playerRespawned", player)
    end
end

-- Experience and leveling system
local ExperienceSystem = {}

function ExperienceSystem:addExperience(playerId, amount)
    local player = PlayerManager:getPlayer(playerId)
    if not player then return false end
    
    player.experience = player.experience + amount
    
    -- Check for level up
    local experienceNeeded = player.level * 100
    if player.experience >= experienceNeeded then
        self:levelUp(playerId)
    end
    
    EventSystem:trigger("experienceGained", player, amount)
    return true
end

function ExperienceSystem:levelUp(playerId)
    local player = PlayerManager:getPlayer(playerId)
    if not player then return false end
    
    player.level = player.level + 1
    player.experience = 0
    player.maxHealth = player.maxHealth + 10
    player.maxEnergy = player.maxEnergy + 10
    player.health = player.maxHealth
    player.energy = player.maxEnergy
    
    EventSystem:trigger("playerLevelUp", player)
    
    -- Broadcast level up message
    ChatSystem:broadcastMessage(
        string.format("🎉 %s reached level %d!", player.username, player.level),
        "SYSTEM"
    )
end

-- Time and day/night cycle
local TimeSystem = {}

function TimeSystem:update(deltaTime)
    GameState.time = GameState.time + deltaTime
    GameState.dayNightCycle = (math.sin(GameState.time * 0.1) + 1) / 2
    
    -- Trigger time-based events
    if GameState.dayNightCycle < 0.1 then
        EventSystem:trigger("dayStarted")
    elseif GameState.dayNightCycle > 0.9 then
        EventSystem:trigger("nightStarted")
    end
end

function TimeSystem:getTime()
    return GameState.time
end

function TimeSystem:getDayNightCycle()
    return GameState.dayNightCycle
end

-- Plugin system
local PluginSystem = {
    plugins = {}
}

function PluginSystem:registerPlugin(name, plugin)
    self.plugins[name] = plugin
    if plugin.onLoad then
        plugin:onLoad()
    end
    EventSystem:trigger("pluginLoaded", name, plugin)
end

function PluginSystem:unregisterPlugin(name)
    local plugin = self.plugins[name]
    if plugin and plugin.onUnload then
        plugin:onUnload()
    end
    self.plugins[name] = nil
    EventSystem:trigger("pluginUnloaded", name)
end

function PluginSystem:getPlugin(name)
    return self.plugins[name]
end

-- Example plugin: Welcome message
local WelcomePlugin = {
    name = "WelcomePlugin",
    version = "1.0.0"
}

function WelcomePlugin:onLoad()
    EventSystem:on("playerJoined", function(player)
        ChatSystem:broadcastMessage(
            string.format("👋 Welcome %s to Roblox Creator Studio!", player.username),
            "SYSTEM"
        )
    end)
end

function WelcomePlugin:onUnload()
    -- Cleanup if needed
end

-- Example plugin: Auto-healing
local AutoHealPlugin = {
    name = "AutoHealPlugin",
    version = "1.0.0"
}

function AutoHealPlugin:onLoad()
    -- Auto-heal players every 30 seconds
    local healTimer = 0
    EventSystem:on("update", function(deltaTime)
        healTimer = healTimer + deltaTime
        if healTimer >= 30 then
            healTimer = 0
            for playerId, player in pairs(GameState.players) do
                if player.health < player.maxHealth then
                    CombatSystem:healPlayer(playerId, 5)
                end
            end
        end
    end)
end

-- Register default plugins
PluginSystem:registerPlugin("WelcomePlugin", WelcomePlugin)
PluginSystem:registerPlugin("AutoHealPlugin", AutoHealPlugin)

-- Main game loop
local function update(deltaTime)
    TimeSystem:update(deltaTime)
    EventSystem:trigger("update", deltaTime)
end

-- API for external access
local API = {
    PlayerManager = PlayerManager,
    WorldManager = WorldManager,
    ChatSystem = ChatSystem,
    BuildingSystem = BuildingSystem,
    CombatSystem = CombatSystem,
    ExperienceSystem = ExperienceSystem,
    TimeSystem = TimeSystem,
    PluginSystem = PluginSystem,
    EventSystem = EventSystem,
    GameState = GameState,
    update = update
}

-- Return the API
return API
