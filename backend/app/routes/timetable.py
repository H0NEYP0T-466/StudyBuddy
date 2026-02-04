from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import List
from bson import ObjectId
from datetime import datetime
import pandas as pd
import io

from app.models.database import get_database
from app.models.schemas import Timetable

router = APIRouter(prefix="/api/timetable", tags=["timetable"])


@router.get("/", response_model=List[dict])
async def get_timetable():
    """Get all timetable entries."""
    db = get_database()
    entries = await db.timetable.find().to_list(1000)
    
    # Convert ObjectId to string
    for entry in entries:
        entry["id"] = str(entry["_id"])
        del entry["_id"]
    
    return entries


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_timetable_entry(entry: dict):
    """Create a new timetable entry."""
    db = get_database()
    
    entry_data = {
        "subject": entry.get("subject"),
        "teacher": entry.get("teacher"),
        "class_number": entry.get("class_number"),
        "class_type": entry.get("class_type"),
        "timings": entry.get("timings"),
        "day": entry.get("day"),
        "created_at": datetime.utcnow()
    }
    
    # Validate required fields
    required = ["subject", "teacher", "class_number", "class_type", "timings", "day"]
    for field in required:
        if not entry_data.get(field):
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    result = await db.timetable.insert_one(entry_data)
    entry_data["id"] = str(result.inserted_id)
    if "_id" in entry_data:
        del entry_data["_id"]
    
    return entry_data


@router.put("/{entry_id}")
async def update_timetable_entry(entry_id: str, entry: dict):
    """Update a timetable entry."""
    db = get_database()
    
    update_data = {
        "subject": entry.get("subject"),
        "teacher": entry.get("teacher"),
        "class_number": entry.get("class_number"),
        "class_type": entry.get("class_type"),
        "timings": entry.get("timings"),
        "day": entry.get("day")
    }
    
    try:
        result = await db.timetable.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": update_data}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid entry ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    return {"message": "Timetable entry updated successfully"}


@router.delete("/{entry_id}")
async def delete_timetable_entry(entry_id: str):
    """Delete a timetable entry."""
    db = get_database()
    
    try:
        result = await db.timetable.delete_one({"_id": ObjectId(entry_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid entry ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    return {"message": "Timetable entry deleted successfully"}


@router.delete("/")
async def delete_all_timetable():
    """Delete all timetable entries."""
    db = get_database()
    result = await db.timetable.delete_many({})
    
    return {"message": f"Deleted {result.deleted_count} entries"}


@router.post("/import")
async def import_timetable(file: UploadFile = File(...)):
    """Import timetable from CSV/XLSX file."""
    db = get_database()
    
    try:
        # Read file
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="File must be CSV or XLSX")
        
        # Validate columns
        required_columns = ['subject', 'teacher', 'class_number', 'class_type', 'timings', 'day']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"CSV must contain columns: {', '.join(required_columns)}"
            )
        
        # Insert entries
        entries = []
        for _, row in df.iterrows():
            entry = {
                "subject": str(row['subject']),
                "teacher": str(row['teacher']),
                "class_number": str(row['class_number']),
                "class_type": str(row['class_type']),
                "timings": str(row['timings']),
                "day": str(row['day']),
                "created_at": datetime.utcnow()
            }
            entries.append(entry)
        
        if entries:
            result = await db.timetable.insert_many(entries)
            return {
                "message": f"Successfully imported {len(result.inserted_ids)} entries",
                "count": len(result.inserted_ids)
            }
        else:
            raise HTTPException(status_code=400, detail="No valid entries found in file")
            
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="File is empty")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
