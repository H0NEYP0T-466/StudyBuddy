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

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.get("/", response_model=List[dict])
async def get_notes(folder_id: Optional[str] = None):
    """Get all notes or notes in a specific folder."""
    db = get_database()
    
    query = {}
    if folder_id:
        query["folder_id"] = folder_id
    
    notes = await db.notes.find(query).sort("updated_at", -1).to_list(1000)
    
    # Convert ObjectId to string
    for note in notes:
        note["id"] = str(note["_id"])
        del note["_id"]
    
    return notes


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_note(note: dict):
    """Create a new note and add to RAG index."""
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
    
    # Add to RAG index
    try:
        rag = await get_rag_system()
        await rag.add_note_to_index(
            note_data["title"], 
            note_data["content"],
            note_id
        )
    except Exception as e:
        print(f"Error adding note to RAG: {e}")
    
    note_data["id"] = note_id
    del note_data["_id"] if "_id" in note_data else None
    
    return note_data


@router.get("/{note_id}")
async def get_note(note_id: str):
    """Get a specific note."""
    db = get_database()
    
    try:
        note = await db.notes.find_one({"_id": ObjectId(note_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid note ID")
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note["id"] = str(note["_id"])
    del note["_id"]
    
    return note


@router.put("/{note_id}")
async def update_note(note_id: str, note: dict):
    """Update a note."""
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
        raise HTTPException(status_code=400, detail="Invalid note ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update RAG index
    try:
        rag = await get_rag_system()
        await rag.add_note_to_index(
            update_data["title"], 
            update_data["content"],
            note_id
        )
    except Exception as e:
        print(f"Error updating note in RAG: {e}")
    
    return {"message": "Note updated successfully"}


@router.delete("/{note_id}")
async def delete_note(note_id: str):
    """Delete a note."""
    db = get_database()
    
    try:
        result = await db.notes.delete_one({"_id": ObjectId(note_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid note ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {"message": "Note deleted successfully"}


@router.post("/generate")
async def generate_notes(
    model: str = Form(...),
    files: List[UploadFile] = File(None)
):
    """Generate notes from uploaded files using AI."""
    
    # Save uploaded files temporarily
    temp_files = []
    extracted_text = ""
    
    try:
        if files:
            os.makedirs("backend/uploads", exist_ok=True)
            
            for file in files:
                file_path = f"backend/uploads/{file.filename}"
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                temp_files.append(file_path)
                
                # Extract text
                text = await extract_text_from_file(file_path)
                extracted_text += text + "\n\n"
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text could be extracted from files")
        
        # Generate notes based on model
        if model.startswith("gemini"):
            notes = await gemini_service.generate_notes(
                extracted_text, 
                model,
                temp_files if files else None
            )
        elif model.startswith("longcat"):
            notes = await longcat_service.generate_notes(extracted_text, model)
        else:
            notes = "Model not supported for notes generation"
        
        return {
            "notes": notes,
            "model_used": model
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temporary files
        for file_path in temp_files:
            try:
                os.remove(file_path)
            except:
                pass


@router.get("/search/{query}")
async def search_notes(query: str):
    """Search notes by title or content."""
    db = get_database()
    
    notes = await db.notes.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"content": {"$regex": query, "$options": "i"}}
        ]
    }).to_list(100)
    
    # Convert ObjectId to string
    for note in notes:
        note["id"] = str(note["_id"])
        del note["_id"]
    
    return notes
