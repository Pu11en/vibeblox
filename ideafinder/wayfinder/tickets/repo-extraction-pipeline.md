Title: Prototype the repo extraction pipeline
Status: closed
Type: prototype
HITL: yes
Blocked by: none
Assigned: Hermes (2026-07-31)

## Question

How do we turn a @GithubAwesome video into a clean list of GitHub repos?

Verified 2026-07-31: video descriptions carry full, timestamped GitHub URLs for every repo (16 and 20 links found in two sample descriptions). No caption parsing needed.

Prototype: newest-video detection via the channel RSS feed (UC9Rrud-8CaHokDtK9FszvRg), fetch the description with yt-dlp, regex out github.com/owner/repo URLs, dedupe, store in the repo DB. Handle videos with zero repo links (the Sora clips video has none) and non-repo links (sponsors, socials). Show Drew the extracted lists from a few videos so he can judge quality. Also decide: backfill all 50 indexed videos into the repo database, idempotent by video_id.

## Resolution

Validated on all 50 indexed videos: descriptions carry exact GitHub URLs, extracted counts matched the video titles on every video (0 to 35 repos each). 1274 mentions, 1217 distinct repos, stored in data/repos.sqlite3 (videos, repos, video_repos tables). Only 1 video had no links (Sora clips video). Backfill: approved by Drew, done, idempotent by video_id. New-video detection: channel RSS (UC9Rrud-8CaHokDtK9FszvRg), verified in the money signals research. Asset: prototype/extract_repos.py (sample and backfill commands); it becomes the seed of the daily scraper, final placement decided in Choose the agent architecture.
