
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.connection import get_db
from app.models import User
from app.schemas import TokenData
from app.security import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print("token", token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("payload", payload)
        user_email: str = payload.get("sub")
        print("user_email", user_email)
        if user_email is None:
            raise credentials_exception
        token_data = TokenData(user_email=user_email)
        print("token_data", token_data)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == token_data.user_email).first()
    if user is None:
        raise credentials_exception
    return user