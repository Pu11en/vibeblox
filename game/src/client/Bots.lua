-- Worker bots on their pads: hop while working. Vault flashes when a repo lands.
local Workspace = game:GetService("Workspace")
local TweenService = game:GetService("TweenService")

local Bots = {}

local bots = {} -- index -> Part
local busy = {} -- index -> bool
local hopTasks = {} -- index -> task

local function findBots()
	local map = Workspace:FindFirstChild("P2B_Map")
	if not map then
		return
	end
	local folder = map:FindFirstChild("WorkerBots")
	if not folder then
		return
	end
	for _, child in ipairs(folder:GetChildren()) do
		local n = child.Name:match("^Bot(%d+)$")
		if n then
			bots[tonumber(n)] = child
		end
	end
end

local function hopLoop(i)
	local bot = bots[i]
	local base = bot.Position
	while busy[i] and bot.Parent do
		local up = TweenService:Create(bot, TweenInfo.new(0.3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
			{ Position = base + Vector3.new(0, 1.2, 0) })
		local down = TweenService:Create(bot, TweenInfo.new(0.3, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
			{ Position = base })
		up:Play()
		up.Completed:Wait()
		if busy[i] then
			down:Play()
			down.Completed:Wait()
		end
		task.wait(0.15)
	end
end

-- returns a free bot index, or nil
function Bots.take()
	findBots()
	for i = 1, 3 do
		if bots[i] and not busy[i] then
			busy[i] = true
			hopTasks[i] = task.spawn(hopLoop, i)
			return i
		end
	end
	return nil
end

function Bots.release(i)
	if i and busy[i] then
		busy[i] = false
		task.cancel(hopTasks[i])
		hopTasks[i] = nil
		local bot = bots[i]
		if bot then
			TweenService:Create(bot, TweenInfo.new(0.3),
				{ Position = bot.Position + Vector3.new(0, -1.2, 0) }):Play()
		end
	end
end

function Bots.flashVault()
	local map = Workspace:FindFirstChild("P2B_Map")
	if not map then
		return
	end
	local door = map:FindFirstChild("VaultDoor")
	if not door then
		return
	end
	local gold = Color3.fromRGB(255, 210, 80)
	local green = Color3.fromRGB(70, 255, 130)
	task.spawn(function()
		for _ = 1, 3 do
			TweenService:Create(door, TweenInfo.new(0.25), { Color = gold }):Play()
			task.wait(0.3)
			TweenService:Create(door, TweenInfo.new(0.25), { Color = green }):Play()
			task.wait(0.3)
		end
	end)
end

findBots()

return Bots
