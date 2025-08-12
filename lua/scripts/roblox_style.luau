--!strict
-- Roblox-style Luau sample (conceptual)

local Players = {}

function onPlayerJoin(playerId: string)
    Players[playerId] = { health = 100, position = {x=0,y=2,z=0} }
end

function onChat(playerId: string, message: string)
    if string.find(message, "spam") then return end
    print("["..playerId.."] "..message)
end