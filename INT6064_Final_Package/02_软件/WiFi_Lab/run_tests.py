"""Run stages separately because the original project uses local data modules."""
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
failed=False
for folder,pattern in [(ROOT,'test_coverage.py'),(ROOT/'stage3','test_*.py')]:
    print(f'Running {folder.name}: {pattern}',flush=True)
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s','.', '-p',pattern,'-v'],cwd=folder)
    failed |= result.returncode != 0
raise SystemExit(1 if failed else 0)
