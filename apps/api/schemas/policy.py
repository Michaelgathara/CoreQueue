from typing import Any

from pydantic import BaseModel


class PolicyRuleSet(BaseModel):
    max_concurrent_gpu_jobs: int | None = None
    max_wall_time: str | int | None = None
    queue_priority: str | None = None
    deny_if_device_thermal_state: str | None = None


class PolicyIn(BaseModel):
    name: str
    match: dict[str, Any]
    rules: PolicyRuleSet


class PolicyOut(PolicyIn):
    id: str
    version: int
