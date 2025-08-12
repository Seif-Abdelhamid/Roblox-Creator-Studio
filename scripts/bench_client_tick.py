#!/usr/bin/env python3
import os
import time

os.environ.setdefault("HEADLESS", "1")
os.environ.setdefault("HEADLESS_TICKS", "0")  # we drive our own loop

import main  # noqa: E402


def run_bench(duration_s: float = 5.0, fps: int = 60):
    start = time.perf_counter()
    game = main.RobloxCreatorStudio()
    tick_dt = 1.0 / fps
    ticks = 0
    while time.perf_counter() - start < duration_s:
        game.game_engine.local_player.update(tick_dt)
        game.game_engine.physics_engine.update(tick_dt)
        ticks += 1
        time.sleep(0.0)
    end = time.perf_counter()
    elapsed = end - start
    tps = ticks / elapsed
    print(f"ticks={ticks} elapsed_s={elapsed:.3f} ticks_per_sec={tps:.1f}")
    return ticks, elapsed, tps


if __name__ == "__main__":
    run_bench()