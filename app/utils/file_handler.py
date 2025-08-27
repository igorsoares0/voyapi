import os
import uuid
from pathlib import Path
from fastapi import UploadFile
import shutil

from app.core.config import get_settings
from .file_validator import FileValidator

settings = get_settings()


class FileHandler:
    @staticmethod
    async def save_uploaded_file(file: UploadFile) -> tuple[str, str, int]:
        """
        Save uploaded file to disk
        Returns: (file_path, original_filename, file_size)
        """
        # Ensure upload directory exists
        upload_dir = FileValidator.ensure_upload_dir()
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            file_size = len(content)
        
        return str(file_path), file.filename, file_size
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete file from disk"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0