"""Compatibility entry point: open the maintained third-stage app."""
from pathlib import Path
import subprocess
import sys
if __name__ == '__main__':
    path = Path(__file__).resolve().parents[1] / 'stage3' / 'stage3_gui.py'
    raise SystemExit(subprocess.call([sys.executable, str(path)], cwd=path.parent))
