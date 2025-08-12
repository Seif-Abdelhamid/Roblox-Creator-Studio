# Architecture

## Components
- Python Client
  - Subsystems: world, physics, camera, lighting, UI
  - Headless mode for CI: no GL/window required
- Go Server
  - WebSocket endpoint `/ws` (scaffold)

## Message Shapes (example)
```json
{
  "type": "playerUpdate",
  "data": { "playerId": "uuid", "position": {"x":0,"y":0,"z":0} }
}
```

## Tradeoffs
- Depth over breadth: prioritize Python + Go paths
- Optional stacks are separated from minimal dev flow