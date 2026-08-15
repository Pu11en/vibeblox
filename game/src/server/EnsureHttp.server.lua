-- Make sure HTTP is allowed for this place (best effort).
-- IMPORTANT: if this errors, enable it in Studio:
--   File -> Game Settings -> Security -> "Allow HTTP Requests" -> ON
local HttpService = game:GetService("HttpService")

local ok, err = pcall(function()
	HttpService.HttpEnabled = true
end)
if ok then
	print("[Play2Build] HTTP enabled at runtime")
else
	warn(
		"[Play2Build] could not enable HTTP from script: "
			.. tostring(err)
			.. " - turn on File > Game Settings > Security > Allow HTTP Requests"
	)
end
