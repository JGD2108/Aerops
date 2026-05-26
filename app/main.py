""" 
Este es el punto de entrada de la aplicación
Aquí es el punto de entrada de FastAPI, se define la aplicación y se incluyen las rutas
"""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.database import check_mongodb_connection
from app.config import config

app = FastAPI(title=config.app_name)

@app.get("/health")
def health():
    return{
        "status": "ok",
        "service" : config.app_name,
    }


@app.get("/ready")
def ready():
    mongo_ready = check_mongodb_connection()

    if not mongo_ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "mongodb": "unavailable",
            },
        )

    return {
        "status": "ready",
        "mongodb": "available",
    }
