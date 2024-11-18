from fastapi import FastAPI
from routers import auth, history, analytics, profile, contact, palm_recognition

app = FastAPI()

@app.get("/")
async def read_root():
    return {"userid": "Bagas!"}

app.include_router(auth.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(contact.router, prefix="/api/v1")
app.include_router(palm_recognition.router, prefix="/api/v1")






