import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
import io
import time
from fastapi import UploadFile, HTTPException

from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

class ImageConfig:
    MAX_SIZE_MB = 10

    @staticmethod
    async def validate_and_upload_profile_picture(file: UploadFile, user_id: str) -> str:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="File is not an image"
            )
        # Read and validate file size
        contents = await file.read()
        if len(contents) > ImageConfig.MAX_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {ImageConfig.MAX_SIZE_MB} MB limit"
            )
        # Prepare file for Cloudinary
        file_stream = io.BytesIO(contents)
        file_stream.name = file.filename

        # Upload to Cloudinary
        try:
            timestamp = int(time.time())
            response = cloudinary.uploader.upload(file_stream, folder=f"users/{user_id}/profile",timestamp=timestamp)
            return response.get('secure_url')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading image: {e}")

    @staticmethod
    def delete_profile_picture(public_id: str):
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            raise Exception(f"Error deleting image: {e}")

image_service = ImageConfig()