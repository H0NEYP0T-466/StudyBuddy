from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import List
from bson import ObjectId
from datetime import datetime
import pandas as pd
import io

from app.models.database import get_database
from app.models.schemas import Timetable
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/timetable", tags=["timetable"])
logger = get_logger("TIMETABLE")


@router.get("/", response_model=List[dict])
async def get_timetable():
    """Get all timetable entries."""
    logger.info("Fetching all timetable entries")
    db = get_database()
    entries = await db.timetable.find().to_list(1000)
    
    # Convert ObjectId to string and ensure proper field names
    for entry in entries:
        entry["id"] = str(entry["_id"])
        del entry["_id"]
    
    logger.success(f"Retrieved {len(entries)} timetable entries")
    return entries


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_timetable_entry(entry: dict):
    """Create a new timetable entry."""
    logger.info(f"Creating new timetable entry for {entry.get('day')}: {entry.get('subject')}")
    db = get_database()
    
    # Frontend expects: day, start_time, end_time, subject, type, location, created_at, updated_at
    entry_data = {
        "day": entry.get("day"),
        "start_time": entry.get("start_time"),
        "end_time": entry.get("end_time"),
        "subject": entry.get("subject"),
        "type": entry.get("type"),
        "location": entry.get("location"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Validate required fields
    required = ["day", "start_time", "end_time", "subject", "type"]
    for field in required:
        if not entry_data.get(field):
            logger.error(f"Missing required field: {field}")
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    result = await db.timetable.insert_one(entry_data)
    entry_data["id"] = str(result.inserted_id)
    if "_id" in entry_data:
        del entry_data["_id"]
    
    logger.success(f"Timetable entry created: {entry_data['subject']} on {entry_data['day']}")
    return entry_data


@router.put("/{entry_id}")
async def update_timetable_entry(entry_id: str, entry: dict):
    """Update a timetable entry."""
    logger.info(f"Updating timetable entry: {entry_id}")
    db = get_database()
    
    # Frontend expects: day, start_time, end_time, subject, type, location
    update_data = {
        "day": entry.get("day"),
        "start_time": entry.get("start_time"),
        "end_time": entry.get("end_time"),
        "subject": entry.get("subject"),
        "type": entry.get("type"),
        "location": entry.get("location"),
        "updated_at": datetime.utcnow()
    }
    
    try:
        result = await db.timetable.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": update_data}
        )
    except:
        logger.error(f"Invalid entry ID: {entry_id}")
        raise HTTPException(status_code=400, detail="Invalid entry ID")
    
    if result.matched_count == 0:
        logger.warning(f"Timetable entry not found: {entry_id}")
        raise HTTPException(status_code=404, detail="Entry not found")
    
    logger.success(f"Timetable entry updated: {entry_id}")
    return {"message": "Timetable entry updated successfully"}


@router.delete("/{entry_id}")
async def delete_timetable_entry(entry_id: str):
    """Delete a timetable entry."""
    logger.info(f"Deleting timetable entry: {entry_id}")
    db = get_database()
    
    try:
        result = await db.timetable.delete_one({"_id": ObjectId(entry_id)})
    except:
        logger.error(f"Invalid entry ID: {entry_id}")
        raise HTTPException(status_code=400, detail="Invalid entry ID")
    
    if result.deleted_count == 0:
        logger.warning(f"Timetable entry not found: {entry_id}")
        raise HTTPException(status_code=404, detail="Entry not found")
    
    logger.success(f"Timetable entry deleted: {entry_id}")
    return {"message": "Timetable entry deleted successfully"}


@router.delete("/")
async def delete_all_timetable():
    """Delete all timetable entries."""
    logger.info("Deleting all timetable entries")
    db = get_database()
    result = await db.timetable.delete_many({})
    
    logger.success(f"Deleted {result.deleted_count} timetable entries")
    return {"message": f"Deleted {result.deleted_count} entries"}


@router.post("/import")
async def import_timetable(file: UploadFile = File(...)):
    """Import timetable from CSV/XLSX file."""
    logger.info(f"Importing timetable from file: {file.filename}")
    db = get_database()
    
    try:
        # Read file
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            logger.error(f"Invalid file format: {file.filename}")
            raise HTTPException(status_code=400, detail="File must be CSV or XLSX")
        
        logger.debug(f"File read successfully, {len(df)} rows found")
        
        # Validate columns - frontend expects: day, start_time, end_time, subject, type, location
        required_columns = ['day', 'start_time', 'end_time', 'subject', 'type']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns in file")
            raise HTTPException(
                status_code=400, 
                detail=f"CSV must contain columns: {', '.join(required_columns)}"
            )
        
        # Insert entries
        entries = []
        for _, row in df.iterrows():
            entry = {
                "day": str(row['day']),
                "start_time": str(row['start_time']),
                "end_time": str(row['end_time']),
                "subject": str(row['subject']),
                "type": str(row['type']),
                "location": str(row.get('location', '')),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            entries.append(entry)
        
        if entries:
            result = await db.timetable.insert_many(entries)
            logger.success(f"Successfully imported {len(result.inserted_ids)} entries from {file.filename}")
            return {
                "message": f"Successfully imported {len(result.inserted_ids)} entries",
                "count": len(result.inserted_ids)
            }
        else:
            logger.warning("No valid entries found in file")
            raise HTTPException(status_code=400, detail="No valid entries found in file")
            
    except pd.errors.EmptyDataError:
        logger.error("File is empty")
        raise HTTPException(status_code=400, detail="File is empty")
    except Exception as e:
        logger.error(f"Import failed: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))
