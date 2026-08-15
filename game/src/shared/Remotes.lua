-- Shared remote registry. SERVER creates them at boot (Remotes.ensure*);
-- clients only find them (Remotes.get / Remotes.waitFor). Clients can never
-- create instances in ReplicatedStorage, so the server owns them.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Remotes = {}

local FOLDER_NAME = "P2B_Remotes"

local function container()
	local folder = ReplicatedStorage:FindFirstChild(FOLDER_NAME)
	if not folder then
		folder = Instance.new("Folder")
		folder.Name = FOLDER_NAME
		folder.Parent = ReplicatedStorage
	end
	return folder
end

function Remotes.ensureEvent(name)
	local c = container()
	local r = c:FindFirstChild(name)
	if not r then
		r = Instance.new("RemoteEvent")
		r.Name = name
		r.Parent = c
	end
	return r
end

function Remotes.ensureFunction(name)
	local c = container()
	local r = c:FindFirstChild(name)
	if not r then
		r = Instance.new("RemoteFunction")
		r.Name = name
		r.Parent = c
	end
	return r
end

function Remotes.get(name)
	local folder = ReplicatedStorage:FindFirstChild(FOLDER_NAME)
	return folder and folder:FindFirstChild(name)
end

function Remotes.waitFor(name)
	local r = Remotes.get(name)
	while not r do
		task.wait(0.1)
		r = Remotes.get(name)
	end
	return r
end

return Remotes
