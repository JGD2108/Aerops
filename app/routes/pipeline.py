import json
import os
from datetime import datetime
from urllib import error, request

from fastapi import APIRouter, HTTPException, status


router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run")
def trigger_pipeline_run():
    """
    Trigger an external orchestrator/job endpoint.
    This API does not execute the heavy batch pipeline in-process.
    """
    trigger_url = os.getenv("AZURE_PIPELINE_TRIGGER_URL")
    bearer_token = os.getenv("AZURE_PIPELINE_TRIGGER_TOKEN")

    if not trigger_url:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "Pipeline trigger is not configured. "
                "Set AZURE_PIPELINE_TRIGGER_URL to enable this endpoint."
            ),
        )

    payload = {
        "requested_at": datetime.utcnow().isoformat(),
        "requested_by": "fastapi_pipeline_trigger",
    }
    payload_bytes = json.dumps(payload).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    req = request.Request(
        trigger_url,
        data=payload_bytes,
        headers=headers,
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8") if response.length != 0 else ""
            return {
                "status": "triggered",
                "trigger_url": trigger_url,
                "http_status": response.status,
                "response_body": body,
            }
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "External pipeline trigger returned an error",
                "http_status": exc.code,
                "response_body": body,
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to call external pipeline trigger: {exc}",
        ) from exc
