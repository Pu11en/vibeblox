-- The terminal: hub -> pick idea -> answer questions -> watch workers -> get repo.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Config = require(ReplicatedStorage.Play2Build.Config)
local UI = require(script.Parent.UI)
local Tycoon = require(script.Parent.TycoonState)
local HUD = require(script.Parent.HUD)
local Talk = require(script.Parent.Talk)
local Bots = require(script.Parent.Bots)

local TerminalUI = {}

local COLORS = UI.Colors

local root
local pages = {}
local data = { ideas = Config.FallbackIdeas, questions = Config.FallbackQuestions }
local currentPage = nil
local currentIdea = nil
local currentAnswers = {}
local activeBot = nil
local startJobRemote = nil

local STAGE_FRACTION = {
	queued = 0.1, planning = 0.2, writing = 0.5, checking = 0.7, pushing = 0.9, done = 1,
}

local function show(page)
	if currentPage then
		currentPage.Visible = false
	end
	currentPage = page
	page.Visible = true
end

local function page(name)
	return pages[name]
end

-- ---------------------------------------------------------------- flow

local function startPlanning(idea)
	currentIdea = idea
	currentAnswers = {}
	page("questions").drawQuestion(data.questions[1], 1)
	show(page("questions"))
end

local function startBuild()
	if Tycoon.idleWorkers() <= 0 then
		HUD.toast("No free workers! Hire one or wait. 👷", COLORS.danger)
		show(page("hub"))
		return
	end
	Tycoon.activeJobs = (Tycoon.activeJobs or 0) + 1
	activeBot = Bots.take()
	local b = page("building")
	b.ideaLabel.Text = currentIdea.emoji .. "  " .. currentIdea.name
	b.status.Text = "Workers are thinking…"
	b.plan.Text = ""
	b.bar.Size = UDim2.fromScale(0.05, 1)
	show(b)
	Talk.say("Workers are building your " .. currentIdea.name .. "!")
	startJobRemote:FireServer(currentIdea, currentAnswers)
end

-- ---------------------------------------------------------------- hub

local function buildHub()
	local p = UI.frame(root, {
		Position = UDim2.fromScale(0, 0),
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
	})
	UI.text(p, {
		Text = "PLAY2BUILD",
		Position = UDim2.fromScale(0, 0.08),
		Size = UDim2.fromScale(1, 0.2),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBlack,
		TextSize = 90,
		TextColor3 = COLORS.accent,
	})
	UI.text(p, {
		Text = "Pick an idea. Tap easy answers.\nThe workers build it. You get a REAL GitHub repo.",
		Position = UDim2.fromScale(0.1, 0.26),
		Size = UDim2.fromScale(0.8, 0.15),
		BackgroundTransparency = 1,
		Font = Enum.Font.Gotham,
		TextSize = 28,
		TextColor3 = COLORS.dim,
		TextWrapped = true,
	})
	UI.button(p, "🗣️  ASK THE WORKERS", UDim2.fromScale(0.3, 0.48), UDim2.fromScale(0.4, 0.12),
		function()
			show(page("ideas"))
		end, { color = COLORS.pink, textSize = 34 })
	UI.button(p, "🛒  SHOP", UDim2.fromScale(0.38, 0.66), UDim2.fromScale(0.24, 0.09),
		function()
			show(page("shop"))
		end, { color = COLORS.panel, textSize = 26 })
	pages.hub = p
end

-- ---------------------------------------------------------------- ideas

local function buildIdeas()
	local p = UI.frame(root, {
		Position = UDim2.fromScale(0, 0),
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
	})
	UI.text(p, {
		Text = "What do you want the workers to make?",
		Position = UDim2.fromScale(0.05, 0.02),
		Size = UDim2.fromScale(0.6, 0.1),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBlack,
		TextSize = 44,
		TextColor3 = COLORS.text,
		TextXAlignment = Enum.TextXAlignment.Left,
	})
	UI.button(p, "⬅ BACK", UDim2.fromScale(0.83, 0.025), UDim2.fromScale(0.12, 0.08),
		function()
			show(page("hub"))
		end, { color = COLORS.panelDark, textSize = 22 })
	UI.button(p, "🎲 SURPRISE ME", UDim2.fromScale(0.05, 0.14), UDim2.fromScale(0.2, 0.07),
		function()
			local pick = data.ideas[math.random(1, #data.ideas)]
			startPlanning(pick)
		end, { color = COLORS.gold, textSize = 20 })

	local gridParent = UI.new("Frame", p, {
		Position = UDim2.fromScale(0.05, 0.23),
		Size = UDim2.fromScale(0.9, 0.74),
		BackgroundTransparency = 1,
	})
	UI.scrollingGrid(gridParent, data.ideas, function(idea)
		local card = UI.button(nil, "", nil, nil, function()
			startPlanning(idea)
		end, { color = COLORS.panel, radius = 16 })
		card.Size = UDim2.fromScale(1, 1)
		card.Position = UDim2.fromScale(0, 0)
		UI.text(card, {
			Text = idea.emoji,
			Position = UDim2.fromScale(0, 0.04),
			Size = UDim2.fromScale(1, 0.4),
			BackgroundTransparency = 1,
			Font = Enum.Font.GothamBlack,
			TextSize = 56,
			TextColor3 = COLORS.text,
		})
		UI.text(card, {
			Text = idea.name,
			Position = UDim2.fromScale(0.06, 0.44),
			Size = UDim2.fromScale(0.88, 0.2),
			BackgroundTransparency = 1,
			Font = Enum.Font.GothamBold,
			TextSize = 24,
			TextColor3 = COLORS.accent,
			TextXAlignment = Enum.TextXAlignment.Left,
		})
		UI.text(card, {
			Text = idea.description,
			Position = UDim2.fromScale(0.06, 0.62),
			Size = UDim2.fromScale(0.88, 0.34),
			BackgroundTransparency = 1,
			Font = Enum.Font.Gotham,
			TextSize = 17,
			TextColor3 = COLORS.dim,
			TextWrapped = true,
			TextXAlignment = Enum.TextXAlignment.Left,
			TextYAlignment = Enum.TextYAlignment.Top,
		})
		return card
	end)
	pages.ideas = p
end

-- ---------------------------------------------------------------- questions

local function buildQuestions()
	local p = UI.frame(root, {
		Position = UDim2.fromScale(0, 0),
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
	})
	local title = UI.text(p, {
		Text = "",
		Position = UDim2.fromScale(0.1, 0.1),
		Size = UDim2.fromScale(0.8, 0.12),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBlack,
		TextSize = 40,
		TextColor3 = COLORS.text,
		TextWrapped = true,
	})
	local dots = UI.text(p, {
		Text = "",
		Position = UDim2.fromScale(0.1, 0.22),
		Size = UDim2.fromScale(0.8, 0.06),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBold,
		TextSize = 22,
		TextColor3 = COLORS.dim,
	})
	local optionsFrame = UI.new("Frame", p, {
		Position = UDim2.fromScale(0.1, 0.32),
		Size = UDim2.fromScale(0.8, 0.5),
		BackgroundTransparency = 1,
	})
	UI.button(p, "⬅ BACK", UDim2.fromScale(0.83, 0.88), UDim2.fromScale(0.12, 0.07),
		function()
			show(page("ideas"))
		end, { color = COLORS.panelDark, textSize = 20 })

	local function drawQuestion(question, index)
		title.Text = question.text
		dots.Text = ""
		for i = 1, #data.questions do
			dots.Text ..= (i < index and "● " or (i == index and "◉ " or "○ "))
		end
		for _, child in ipairs(optionsFrame:GetChildren()) do
			child:Destroy()
		end
		local y = 0
		for _, opt in ipairs(question.options) do
			local btn = UI.button(optionsFrame, opt.emoji .. "  " .. opt.label,
				UDim2.fromScale(0.1, y), UDim2.fromScale(0.8, 0.26), function()
					currentAnswers[question.id] = { id = question.id, label = opt.label }
					if index < #data.questions then
						drawQuestion(data.questions[index + 1], index + 1)
					else
						startBuild()
					end
				end, { color = COLORS.panel, textSize = 30 })
			UI.text(btn, {
				Text = opt.description,
				Position = UDim2.fromScale(0.02, 0.62),
				Size = UDim2.fromScale(0.96, 0.3),
				BackgroundTransparency = 1,
				Font = Enum.Font.Gotham,
				TextSize = 17,
				TextColor3 = COLORS.dim,
				TextWrapped = true,
			})
			y += 0.27
		end
	end
	p.drawQuestion = drawQuestion
	pages.questions = p
end

-- ---------------------------------------------------------------- building

local function buildBuilding()
	local p = UI.frame(root, {
		Position = UDim2.fromScale(0, 0),
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
	})
	local ideaLabel = UI.text(p, {
		Text = "",
		Position = UDim2.fromScale(0.1, 0.1),
		Size = UDim2.fromScale(0.8, 0.1),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBlack,
		TextSize = 40,
		TextColor3 = COLORS.accent,
	})
	local status = UI.text(p, {
		Text = "Workers are thinking…",
		Position = UDim2.fromScale(0.1, 0.22),
		Size = UDim2.fromScale(0.8, 0.09),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBold,
		TextSize = 30,
		TextColor3 = COLORS.text,
	})
	local plan = UI.text(p, {
		Text = "",
		Position = UDim2.fromScale(0.15, 0.32),
		Size = UDim2.fromScale(0.7, 0.12),
		BackgroundTransparency = 1,
		Font = Enum.Font.Gotham,
		TextSize = 22,
		TextColor3 = COLORS.dim,
		TextWrapped = true,
	})
	local barBg = UI.frame(p, {
		Position = UDim2.fromScale(0.15, 0.5),
		Size = UDim2.fromScale(0.7, 0.05),
		BackgroundColor3 = COLORS.panelDark,
	})
	local bar = UI.frame(barBg, {
		Position = UDim2.fromScale(0, 0),
		Size = UDim2.fromScale(0.05, 1),
		BackgroundColor3 = COLORS.pink,
	})
	UI.text(p, {
		Text = "The workers are doing REAL work. This takes a little time.",
		Position = UDim2.fromScale(0.1, 0.6),
		Size = UDim2.fromScale(0.8, 0.08),
		BackgroundTransparency = 1,
		Font = Enum.Font.Gotham,
		TextSize = 20,
		TextColor3 = COLORS.dim,
	})
	p.ideaLabel = ideaLabel
	p.status = status
	p.plan = plan
	p.bar = bar
	pages.building = p
end

-- ---------------------------------------------------------------- done / failed

local function buildDone()
	local p = UI.frame(root, {
		Position = UDim2.fromScale(0, 0),
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
	})
	UI.text(p, {
		Text = "🎉 REPO IS LIVE!",
		Position = UDim2.fromScale(0.1, 0.1),
		Size = UDim2.fromScale(0.8, 0.15),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBlack,
		TextSize = 60,
		TextColor3 = COLORS.green,
	})
	UI.text(p, {
		Text = "Real code. On your GitHub. Made by your workers.",
		Position = UDim2.fromScale(0.1, 0.25),
		Size = UDim2.fromScale(0.8, 0.07),
		BackgroundTransparency = 1,
		Font = Enum.Font.Gotham,
		TextSize = 26,
		TextColor3 = COLORS.dim,
	})
	local urlBox = UI.new("TextBox", p, {
		Text = "",
		Position = UDim2.fromScale(0.15, 0.36),
		Size = UDim2.fromScale(0.7, 0.09),
		BackgroundColor3 = COLORS.panelDark,
		TextColor3 = COLORS.accent,
		Font = Enum.Font.Code,
		TextSize = 24,
		TextEditable = false,
		ClearTextOnFocus = false,
		TextXAlignment = Enum.TextXAlignment.Center,
	})
	UI.round(urlBox, 10)
	local cashLabel = UI.text(p, {
		Text = "",
		Position = UDim2.fromScale(0.1, 0.5),
		Size = UDim2.fromScale(0.8, 0.1),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBlack,
		TextSize = 44,
		TextColor3 = COLORS.gold,
	})
	UI.button(p, "🎁  MAKE ANOTHER ONE", UDim2.fromScale(0.3, 0.66), UDim2.fromScale(0.4, 0.1),
		function()
			show(page("ideas"))
		end, { color = COLORS.pink, textSize = 30 })
	UI.button(p, "🏠 HOME", UDim2.fromScale(0.4, 0.8), UDim2.fromScale(0.2, 0.08),
		function()
			show(page("hub"))
		end, { color = COLORS.panel, textSize = 22 })
	p.urlBox = urlBox
	p.cashLabel = cashLabel
	pages.done = p
end

local function buildFailed()
	local p = UI.frame(root, {
		Position = UDim2.fromScale(0, 0),
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
	})
	UI.text(p, {
		Text = "😵 Workers hit a snag",
		Position = UDim2.fromScale(0.1, 0.15),
		Size = UDim2.fromScale(0.8, 0.12),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBlack,
		TextSize = 48,
		TextColor3 = COLORS.danger,
	})
	local detail = UI.text(p, {
		Text = "",
		Position = UDim2.fromScale(0.15, 0.3),
		Size = UDim2.fromScale(0.7, 0.2),
		BackgroundTransparency = 1,
		Font = Enum.Font.Gotham,
		TextSize = 22,
		TextColor3 = COLORS.dim,
		TextWrapped = true,
	})
	UI.button(p, "🔁 TRY AGAIN", UDim2.fromScale(0.3, 0.55), UDim2.fromScale(0.4, 0.1),
		function()
			show(page("ideas"))
		end, { color = COLORS.panel, textSize = 28 })
	UI.button(p, "🏠 HOME", UDim2.fromScale(0.4, 0.7), UDim2.fromScale(0.2, 0.08),
		function()
			show(page("hub"))
		end, { color = COLORS.panelDark, textSize = 22 })
	p.detail = detail
	pages.failed = p
end

-- ---------------------------------------------------------------- shop

local function buildShop()
	local p = UI.frame(root, {
		Position = UDim2.fromScale(0, 0),
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
	})
	UI.text(p, {
		Text = "🛒 Shop",
		Position = UDim2.fromScale(0.1, 0.06),
		Size = UDim2.fromScale(0.5, 0.1),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBlack,
		TextSize = 44,
		TextColor3 = COLORS.text,
	})
	UI.button(p, "⬅ BACK", UDim2.fromScale(0.83, 0.07), UDim2.fromScale(0.12, 0.08),
		function()
			show(page("hub"))
		end, { color = COLORS.panelDark, textSize = 22 })

	local function shopCard(y, emoji, name, price, desc, owned, buyFn)
		local card = UI.frame(p, {
			Position = UDim2.fromScale(0.12, y),
			Size = UDim2.fromScale(0.76, 0.2),
			BackgroundColor3 = COLORS.panel,
		})
		UI.text(card, {
			Text = emoji,
			Position = UDim2.fromScale(0.03, 0.05),
			Size = UDim2.fromScale(0.15, 0.9),
			BackgroundTransparency = 1,
			Font = Enum.Font.GothamBlack,
			TextSize = 44,
		})
		UI.text(card, {
			Text = name .. (owned and "  ✅" or ""),
			Position = UDim2.fromScale(0.2, 0.08),
			Size = UDim2.fromScale(0.5, 0.35),
			BackgroundTransparency = 1,
			Font = Enum.Font.GothamBold,
			TextSize = 28,
			TextColor3 = COLORS.text,
			TextXAlignment = Enum.TextXAlignment.Left,
		})
		UI.text(card, {
			Text = desc,
			Position = UDim2.fromScale(0.2, 0.42),
			Size = UDim2.fromScale(0.5, 0.5),
			BackgroundTransparency = 1,
			Font = Enum.Font.Gotham,
			TextSize = 18,
			TextColor3 = COLORS.dim,
			TextWrapped = true,
			TextXAlignment = Enum.TextXAlignment.Left,
			TextYAlignment = Enum.TextYAlignment.Top,
		})
		local btn = UI.button(card, "💰 " .. tostring(price),
			UDim2.fromScale(0.72, 0.2), UDim2.fromScale(0.25, 0.6), buyFn,
			{ color = COLORS.green, textSize = 26 })
		if owned then
			btn.Text = "OWNED"
			btn.BackgroundColor3 = COLORS.panelDark
		end
		return btn
	end

	shopCard(0.2, "👷", "Hire a Worker", Config.Economy.WorkerPrice,
		"One more worker = one more project at the same time.", false, function()
			if Tycoon.hireWorker() then
				HUD.toast("Worker hired! 👷", COLORS.green)
				show(page("shop"))
			else
				HUD.toast("Not enough cash! Finish a project! 🛠️", COLORS.danger)
			end
		end)
	shopCard(0.44, "💰", "Cash Machine", Config.Economy.CashMachinePrice,
		"Finishing a project earns DOUBLE cash.", false, function()
			if Tycoon.buyCashMachine() then
				HUD.toast("Cash machine installed! 💰", COLORS.gold)
				show(page("shop"))
			else
				HUD.toast("Not enough cash! Finish a project! 🛠️", COLORS.danger)
			end
		end)
	pages.shop = p
end

-- ---------------------------------------------------------------- updates

function TerminalUI.setData(d)
	if d and d.ideas and d.questions then
		data = d
	end
end

local function updateProgress(snap)
	local b = page("building")
	local frac = STAGE_FRACTION[snap.stage] or 0.1
	TweenService:Create(b.bar, TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Size = UDim2.fromScale(frac, 1) }):Play()
	if snap.message and snap.message ~= "" then
		b.status.Text = snap.message
	end
	if snap.detail and snap.detail ~= "" and snap.stage == "planning" then
		b.plan.Text = snap.detail
	end
	if snap.stage == "writing" then
		b.plan.Text = snap.detail
	end
end

function TerminalUI.onJobUpdate(snap)
	if not snap then
		return
	end
	if snap.state == "nope" then
		HUD.toast(snap.message, COLORS.danger)
		Tycoon.activeJobs = math.max(0, (Tycoon.activeJobs or 1) - 1)
		Bots.release(activeBot)
		activeBot = nil
		if page("building") and page("building").Visible then
			show(page("hub"))
		end
		return
	end
	if snap.state == "running" then
		if page("building") and not page("building").Visible then
			show(page("building"))
		end
		updateProgress(snap)
		return
	end
	if snap.state == "done" then
		Tycoon.activeJobs = math.max(0, (Tycoon.activeJobs or 1) - 1)
		Bots.release(activeBot)
		activeBot = nil
		Bots.flashVault()
		local sizeMult = 1
		for _, a in ipairs(currentAnswers) do
			if a.id == "size" then
				sizeMult = Config.Economy.RewardSizeMult[a.label:lower()] or 1
			end
		end
		local reward = Tycoon.rewardFor(sizeMult)
		Tycoon.addCash(reward)
		local d = page("done")
		d.urlBox.Text = snap.repoUrl or "???"
		d.cashLabel.Text = "💰 +" .. tostring(reward) .. " cash!"
		show(d)
		HUD.toast("Repo is live! 🎉", COLORS.green)
		Talk.say("Your " .. (snap.idea or currentIdea and currentIdea.name or "project")
			.. " is live! Go check it out!")
		return
	end
	if snap.state == "failed" then
		Tycoon.activeJobs = math.max(0, (Tycoon.activeJobs or 1) - 1)
		Bots.release(activeBot)
		activeBot = nil
		local f = page("failed")
		f.detail.Text = snap.detail or snap.message or "Something went wrong."
		show(f)
		HUD.toast("The build failed 😵", COLORS.danger)
	end
end

function TerminalUI.attach(screenGui, startJob)
	root = screenGui
	startJobRemote = startJob
	buildHub()
	buildIdeas()
	buildQuestions()
	buildBuilding()
	buildDone()
	buildFailed()
	buildShop()
	show(page("hub"))
end

return TerminalUI
