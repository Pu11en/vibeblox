-- The tycoon wallet: cash, workers, upgrades. Session-only (resets on leave).
-- Money is the fun part - the real reward is the repo.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Vibeblox.Config)

local Tycoon = {
	cash = Config.Economy.StartCash,
	workers = 1, -- one free worker at the start
	cashMachine = false,
}

local listeners = {}

function Tycoon.listen(cb)
	table.insert(listeners, cb)
end

local function emit()
	for _, cb in ipairs(listeners) do
		pcall(cb)
	end
end

function Tycoon.addCash(amount)
	Tycoon.cash = Tycoon.cash + amount
	emit()
end

function Tycoon.spend(amount)
	if Tycoon.cash < amount then
		return false
	end
	Tycoon.cash -= amount
	emit()
	return true
end

function Tycoon.hireWorker()
	if Tycoon.workers >= Config.MaxWorkers then
		return false
	end
	if not Tycoon.spend(Config.Economy.WorkerPrice) then
		return false
	end
	Tycoon.workers = Tycoon.workers + 1
	emit()
	return true
end

function Tycoon.buyCashMachine()
	if Tycoon.cashMachine then
		return false
	end
	if not Tycoon.spend(Config.Economy.CashMachinePrice) then
		return false
	end
	Tycoon.cashMachine = true
	emit()
	return true
end

-- reward for finishing a project of a given size
function Tycoon.rewardFor(sizeId)
	local mult = Config.Economy.RewardSizeMult[sizeId] or 1
	local base = Config.Economy.BaseReward * mult
	if Tycoon.cashMachine then
		base = base * Config.Economy.CashMachineMult
	end
	return math.floor(base)
end

function Tycoon.idleWorkers()
	return math.max(0, Tycoon.workers - Tycoon.activeJobs)
end

return Tycoon
