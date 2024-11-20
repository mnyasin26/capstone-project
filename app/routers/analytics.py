from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.connection import get_db
from app.models import Analytics, User
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/analytic")
async def get_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analytics = db.query(Analytics).filter(Analytics.user_id == current_user.user_id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    return {
        "i_scanned": {
            "total": analytics.total_i_scanned,
            "successful": analytics.successful_i_scanned,
            "failed": analytics.failed_i_scanned,
            "last_time": analytics.last_time_i_scanned
        },
        "whos_scanned_me": {
            "total": analytics.total_whos_scanned_me,
            "successful": analytics.successful_whos_scanned_me,
            "failed": analytics.failed_whos_scanned_me,
            "last_time": analytics.last_time_whos_scanned_me
        }
    }