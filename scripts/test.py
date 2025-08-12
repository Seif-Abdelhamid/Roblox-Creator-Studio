#!/usr/bin/env python3
import os
import subprocess
import sys


def run_smoke():
    env = dict(os.environ)
    env.setdefault("HEADLESS", "1")
    env.setdefault("HEADLESS_TICKS", "60")
    print("Running headless smoke test...")
    result = subprocess.run([sys.executable, "main.py"], env=env, cwd=os.path.dirname(__file__) + "/..")
    return result.returncode


if __name__ == "__main__":
    code = run_smoke()
    sys.exit(code)