-- The game's mouth: reads progress out loud in plain words (mute-able).
local Players = game:GetService("Players")
local TextToSpeechService = game:GetService("TextToSpeechService")

local Talk = { muted = false }

function Talk.say(text)
	if Talk.muted then
		return
	end
	local player = Players.LocalPlayer
	if not player then
		return
	end
	-- SpeakAsync yields and can fail (no mic access, studio quirks) - never break the game
	task.spawn(function()
		local ok, tts = pcall(function()
			return TextToSpeechService:SpeakAsync(player, text, 1.0, 1.0)
		end)
		if ok and tts then
			pcall(function()
				tts:Play()
			end)
		end
	end)
end

function Talk.toggle()
	Talk.muted = not Talk.muted
	return Talk.muted
end

return Talk
