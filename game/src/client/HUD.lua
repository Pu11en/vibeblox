-- Always-on top bar (cash, workers, mute) + toast notifications.

local ReplicatedStorage = game:GetService("ReplicatedStorage")


local Config = require(ReplicatedStorage.Play2Build.Config)
local UI = require(script.Parent.UI)
local Tycoon = require(script.Parent.TycoonState)
local Talk = require(script.Parent.Talk)

local HUD = {}

local cashLabel, workerLabel, muteButton
local toastStack

local COLORS = UI.Colors

function HUD.build(parent)
	local bar = UI.frame(parent, {
		Position = UDim2.fromScale(0.02, 0.02),
		Size = UDim2.fromScale(0.96, 0.09),
		BackgroundColor3 = COLORS.panel,
		BackgroundTransparency = 0.15,
	})
	UI.text(bar, {
		Text = "PLAY2BUILD",
		Position = UDim2.fromScale(0.03, 0),
		Size = UDim2.fromScale(0.25, 1),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBlack,
		TextSize = 34,
		TextColor3 = COLORS.accent,
		TextXAlignment = Enum.TextXAlignment.Left,
	})
	cashLabel = UI.text(bar, {
		Text = "💰 " .. tostring(Tycoon.cash),
		Position = UDim2.fromScale(0.55, 0),
		Size = UDim2.fromScale(0.18, 1),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBold,
		TextSize = 28,
		TextColor3 = COLORS.gold,
	})
	workerLabel = UI.text(bar, {
		Text = "👷 " .. tostring(Tycoon.workers),
		Position = UDim2.fromScale(0.73, 0),
		Size = UDim2.fromScale(0.12, 1),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBold,
		TextSize = 28,
		TextColor3 = COLORS.green,
	})
	muteButton = UI.button(bar, "🔊", UDim2.fromScale(0.88, 0.1), UDim2.fromScale(0.09, 0.8), function()
		local muted = Talk.toggle()
		muteButton.Text = muted and "🔇" or "🔊"
	end, { color = COLORS.panelDark, textSize = 26, radius = 10 })

	toastStack = UI.new("Frame", parent, {
		Position = UDim2.fromScale(0.02, 0.5),
		Size = UDim2.new(0, 460, 0, 260),
		BackgroundTransparency = 1,
		ZIndex = 40,
	})

	Tycoon.listen(function()
		cashLabel.Text = "💰 " .. tostring(Tycoon.cash)
		workerLabel.Text = "👷 " .. tostring(Tycoon.workers) .. "/" .. tostring(Config.MaxWorkers)
	end)
end

local toastCount = 0

function HUD.toast(text, color)
	toastCount += 1
	local slot = toastCount
	local t = UI.frame(toastStack, {
		Position = UDim2.new(0, 0, 0, (slot - 1) * 74),
		Size = UDim2.new(0, 440, 0, 64),
		BackgroundColor3 = color or COLORS.panel,
		BackgroundTransparency = 0.1,
		ZIndex = 50,
	})
	UI.text(t, {
		Text = text,
		Position = UDim2.fromScale(0.05, 0),
		Size = UDim2.fromScale(0.9, 1),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBold,
		TextSize = 20,
		TextColor3 = COLORS.text,
		TextWrapped = true,
		TextXAlignment = Enum.TextXAlignment.Left,
	})
	task.spawn(function()
		task.wait(4)
		t:TweenSize(UDim2.fromScale(0, 0), Enum.EasingDirection.In, Enum.EasingStyle.Quad, 0.3, true)
		task.wait(0.35)
		t:Destroy()
	end)
	return t
end

return HUD
