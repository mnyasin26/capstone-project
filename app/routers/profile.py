from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
from sqlalchemy.orm import Session
from app.schemas import EditProfileRequest
from app.connection import get_db
from app.dependencies import get_current_user
from app.models import User, Profile
import uuid

router = APIRouter()

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get profile logic using current_user
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "username": current_user.name,
        "bio": profile.bio,
        "company": profile.company,
        "job_title": profile.job_title,
        "profile_picture": profile.profile_picture
    }

@router.post("/profile/edit")
async def edit_profile(
    name: str = Form(...),
    bio: str = Form(...),
    company: str = Form(...),
    job_title: str = Form(...),
    profile_picture: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Edit profile logic using current_user
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    
    # Update user and profile details
    user.name = name
    profile.bio = bio
    profile.company = company
    profile.job_title = job_title

    if profile_picture:
        unique_filename = f"{uuid.uuid4()}{profile_picture.filename}"
        profile.profile_picture = unique_filename
        with open(f"uploads/{unique_filename}", "wb") as buffer:
            buffer.write(profile_picture.file.read())

    try:
        db.commit()
        db.refresh(user)
        db.refresh(profile)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return {
        "message": "Profile updated successfully",
        "user": {
            "user_id": user.user_id,
            "email": user.email or "",
            "username": user.name or ""
        },
        "profile": {
            "bio": profile.bio or "",
            "company": profile.company or "",
            "job_title": profile.job_title or "",
            "profile_picture": profile.profile_picture or ""
        }
    }





