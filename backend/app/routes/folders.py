from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from app.models.database import get_database
from app.models.schemas import Folder

router = APIRouter(prefix="/api/folders", tags=["folders"])


@router.get("/", response_model=List[dict])
async def get_folders():
    """Get all folders."""
    db = get_database()
    folders = await db.folders.find().to_list(1000)
    
    # Convert ObjectId to string
    for folder in folders:
        folder["id"] = str(folder["_id"])
        del folder["_id"]
    
    return folders


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_folder(folder: dict):
    """Create a new folder."""
    db = get_database()
    
    folder_data = {
        "name": folder.get("name"),
        "created_at": datetime.utcnow()
    }
    
    result = await db.folders.insert_one(folder_data)
    folder_data["id"] = str(result.inserted_id)
    del folder_data["_id"] if "_id" in folder_data else None
    
    return folder_data


@router.get("/{folder_id}")
async def get_folder(folder_id: str):
    """Get a specific folder."""
    db = get_database()
    
    try:
        folder = await db.folders.find_one({"_id": ObjectId(folder_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid folder ID")
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    folder["id"] = str(folder["_id"])
    del folder["_id"]
    
    return folder


@router.put("/{folder_id}")
async def update_folder(folder_id: str, folder: dict):
    """Update a folder."""
    db = get_database()
    
    try:
        result = await db.folders.update_one(
            {"_id": ObjectId(folder_id)},
            {"$set": {"name": folder.get("name")}}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid folder ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    return {"message": "Folder updated successfully"}


@router.delete("/{folder_id}")
async def delete_folder(folder_id: str):
    """Delete a folder and all its notes."""
    db = get_database()
    
    try:
        # Delete all notes in the folder
        await db.notes.delete_many({"folder_id": folder_id})
        
        # Delete the folder
        result = await db.folders.delete_one({"_id": ObjectId(folder_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid folder ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    return {"message": "Folder and its notes deleted successfully"}
