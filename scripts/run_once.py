"""Manual trigger to run the pipeline once, from anywhere."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from pipeline.nightly_run import run_pipeline
from delivery.emailer import send_briefing_email # repo root, not /app


if __name__ == "__main__":
    briefing = run_pipeline()
    print("\n--- TONIGHT'S BRIEFING ---\n")
    print(briefing)

    try:
        send_briefing_email(briefing)
    except Exception as e:
        print(f"Email failed: {e}")