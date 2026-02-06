from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import json
from datetime import datetime

from app.models.database import get_database
from app.services.rag_service import get_rag_system
from app.services.gemini_service import gemini_service
from app.services.longcat_service import longcat_service
from app.services.github_models_service import github_models_service
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/assistant", tags=["assistant"])
logger = get_logger("ASSISTANT")


@router.get("/messages")
async def get_chat_messages(limit: int = 15):
    """Get recent chat messages."""
    logger.info(f"Fetching last {limit} chat messages")
    db = get_database()
    
    try:
        messages = await db.chat_messages.find().sort("created_at", -1).limit(limit * 2).to_list(limit * 2)
        # Reverse to get chronological order
        messages.reverse()
        
        # Convert to expected format
        result = []
        for msg in messages:
            result.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        logger.success(f"Retrieved {len(result)} messages")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch messages: {str(e)}")
        return []


@router.post("/chat")
async def chat_with_assistant(
    message: str = Form(...),
    model: str = Form(...),
    chat_history: Optional[str] = Form(None),
    context_notes: Optional[str] = Form(None),
    use_rag: bool = Form(True),
    isolate_message: bool = Form(False)
):
    """Chat with AI assistant Isabella with RAG integration."""
    import time
    start_time = time.time()
    
    logger.info(f"=== Chat Request Started ===")
    logger.info(f"Model: {model}")
    logger.info(f"RAG Enabled: {use_rag}")
    logger.info(f"Isolate Message: {isolate_message}")
    logger.debug(f"User message: {message[:100]}..." if len(message) > 100 else f"User message: {message}")
    
    try:
        # Parse chat history
        history = []
        if chat_history and not isolate_message:
            try:
                history = json.loads(chat_history)
                logger.info(f"Chat history loaded: {len(history)} messages")
                # Use last 10 messages for context
                if len(history) > 10:
                    history = history[-10:]
                    logger.info(f"Limited to last 10 messages for context")
            except:
                logger.warning("Failed to parse chat history, continuing without it")
                history = []
        elif isolate_message:
            logger.info("Isolate message mode - ignoring conversation history")
        
        # Build context from RAG
        rag_context = ""
        sources = []
        
        if use_rag:
            logger.info("Searching RAG database for relevant context...")
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
                logger.success(f"Found {len(sources)} relevant sources from RAG")
                for i, source in enumerate(sources, 1):
                    logger.debug(f"  Source {i}: {source['filename']} (similarity: {source['similarity']:.3f})")
            else:
                logger.info("No relevant RAG context found")
        
        # Add context notes
        notes_context = ""
        if context_notes:
            notes_context = f"\n\nAdditional context notes:\n{context_notes}\n"
            logger.info(f"Notes context added: {len(context_notes)} characters")
        
        # Build final prompt
        final_message = message
        if rag_context or notes_context:
            final_message = f"{rag_context}{notes_context}\n\nUser question: {message}"
        
        logger.info(f"Final prompt length: {len(final_message)} characters")
        logger.info(f"Conversation history length: {len(history)} messages")
        
        # Generate response based on model
        response_text = ""
        
        if model.startswith("gemini"):
            logger.info(f"Generating response using Gemini model: {model}")
            response_text = await gemini_service.generate_text(
                final_message,
                model,
                chat_history=history if history else None
            )
            logger.success(f"Gemini response generated ({len(response_text)} characters)")
            
        elif model.startswith("longcat"):
            logger.info(f"Generating response using LongCat model: {model}")
            # Build proper chat history for LongCat
            longcat_history = []
            if history:
                for msg in history[-10:]:  # Last 10 messages
                    longcat_history.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
                logger.debug(f"Using {len(longcat_history)} messages from history")
            
            response_text = await longcat_service.generate_text(
                final_message,
                model,
                chat_history=longcat_history if longcat_history else None,
                system_prompt="You are Isabella, a helpful AI assistant. Answer questions accurately and helpfully."
            )
            logger.success(f"LongCat response generated ({len(response_text)} characters)")
            
        elif model in ["gpt-4o", "gpt-4o-mini", "gpt-5", "o1-mini", 
                       "llama-3.2-90b-vision-instruct", "llama-3.2-11b-vision-instruct",
                       "mistral-large-2411", "mistral-small", "mistral-nemo", "phi-4",
                       "gemini-2.5-pro"]:
            logger.info(f"Generating response using GitHub Models: {model}")
            # GitHub Models
            github_history = []
            if history:
                for msg in history[-10:]:
                    github_history.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
                logger.debug(f"Using {len(github_history)} messages from history")
            
            response_text = await github_models_service.generate_text(
                final_message,
                model,
                chat_history=github_history if github_history else None,
                system_prompt="You are Isabella, a helpful AI assistant."
            )
            logger.success(f"GitHub Models response generated ({len(response_text)} characters)")
        else:
            logger.error(f"Unknown model specified: {model}")
            response_text = "Error: Unknown model specified"
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Store messages in database
        db = get_database()
        try:
            # Store user message
            await db.chat_messages.insert_one({
                "role": "user",
                "content": message,
                "model": model,
                "created_at": datetime.utcnow()
            })
            # Store assistant response
            await db.chat_messages.insert_one({
                "role": "assistant",
                "content": response_text,
                "model": model,
                "created_at": datetime.utcnow()
            })
            logger.debug("Messages saved to database")
        except Exception as e:
            logger.warning(f"Failed to save messages to database: {str(e)}")
        
        # Final log summary
        logger.info(f"=== Chat Completed Successfully ===")
        logger.info(f"Response length: {len(response_text)} characters")
        logger.info(f"Processing time: {processing_time:.2f} seconds")
        logger.info(f"Sources returned: {len(sources)}")
        logger.debug(f"Response preview: {response_text[:100]}..." if len(response_text) > 100 else f"Response: {response_text}")
        
        return {
            "response": response_text,
            "sources": sources,
            "model": model
        }
        
    except Exception as e:
        logger.error(f"Chat request failed: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-image")
async def upload_image_for_chat(
    file: UploadFile = File(...),
    message: str = Form(...),
    model: str = Form("gemini-2.0-flash-exp")
):
    """Upload image for Gemini vision models."""
    logger.info(f"Image upload request - Filename: {file.filename}, Model: {model}")
    
    # Only Gemini supports images
    if not model.startswith("gemini"):
        logger.error(f"Non-Gemini model used for image upload: {model}")
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
        logger.debug(f"Saved image temporarily: {file_path}")
        
        logger.info(f"Processing image with Gemini: {file.filename}")
        logger.debug(f"User message: {message}")
        
        # Generate response with image
        response_text = await gemini_service.generate_text(
            message,
            model,
            file_paths=[file_path]
        )
        
        logger.success(f"Image processed successfully ({len(response_text)} characters)")
        
        # Clean up
        try:
            os.remove(file_path)
            logger.debug(f"Cleaned up temporary file: {file_path}")
        except:
            logger.warning(f"Failed to clean up temporary file: {file_path}")
        
        return {
            "message": response_text,
            "model": model
        }
        
    except Exception as e:
        logger.error(f"Image upload failed: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))
