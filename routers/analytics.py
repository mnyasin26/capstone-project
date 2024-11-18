
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/analytic/{UUID_user_id}")
async def get_analytics(UUID_user_id: str):
    # Get analytics logic
    pass