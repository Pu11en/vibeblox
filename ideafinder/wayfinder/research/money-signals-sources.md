# Money signals data sources

Research for: [money-signals-sources](tickets/money-signals-sources.md) ticket.
Date: 2026-07-31. Method: every source below was hit with a real curl call from this machine (git-bash on Windows). Status codes, limits, and quirks recorded are what those calls actually returned. No em dashes in this doc, per Drew's preference.

## The short version

Verified and usable for free, no API key:
- GitHub REST API (core + search). Core: 60 req/hr unauthenticated. Search: 10 req/min unauthenticated.
- Hacker News Algolia API. No auth, no rate limit observed (all calls 200).
- npm downloads API. No auth.
- crates.io API. No auth, but requires a User-Agent header.
- PyPI metadata API (pypi.org). No auth. Download counts (pypistats.org) are rate limited: 429 observed.
- YouTube: oEmbed endpoint, channel RSS feed, and yt-dlp (installed, v2026.07.04). No auth.
- Substack per-publication API (archive + posts). No auth. Public search API is dead (404).
- pullpush.io (Reddit archive). No auth, but data frozen around mid-May 2025.
- Product Hunt RSS feed. No auth.

Blocked or not automatable from here:
- Reddit JSON endpoints (www.reddit.com and old.reddit.com): 403 block page, with or without a browser User-Agent. Use pullpush.io (historical) or a Reddit OAuth script app (unverified, needs app creation).
- Google Trends API: 429.
- DuckDuckGo HTML/lite search: blocked, zero results returned.
- pepy.tech API v2: requires API key.
- Substack public search API: 404 on all variants tried.

## Verified sources, detail

### 1. GitHub REST API

Repo metadata endpoint, no auth:
```
GET https://api.github.com/repos/{owner}/{repo}
```
Observed response fields used for scoring: stargazers_count, forks_count, language, topics, license.spdx_id, archived, homepage, description, pushed_at, open_issues_count.
Test: awesome-selfhosted/awesome-selfhosted returned stars 309622, forks 14527, topics 8, archived false. 200 OK.
Rate limit: core = 60 requests/hour unauthenticated (rate_limit endpoint returned core 60/hr, remaining 58 after one call). A free personal access token (no scopes needed) raises this to 5000/hr; recommended before building the ranker.

Search API, no auth:
```
GET https://api.github.com/search/repositories?q={query}&per_page=1
```
Headers observed: X-RateLimit-Limit: 10, X-RateLimit-Remaining: 9 after one call, X-RateLimit-Resource: search. So 10 search requests per minute unauthenticated, 30/min with a token. total_count in the response is the cheap way to size a niche (query returns 62875 repos for q=self-hosted+in:description).

What it signals for email marketing: stars = proof of builder interest in the problem; topics = the niche keywords to feed every downstream search; license = whether a product can legally be built on the code (MIT/Apache permissive, AGPL hostile); homepage = where the project's site lives (outreach target); archived = dead idea, skip.

### 2. Hacker News Algolia API

No auth, JSON, fast. Endpoints verified:
```
GET https://hn.algolia.com/api/v1/search?query={query}&tags=story&hitsPerPage=5
```
Two query patterns both verified:
- Repo URL mentions: query=github.com%2F{owner}%2F{repo} (returned 27 hits for awesome-selfhosted).
- Keyword: query=self-hosted returned nbHits 4496, top story 820 points.
- Newsletter discovery: query=substack.com%20{keyword} returned 7 hits, all real Substack newsletter posts covering the niche (datamethods.substack.com, nvnt.substack.com, r0bbie.substack.com).

Response fields: nbHits, hits[].title, hits[].points, hits[].created_at, hits[].url.
No rate limit headers observed; 6 calls in quick succession all returned 200.

What it signals: HN mentions = builders and early adopters interested in the problem. "Show HN:" titles = someone already tried to productize it. Points on mentions = strength of interest. Newsletters found via HN = existing email channels in the niche.

### 3. Reddit JSON endpoints: blocked, with fallback

```
GET https://www.reddit.com/search.json?q=...           -> 403 (block page HTML)
GET https://www.reddit.com/r/{sub}/about.json          -> 403 (block page HTML)
GET https://old.reddit.com/r/{sub}/about.json          -> 403 (block page HTML)
```
All three returned 403 with Reddit's "theme-beta" block page, both with a descriptive research User-Agent and with a full browser User-Agent. Without any User-Agent: 403 as well. So subscriber counts and live search are NOT automatable from this machine right now.

Fallback that works, no auth:
```
GET https://api.pullpush.io/reddit/search/submission/?q={keyword}&size=100
GET https://api.pullpush.io/reddit/search/submission/?subreddit={sub}&q={keyword}&size=100
GET https://api.pullpush.io/reddit/search/comment/?q={keyword}&size=100
```
Verified: q=homelab&size=100 returned 100 posts; subreddit frequency aggregated to homelab 45, selfhosted 10, homelabsales 7, hardwareswap 5, HomeNetworking 3. Comment search works too. Subreddit filter works.
Caveat observed: newest created_utc in results is 1747659447, which is mid-May 2025. The archive is frozen there. Treat pullpush as a historical floor (activity and complaint density through May 2025), not live data.
Also caveat: keyword matching is loose (a q=self-hosted search returned off-topic posts), so always combine subreddit= with q= and filter titles client-side.

What it signals: which subreddits talk about the niche and how much (reachable buyer communities), and complaint/request language in titles and comments ("alternative", "instead of", "expensive") = demand for a fix.

### 4. Substack

Per-publication API, no auth, verified:
```
GET https://{slug}.substack.com/api/v1/archive?sort=new&limit=50
GET https://{slug}.substack.com/api/v1/posts?limit=50
```
Test: newsletter.pragmaticengineer.com archive returned JSON posts. Key fields: audience ("everyone" for free posts, "only_paid" for paid-only), reaction_count, reactions, comment_count, post_date, wordcount, section_name, title, subtitle, truncated_body_text.
Public discovery/search API is dead: substack.com/api/v1/search, /search/posts, /search/publications, /discover all 404. The /search/ page is JavaScript-rendered. Discovery pattern that works: HN Algolia query "substack.com {keyword}" (verified above), plus known newsletter slugs from the niche.

What it signals: newsletters already covering the niche = proof email money flows in this niche, plus a competitor and outreach-target list. Share of posts marked only_paid = the newsletter actually monetizes. Reactions per post = engagement. No subscriber counts are public anywhere in the API (checked archive/post fields).

### 5. YouTube

All verified, no auth:
```
GET https://www.youtube.com/oembed?url={video_url}&format=json     -> title, author_name
GET https://www.youtube.com/feeds/videos.xml?channel_id={id}      -> latest 15 videos as XML
```
@GithubAwesome resolved to channel UC9Rrud-8CaHokDtK9FszvRg (both via the handle page's externalId field and via yt-dlp). Its RSS feed title is "Github Awesome" and the latest entries are exactly the weekly repo roundups, with repo names inside video titles.
yt-dlp is installed (v2026.07.04) and works for channel listing:
```
yt-dlp --flat-playlist --playlist-end 5 --print "%(channel_id)s | %(title)s" "https://www.youtube.com/@GithubAwesome/videos"
```
It prints a warning that no JavaScript runtime is installed (needed only for format extraction, not for titles/ids from flat playlists). View counts and full metadata are available for top-priority ideas via the same tool.

What it signals: the channel RSS is the idea pipeline itself (daily poll, free). Video titles name the repos. Review coverage for an idea: yt-dlp ytsearch query "repo name review" shows whether reviewers already cover it = distribution proof.

### 6. Package registries (usage signals)

All verified, no auth:
```
GET https://api.npmjs.org/downloads/point/last-week/{package}      -> downloads (126M/wk for express)
GET https://api.npmjs.org/downloads/range/{start}:{end}/{package}  -> daily series
GET https://crates.io/api/v1/crates/{crate}                        -> total + recent downloads (needs a User-Agent header)
GET https://pypi.org/pypi/{package}/json                           -> metadata (no download counts)
```
PyPI download counts via https://pypistats.org/api/packages/{pkg}/recent: one 200, then 429 RATE LIMIT EXCEEDED on a later call. Usable only heavily throttled, top ideas only. pepy.tech v2 requires an API key ("No API Key provided").

What it signals: real weekly downloads = actual users of the underlying library = validation plus a warm outreach pool (users of the OSS project are the first email list for the paid product).

### 7. Product Hunt RSS feed

Verified, no auth:
```
GET https://www.producthunt.com/feed     -> Atom XML, 200 OK, today's featured products
```
One call per day, cached. Searching it for a specific repo rarely hits, but counting launches whose titles contain the niche keyword over 90 days = launch velocity in the niche. Low value per idea; run as a daily cached job, not per idea.

### 8. Competitor pricing pages (web fetch)

Verified pattern: curl -L {homepage}/pricing then regex for dollar amounts.
- umami.is/pricing returned price strings ($1, $5, $11). Works.
- plausible.io/pricing returned nothing (JavaScript-rendered). Fails.
So pricing scraping works per-site, not generically. Run for top-priority ideas only, and treat empty results as "unknown", not "free".

## Blocked sources (do not build on these)

- Reddit JSON: 403 observed. Reddit OAuth (free script app) is the documented fix but unverified here (needs app creation).
- Google Trends unofficial endpoint: 429 observed. pytrends exists but relies on cookies and is flaky; unverified.
- DuckDuckGo HTML and lite search: zero results observed (anti-bot). No free general web search is reliably automatable from here.
- Substack search API: 404 observed.
- Libraries.io: requires API key (not tested).
- pepy.tech v2: requires API key (observed).

## Proposed signal list for the ranking agent

Tier 1: cheap enough to run for every idea (about 5 HTTP calls per idea).

| # | Signal | Endpoint | Query pattern | Score computation | What it means |
|---|--------|----------|---------------|-------------------|---------------|
| S1 | Repo size and health | GET api.github.com/repos/{owner}/{repo} | repo from the channel video | popularity = log10(1+stars); activity = 1 if pushed_at within 90 days else 0; license_ok = 1 for MIT/Apache/BSD, 0.5 GPL, 0.25 AGPL, 0 none; archived = kill switch | Stars = builder interest in the problem. License = can we legally ship a product. Freshness = maintained |
| S2 | Niche size | GET api.github.com/search/repositories?q={kw}+in:description,readme&per_page=1 | kw = strongest topic from S1 plus "self-hosted", e.g. "self-hosted analytics" | niche_size = log10(1+total_count) | Bigger niche = more demand and more competitors. Watch the 10/min search limit |
| S3 | HN interest | GET hn.algolia.com/api/v1/search?query=github.com%2F{o}%2F{r}&tags=story&hitsPerPage=5, plus the same with query={repo name} | repo URL, then bare repo name | hn = min(5, url_hits)*2 + min(3, name_hits) + sum(top 3 points)/(days since + 30) | Builders care about this problem. Show HN hits = productization proof |
| S4 | Real users | npm: api.npmjs.org/downloads/point/last-week/{pkg}; crates: crates.io/api/v1/crates/{crate}; python: pypi.org metadata only | package name = repo name (drop owner prefix) | users = log10(1+weekly downloads) or log10(1+recent_downloads) | Users of the OSS library = first email list for the paid product |
| S5 | Channel placement (cached daily) | youtube.com/feeds/videos.xml?channel_id=UC9Rrud-8CaHokDtK9FszvRg | none, one fetch per day | presence = 1 (all ideas come from here); video title names the repos | Distribution already exists; idea pool source |

Tier 2: shortlist only (after Tier 1 filters to maybe 20 to 40 ideas), 3 to 8 extra calls.

| # | Signal | Endpoint | Query pattern | Score computation | What it means |
|---|--------|----------|---------------|-------------------|---------------|
| S6 | Niche communities and pain | pullpush.io/reddit/search/submission/?q={kw}&size=100, plus ?subreddit={main_sub}&q={kw}&size=100, plus comment search | kw from S1 topics | communities = log10(1+posts in top 3 subs); pain = share of titles matching /alternative\|instead of\|expensive\|frustrat\|migrat\|replace\|self-host/ | Reachable buyer communities and complaint density. Archive frozen May 2025: treat as historical floor |
| S7 | Existing email channels | hn.algolia.com/api/v1/search?query=substack.com%20{kw}&tags=story&hitsPerPage=10, then {slug}.substack.com/api/v1/archive?sort=new&limit=50 per found slug | kw from S1 topics | paid_share = fraction of posts with audience "only_paid"; engagement = median reaction_count; newsletter_count = distinct slugs found | Newsletters monetizing the niche = proof email money flows there, plus competitor/outreach list |
| S8 | Review coverage | yt-dlp "ytsearch5:{repo name} review" --flat-playlist --print "%(title)s|%(view_count)s" | repo name + " review" | reviewers = count of videos; reach = log10(1+sum views) | Distribution proof; reviewers already explain the problem to buyers |
| S9 | Price point | curl -L {homepage}/pricing (only if S1 homepage exists), regex dollar amounts | homepage from S1 | price = median parsed amount, 0 if none found | Realistic price for the email pitch and revenue estimate |

Tier 3: top 10 ideas only, and sources that need credentials.

- Subscriber counts: Reddit r/{sub}/about.json is 403 from here. If a free Reddit OAuth script app is created, GET oauth.reddit.com/r/{sub}/about.json (unverified). Proxy without it: S6 post volume and S7 reaction counts.
- Google Trends: 429 blocked. Skip unless someone wires pytrends with cookies (flaky, unverified).
- Product Hunt feed: daily cached job, count niche launches over 90 days. Run once a day, not per idea.
- pypistats download counts: 429 observed; only for top Python ideas, one call, long gaps.

## Budget and operational notes

- 50 ideas x Tier 1 = 250 calls. GitHub core 60/hr unauth means 4+ hours; get a free GitHub PAT (no scopes) for 5000/hr and 30 search/min. Search API is the binding constraint: 10/min unauth, so sleep 6s between S2 calls or batch them.
- HN Algolia, npm, crates.io, pullpush, Substack archive: no observed limits; safe to parallelize moderately.
- Caching: channel RSS 1/day, Product Hunt feed 1/day, subreddit maps 1/week, Substack archives 1/week. Per-idea calls are only S1 to S4 and S8/S9.
- Send a descriptive User-Agent on every call. Reddit and crates.io both care.
- Windows curl pitfall observed: native curl.exe cannot write MSYS-style /tmp paths (-o /tmp/x.json silently fails). Pipe responses or use -D - for headers.
- Add -L (follow redirects) and --compressed on hosts that gzip (Substack, Reddit).

## Recommendations

1. Create a free GitHub PAT now: lifts the only real rate ceiling (60/hr core, 10/min search).
2. Do not build on Reddit JSON, Google Trends, or DuckDuckGo: all blocked from this machine (403, 429, 0 results observed).
3. If live Reddit data matters (post-May 2025), create a free Reddit OAuth script app; unverified until then, pullpush covers history.
4. Weighting of these signals into one money-odds score belongs to the money-odds-rubric ticket, not this research.
