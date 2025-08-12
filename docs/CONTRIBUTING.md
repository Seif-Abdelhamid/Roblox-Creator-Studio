# Contributing

## Go module housekeeping
If you add or change Go imports, run:
```bash
cd go
go mod tidy
```
This will update `go.sum` to include new modules so CI passes.