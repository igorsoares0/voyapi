from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import voice_notes
from app.core.config import get_settings

app = FastAPI(
    title="Voice Notes API",
    description="MVP API for voice notes with audio transcription",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_notes.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Voice Notes API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/setup-database")
async def setup_database():
    """Temporary endpoint to create database tables"""
    try:
        from app.core.database import engine
        from app.models.voice_note import Base
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        return {"message": "Database tables created successfully"}
    except Exception as e:
        return {"error": f"Failed to create tables: {str(e)}"}