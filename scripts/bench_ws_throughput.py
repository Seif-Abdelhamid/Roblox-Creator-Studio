#!/usr/bin/env python3
import json
import os
import sys
import threading
import time

# Ensure repo root on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from headless_shims import activate_headless_shims
activate_headless_shims()

import websocket

SERVER = os.environ.get("WS_URL", "ws://localhost:8081/ws")
CLIENTS = int(os.environ.get("BENCH_WS_CLIENTS", "5"))
MESSAGES = int(os.environ.get("BENCH_WS_MESSAGES", "50"))


def worker(idx, results):
    ws = websocket.WebSocket()
    ws.connect(SERVER)
    sent = 0
    for i in range(MESSAGES):
        ws.send(json.dumps({"type": "chat", "data": {"message": f"hi {idx}-{i}"}}))
        sent += 1
    ws.close()
    results[idx] = sent


def main():
    threads = []
    results = [0] * CLIENTS
    t0 = time.perf_counter()
    for i in range(CLIENTS):
        t = threading.Thread(target=worker, args=(i, results))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - t0
    total = sum(results)
    rate = total / elapsed
    print(f"clients={CLIENTS} messages={MESSAGES} total={total} elapsed_s={elapsed:.2f} msgs_per_s={rate:.1f}")


if __name__ == "__main__":
    sys.exit(main() or 0)