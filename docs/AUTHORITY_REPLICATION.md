# Server Authority & Replication

## Authority model
- Go server is authoritative for player state and world mutations.
- Clients send intents (movement deltas, chat, build actions).
- Server validates, updates state, and replicates deltas to interested clients.

## Replication protocol (plan)
- Messages carry `type` and `data`; server batches updates at tick.
- Delta compression: only changed fields since last ack per client.
- Interest management: spatial grid (e.g., 64x64). Replicate only to nearby cells.

## Anti-abuse
- Per-client rate-limit on chat and build.
- Moderation stub for chat: block banned terms.

## Observability
- Prometheus counters on message rx/tx, errors, clients online.

## Next steps
- Implement spatial grid and per-client last-ack cache for deltas.
- Add server reconciliation hooks to client for movement.