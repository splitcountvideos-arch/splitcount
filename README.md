# Split Count

Daily physics-simulation Shorts for YouTube, TikTok and Instagram.

## Layout
- `generator/` – Python scripts that render the videos (numpy + Pillow + ffmpeg)
  - `battle_royale.py` battle-royale (`STEER=.. EAT=.. python3 generator/battle_royale.py OUT SEED BITE TAKE0 [--long]`)
  - `escape_rings.py` escape the spinning rings (`GAP=45 python3 generator/escape_rings.py OUT SEED [--long] [--dry]`)
  - `split_sim.py` short version · `split_long.py` TikTok long version (`python3 generator/split_long.py OUT.mp4 0.165`)
- `videos/` – finished videos, named `YYYY-MM-DD_<idea>_<LANG>.mp4`
- `assets/` – profile picture, banner, watermark

## Strategy (goal: revenue)
- **TikTok first.** Creator Rewards (Germany): 10k followers, 100k views / 30 days, personal account, videos **> 1 minute**.
  → Every day: a short version (8–25 s) for YouTube Shorts + Instagram Reels, and a **long version (61–75 s)** for TikTok.
- **YouTube:** first milestone 500 subs + 3M Shorts views / 90 days (fan funding); ads need 1,000 subs + 20M Shorts views / 90 days from 1 Feb 2027.
- **Every day a genuinely new rule/idea** – no near-duplicates (YouTube "inauthentic content" policy).
- **Double down on winners:** if a video clearly outperforms, make a sequel/"part 2" within 1–2 days.
- **Weekly review (Mondays):** pull Metricool analytics, compare platforms and ideas, adjust.

## Daily flow
1. Pick an idea together, approve it.
2. Render the video (1080×1920, 30 fps, with sound).
3. Commit it to `videos/` and push to `main`.
4. Schedule via Metricool using the raw URL:
   `https://raw.githubusercontent.com/splitcountvideos-arch/splitcount/main/videos/<file>.mp4`
   Times (Europe/Berlin): YouTube 18:00 · TikTok 19:00 · Instagram 20:00

## Video log
| Date | Idea | Languages |
|---|---|---|
| 2026-11-22 | Ball splits on every wall hit – how fast to 2000? | EN, DE, TR |
| 2026-11-22 | (v2: texts moved out of the bottom UI zone) TikTok long: 16.5% split chance – 10,000 before 1 minute? (67 s, missed: 63.4 s) | EN |
| 2026-11-23 | Battle royale: 12 colored balls, bigger eats smaller, zone shrinks – short 17 s (LIME wins) | EN |
| 2026-11-23 | TikTok long: battle royale, 65.5 s, final duel decided at 1:01 (PURPLE wins) – `generator/battle_royale.py` | EN |
| 2026-11-24 | Escape 15 spinning rings – short 18 s (gap 100°, seed 25, escaped 15.07 s) | EN |
| 2026-11-24 | Comment-driven: 'No-cheating version' (1 split per real bounce, 0.6 s cooldown) + MVP crown – short 20 s, 2000 in 16.6 s (was 6.1 s) – `generator/split_fair.py` | EN |
| 2026-11-24 | TikTok long: no-cheating to 10,000 (4.0 s cooldown) – 68 s, reached 64.5 s | EN |
| 2026-11-24 | TikTok long: escape 15 rings before 1:00? 64 s, last ring from 0:52, escaped 59.70 s (gap 45°, seed 25) – `generator/escape_rings.py` | EN |

## Layout rule (safe zone)
Platform UI (username, caption, buttons) covers roughly the bottom 25 % and the right edge of the screen.
Keep all text and the main action between y ≈ 150 and y ≈ 1500 (of 1920). Circle: center y 900, radius 400.

## Idea queue from comments (propose these first)
When a comment sparks an idea, add it here; the daily idea session offers the top item as one of its 3 ideas and removes it once made.
- [done 2026-11-24] 'It's a bug' → no-cheating version (split_fair.py)
- MVP ball crown → follow one 'hero' ball through a whole video (does the crown ball survive / win?)

## Learnings (keep updated)
Living notes on what works. Update after every weekly review and every comment session.
- Comments: prefer short, playful replies that ask a follow-up question ("What should we simulate next?") – questions keep threads alive.
- 2026-11-23 (week 1 review): only 1 video live (22 Nov); TikTok 0 views after ~1 day, YouTube no data yet, Instagram post failed (account verification). Metricool analytics lag 1–2 days → judge a video only after ≥48 h. Fix IG verification before counting IG.
- 2026-11-24: First comments came on YouTube. A 'this is a bug' comment started a 5-reply debate → debates drive engagement. Idea queued: 'no-cheating' version (wall-hit cooldown so sliding balls don't split every frame).
- Tech: replying in YouTube Studio via the built-in browser – typing doesn't reach the textarea; use find('Yanıt ekleyin') → form_input on the textbox, then click the 'Yanıtla' button that follows 'İptal'.
- 2026-11-24: TikTok shows 0 views on API-posted videos (new account posted via scheduler from day 1 → likely flagged). Warm-up until 2026-12-01: Marley uses TikTok normally 10–15 min/day; TikTok posts go out with autoPublish=false (Metricool push → Marley posts in the TikTok app, optionally adds a trending sound at low volume). Re-evaluate on 2026-12-02.
- (add findings here: which ideas/hooks/lengths performed best, which reply styles got likes/replies)

## Comment reply log
`state/reply_log.md` – date, platform, video, comment, our reply, reaction (likes/replies) a few days later.
