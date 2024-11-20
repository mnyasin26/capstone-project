from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, history, analytics, profile, palm_recognition
from app.routers import contact
from app.models import Base
from app.connection import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
# import mediapipe as mp
import os

app = FastAPI()

# Serve static files from the "uploads" directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def read_root():
    return {"userid": "Bagas!"}

app.include_router(auth.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(contact.router, prefix="/api/v1")
app.include_router(palm_recognition.router, prefix="/api/v1")

# Create all tables in the database
@app.on_event("startup")
async def startup_event():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Execute dummies.sql
    Session = sessionmaker(bind=engine)
    session = Session()
    with open('sql\dummies.sql', 'r') as file:
        sql_commands = file.read().split(';')
        for command in sql_commands:
            if command.strip():
                session.execute(text(command))
        session.commit()
    session.close()









