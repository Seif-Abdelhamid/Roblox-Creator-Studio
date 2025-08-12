# Creator Studio (Roblox-inspired) – 3D Multiplayer Game Engine

> A focused, demo-first showcase of real-time 3D, networking, and systems engineering.

## TL;DR (Run it in 10 seconds)

- Headless smoke (no OpenGL needed):
```bash
HEADLESS=1 python3 main.py
```

- Full desktop (requires OpenGL + pygame):
```bash
python3 main.py
```

- Minimal backend (Go WebSocket server):
```bash
cd docker && docker compose -f docker-compose.min.yml up --build -d
```

- Dev helper:
```bash
bash scripts/dev headless    # headless smoke
bash scripts/dev server      # Go server only
bash scripts/dev run         # server + local client (desktop)
```

## What this project demonstrates
- Real-time 3D client (Python, OpenGL) with engine subsystems (world, physics, camera, lighting, UI)
- WebSocket server (Go) scaffolding for multiplayer
- Clear, reproducible dev flows, CI, and code-quality gates

## Quick demo
- Add a short screen capture/GIF to `docs/demo.gif` and embed it here.

## Architecture (high level)
```
Python Client (OpenGL)  <——WS——>  Go Server
        |                             |
   Assets/Physics                (DB/Cache optional)
```
See `docs/ARCHITECTURE.md` for component responsibilities and message shapes.

## Development
- Python: `HEADLESS=1 python3 main.py`
- Go server: `cd docker && docker compose -f docker-compose.min.yml up --build -d`
- Chat demo:
```bash
# Terminal A: start server
cd docker && docker compose -f docker-compose.min.yml up --build -d

# Terminal B: run a simple chat client
python3 scripts/ws_chat.py
```
- Tests (CI uses headless smoke):
```bash
pytest -q            # if you have pytest installed
```

## Performance
- Replace targets with measured results and scripts in `bench/`.
- Example metrics (to be reproduced):
  - Client tick: 60 FPS headless loop stable on CI
  - WS broadcast (Go): ~2k msgs/sec (M2/16GB) – scripts in `bench/`

## Optional stacks
- Extra services (Prometheus, Grafana, ELK, Nginx) are included as examples under `docker/` but not required for core demo.

## Disclaimer
- This project is inspired by Roblox creator experiences. It is not affiliated with, endorsed by, or a product of Roblox.

## Author
- Seif Abdelhamid
