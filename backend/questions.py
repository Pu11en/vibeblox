# The planning questions. Plain text, no decoration. One tap per question.
QUESTIONS = [
    {
        "id": "size",
        "text": "How big should it be?",
        "options": [
            {"id": "small", "label": "Small", "description": "One core feature. Fastest to build."},
            {"id": "medium", "label": "Medium", "description": "Core feature plus the essentials."},
            {"id": "large", "label": "Large", "description": "Full build. Takes the longest."},
        ],
    },
    {
        "id": "language",
        "text": "What should the workers build it with?",
        "options": [
            {"id": "python", "label": "Python", "description": "Runs anywhere. Good default."},
            {"id": "javascript", "label": "JavaScript", "description": "Runs in a browser. Easy to share."},
            {"id": "auto", "label": "Workers decide", "description": "The workers pick the best fit."},
        ],
    },
    {
        "id": "quality",
        "text": "How polished should the result be?",
        "options": [
            {"id": "simple", "label": "Simple", "description": "Works, minimal extras."},
            {"id": "solid", "label": "Solid", "description": "Works well, looks good."},
            {"id": "premium", "label": "Premium", "description": "Best quality, most time."},
        ],
    },
]
