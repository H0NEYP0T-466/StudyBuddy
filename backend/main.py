from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.models.database import connect_to_mongo, close_mongo_connection
from app.services.rag_service import get_rag_system
from app.routes import folders, notes, timetable, todos, assistant, pen2pdf


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting StudyBuddy...")
    await connect_to_mongo()
    
    # Initialize RAG system
    print("Initializing RAG system...")
    await get_rag_system()
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await close_mongo_connection()


app = FastAPI(
    title="StudyBuddy",
    description="Complete productivity suite with AI-powered features",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(folders.router)
app.include_router(notes.router)
app.include_router(timetable.router)
app.include_router(todos.router)
app.include_router(assistant.router)
app.include_router(pen2pdf.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to StudyBuddy v2.0 API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
