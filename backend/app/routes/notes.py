from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import os
import shutil

from app.models.database import get_database
from app.models.schemas import Note
from app.services.rag_service import get_rag_system
from app.services.gemini_service import gemini_service
from app.services.longcat_service import longcat_service
from app.utils.file_processor import extract_text_from_file
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/notes", tags=["notes"])
logger = get_logger("NOTES")


@router.get("/", response_model=List[dict])
async def get_notes(folder_id: Optional[str] = None):
    """Get all notes or notes in a specific folder."""
    logger.info(f"Fetching notes" + (f" for folder: {folder_id}" if folder_id else " (all folders)"))
    db = get_database()
    
    query = {}
    if folder_id:
        query["folder_id"] = folder_id
    
    notes = await db.notes.find(query).sort("updated_at", -1).to_list(1000)
    logger.success(f"Retrieved {len(notes)} notes")
    
    # Convert ObjectId to string
    for note in notes:
        note["id"] = str(note["_id"])
        del note["_id"]
    
    return notes


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_note(note: dict):
    """Create a new note and add to RAG index."""
    logger.info(f"Creating new note: {note.get('title', 'Untitled')}")
    db = get_database()
    
    note_data = {
        "title": note.get("title"),
        "content": note.get("content", ""),
        "folder_id": note.get("folder_id"),
        "model_used": note.get("model_used"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.notes.insert_one(note_data)
    note_id = str(result.inserted_id)
    logger.debug(f"Note inserted with ID: {note_id}")
    
    # Add to RAG index
    try:
        logger.info("Adding note to RAG index...")
        rag = await get_rag_system()
        await rag.add_note_to_index(
            note_data["title"], 
            note_data["content"],
            note_id
        )
        logger.success(f"Note added to RAG index successfully")
    except Exception as e:
        logger.error(f"Failed to add note to RAG: {str(e)}", exc_info=e)
    
    note_data["id"] = note_id
    if "_id" in note_data:
        del note_data["_id"]
    
    logger.success(f"Note created successfully: {note_data['title']}")
    return note_data


@router.get("/{note_id}")
async def get_note(note_id: str):
    """Get a specific note."""
    logger.info(f"Fetching note: {note_id}")
    db = get_database()
    
    try:
        note = await db.notes.find_one({"_id": ObjectId(note_id)})
    except:
        logger.error(f"Invalid note ID: {note_id}")
        raise HTTPException(status_code=400, detail="Invalid note ID")
    
    if not note:
        logger.warning(f"Note not found: {note_id}")
        raise HTTPException(status_code=404, detail="Note not found")
    
    note["id"] = str(note["_id"])
    del note["_id"]
    
    logger.success(f"Retrieved note: {note.get('title', 'Untitled')}")
    return note


@router.put("/{note_id}")
async def update_note(note_id: str, note: dict):
    """Update a note."""
    logger.info(f"Updating note: {note_id}")
    db = get_database()
    
    update_data = {
        "title": note.get("title"),
        "content": note.get("content"),
        "folder_id": note.get("folder_id"),
        "updated_at": datetime.utcnow()
    }
    
    try:
        result = await db.notes.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": update_data}
        )
    except:
        logger.error(f"Invalid note ID: {note_id}")
        raise HTTPException(status_code=400, detail="Invalid note ID")
    
    if result.matched_count == 0:
        logger.warning(f"Note not found: {note_id}")
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update RAG index
    try:
        logger.info("Updating note in RAG index...")
        rag = await get_rag_system()
        await rag.add_note_to_index(
            update_data["title"], 
            update_data["content"],
            note_id
        )
        logger.success("Note updated in RAG index")
    except Exception as e:
        logger.error(f"Failed to update note in RAG: {str(e)}", exc_info=e)
    
    logger.success(f"Note updated successfully: {update_data['title']}")
    return {"message": "Note updated successfully"}


@router.delete("/{note_id}")
async def delete_note(note_id: str):
    """Delete a note."""
    logger.info(f"Deleting note: {note_id}")
    db = get_database()
    
    try:
        result = await db.notes.delete_one({"_id": ObjectId(note_id)})
    except:
        logger.error(f"Invalid note ID: {note_id}")
        raise HTTPException(status_code=400, detail="Invalid note ID")
    
    if result.deleted_count == 0:
        logger.warning(f"Note not found: {note_id}")
        raise HTTPException(status_code=404, detail="Note not found")
    
    logger.success(f"Note deleted successfully: {note_id}")
    return {"message": "Note deleted successfully"}


@router.post("/generate")
async def generate_notes(
    model: str = Form(...),
    files: List[UploadFile] = File(None)
):
    """Generate notes from uploaded files using AI."""
    logger.info(f"Generating notes using model: {model}")
    
    # Save uploaded files temporarily
    temp_files = []
    extracted_text = ""
    
    try:
        if files:
            logger.debug(f"Processing {len(files)} files")
            os.makedirs("backend/uploads", exist_ok=True)
            
            for file in files:
                file_path = f"backend/uploads/{file.filename}"
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                temp_files.append(file_path)
                logger.info(f"Saved file: {file.filename}")
                
                # Extract text
                text = await extract_text_from_file(file_path)
                extracted_text += text + "\n\n"
                logger.debug(f"Extracted {len(text)} characters from {file.filename}")
        
        if not extracted_text:
            logger.error("No text extracted from files")
            raise HTTPException(status_code=400, detail="No text could be extracted from files")
        
        logger.info(f"Total extracted text: {len(extracted_text)} characters")
        
        # Generate notes based on model
        if model.startswith("gemini"):
            logger.info(f"Generating notes with Gemini: {model}")
            notes = await gemini_service.generate_notes(
                extracted_text, 
                model,
                temp_files if files else None
            )
            logger.success(f"Gemini notes generated ({len(notes)} characters)")
        elif model.startswith("longcat"):
            logger.info(f"Generating notes with LongCat: {model}")
            notes = await longcat_service.generate_notes(extracted_text, model)
            logger.success(f"LongCat notes generated ({len(notes)} characters)")
        else:
            logger.error(f"Model not supported: {model}")
            notes = "Model not supported for notes generation"
        
        return {
            "notes": notes,
            "model_used": model
        }
        
    except Exception as e:
        logger.error(f"Note generation failed: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temporary files
        for file_path in temp_files:
            try:
                os.remove(file_path)
                logger.debug(f"Cleaned up: {file_path}")
            except:
                logger.warning(f"Failed to clean up: {file_path}")


@router.get("/search/{query}")
async def search_notes(query: str):
    """Search notes by title or content."""
    logger.info(f"Searching notes with query: {query}")
    db = get_database()
    
    notes = await db.notes.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"content": {"$regex": query, "$options": "i"}}
        ]
    }).to_list(100)
    
    logger.success(f"Found {len(notes)} notes matching query: {query}")
    
    # Convert ObjectId to string
    for note in notes:
        note["id"] = str(note["_id"])
        del note["_id"]
    
    return notes
