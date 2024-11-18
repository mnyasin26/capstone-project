
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/contact_info/{UUID_user_id}")
async def get_contact_info(UUID_user_id: str):
    # Get contact info logic
    pass

@router.post("/contact_info/add")
async def add_contact_info():
    # Add contact info logic
    pass

@router.put("/contact_info/edit")
async def edit_contact_info():
    # Edit contact info logic
    pass

@router.delete("/contact_info/delete")
async def delete_contact_info():
    # Delete contact info logic
    pass