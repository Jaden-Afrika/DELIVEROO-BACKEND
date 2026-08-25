from abc import ABC, abstractmethod
from typing import Optional


class StorageService(ABC):
    @abstractmethod
    def upload(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        """Returns a URL/path to the uploaded file."""
        ...

    @abstractmethod
    def get_url(self, file_path: str) -> Optional[str]:
        ...


class LocalStorageService(StorageService):
    """Stores files locally. For development only."""

    def __init__(self, base_path: str = "uploads"):
        self.base_path = base_path

    def upload(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        import os
        os.makedirs(self.base_path, exist_ok=True)
        path = os.path.join(self.base_path, filename)
        with open(path, "wb") as f:
            f.write(file_bytes)
        return path

    def get_url(self, file_path: str) -> Optional[str]:
        return f"/uploads/{file_path}"
