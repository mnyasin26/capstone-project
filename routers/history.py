
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/history/{UUID_user_id}")
async def get_history(UUID_user_id: str):
    # Get history logic
    pass