-- Procedural tycoon map. Small, neon, and cozy.
-- Everything lives under Workspace.P2B_Map so the client can find named bits.
local Workspace = game:GetService("Workspace")

local BuildMap = {}

local function part(name, parent, size, pos, color, material)
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.Position = pos
	p.Color = color
	p.Material = material or Enum.Material.Plastic
	p.Anchored = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent
	return p
end

local function neon(parent, cf, color, size, name)
	local p = Instance.new("Part")
	p.Name = name or "neon"
	p.CFrame = cf
	p.Size = size
	p.Color = color
	p.Material = Enum.Material.Neon
	p.Anchored = true
	p.CanCollide = false
	p.Parent = parent
	return p
end

local NIGHT_BLUE = Color3.fromRGB(24, 26, 48)
local TILE_A = Color3.fromRGB(48, 52, 96)
local TILE_B = Color3.fromRGB(40, 44, 84)
local CYAN = Color3.fromRGB(0, 229, 255)
local PINK = Color3.fromRGB(255, 64, 200)
local GREEN = Color3.fromRGB(70, 255, 130)
local GOLD = Color3.fromRGB(255, 210, 80)
local WHITE = Color3.fromRGB(240, 244, 255)

function BuildMap.build()
	local map = Instance.new("Folder")
	map.Name = "P2B_Map"
	map.Parent = Workspace

	-- The main platform
	part("Floor", map, Vector3.new(64, 1, 44), Vector3.new(0, -0.5, 0), NIGHT_BLUE)

	-- Spawn pad + SpawnLocation so players ALWAYS appear on solid ground
	local _spawnPad = part(
		"SpawnPad",
		map,
		Vector3.new(8, 0.4, 8),
		Vector3.new(0, 0.4, 0),
		Color3.fromRGB(40, 44, 84)
	)
	neon(map, CFrame.new(0, 0.8, 0), CYAN, Vector3.new(7.4, 0.15, 7.4), "SpawnRing")
	local spawnLoc = Instance.new("SpawnLocation")
	spawnLoc.Name = "SpawnLocation"
	spawnLoc.Neutral = true
	spawnLoc.Duration = 0
	spawnLoc.Anchored = true
	spawnLoc.Size = Vector3.new(6, 0.4, 6)
	spawnLoc.Position = Vector3.new(0, 1.2, 0)
	spawnLoc.Color = Color3.fromRGB(30, 34, 64)
	spawnLoc.Material = Enum.Material.Neon
	spawnLoc.CanCollide = false
	spawnLoc.Parent = map
	spawnLoc.Transparency = 0.4
	-- checkered tiles
	for x = -30, 30, 6 do
		for z = -20, 20, 6 do
			local tile = part(
				"Tile",
				map,
				Vector3.new(5.6, 1.02, 5.6),
				Vector3.new(x, 0, z),
				(x + z) % 12 == 0 and TILE_A or TILE_B
			)
			tile.CanCollide = false
		end
	end
	-- glowing rim
	for x = -32, 32, 4 do
		neon(
			map,
			CFrame.new(x, 1, -22) * CFrame.Angles(0, 0, math.rad(90)),
			CYAN,
			Vector3.new(4, 0.3, 0.3)
		)
		neon(
			map,
			CFrame.new(x, 1, 22) * CFrame.Angles(0, 0, math.rad(90)),
			CYAN,
			Vector3.new(4, 0.3, 0.3)
		)
	end
	for z = -20, 20, 4 do
		neon(
			map,
			CFrame.new(-32, 1, z) * CFrame.Angles(0, math.rad(90), 0),
			CYAN,
			Vector3.new(4, 0.3, 0.3)
		)
		neon(
			map,
			CFrame.new(32, 1, z) * CFrame.Angles(0, math.rad(90), 0),
			CYAN,
			Vector3.new(4, 0.3, 0.3)
		)
	end

	-- The kiosk (decorative - the real UI is a screen overlay)
	part("Kiosk", map, Vector3.new(6, 4.5, 3), Vector3.new(0, 2.25, -8), Color3.fromRGB(34, 36, 66))
	part(
		"KioskScreen",
		map,
		Vector3.new(4.6, 2.6, 0.2),
		Vector3.new(0, 3.2, -6.45),
		CYAN,
		Enum.Material.Neon
	)

	-- WELCOME signboard - big readable surface, both sides, tagline below
	local signboard = part(
		"WelcomeSign",
		map,
		Vector3.new(24, 3.6, 0.4),
		Vector3.new(0, 6.6, -9.5),
		Color3.fromRGB(24, 26, 52)
	)
	neon(map, CFrame.new(0, 8.45, -9.5), PINK, Vector3.new(24.6, 0.3, 0.5), "SignRim")
	for i, face in ipairs({ Enum.NormalId.Front, Enum.NormalId.Back }) do
		local gui = Instance.new("SurfaceGui")
		gui.Name = "WelcomeGui" .. i
		gui.Face = face
		gui.CanvasSize = Vector2.new(1200, 180)
		gui.Parent = signboard
		local label = Instance.new("TextLabel")
		label.Size = UDim2.fromScale(0.94, 0.7)
		label.Position = UDim2.fromScale(0.03, 0.05)
		label.BackgroundTransparency = 1
		label.Text = "👋 WELCOME TO PLAY2BUILD!"
		label.TextColor3 = Color3.fromRGB(255, 255, 255)
		label.Font = Enum.Font.GothamBlack
		label.TextScaled = true
		label.Parent = gui
		local sub = Instance.new("TextLabel")
		sub.Size = UDim2.fromScale(0.94, 0.22)
		sub.Position = UDim2.fromScale(0.03, 0.72)
		sub.BackgroundTransparency = 1
		sub.Text = "pick an idea  ·  answer easy questions  ·  get a REAL repo"
		sub.TextColor3 = Color3.fromRGB(0, 229, 255)
		sub.Font = Enum.Font.GothamBold
		sub.TextScaled = true
		sub.Parent = gui
	end
	-- little flags
	for i, dx in ipairs({ -2, 0, 2 }) do
		part("Pole", map, Vector3.new(0.2, 2.4, 0.2), Vector3.new(dx, 4.4, -12), WHITE)
		local flag = part(
			"Flag",
			map,
			Vector3.new(1.4, 0.8, 0.12),
			Vector3.new(dx + 0.8, 5.6, -12),
			i == 2 and CYAN or PINK
		)
		flag.CanCollide = false
	end

	-- Worker pads + bots (client animates the bots by index)
	local bots = Instance.new("Folder")
	bots.Name = "WorkerBots"
	bots.Parent = map
	for i = 1, 3 do
		local z = -12 + (i - 1) * 5
		part(
			"Pad" .. i,
			map,
			Vector3.new(3.4, 0.3, 3.4),
			Vector3.new(-22, 0.3, z),
			Color3.fromRGB(30, 32, 60)
		)
		neon(map, CFrame.new(-22, 0.65, z), CYAN, Vector3.new(3, 0.1, 3), "PadRing" .. i)
		local bot =
			part("Bot" .. i, bots, Vector3.new(1.4, 1.4, 1.4), Vector3.new(-22, 1.5, z), WHITE)
		bot.CanCollide = false
		local eye = part(
			"Eye" .. i,
			bot,
			Vector3.new(0.5, 0.5, 0.2),
			Vector3.new(-22, 1.6, z + 0.8),
			CYAN,
			Enum.Material.Neon
		)
		eye.CanCollide = false
		local hat =
			part("Hat" .. i, bot, Vector3.new(0.9, 0.4, 0.9), Vector3.new(-22, 2.5, z), GOLD)
		hat.CanCollide = false
	end

	-- The repo vault - flashes green when a build lands
	part("Vault", map, Vector3.new(5, 3.4, 4), Vector3.new(24, 1.7, 0), Color3.fromRGB(36, 38, 72))
	local vaultDoor = part(
		"VaultDoor",
		map,
		Vector3.new(3.4, 2.6, 0.2),
		Vector3.new(24, 1.7, -2.2),
		GREEN,
		Enum.Material.Neon
	)
	vaultDoor.CanCollide = false

	-- A few neon columns for vibes
	for i, spot in ipairs({ { -26, 16 }, { 26, 16 }, { -26, -16 }, { 26, -16 } }) do
		part(
			"Column",
			map,
			Vector3.new(1.4, 8, 1.4),
			Vector3.new(spot[1], 4, spot[2]),
			Color3.fromRGB(30, 32, 60)
		)
		neon(
			map,
			CFrame.new(spot[1], 8, spot[2]),
			i % 2 == 0 and PINK or CYAN,
			Vector3.new(1.6, 0.3, 1.6),
			"Cap"
		)
	end
end

return BuildMap
