from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from app.models.database import get_database
from app.models.schemas import Todo, Subtask
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/todos", tags=["todos"])
logger = get_logger("TODOS")


@router.get("/", response_model=List[dict])
async def get_todos():
    """Get all todos."""
    logger.info("Fetching all todos")
    db = get_database()
    todos = await db.todos.find().sort("created_at", -1).to_list(1000)
    
    # Convert ObjectId to string
    for todo in todos:
        todo["id"] = str(todo["_id"])
        del todo["_id"]
    
    logger.success(f"Retrieved {len(todos)} todos")
    return todos


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: dict):
    """Create a new todo."""
    logger.info(f"Creating new todo: {todo.get('title', 'Untitled')}")
    db = get_database()
    
    # Frontend expects: id, title, description, completed, pinned, due_date, created_at, updated_at, subtasks[]
    todo_data = {
        "title": todo.get("title"),
        "description": todo.get("description", ""),
        "completed": todo.get("completed", False),
        "pinned": todo.get("pinned", False),
        "due_date": todo.get("due_date"),
        "subtasks": todo.get("subtasks", []),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.todos.insert_one(todo_data)
    todo_data["id"] = str(result.inserted_id)
    if "_id" in todo_data:
        del todo_data["_id"]
    
    logger.success(f"Todo created: {todo_data['title']}")
    return todo_data


@router.get("/{todo_id}")
async def get_todo(todo_id: str):
    """Get a specific todo."""
    logger.info(f"Fetching todo: {todo_id}")
    db = get_database()
    
    try:
        todo = await db.todos.find_one({"_id": ObjectId(todo_id)})
    except:
        logger.error(f"Invalid todo ID: {todo_id}")
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    if not todo:
        logger.warning(f"Todo not found: {todo_id}")
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo["id"] = str(todo["_id"])
    del todo["_id"]
    
    logger.success(f"Retrieved todo: {todo.get('title', 'Untitled')}")
    return todo


@router.put("/{todo_id}")
async def update_todo(todo_id: str, todo: dict):
    """Update a todo."""
    logger.info(f"Updating todo: {todo_id}")
    db = get_database()
    
    # Frontend expects: title, description, completed, pinned, due_date, subtasks
    update_data = {
        "title": todo.get("title"),
        "description": todo.get("description", ""),
        "completed": todo.get("completed", False),
        "pinned": todo.get("pinned", False),
        "due_date": todo.get("due_date"),
        "subtasks": todo.get("subtasks", []),
        "updated_at": datetime.utcnow()
    }
    
    try:
        result = await db.todos.update_one(
            {"_id": ObjectId(todo_id)},
            {"$set": update_data}
        )
    except:
        logger.error(f"Invalid todo ID: {todo_id}")
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    if result.matched_count == 0:
        logger.warning(f"Todo not found: {todo_id}")
        raise HTTPException(status_code=404, detail="Todo not found")
    
    logger.success(f"Todo updated: {update_data['title']}")
    return {"message": "Todo updated successfully"}


@router.delete("/{todo_id}")
async def delete_todo(todo_id: str):
    """Delete a todo."""
    logger.info(f"Deleting todo: {todo_id}")
    db = get_database()
    
    try:
        result = await db.todos.delete_one({"_id": ObjectId(todo_id)})
    except:
        logger.error(f"Invalid todo ID: {todo_id}")
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    if result.deleted_count == 0:
        logger.warning(f"Todo not found: {todo_id}")
        raise HTTPException(status_code=404, detail="Todo not found")
    
    logger.success(f"Todo deleted: {todo_id}")
    return {"message": "Todo deleted successfully"}


@router.post("/{todo_id}/subtasks")
async def add_subtask(todo_id: str, subtask: dict):
    """Add a subtask to a todo."""
    logger.info(f"Adding subtask to todo: {todo_id}")
    db = get_database()
    
    # Frontend expects subtasks to have: id, todo_id, title, completed, created_at, updated_at
    subtask_data = {
        "id": str(ObjectId()),
        "todo_id": todo_id,
        "title": subtask.get("title"),
        "completed": subtask.get("completed", False),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
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
        logger.error(f"Invalid todo ID: {todo_id}")
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    if result.matched_count == 0:
        logger.warning(f"Todo not found: {todo_id}")
        raise HTTPException(status_code=404, detail="Todo not found")
    
    logger.success(f"Subtask added to todo {todo_id}: {subtask_data['title']}")
    return subtask_data


@router.put("/{todo_id}/subtasks/{subtask_id}")
async def update_subtask(todo_id: str, subtask_id: str, subtask: dict):
    """Update a subtask."""
    logger.info(f"Updating subtask {subtask_id} in todo {todo_id}")
    db = get_database()
    
    try:
        # Get the todo
        todo = await db.todos.find_one({"_id": ObjectId(todo_id)})
        if not todo:
            logger.warning(f"Todo not found: {todo_id}")
            raise HTTPException(status_code=404, detail="Todo not found")
        
        # Update the subtask
        subtasks = todo.get("subtasks", [])
        updated = False
        for i, st in enumerate(subtasks):
            if st.get("id") == subtask_id:
                subtasks[i].update({
                    "title": subtask.get("title", st.get("title")),
                    "completed": subtask.get("completed", st.get("completed")),
                    "updated_at": datetime.utcnow()
                })
                updated = True
                break
        
        if not updated:
            logger.warning(f"Subtask not found: {subtask_id}")
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
        
        logger.success(f"Subtask updated: {subtask_id}")
        return {"message": "Subtask updated successfully"}
        
    except HTTPException:
        raise
    except:
        logger.error(f"Invalid ID provided")
        raise HTTPException(status_code=400, detail="Invalid ID")


@router.delete("/{todo_id}/subtasks/{subtask_id}")
async def delete_subtask(todo_id: str, subtask_id: str):
    """Delete a subtask."""
    logger.info(f"Deleting subtask {subtask_id} from todo {todo_id}")
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
        logger.error(f"Invalid todo ID: {todo_id}")
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    if result.matched_count == 0:
        logger.warning(f"Todo not found: {todo_id}")
        raise HTTPException(status_code=404, detail="Todo not found")
    
    logger.success(f"Subtask deleted: {subtask_id}")
    return {"message": "Subtask deleted successfully"}
