-- Client boot: build the UI, fetch idea cards, listen for job updates.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Remotes = require(ReplicatedStorage.Play2Build.Remotes)
local HUD = require(script.Parent.HUD)
local TerminalUI = require(script.Parent.TerminalUI)

local player = Players.LocalPlayer

local gui = Instance.new("ScreenGui")
gui.Name = "P2B_UI"
gui.ResetOnSpawn = false
gui.Parent = player:WaitForChild("PlayerGui")

HUD.build(gui)
TerminalUI.attach(gui, Remotes.waitFor("StartJob"))

-- Fetch the idea cards + questions (server got them from the factory)
task.spawn(function()
	local ok, d = pcall(function()
		return Remotes.waitFor("FetchData"):InvokeServer()
	end)
	if ok and d then
		TerminalUI.setData(d)
	end
end)

Remotes.waitFor("JobUpdate").OnClientEvent:Connect(function(snap)
	TerminalUI.onJobUpdate(snap)
end)
