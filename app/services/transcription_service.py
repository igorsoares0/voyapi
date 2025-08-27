import asyncio
import httpx
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.voice_note import VoiceNote, TranscriptionStatus

settings = get_settings()


class AssemblyAIService:
    def __init__(self):
        self.api_key = settings.ASSEMBLYAI_API_KEY
        self.base_url = "https://api.assemblyai.com/v2"
        self.headers = {"authorization": self.api_key}
    
    async def upload_file(self, file_path: str) -> Optional[str]:
        """Upload audio file to AssemblyAI and return upload URL"""
        try:
            async with httpx.AsyncClient() as client:
                with open(file_path, "rb") as f:
                    response = await client.post(
                        f"{self.base_url}/upload",
                        headers=self.headers,
                        files={"file": f}
                    )
                
                if response.status_code == 200:
                    return response.json()["upload_url"]
                else:
                    print(f"Upload failed: {response.text}")
                    return None
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    async def request_transcription(self, audio_url: str) -> Optional[str]:
        """Request transcription from AssemblyAI and return job ID"""
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "audio_url": audio_url,
                    "language_detection": True,
                }
                
                response = await client.post(
                    f"{self.base_url}/transcript",
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code == 200:
                    return response.json()["id"]
                else:
                    print(f"Transcription request failed: {response.text}")
                    return None
        except Exception as e:
            print(f"Error requesting transcription: {e}")
            return None
    
    async def get_transcription_status(self, job_id: str) -> tuple[str, Optional[str]]:
        """Get transcription status and text if completed"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/transcript/{job_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data["status"]
                    text = data.get("text") if status == "completed" else None
                    return status, text
                else:
                    print(f"Status check failed: {response.text}")
                    return "error", None
        except Exception as e:
            print(f"Error checking transcription status: {e}")
            return "error", None
    
    async def transcribe_audio_file(self, file_path: str, voice_note_id: int, db: Session):
        """Complete transcription workflow"""
        try:
            # Update status to processing
            voice_note = db.query(VoiceNote).filter(VoiceNote.id == voice_note_id).first()
            if not voice_note:
                return
            
            voice_note.transcription_status = TranscriptionStatus.PROCESSING
            db.commit()
            
            # Upload file
            audio_url = await self.upload_file(file_path)
            if not audio_url:
                voice_note.transcription_status = TranscriptionStatus.FAILED
                db.commit()
                return
            
            # Request transcription
            job_id = await self.request_transcription(audio_url)
            if not job_id:
                voice_note.transcription_status = TranscriptionStatus.FAILED
                db.commit()
                return
            
            # Save job ID
            voice_note.assemblyai_job_id = job_id
            db.commit()
            
            # Poll for completion (in production, use webhooks)
            max_attempts = 60  # 5 minutes with 5-second intervals
            attempt = 0
            
            while attempt < max_attempts:
                status, text = await self.get_transcription_status(job_id)
                
                if status == "completed":
                    voice_note.transcription_text = text
                    voice_note.transcription_status = TranscriptionStatus.COMPLETED
                    db.commit()
                    break
                elif status == "error":
                    voice_note.transcription_status = TranscriptionStatus.FAILED
                    db.commit()
                    break
                
                await asyncio.sleep(5)
                attempt += 1
            
            # If we reached max attempts, mark as failed
            if attempt >= max_attempts:
                voice_note.transcription_status = TranscriptionStatus.FAILED
                db.commit()
                
        except Exception as e:
            print(f"Error in transcription workflow: {e}")
            if 'voice_note' in locals():
                voice_note.transcription_status = TranscriptionStatus.FAILED
                db.commit()