from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session
from connection import get_db
from models import User  # Assuming you have a User model defined
from security import hash_password, verify_password, create_access_token, invalidate_token

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LogoutRequest(BaseModel):
    token: str

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
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    email = request.email
    username = request.username
    password = request.password

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
            detail=str(e)
        )

@router.post("/password_reset")
async def password_reset():
    # Password reset logic
    pass