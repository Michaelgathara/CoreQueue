from pathlib import Path

from apps.api.core.paths import artifacts_dir, safe_filename


def write_artifact(data_root: str, job_id: str, filename: str, data: bytes) -> Path:
    target_dir = artifacts_dir(data_root, job_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    fname = safe_filename(filename)
    dest = target_dir / fname
    with open(dest, "wb") as f:
        f.write(data)
    return dest


def list_artifacts(data_root: str, job_id: str) -> list[str]:
    target_dir = artifacts_dir(data_root, job_id)
    if not target_dir.exists():
        return []

    artifacts = []
    for p in target_dir.iterdir():
        if p.is_file():
            artifacts.append(p.name)

    return sorted(artifacts)


def read_artifact(data_root: str, job_id: str, filename: str) -> Path:
    target_dir = artifacts_dir(data_root, job_id)
    return target_dir / safe_filename(filename)
