
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/profile/{UUID_user_id}")
async def get_profile(UUID_user_id: str):
    # Get profile logic
    pass

@router.post("/profile/edit")
async def edit_profile():
    # Edit profile logic
    pass