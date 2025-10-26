from apps.api.core.paths import logs_path


def append_log_line(data_root: str, job_id: str, line: str) -> None:
    path = logs_path(data_root, job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def read_log(data_root: str, job_id: str, max_bytes: int | None = None) -> bytes:
    path = logs_path(data_root, job_id)
    if not path.exists():
        return b""
    
    data = path.read_bytes()
    if max_bytes is not None and len(data) > max_bytes:
        return data[-max_bytes:]
    return data

