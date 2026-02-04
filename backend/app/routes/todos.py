from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from app.models.database import get_database
from app.models.schemas import Todo, Subtask

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("/", response_model=List[dict])
async def get_todos():
    """Get all todos."""
    db = get_database()
    todos = await db.todos.find().sort("created_at", -1).to_list(1000)
    
    # Convert ObjectId to string
    for todo in todos:
        todo["id"] = str(todo["_id"])
        del todo["_id"]
    
    return todos


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: dict):
    """Create a new todo."""
    db = get_database()
    
    todo_data = {
        "title": todo.get("title"),
        "subtasks": todo.get("subtasks", []),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.todos.insert_one(todo_data)
    todo_data["id"] = str(result.inserted_id)
    if "_id" in todo_data:
        del todo_data["_id"]
    
    
    return todo_data


@router.get("/{todo_id}")
async def get_todo(todo_id: str):
    """Get a specific todo."""
    db = get_database()
    
    try:
        todo = await db.todos.find_one({"_id": ObjectId(todo_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo["id"] = str(todo["_id"])
    del todo["_id"]
    
    return todo


@router.put("/{todo_id}")
async def update_todo(todo_id: str, todo: dict):
    """Update a todo."""
    db = get_database()
    
    update_data = {
        "title": todo.get("title"),
        "subtasks": todo.get("subtasks", []),
        "updated_at": datetime.utcnow()
    }
    
    try:
        result = await db.todos.update_one(
            {"_id": ObjectId(todo_id)},
            {"$set": update_data}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return {"message": "Todo updated successfully"}


@router.delete("/{todo_id}")
async def delete_todo(todo_id: str):
    """Delete a todo."""
    db = get_database()
    
    try:
        result = await db.todos.delete_one({"_id": ObjectId(todo_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return {"message": "Todo deleted successfully"}


@router.post("/{todo_id}/subtasks")
async def add_subtask(todo_id: str, subtask: dict):
    """Add a subtask to a todo."""
    db = get_database()
    
    subtask_data = {
        "id": str(ObjectId()),
        "text": subtask.get("text"),
        "completed": subtask.get("completed", False),
        "pinned": subtask.get("pinned", False)
    }
    
    try:
        result = await db.todos.update_one(
            {"_id": ObjectId(todo_id)},
            {
                "$push": {"subtasks": subtask_data},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return subtask_data


@router.put("/{todo_id}/subtasks/{subtask_id}")
async def update_subtask(todo_id: str, subtask_id: str, subtask: dict):
    """Update a subtask."""
    db = get_database()
    
    try:
        # Get the todo
        todo = await db.todos.find_one({"_id": ObjectId(todo_id)})
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        # Update the subtask
        subtasks = todo.get("subtasks", [])
        updated = False
        for i, st in enumerate(subtasks):
            if st.get("id") == subtask_id:
                subtasks[i].update({
                    "text": subtask.get("text", st.get("text")),
                    "completed": subtask.get("completed", st.get("completed")),
                    "pinned": subtask.get("pinned", st.get("pinned"))
                })
                updated = True
                break
        
        if not updated:
            raise HTTPException(status_code=404, detail="Subtask not found")
        
        # Save back
        await db.todos.update_one(
            {"_id": ObjectId(todo_id)},
            {
                "$set": {
                    "subtasks": subtasks,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Subtask updated successfully"}
        
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")


@router.delete("/{todo_id}/subtasks/{subtask_id}")
async def delete_subtask(todo_id: str, subtask_id: str):
    """Delete a subtask."""
    db = get_database()
    
    try:
        result = await db.todos.update_one(
            {"_id": ObjectId(todo_id)},
            {
                "$pull": {"subtasks": {"id": subtask_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return {"message": "Subtask deleted successfully"}
