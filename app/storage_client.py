import os
from pathlib import Path


class StorageClient:
    def __init__(self):
        self.backend = os.getenv("STORAGE_BACKEND", "local").strip().lower()

        if self.backend not in {"local", "azure_blob"}:
            raise ValueError("STORAGE_BACKEND must be 'local' or 'azure_blob'")

        self.base_dir = Path(__file__).resolve().parent.parent
        self.raw_local_dir = self.base_dir / "data" / "raw"
        self.processed_local_dir = self.base_dir / "data" / "processed"

        self._blob_service = None
        self._raw_container = os.getenv("RAW_CONTAINER", "aeroops-raw")
        self._processed_container = os.getenv("PROCESSED_CONTAINER", "aeroops-processed")
        self._raw_prefix = os.getenv("RAW_PREFIX", "").strip("/")
        self._processed_prefix = os.getenv("PROCESSED_PREFIX", "").strip("/")

        if self.backend == "azure_blob":
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            if not connection_string:
                raise ValueError(
                    "AZURE_STORAGE_CONNECTION_STRING is required when STORAGE_BACKEND=azure_blob"
                )
            try:
                from azure.storage.blob import BlobServiceClient  # lazy import
            except ImportError as exc:
                raise ImportError(
                    "azure-storage-blob is required for STORAGE_BACKEND=azure_blob"
                ) from exc
            self._blob_service = BlobServiceClient.from_connection_string(connection_string)

    def _blob_path(self, area: str, key: str) -> tuple[str, str]:
        if area not in {"raw", "processed"}:
            raise ValueError("area must be 'raw' or 'processed'")

        if area == "raw":
            container = self._raw_container
            prefix = self._raw_prefix
        else:
            container = self._processed_container
            prefix = self._processed_prefix

        key = key.lstrip("/")
        blob_name = f"{prefix}/{key}" if prefix else key
        return container, blob_name

    def _local_path(self, area: str, key: str) -> Path:
        if area == "raw":
            return self.raw_local_dir / key
        if area == "processed":
            return self.processed_local_dir / key
        raise ValueError("area must be 'raw' or 'processed'")

    def read_text(self, area: str, key: str) -> str:
        if self.backend == "local":
            file_path = self._local_path(area, key)
            return file_path.read_text(encoding="utf-8")

        container, blob_name = self._blob_path(area, key)
        blob_client = self._blob_service.get_blob_client(container=container, blob=blob_name)
        return blob_client.download_blob().readall().decode("utf-8")

    def write_text(self, area: str, key: str, content: str):
        if self.backend == "local":
            file_path = self._local_path(area, key)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            return

        container, blob_name = self._blob_path(area, key)
        container_client = self._blob_service.get_container_client(container)
        try:
            container_client.create_container()
        except Exception:
            pass
        blob_client = self._blob_service.get_blob_client(container=container, blob=blob_name)
        blob_client.upload_blob(content.encode("utf-8"), overwrite=True)


def get_storage_client() -> StorageClient:
    return StorageClient()
