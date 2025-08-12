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

[How to record and add a demo GIF](docs/DEMO.md) — only include it if the capture is real and working.

## What this project demonstrates
- 3D engine subsystems (Python):
  - Physics: `physics_engine.py`
  - World/terrain: `world.py`
  - Camera: `camera.py`
  - Lighting: `lighting.py`
  - Rendering/game loop: `game_engine.py`, `main.py`
  - UI: `ui_manager.py`
  - Assets: `asset_manager.py`
- Multiplayer (Go):
  - WebSockets server: `go/server/main.go`
  - Client session handling: `go/networking/client.go`
  - Messages: `go/models/models.go`
- Headless test path for CI: `HEADLESS=1 python3 main.py`
- Bench harness: `bench/`, `scripts/bench_*`
- Safety/authority design and stubs: see `docs/AUTHORITY_REPLICATION.md`
- Observability: Prometheus `/metrics` on Go server (see docs)

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
- Measured results: see `bench/RESULTS.md`
- Bench scripts: `scripts/bench_client_tick.py`, `scripts/bench_ws_throughput.py`

## Safety / Authority / Replication
- Design: `docs/AUTHORITY_REPLICATION.md`
- Anti-abuse: basic rate-limit + moderation stub in Go chat handler

## Observability
- Go server exposes Prometheus metrics at `/metrics`
- See `docker/monitoring/prometheus.yml` for scrape example

## Optional stacks
- Extra services (Prometheus, Grafana, ELK, Nginx) are examples under `docker/` but not required for core demo.

## Team & contribution signals
- See `docs/GOOD_FIRST_ISSUES.md` and `docs/PROJECTS.md`

## Disclaimer
- This project is inspired by Roblox creator experiences. It is not affiliated with, endorsed by, or a product of Roblox.

## Author
- Seif Abdelhamid
