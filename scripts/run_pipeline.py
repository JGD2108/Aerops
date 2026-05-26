from datetime import datetime
import os
import traceback

from app.database import db
from scripts.build_analytics_snapshots import build_analytics_snapshots
from scripts.cosmos_retry import run_with_cosmos_retry
from scripts.create_indexes import create_indexes
from scripts.generate_events import generate_events
from scripts.generate_passengers import generate_passengers
from scripts.load_airports import load_airports
from scripts.load_flights import load_flights
from scripts.process_raw_data import process_raw_data


PIPELINE_STEPS = [
    ("process_raw_data", process_raw_data),
    ("load_airports", load_airports),
    ("load_flights", load_flights),
    ("create_indexes", create_indexes),
    ("generate_events", generate_events),
    ("generate_passengers", generate_passengers),
    ("build_analytics_snapshots", build_analytics_snapshots),
]


def _validate_pipeline_env():
    missing = []
    for name in ("MONGODB_URI",):
        if not os.getenv(name):
            missing.append(name)

    if not (os.getenv("MONGODB_DATABASE") or os.getenv("MONGODB_DB_NAME")):
        missing.append("MONGODB_DATABASE (or MONGODB_DB_NAME)")

    backend = os.getenv("STORAGE_BACKEND", "local").strip().lower()
    if backend == "azure_blob" and not os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
        missing.append("AZURE_STORAGE_CONNECTION_STRING")

    if missing:
        raise ValueError(f"Missing required pipeline environment variables: {', '.join(missing)}")


def run_pipeline():
    _validate_pipeline_env()
    started_at = datetime.utcnow()
    steps = []
    failed = False

    for step_name, step_fn in PIPELINE_STEPS:
        step_started = datetime.utcnow()
        step_status = "SUCCESS"
        step_error = None

        try:
            step_fn()
        except Exception as exc:
            step_status = "FAILED"
            step_error = f"{type(exc).__name__}: {exc}"
            failed = True

        step_finished = datetime.utcnow()
        steps.append({
            "name": step_name,
            "status": step_status,
            "started_at": step_started,
            "finished_at": step_finished,
            "duration_seconds": round((step_finished - step_started).total_seconds(), 2),
            "error": step_error,
        })

        if failed:
            break

    finished_at = datetime.utcnow()
    status = "FAILED" if failed else "SUCCESS"
    errors = [step["error"] for step in steps if step["error"]]

    run_with_cosmos_retry(lambda: db.audit_runs.insert_one({
        "process_name": "run_pipeline",
        "status": status,
        "started_at": started_at,
        "finished_at": finished_at,
        "records_processed": 0,
        "records_inserted": 0,
        "steps": steps,
        "errors": errors,
    }))

    print(f"Pipeline finished with status: {status}")
    print(f"Total duration: {finished_at - started_at}")
    print(f"Executed steps: {len(steps)}")

    if failed:
        print("Pipeline failed. Last step details:")
        print(steps[-1])
        raise RuntimeError(f"Pipeline failed at step: {steps[-1]['name']}")


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception:
        traceback.print_exc()
        raise
