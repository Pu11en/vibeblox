-- Play2Build shared config. THE TWO THINGS TO CHANGE:
--   BackendUrl -> the tunnel URL (or http://127.0.0.1:8000 while testing in Studio)
--   Secret     -> must match P2B_SECRET in backend/.env

local Config = {
	-- dev mode (Studio): localhost. For published play: the tunnel URL (publish.sh swaps it).
	BackendUrl = "http://127.0.0.1:8000",
	Secret = "dev-secret-change-me",

	-- How often the game asks the factory "are we done yet?"
	PollSeconds = 4,

	-- Hard cap on jobs running at once per player (backend allows more; keep it cozy)
	MaxWorkers = 3,

	-- The tycoon economy (money is fun-fantasy, the repo is the real reward)
	Economy = {
		StartCash = 100,
		WorkerPrice = 150,
		CashMachinePrice = 300,
		CashMachineMult = 2,
		BaseReward = 200,
		RewardSizeMult = { tiny = 1, medium = 2, big = 3 },
	},

	-- Used only if the factory can't be reached (game still opens)
	FallbackIdeas = {
		{
			id = "snake-game",
			name = "Snake Game",
			emoji = "🐍",
			description = "A classic snake game. Eat food, get long, don't hit yourself.",
		},
		{
			id = "cookie-clicker",
			name = "Cookie Clicker",
			emoji = "🍪",
			description = "Click cookies. Get more cookies. Numbers go up.",
		},
		{
			id = "quiz-bot",
			name = "Quiz Bot",
			emoji = "❓",
			description = "A robot that asks you questions and says if you got it right.",
		},
		{
			id = "mad-libs",
			name = "Mad Libs",
			emoji = "📝",
			description = "Type silly words. Get a silly story back.",
		},
		{
			id = "rock-paper-scissors",
			name = "Rock Paper Scissors",
			emoji = "✊",
			description = "Play rock, paper, scissors against the computer.",
		},
		{
			id = "cat-facts",
			name = "Cat Facts",
			emoji = "🐱",
			description = "Press a button. Get a cat fact. That's it. That's the whole thing.",
		},
		{
			id = "pet-rock",
			name = "Pet Rock",
			emoji = "🪨",
			description = "A pet rock. Feed it, play with it, put it to sleep.",
		},
		{
			id = "dice-roller",
			name = "Dice Roller",
			emoji = "🎲",
			description = "Roll dice. See numbers. Random fun.",
		},
		{
			id = "to-do-list",
			name = "To-Do List",
			emoji = "✅",
			description = "Keep a list of things to do. Cross them off. Feel great.",
		},
		{
			id = "pixel-art",
			name = "Pixel Art Maker",
			emoji = "🎨",
			description = "Make little pictures out of colored squares.",
		},
		{
			id = "number-guesser",
			name = "Number Guesser",
			emoji = "🎯",
			description = "Computer picks a secret number. You guess it.",
		},
		{
			id = "countdown-timer",
			name = "Countdown Timer",
			emoji = "⏰",
			description = "Set a timer and watch it count down. Tick tock.",
		},
	},

	FallbackQuestions = {
		{
			id = "size",
			text = "How BIG should it be?",
			options = {
				{
					id = "tiny",
					label = "Tiny",
					emoji = "🐣",
					description = "One little thing. Done fast.",
				},
				{
					id = "medium",
					label = "Medium",
					emoji = "🐥",
					description = "A few pieces. A little bigger.",
				},
				{
					id = "big",
					label = "Big",
					emoji = "🦅",
					description = "Lots of stuff. Takes more time.",
				},
			},
		},
		{
			id = "language",
			text = "What should the workers build it with?",
			options = {
				{
					id = "python",
					label = "Python",
					emoji = "🐍",
					description = "A good all-rounder. Runs anywhere.",
				},
				{
					id = "javascript",
					label = "JavaScript",
					emoji = "🌐",
					description = "Runs in your browser. Easy to share.",
				},
				{
					id = "auto",
					label = "Workers pick",
					emoji = "🛠️",
					description = "The workers choose the best one for the job.",
				},
			},
		},
		{
			id = "fancy",
			text = "How fancy should it look?",
			options = {
				{
					id = "simple",
					label = "Simple",
					emoji = "🧼",
					description = "Clean and easy to read.",
				},
				{
					id = "nice",
					label = "Nice",
					emoji = "😎",
					description = "Looks good. Colors. Style.",
				},
				{
					id = "fancy",
					label = "Fancy",
					emoji = "✨",
					description = "Pretty and polished. Show it off.",
				},
			},
		},
	},
}

return Config
