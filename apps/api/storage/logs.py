from apps.api.core.config import Settings
from apps.api.storage.artifacts import get_storage


def append_log_line(settings: Settings, job_id: str, line: str) -> None:
    """
    Append a line to the log.
    Note: S3 doesn't support append. For S3, this is inefficient (read-modify-write).
    For high-scale production S3 logging, we'd use a different strategy (stream to CloudWatch/etc or write chunks).
    For this iteration, we will just accept the inefficiency or assume local storage for high-frequency logs.
    """
    storage = get_storage(settings)
    path = f"logs/{job_id}.log"

    current = storage.read(path)
    line_bytes = line.encode("utf-8") if isinstance(line, str) else line

    new_data = current + line_bytes
    storage.write(path, new_data)


def read_log(settings: Settings, job_id: str, max_bytes: int | None = None) -> bytes:
    storage = get_storage(settings)
    path = f"logs/{job_id}.log"

    data = storage.read(path)

    if max_bytes is not None and len(data) > max_bytes:
        return data[-max_bytes:]
    return data
