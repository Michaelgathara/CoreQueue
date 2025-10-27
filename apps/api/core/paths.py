import os
from pathlib import Path


def ensure_dirs(data_root: str) -> None:
    Path(data_root).mkdir(parents=True, exist_ok=True)
    Path(data_root, "artifacts").mkdir(parents=True, exist_ok=True)
    Path(data_root, "logs").mkdir(parents=True, exist_ok=True)


def artifacts_dir(data_root: str, job_id: str) -> Path:
    return Path(data_root) / "artifacts" / job_id


def logs_path(data_root: str, job_id: str) -> Path:
    return Path(data_root) / "logs" / f"{job_id}.log"


def safe_filename(name: str) -> str:
    return os.path.basename(name)
