from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO


class StorageProvider(ABC):
    @abstractmethod
    def write(self, path: str, data: bytes | BinaryIO) -> str:
        """Write data to the specified path. Returns the path/key written."""
        pass

    @abstractmethod
    def read(self, path: str) -> bytes:
        """Read data from the specified path."""
        pass

    @abstractmethod
    def list(self, prefix: str) -> list[str]:
        """List files starting with prefix."""
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if a file exists at path."""
        pass
