"""
Este archivo se encarga de leer configuración desde variables de entorno
No se conecta a MONGODB solo lee las variables 
"""

import os 
from pathlib import Path
from dotenv import load_dotenv

# Carga el archivo .env desde la raiz del proyecto, sin depender del cwd.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Config:
    def __init__(self):
        self.MONGODB_URI = os.getenv("MONGODB_URI")
        # Soporta ambos nombres para compatibilidad.
        self.MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME") or os.getenv("MONGODB_DATABASE")
        self.app_name = os.getenv("APP_NAME", "AeroOps NoSQL Control Tower")

        missing = []
        if not self.MONGODB_URI:
            missing.append("MONGODB_URI")
        if not self.MONGODB_DB_NAME:
            missing.append("MONGODB_DB_NAME (or MONGODB_DATABASE)")

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Verify values in {ENV_PATH}."
            )
    
config = Config()
    
    