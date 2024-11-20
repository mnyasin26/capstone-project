from fastapi import UploadFile, HTTPException
import numpy as np
import cv2
import os
from datetime import datetime
import uuid
from app.ml_utils.preprocessing.palm_processor import PalmPreprocessor
import logging


print("Hello World")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup folders
base_dir = "data"
raw_dir = os.path.join(base_dir, "raw")
aug_dir = os.path.join(base_dir, "aug")

os.makedirs(raw_dir, exist_ok=True)
os.makedirs(aug_dir, exist_ok=True)


async def process_palm_image(file: UploadFile) -> tuple:
    """Process uploaded palm image"""
    try:
        # Read image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Save original image
        user_id = str(uuid.uuid4())
        original_path = os.path.join(raw_dir, f"{user_id}.jpg")
        cv2.imwrite(original_path, img)

        return img, user_id

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))