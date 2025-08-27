import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.voice_note import VoiceNote
from app.schemas.voice_note import (
    VoiceNoteCreate, 
    VoiceNoteUpdate, 
    VoiceNoteResponse, 
    VoiceNoteList,
    TranscriptionResponse
)
from app.utils.file_validator import FileValidator
from app.utils.file_handler import FileHandler
from app.services.transcription_service import AssemblyAIService

router = APIRouter(prefix="/voice-notes", tags=["voice-notes"])


@router.post("/", response_model=VoiceNoteResponse)
async def create_voice_note(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload audio file and create voice note"""
    
    # Validate file
    is_valid, error_message = FileValidator.validate_audio_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    try:
        # Save file
        file_path, original_filename, file_size = await FileHandler.save_uploaded_file(file)
        
        # Get MIME type
        mime_type = FileValidator.get_mime_type(file_path)
        
        # Create voice note in database
        voice_note = VoiceNote(
            title=title,
            description=description,
            file_path=file_path,
            file_name=original_filename,
            file_size=file_size,
            mime_type=mime_type
        )
        
        db.add(voice_note)
        db.commit()
        db.refresh(voice_note)
        
        # Start transcription in background
        transcription_service = AssemblyAIService()
        background_tasks.add_task(
            transcription_service.transcribe_audio_file,
            file_path,
            voice_note.id,
            db
        )
        
        return voice_note
        
    except Exception as e:
        # Clean up file if database operation fails
        if 'file_path' in locals():
            FileHandler.delete_file(file_path)
        raise HTTPException(status_code=500, detail=f"Error creating voice note: {str(e)}")


@router.get("/", response_model=VoiceNoteList)
async def list_voice_notes(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    """List all voice notes with pagination"""
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    total = db.query(func.count(VoiceNote.id)).scalar()
    
    # Get paginated results
    voice_notes = db.query(VoiceNote)\
        .order_by(VoiceNote.created_at.desc())\
        .offset(offset)\
        .limit(per_page)\
        .all()
    
    # Calculate total pages
    pages = (total + per_page - 1) // per_page
    
    return VoiceNoteList(
        items=voice_notes,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.get("/{voice_note_id}", response_model=VoiceNoteResponse)
async def get_voice_note(voice_note_id: int, db: Session = Depends(get_db)):
    """Get specific voice note by ID"""
    
    voice_note = db.query(VoiceNote).filter(VoiceNote.id == voice_note_id).first()
    if not voice_note:
        raise HTTPException(status_code=404, detail="Voice note not found")
    
    return voice_note


@router.put("/{voice_note_id}", response_model=VoiceNoteResponse)
async def update_voice_note(
    voice_note_id: int,
    voice_note_update: VoiceNoteUpdate,
    db: Session = Depends(get_db)
):
    """Update voice note metadata"""
    
    voice_note = db.query(VoiceNote).filter(VoiceNote.id == voice_note_id).first()
    if not voice_note:
        raise HTTPException(status_code=404, detail="Voice note not found")
    
    # Update fields
    update_data = voice_note_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(voice_note, field, value)
    
    db.commit()
    db.refresh(voice_note)
    
    return voice_note


@router.delete("/{voice_note_id}")
async def delete_voice_note(voice_note_id: int, db: Session = Depends(get_db)):
    """Delete voice note and associated file"""
    
    voice_note = db.query(VoiceNote).filter(VoiceNote.id == voice_note_id).first()
    if not voice_note:
        raise HTTPException(status_code=404, detail="Voice note not found")
    
    # Delete file from disk
    FileHandler.delete_file(voice_note.file_path)
    
    # Delete from database
    db.delete(voice_note)
    db.commit()
    
    return {"message": "Voice note deleted successfully"}


@router.get("/{voice_note_id}/transcription", response_model=TranscriptionResponse)
async def get_transcription(voice_note_id: int, db: Session = Depends(get_db)):
    """Get transcription for voice note"""
    
    voice_note = db.query(VoiceNote).filter(VoiceNote.id == voice_note_id).first()
    if not voice_note:
        raise HTTPException(status_code=404, detail="Voice note not found")
    
    return TranscriptionResponse(
        id=voice_note.id,
        transcription_text=voice_note.transcription_text,
        transcription_status=voice_note.transcription_status,
        created_at=voice_note.created_at,
        updated_at=voice_note.updated_at
    )