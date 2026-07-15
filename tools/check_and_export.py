"""Convenience script: run puzzle checks, write JSON and readable report."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scripts = ROOT / "tools"

# generate JSON
subprocess.run(["python", str(scripts / "puzzles_metrics_json.py")], check=True)
# generate report (show up to 5 solutions)
subprocess.run(["python", str(scripts / "generate_readable_report.py"), "5"], check=True)

print("Generated reports in:", ROOT / "reports")
