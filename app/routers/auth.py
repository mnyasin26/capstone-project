from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.connection import get_db
from app.models import User, PasswordReset, Profile
from app.security import hash_password, verify_password, create_access_token, invalidate_token
from app.schemas import RegisterRequest, LoginRequest, LogoutRequest, PasswordResetRequest, PasswordResetConfirm
from app.email_utils import send_reset_email  # Assuming you have a utility to send emails
from app.ml_utils.ml_utils import process_palm_image
# from app.ml_utils.preprocessing.palm_processor import PalmPreprocessor
import os
import logging

router = APIRouter()

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Initialize preprocessor
# preprocessor = PalmPreprocessor(target_size=(128, 128))

# # Setup folders
# base_dir = "data"
# raw_dir = os.path.join(base_dir, "raw")
# aug_dir = os.path.join(base_dir, "aug")

# os.makedirs(raw_dir, exist_ok=True)
# os.makedirs(aug_dir, exist_ok=True)

"""
Registers a new user.
This endpoint allows a new user to register by providing their email, username, and password.
The password is hashed before storing it in the database.
Args:
    request (RegisterRequest): The registration request containing user details.
    db (Session, optional): The database session dependency.
Returns:
    dict: A dictionary containing a success message and the registered user's email and username,
          or an error message if the registration fails.
"""
@router.post("/register")
async def register(
    palm_image: UploadFile = File(...),
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    email = email
    username = username
    password = password

    

    # try:
    #     # Process uploaded image
    #     img, user_id = await process_palm_image(palm_image)

    #     # Preprocess image
    #     processed_image = preprocessor.preprocess_image(img)

    #     if processed_image is None:
    #         raise HTTPException(
    #             status_code=400, detail="Failed to preprocess palm image"
    #         )

    #     # Generate augmentations
    #     augmented_images = preprocessor.generate_augmentations(processed_image)

    #     # Save augmented images
    #     person_id = preprocessor.save_augmented_images(
    #         augmented_images, base_dir=base_dir
    #     )

    #     return {
    #         "content":{
    #             "status": "success",
    #             "message": "Registration successful",
    #             "user_id": user_id,
    #             "person_id": person_id,
    #             "timestamp": datetime.now().isoformat(),
    #         }
    #     }

    # except Exception as e:
    #     logger.error(f"Registration error: {str(e)}")
    #     raise HTTPException(status_code=500, detail=str(e))




    # hash the password
    password = hash_password(password)

    # Create a new user instance
    new_user = User(email=email, name=username, password_hash=password)  # Hash the password before saving

    # check if the email is already in use
    user = db.query(User).filter(User.email == email).first()
    if user:
        return {"error": "Email already in use"}    
    
    # add the new user to the database
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:  
        db.rollback()
        return {"error": str(e)}
    
    # add profile
    new_profile = Profile(user_id=new_user.user_id)

    try:
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
    except Exception as e:
        db.rollback()
        return {"error": str(e)}


    # return the user details
    return {"message": "Registration successful", "email": email, "username": username}

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(request: LogoutRequest, db: Session = Depends(get_db)):
    try:
        invalidate_token(request.token, db)
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )

@router.post("/password_reset")
async def password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    print(user.user_id)

    reset_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(hours=1))
    password_reset = PasswordReset(
        user_id=user.user_id,
        reset_token=reset_token,
        token_expiration=datetime.utcnow() + timedelta(hours=1),
        is_used=False
    )

    db.add(password_reset)
    db.commit()

    send_reset_email(user.email, reset_token)  # Send the reset email

    return {"message": "Password reset email sent"}

@router.post("/password_reset/confirm")
async def password_reset_confirm(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    password_reset = db.query(PasswordReset).filter(PasswordReset.reset_token == request.token).first()
    if not password_reset or password_reset.is_used or password_reset.token_expiration < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user = db.query(User).filter(User.user_id == password_reset.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.password_hash = hash_password(request.new_password)
    password_reset.is_used = True

    db.commit()

    return {"message": "Password reset successful"}