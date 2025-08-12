import os
import subprocess
import sys


def test_headless_smoke():
    env = dict(os.environ)
    env.setdefault("HEADLESS", "1")
    env.setdefault("HEADLESS_TICKS", "10")
    proc = subprocess.run([sys.executable, "main.py"], env=env, cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    assert proc.returncode == 0