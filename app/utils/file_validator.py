import os
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException

from app.core.config import get_settings

settings = get_settings()


class FileValidator:
    @staticmethod
    def validate_audio_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
        """Validate if uploaded file is a valid audio file"""
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.ALLOWED_AUDIO_EXTENSIONS:
            return False, f"File extension {file_extension} not allowed. Allowed extensions: {settings.ALLOWED_AUDIO_EXTENSIONS}"
        
        # Check file size
        if hasattr(file.file, 'seek'):
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Seek back to beginning
            
            if file_size > settings.MAX_FILE_SIZE:
                return False, f"File size {file_size} bytes exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        
        return True, None
    
    @staticmethod
    def get_mime_type(file_path: str) -> str:
        """Get MIME type of file using extension mapping"""
        extension_to_mime = {
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.m4a': 'audio/mp4'
        }
        file_extension = Path(file_path).suffix.lower()
        return extension_to_mime.get(file_extension, 'application/octet-stream')
    
    @staticmethod
    def ensure_upload_dir():
        """Ensure upload directory exists"""
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir