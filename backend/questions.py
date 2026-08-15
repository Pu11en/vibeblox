# The planning questions. Player taps one big button per question — no typing.
# Each question: id, text (caveman-simple), options: [{id, label, emoji, description}]
QUESTIONS = [
    {
        "id": "size",
        "text": "How BIG should it be?",
        "options": [
            {"id": "tiny", "label": "Tiny", "emoji": "🐣",
             "description": "One little thing. Done fast."},
            {"id": "medium", "label": "Medium", "emoji": "🐥",
             "description": "A few pieces. A little bigger."},
            {"id": "big", "label": "Big", "emoji": "🦅",
             "description": "Lots of stuff. Takes more time."},
        ],
    },
    {
        "id": "language",
        "text": "What should the workers build it with?",
        "options": [
            {"id": "python", "label": "Python", "emoji": "🐍",
             "description": "A good all-rounder. Runs anywhere."},
            {"id": "javascript", "label": "JavaScript", "emoji": "🌐",
             "description": "Runs in your browser. Easy to share."},
            {"id": "auto", "label": "Workers pick", "emoji": "🛠️",
             "description": "The workers choose the best one for the job."},
        ],
    },
    {
        "id": "fancy",
        "text": "How fancy should it look?",
        "options": [
            {"id": "simple", "label": "Simple", "emoji": "🧼",
             "description": "Clean and easy to read."},
            {"id": "nice", "label": "Nice", "emoji": "😎",
             "description": "Looks good. Colors. Style."},
            {"id": "fancy", "label": "Fancy", "emoji": "✨",
             "description": "Pretty and polished. Show it off."},
        ],
    },
]
