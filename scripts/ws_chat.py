#!/usr/bin/env python3
import json
import os
import sys
import time

from headless_shims import activate_headless_shims
activate_headless_shims()

import websocket

SERVER = os.environ.get("WS_URL", "ws://localhost:8081/ws")


def main():
    print(f"Connecting to {SERVER} ...")
    messages = [
        {"type": "chat", "data": {"message": "hello from client"}},
        {"type": "playerUpdate", "data": {"playerId": "demo", "position": {"x": 0, "y": 0, "z": 0}}},
    ]

    def on_open(ws):
        print("Opened")
        for m in messages:
            ws.send(json.dumps(m))
            time.sleep(0.2)

    def on_message(ws, msg):
        try:
            data = json.loads(msg)
        except Exception:
            data = msg
        print("<-", data)

    def on_error(ws, err):
        print("ERR:", err)

    def on_close(ws, a, b):
        print("Closed")

    ws = websocket.WebSocketApp(
        SERVER, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close
    )
    ws.run_forever()


if __name__ == "__main__":
    sys.exit(main() or 0)