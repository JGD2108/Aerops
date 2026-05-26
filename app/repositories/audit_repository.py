from app.database import db


def serialize_document(document):
    document["_id"] = str(document["_id"])

    if "started_at" in document:
        document["started_at"] = document["started_at"].isoformat()

    if "finished_at" in document:
        document["finished_at"] = document["finished_at"].isoformat()

    if "ended_at" in document:
        document["ended_at"] = document["ended_at"].isoformat()

    return document


def get_audit_runs(limit: int = 20):
    cursor = (
        db.audit_runs
        .find({})
        .sort("started_at", -1)
        .limit(limit)
    )

    return [serialize_document(document) for document in cursor]