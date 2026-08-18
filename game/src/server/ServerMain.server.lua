-- Server boot: create remotes, fetch idea cards from the factory, build the map.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local Workspace = game:GetService("Workspace")

local Remotes = require(ReplicatedStorage.Vibeblox.Remotes)
local IdeaService = require(script.Parent.IdeaService)
local JobService = require(script.Parent.JobService)
local BuildMap = require(script.Parent.BuildMap)

-- Clients can only find remotes, so the server must create them first
local fetchData = Remotes.ensureFunction("FetchData")
local startJob = Remotes.ensureEvent("StartJob")
local jobUpdate = Remotes.ensureEvent("JobUpdate")

-- Fetch idea cards + questions once at boot, before anyone can ask
IdeaService.boot()

-- Build the world. If anything goes wrong, warn loudly but keep going,
-- and ALWAYS guarantee a floor under the spawn so nobody falls.
local ok, err = pcall(BuildMap.build)
if not ok then
	warn("[Vibeblox] map build failed: " .. tostring(err))
end
local map = Workspace:FindFirstChild("P2B_Map")
if not map or not map:FindFirstChild("Floor") then
	warn("[Vibeblox] map missing - building emergency floor")
	local floor = Instance.new("Part")
	floor.Name = "Floor"
	floor.Anchored = true
	floor.Size = Vector3.new(100, 1, 100)
	floor.Position = Vector3.new(0, -0.5, 0)
	floor.Color = Color3.fromRGB(30, 32, 60)
	floor.Parent = Workspace
end
print("[Vibeblox] map ready, parts: " .. tostring(if map then #map:GetDescendants() + 1 else 1))

-- Always land players on the pad, no matter what Roblox thinks a spawn is
local function onCharacter(_player, character)
	task.spawn(function()
		local hrp = character:WaitForChild("HumanoidRootPart", 10)
		if hrp then
			hrp.CFrame = CFrame.new(0, 4, 0)
		end
	end)
end

local function onPlayerJoined(player)
	player.CharacterAdded:Connect(onCharacter)
	jobUpdate:FireClient(player, {
		state = "idle",
		stage = "idle",
		message = "",
		detail = "",
		repoUrl = nil,
		idea = "",
	})
end

Players.PlayerAdded:Connect(onPlayerJoined)
for _, p in ipairs(Players:GetPlayers()) do
	onPlayerJoined(p)
end

-- Client asks for idea cards + questions (server holds the fetched copy)
fetchData.OnServerInvoke = function(_player)
	return IdeaService.data()
end

-- Client says "build this!"
startJob.OnServerEvent:Connect(function(player, idea, answers)
	JobService.start(player, idea, answers)
end)

BuildMap.build()
print("[Vibeblox] factory connected to the game")
