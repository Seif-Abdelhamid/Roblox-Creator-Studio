# Recording the demo GIF

Goal: a 10–20s clip showing client launch, basic movement, and a chat event.

## Option A: Simple (Peek or OBS)
1. Start the client: `python3 main.py` (desktop mode)
2. Start the Go server (optional for chat demo): `cd docker && docker compose -f docker-compose.min.yml up -d`
3. Record the game window with Peek/OBS; export to GIF as `docs/demo.gif`.

## Option B: ffmpeg (MP4 -> GIF)
1. Record a short MP4 (choose your screen capture tool)
2. Convert to GIF:
```bash
bash scripts/make_demo_gif.sh your.mp4 docs/demo.gif
```

Tips:
- Keep under 20 seconds and under ~8MB for fast loading.
- Capture a moment with movement and a visible message from `scripts/ws_chat.py`.