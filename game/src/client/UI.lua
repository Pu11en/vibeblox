-- Tiny UI kit: frames, text, buttons with hover, panels.
-- Everything scale-based so it looks fine at any screen size.
local UI = {}

local COLORS = {
	bg = Color3.fromRGB(20, 22, 42),
	panel = Color3.fromRGB(32, 35, 62),
	panelDark = Color3.fromRGB(26, 28, 50),
	text = Color3.fromRGB(240, 244, 255),
	dim = Color3.fromRGB(150, 156, 190),
	accent = Color3.fromRGB(0, 229, 255),
	pink = Color3.fromRGB(255, 64, 200),
	green = Color3.fromRGB(70, 255, 130),
	gold = Color3.fromRGB(255, 210, 80),
	danger = Color3.fromRGB(255, 90, 90),
}

UI.Colors = COLORS

local function apply(instance, props)
	for k, v in pairs(props) do
		instance[k] = v
	end
end

function UI.new(className, parent, props)
	local inst = Instance.new(className)
	inst.Parent = parent
	if props then
		apply(inst, props)
	end
	return inst
end

function UI.frame(parent, props)
	local f = UI.new("Frame", parent, props)
	UI.new("UICorner", f, { CornerRadius = UDim.new(0, 12) })
	return f
end

function UI.text(parent, props)
	return UI.new("TextLabel", parent, props)
end

function UI.round(parent, radius)
	return UI.new("UICorner", parent, { CornerRadius = UDim.new(0, radius or 12) })
end

function UI.stroke(parent, color, thickness)
	UI.new("UIStroke", parent, {
		Color = color or Color3.new(1, 1, 1),
		Thickness = thickness or 1,
		Transparency = 0.75,
		ApplyStrokeMode = Enum.ApplyStrokeMode.Border,
	})
end

function UI.button(parent, text, position, size, onClick, opts)
	opts = opts or {}
	local b = UI.new("TextButton", parent, {
		Text = text,
		Position = position,
		Size = size,
		BackgroundColor3 = opts.color or COLORS.panel,
		TextColor3 = opts.textColor or COLORS.text,
		Font = opts.font or Enum.Font.GothamBold,
		TextSize = opts.textSize or 24,
		AutoButtonColor = false,
		ZIndex = opts.zindex or 1,
		TextWrapped = true,
	})
	UI.round(b, opts.radius or 14)
	UI.stroke(b, opts.stroke or COLORS.dim, opts.strokeThickness or 1)

	b.MouseEnter:Connect(function()
		b:TweenSize(UDim2.fromScale(b.Size.X.Scale * 1.03, b.Size.Y.Scale * 1.03),
			Enum.EasingDirection.Out, Enum.EasingStyle.Quad, 0.12, true)
	end)
	b.MouseLeave:Connect(function()
		b:TweenSize(UDim2.fromScale(b.Size.X.Scale / 1.03, b.Size.Y.Scale / 1.03),
			Enum.EasingDirection.Out, Enum.EasingStyle.Quad, 0.12, true)
	end)
	if onClick then
		b.Activated:Connect(onClick)
	end
	return b
end

function UI.scrollingGrid(parent, items, itemFactory)
	local clip = UI.frame(parent, {
		Position = UDim2.fromScale(0, 0),
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
	})
	UI.new("UIClippingBehavior", clip, { ClipsDescendants = true })
	local list = UI.new("ScrollingFrame", clip, {
		Position = UDim2.fromScale(0, 0),
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = COLORS.dim,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.fromScale(0, 0),
	})
	local grid = UI.new("UIGridLayout", list, {
		CellSize = UDim2.fromScale(0.31, 0.42),
		CellPadding = UDim2.fromScale(0.02, 0.02),
		SortOrder = Enum.SortOrder.LayoutOrder,
	})
	for i, item in ipairs(items) do
		local card = itemFactory(item, i)
		if card then
			card.LayoutOrder = i
			card.Parent = list
		end
	end
	grid:ApplyLayout() -- force layout before first frame
	return clip
end

return UI
