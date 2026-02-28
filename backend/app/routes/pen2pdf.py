from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List
from mistralai import Mistral
import os
import shutil
import base64
from app.utils.file_processor import extract_text_from_file
from app.utils.logger import get_logger
from dotenv import load_dotenv
from app.services.export_service import export_service

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY is not set in environment variables")
client = Mistral(api_key=api_key)
router = APIRouter(prefix="/api/pen2pdf", tags=["pen2pdf"])
logger = get_logger("PEN2PDF")

# Helper function to encode files to base64
def encode_file_to_base64(file_path: str) -> str:
    """Encode a file to base64 string."""
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode('utf-8')

# app/routes/pen2pdf.py

@router.post("/extract")
async def extract_documents(
    files: List[UploadFile] = File(...),
    model: str = Form("gemini-2.5-flash")
):
    logger.info(f"Received document extraction request for {len(files)} files using model: {model}")
    temp_files = []
    extracted_content = []
    
    try:
        os.makedirs("backend/uploads", exist_ok=True)
        logger.debug("Created uploads directory")
        
        # Save files
        for file in files:
            file_path = f"backend/uploads/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_files.append(file_path)
            logger.info(f"Saved file: {file.filename} ({file.size} bytes)" if hasattr(file, 'size') else f"Saved file: {file.filename}")
        
        # Process files
        for file_path in temp_files:
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in ['.pdf', '.png', '.jpg', '.jpeg', '.webp']:
                logger.info(f"Processing {filename} with Mistral OCR...")
                
                # Encode file to base64
                base64_file = encode_file_to_base64(file_path)
                
                # Determine document type and mime type
                if ext == '.pdf':
                    document_type = "document_url"
                    mime_type = "application/pdf"
                else:
                    document_type = "image_url"
                    # Map extensions to mime types
                    mime_map = {
                        '.png': 'image/png',
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.webp': 'image/webp'
                    }
                    mime_type = mime_map.get(ext, 'image/jpeg')
                
                # Perform OCR
                try:
                    ocr_response = client.ocr.process(
                        model="mistral-ocr-latest",
                        document={
                            "type": document_type,
                            f"{document_type}": f"data:{mime_type};base64,{base64_file}"
                        },
                        table_format="html",
                        include_image_base64=False
                    )
                    
                    # Extract markdown from all pages
                    text = "\n\n".join([page.markdown for page in ocr_response.pages])
                    logger.success(f"Successfully extracted text from {filename} using Mistral OCR")
                except Exception as ocr_error:
                    logger.error(f"Mistral OCR failed for {filename}: {str(ocr_error)}")
                    raise
            else:
                logger.info(f"Processing {filename} with text extraction...")
                text = await extract_text_from_file(file_path)
                logger.success(f"Successfully extracted text from {filename}")
            
            extracted_content.append({"filename": filename, "content": text})
            logger.debug(f"Content length for {filename}: {len(text)} characters")
        
        combined_content = "\n\n---\n\n".join([
            f"## {item['filename']}\n\n{item['content']}" for item in extracted_content
        ])
        
        logger.success(f"Document extraction complete! Processed {len(extracted_content)} files. Total content: {len(combined_content)} characters")
        
        # Frontend expects 'markdown' field
        return {
            "markdown": combined_content, 
            "files_processed": len(extracted_content)
        }
        
    except Exception as e:
        logger.error(f"Document extraction failed: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # ALWAYS delete files after processing
        for path in temp_files:
            if os.path.exists(path):
                os.remove(path)
                logger.debug(f"Cleaned up temporary file: {path}")

@router.post("/export")
async def export_document(
    content: str = Form(...),
    title: str = Form(...),
    format: str = Form(...),
    add_watermark: bool = Form(True)
):
    """Export document to PDF, DOCX, or Markdown."""
    logger.info(f"Received export request: title='{title}', format={format}, watermark={add_watermark}")
    
    try:
        if format == "pdf":
            logger.debug("Exporting to PDF format")
            output = await export_service.export_to_pdf(content, title, add_watermark)
            media_type = "application/pdf"
            filename = f"{title}.pdf"
        elif format == "docx":
            logger.debug("Exporting to DOCX format")
            output = export_service.export_to_docx(content, title)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"{title}.docx"
        elif format == "markdown":
            logger.debug("Exporting to Markdown format")
            output = export_service.export_to_markdown(content, title)
            media_type = "text/markdown"
            filename = f"{title}.md"
        else:
            logger.error(f"Invalid export format requested: {format}")
            raise HTTPException(status_code=400, detail="Invalid format")
        
        logger.success(f"Successfully exported '{title}' to {format.upper()} format")
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Export failed: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))