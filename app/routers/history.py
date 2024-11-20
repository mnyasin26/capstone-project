from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.connection import get_db
from app.models import PalmRecognitionActivity, ContactInfo, User, Profile
from app.dependencies import get_current_user  # Assuming you have this dependency

router = APIRouter()

@router.get("/history")
async def get_history(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    who_scanned_me = db.query(PalmRecognitionActivity).filter(PalmRecognitionActivity.scanned_user_id == current_user.user_id).all()
    who_i_scanned = db.query(PalmRecognitionActivity).filter(PalmRecognitionActivity.user_id == current_user.user_id).all()

    if not who_scanned_me and not who_i_scanned:
        raise HTTPException(status_code=404, detail="History not found")

    def get_contacts(user_ids):
        return db.query(ContactInfo).filter(ContactInfo.user_id.in_(user_ids)).all()

    def get_profiles(user_ids):
        return db.query(User, Profile).filter(User.user_id == Profile.user_id, User.user_id.in_(user_ids)).all()

    who_scanned_me_contacts = get_contacts([activity.user_id for activity in who_scanned_me])
    who_i_scanned_contacts = get_contacts([activity.scanned_user_id for activity in who_i_scanned])

    who_scanned_me_profiles = get_profiles([activity.user_id for activity in who_scanned_me])
    who_i_scanned_profiles = get_profiles([activity.scanned_user_id for activity in who_i_scanned])

    def attach_contacts_and_profiles(activities, contacts, profiles):
        contact_dict = {contact.user_id: [] for contact in contacts}
        for contact in contacts:
            contact_dict[contact.user_id].append({
                "notes": contact.notes,
                "contact_type": contact.contact_type,
                "contact_value": contact.contact_value
            })

        profile_dict = {profile.User.user_id: {
            "name": profile.User.name,
            "bio": profile.Profile.bio,
            "job_title": profile.Profile.job_title,
            "company": profile.Profile.company,
            "profile_picture": profile.Profile.profile_picture
        } for profile in profiles}

        result = []
        for activity in activities:
            user_id = activity.user_id if activity.user_id in contact_dict else activity.scanned_user_id
            result.append({
                "time_scanned": activity.time_scanned,
                "profile": profile_dict.get(user_id, {}),
                "contacts": contact_dict.get(user_id, [])
            })
        return result

    who_scanned_me = attach_contacts_and_profiles(who_scanned_me, who_scanned_me_contacts, who_scanned_me_profiles)
    who_i_scanned = attach_contacts_and_profiles(who_i_scanned, who_i_scanned_contacts, who_i_scanned_profiles)

    return {
        "who_scanned_me": who_scanned_me,
        "who_i_scanned": who_i_scanned
    }