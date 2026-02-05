from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List
import os
import shutil

from app.services.gemini_service import gemini_service
from app.services.export_service import export_service
from app.utils.file_processor import extract_text_from_file

router = APIRouter(prefix="/api/pen2pdf", tags=["pen2pdf"])


# app/routes/pen2pdf.py

@router.post("/extract")
async def extract_documents(
    files: List[UploadFile] = File(...),
    model: str = Form("gemini-2.5-flash")
):
    print(f"Backend received request for {len(files)} files")
    temp_files = []
    extracted_content = []
    
    try:
        os.makedirs("backend/uploads", exist_ok=True)
        
        # Save files
        for file in files:
            file_path = f"backend/uploads/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_files.append(file_path)
        
        # Process files
        for file_path in temp_files:
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in ['.pdf', '.png', '.jpg', '.jpeg', '.webp', '.ppt', '.pptx']:
                print(f"Processing {filename} with Gemini...")
                prompt = "Extract all text content from this document. Return in clean markdown."
                text = await gemini_service.generate_text(
                    prompt=prompt,
                    model_name=model,
                    file_paths=[file_path]
                )
            else:
                text = await extract_text_from_file(file_path)
            
            extracted_content.append({"filename": filename, "content": text})
        
        combined_content = "\n\n---\n\n".join([
            f"## {item['filename']}\n\n{item['content']}" for item in extracted_content
        ])
        
        print(f"Success! Preview: {combined_content[:50]}...")
        
        # Frontend expects 'markdown' field
        return {
            "markdown": combined_content, 
            "files_processed": len(extracted_content)
        }
        
    except Exception as e:
        print(f"Route Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # ALWAYS delete files after processing
        for path in temp_files:
            if os.path.exists(path):
                os.remove(path)

@router.post("/export")
async def export_document(
    content: str = Form(...),
    title: str = Form(...),
    format: str = Form(...),
    add_watermark: bool = Form(True)
):
    """Export document to PDF, DOCX, or Markdown."""
    
    try:
        if format == "pdf":
            output = export_service.export_to_pdf(content, title, add_watermark)
            media_type = "application/pdf"
            filename = f"{title}.pdf"
        elif format == "docx":
            output = export_service.export_to_docx(content, title)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"{title}.docx"
        elif format == "markdown":
            output = export_service.export_to_markdown(content, title)
            media_type = "text/markdown"
            filename = f"{title}.md"
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
        
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))