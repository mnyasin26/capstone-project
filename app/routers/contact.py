
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import ContactInfo, User
from app.connection import get_db
from app.schemas import AddContactInfoRequest, DeleteContactInfoRequest, EditContactInfoRequest
from app.dependencies import get_current_user
import uuid


router = APIRouter()

@router.get("/contact_info")
async def get_contact_info(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Get contact info logic
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    contact_infos = db.query(ContactInfo).filter(ContactInfo.user_id == current_user.user_id).all()
    
    if not contact_infos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No contact information found for the user.",
        )
    return {
        "contacts": [
            {
                "contact_id": contact.contact_id,
                "contact_type": contact.contact_type,
                "contact_value": contact.contact_value,
                "notes": contact.notes
            }
            for contact in contact_infos
        ]
    }

@router.post("/contact_info/add")
async def add_contact_info(request: AddContactInfoRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_contact_info = ContactInfo(
        contact_id=str(uuid.uuid4()),  # Generate UUID untuk contact_id
        user_id=current_user.user_id,
        contact_type=request.contact_type,
        contact_value=request.contact_value,
        notes=request.notes
    )

    try:
        # Menyimpan data ke database
        db.add(new_contact_info)
        db.commit()
        db.refresh(new_contact_info)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add contact info: {str(e)}",
        )
        
    return {
        "message": "Contact information added successfully",
        "contact_info": {
            "contact_id": new_contact_info.contact_id,
            "user_id": new_contact_info.user_id,
            "contact_type": new_contact_info.contact_type,
            "contact_value": new_contact_info.contact_value,
            "notes": new_contact_info.notes
        }
    }

@router.put("/contact_info/edit")
async def edit_contact_info(request: EditContactInfoRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    
    contact_info = db.query(ContactInfo).filter(
        ContactInfo.contact_id == request.contact_id,
        ContactInfo.user_id == current_user.user_id
    ).first()

    if not contact_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact information not found or you do not have permission to edit it."
        )
    
    # Update fields if they are provided in the request
    if request.contact_type:
        contact_info.contact_type = request.contact_type
    if request.contact_value:
        contact_info.contact_value = request.contact_value
    if request.notes:
        contact_info.notes = request.notes

    try:
        db.commit()  # Commit the changes to the database
        db.refresh(contact_info)  # Refresh to get the latest data
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {
        "message": "Contact information updated successfully",
        "contact_info": {
            "contact_id": contact_info.contact_id,
            "user_id": contact_info.user_id,
            "contact_type": contact_info.contact_type,
            "contact_value": contact_info.contact_value,
            "notes": contact_info.notes
        }
    }

@router.delete("/contact_info/delete")
async def delete_contact_info(request: DeleteContactInfoRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    
    contact_info = db.query(ContactInfo).filter(
        ContactInfo.contact_id == request.contact_id, 
        ContactInfo.user_id == current_user.user_id
    ).first()

    if not contact_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact information not found or you do not have permission to delete it."
        )
    
    try:
        db.delete(contact_info)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {
        "message": "Contact information deleted successfully",
        "contact_id": request.contact_id
    }