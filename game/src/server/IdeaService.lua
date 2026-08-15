-- Fetches idea cards + questions from the factory once at boot.
-- Falls back to the built-in list if the factory is unreachable.
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Play2Build.Config)

local IdeaService = {}

local cache = nil

local HEADERS = {
	["Content-Type"] = "application/json",
	["X-P2B-Secret"] = Config.Secret,
}

function IdeaService.boot()
	local ok, ideas = pcall(function()
		return HttpService:GetAsync(Config.BackendUrl .. "/api/ideas", false, HEADERS)
	end)
	local ok2, questions = pcall(function()
		return HttpService:GetAsync(Config.BackendUrl .. "/api/questions", false, HEADERS)
	end)
	if ok and ok2 then
		local ideasData, qData
		local ok3, ideasJson = pcall(HttpService.JSONDecode, HttpService, ideas)
		local ok4, questionsJson = pcall(HttpService.JSONDecode, HttpService, questions)
		if ok3 and ok4 then
			ideasData = ideasJson.ideas
			qData = questionsJson.questions
			if
				type(ideasData) == "table"
				and #ideasData > 0
				and type(qData) == "table"
				and #qData > 0
			then
				cache = { ideas = ideasData, questions = qData }
				print("[Play2Build] got " .. #ideasData .. " ideas from the factory")
				return
			end
		end
	end
	print("[Play2Build] factory unreachable - using built-in idea cards")
	cache = { ideas = Config.FallbackIdeas, questions = Config.FallbackQuestions }
end

function IdeaService.data()
	return cache
end

return IdeaService
