from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import json

from app.services.rag_service import get_rag_system
from app.services.gemini_service import gemini_service
from app.services.longcat_service import longcat_service
from app.services.github_models_service import github_models_service

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/chat")
async def chat_with_assistant(
    message: str = Form(...),
    model: str = Form(...),
    chat_history: Optional[str] = Form(None),
    context_notes: Optional[str] = Form(None),
    use_rag: bool = Form(True)
):
    """Chat with AI assistant Isabella with RAG integration."""
    
    try:
        # Parse chat history
        history = []
        if chat_history:
            try:
                history = json.loads(chat_history)
            except:
                history = []
        
        # Build context from RAG
        rag_context = ""
        sources = []
        
        if use_rag:
            rag = await get_rag_system()
            results = rag.search(message, k=3)
            
            if results:
                rag_context = "\n\nRelevant context from your documents:\n"
                for i, result in enumerate(results, 1):
                    rag_context += f"\n[Source {i}: {result['filename']}]\n{result['chunk']}\n"
                    sources.append({
                        "filename": result['filename'],
                        "chunk": result['chunk'][:200] + "..." if len(result['chunk']) > 200 else result['chunk'],
                        "similarity": result['similarity']
                    })
        
        # Add context notes
        notes_context = ""
        if context_notes:
            notes_context = f"\n\nAdditional context notes:\n{context_notes}\n"
        
        # Build final prompt
        final_message = message
        if rag_context or notes_context:
            final_message = f"{rag_context}{notes_context}\n\nUser question: {message}"
        
        # Generate response based on model
        response_text = ""
        
        if model.startswith("gemini"):
            response_text = await gemini_service.generate_text(
                final_message,
                model,
                chat_history=history if history else None
            )
        elif model.startswith("longcat"):
            # Build proper chat history for LongCat
            longcat_history = []
            if history:
                for msg in history[-10:]:  # Last 10 messages
                    longcat_history.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            response_text = await longcat_service.generate_text(
                final_message,
                model,
                chat_history=longcat_history if longcat_history else None,
                system_prompt="You are Isabella, a helpful AI assistant. Answer questions accurately and helpfully."
            )
        elif model in ["gpt-4o", "gpt-4o-mini", "gpt-5", "o1-mini", 
                       "llama-3.2-90b-vision-instruct", "llama-3.2-11b-vision-instruct",
                       "mistral-large-2411", "mistral-small", "mistral-nemo", "phi-4"]:
            # GitHub Models
            github_history = []
            if history:
                for msg in history[-10:]:
                    github_history.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            response_text = await github_models_service.generate_text(
                final_message,
                model,
                chat_history=github_history if github_history else None,
                system_prompt="You are Isabella, a helpful AI assistant."
            )
        else:
            response_text = "Error: Unknown model specified"
        
        return {
            "message": response_text,
            "sources": sources,
            "model": model
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-image")
async def upload_image_for_chat(
    file: UploadFile = File(...),
    message: str = Form(...),
    model: str = Form("gemini-2.0-flash-exp")
):
    """Upload image for Gemini vision models."""
    
    # Only Gemini supports images
    if not model.startswith("gemini"):
        raise HTTPException(
            status_code=400, 
            detail="Only Gemini models support image uploads"
        )
    
    try:
        import os
        import shutil
        
        # Save file temporarily
        os.makedirs("backend/uploads", exist_ok=True)
        file_path = f"backend/uploads/{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate response with image
        response_text = await gemini_service.generate_text(
            message,
            model,
            file_paths=[file_path]
        )
        
        # Clean up
        try:
            os.remove(file_path)
        except:
            pass
        
        return {
            "message": response_text,
            "model": model
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
