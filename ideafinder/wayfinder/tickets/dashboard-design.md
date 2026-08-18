Title: Design the dashboard
Status: closed
Type: grilling
HITL: yes
Blocked by: none
Assigned:

## Question

What does the dashboard look like and what is under it?

Pages: endless repo feed with AI summaries (Page 1), live idea board with idea cards sorted by money-odds score (Page 2), plus video and repo detail views.

Stack recommendation: FastAPI + SQLite + plain HTML/JS in one process on a local port (pattern: Cinco H Ranch dashboard at :4323), project at ~/main-projects/repo-idea-lab, reading the channel-brains DB read-only. Confirm the pages, stack, and data model (videos, repos, ideas, rankings).

## Resolution (approved by Drew 2026-07-31)

- FastAPI + SQLite + vanilla HTML/JS, one process, local port 4324, project at C:\Users\drewp\main-projects\repo-idea-lab.
- Page 1 (home): endless repo feed: name, owner, stars, language, AI summary, first-seen video, GitHub link; search and tag filter; infinite scroll.
- Page 2 (/ideas): idea board sorted by money-odds score. Cards show pitch, repos used, score with per-dimension breakdown, evidence links, and the outreach email draft with a copy button.
- Detail pages for video, repo, and idea.
- Tables added to the existing repos.sqlite3: repo_summaries, ideas, idea_repos, idea_scores (signal values, score, evidence JSON), email_drafts.
- Channel-brains DB stays read-only.

## Amendment (2026-08-14)

The dashboard was never productized beyond the local prototype. When the
project became the GITBUTT ZCode plugin, the FastAPI server and static pages
were deleted; browsing and idea work happen through the plugin's MCP tools in
sessions instead. The idea-space tables and scoring rubric survive unchanged.
Project path is now `/home/drewp/main-projects/GITBUTT`.
