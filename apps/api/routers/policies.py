from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.core.db import get_session
from apps.api.schemas.policy import PolicyIn
from apps.api.services.policy_service import dry_run, list_policies, upsert_policy

router = APIRouter()


@router.get("/policies")
def get_policies(db: Session = Depends(get_session)):
    rows = list_policies(db)
    return {
        "policies": [
            {
                "id": p.id,
                "name": p.name,
                "match": p.match,
                "rules": p.rules,
                "version": p.version,
            }
            for p in rows
        ]
    }


@router.post("/policies/apply")
def apply_policy(
    body: PolicyIn, dry_run_only: bool = False, db: Session = Depends(get_session)
):
    if dry_run_only:
        return dry_run(db, body)
    p = upsert_policy(db, body)
    return {"id": p.id, "version": p.version}
