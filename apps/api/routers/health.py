from fastapi import APIRouter

router = APIRouter()


@router.get("/alive")
def alive():
    return {"ok": True}
