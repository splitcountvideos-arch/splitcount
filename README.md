# Split Count

Daily physics-simulation Shorts for YouTube, TikTok and Instagram.

## Layout
- `generator/` – Python scripts that render the videos (numpy + Pillow + ffmpeg)
- `videos/` – finished videos, named `YYYY-MM-DD_<idea>_<LANG>.mp4`
- `assets/` – profile picture, banner, watermark

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
