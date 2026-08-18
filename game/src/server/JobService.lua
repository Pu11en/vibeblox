-- The bridge to the factory: starts jobs, polls status, tells the player.
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Vibeblox.Config)
local Remotes = require(ReplicatedStorage.Vibeblox.Remotes)

local JobService = {}

-- remotes are created by ServerMain AFTER requires, so look them up lazily
local function jobUpdate()
	return Remotes.get("JobUpdate")
end

local HEADERS = {
	["Content-Type"] = "application/json",
	["X-P2B-Secret"] = Config.Secret,
}

-- player -> list of { jobId, finished, idea }
local activeJobs = {}

function JobService.start(player, idea, answers)
	if not idea or type(idea) ~= "table" or not idea.id then
		return
	end
	local mine = activeJobs[player] or {}
	local running = 0
	for _, j in ipairs(mine) do
		if not j.finished then
			running = running + 1
		end
	end
	if running >= Config.MaxWorkers then
		jobUpdate():FireClient(player, {
			state = "nope",
			stage = "nope",
			message = "All your workers are busy! Hire another one or wait.",
			detail = "",
			repoUrl = nil,
			idea = idea.name or "",
		})
		return
	end

	local body = HttpService:JSONEncode({
		idea = idea,
		answers = answers or {},
		playerName = player.Name,
	})

	local ok, res = pcall(function()
		return HttpService:PostAsync(
			Config.BackendUrl .. "/api/start",
			body,
			Enum.HttpContentType.ApplicationJson,
			false,
			HEADERS
		)
	end)
	if not ok then
		jobUpdate():FireClient(player, {
			state = "nope",
			stage = "nope",
			message = "Can't reach the factory. Is the backend running?",
			detail = tostring(res),
			repoUrl = nil,
			idea = idea.name or "",
		})
		return
	end

	local data = HttpService:JSONDecode(res)
	local jobId = data.jobId
	if not jobId then
		jobUpdate():FireClient(player, {
			state = "nope",
			stage = "nope",
			message = "The factory said something weird. Try again.",
			detail = tostring(res),
			repoUrl = nil,
			idea = idea.name or "",
		})
		return
	end

	local job = { jobId = jobId, finished = false, idea = idea.name or "" }
	table.insert(mine, job)
	activeJobs[player] = mine

	task.spawn(function()
		while true do
			task.wait(Config.PollSeconds)
			local ok2, res2 = pcall(function()
				return HttpService:GetAsync(
					Config.BackendUrl .. "/api/status?job=" .. jobId,
					false,
					HEADERS
				)
			end)
			if ok2 then
				local snap = HttpService:JSONDecode(res2)
				snap.idea = job.idea
				jobUpdate():FireClient(player, snap)
				if snap.state == "done" or snap.state == "failed" then
					job.finished = true
					break
				end
			end
		end
	end)
end

Players.PlayerRemoving:Connect(function(player)
	activeJobs[player] = nil
end)

return JobService
