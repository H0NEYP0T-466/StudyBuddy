# Pen2PDF v2.0 🎓

A complete productivity suite for students with AI-powered document processing, intelligent note-taking, timetable management, and more.

## ✨ Features

### 🤖 AI-Powered Tools
- **Pen2PDF**: Extract text from PDFs, PowerPoints, and images using AI
- **Notes Generator**: AI-generated structured study notes from documents
- **Isabella AI Assistant**: Intelligent chatbot with RAG (Retrieval Augmented Generation)
- Multiple AI models supported: Gemini, LongCat, GitHub Models (GPT-4, Claude, Llama, etc.)

### 📚 Organization
- **Notes Library**: Hierarchical folder system for organizing notes
- **Timetable**: Weekly schedule management with CSV import
- **Todo List**: Task management with subtasks, pinning, and completion tracking
- **Week Counter**: Track current academic week

### 🎨 Modern Design
- Dark theme optimized for extended use
- Clean, minimalistic, aesthetic UI
- Markdown rendering with LaTeX/KaTeX support
- Responsive design for all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required API keys:
- `GEMINI_API_KEY`: Google Gemini API key
- `LONGCAT_API_KEY`: LongCat API key (optional)
- `GITHUB_TOKEN`: GitHub Personal Access Token for GitHub Models (optional)
- `MONGODB_URL`: MongoDB connection string

5. Start the backend server:
```bash
# From the backend directory
./run.sh

# Or manually:
cd ..
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8003 --reload
```

Server will be available at: `http://localhost:8003`

### Frontend Setup

1. Navigate to project root:
```bash
cd /path/to/StudyBuddy
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 📖 Usage Guide

### Pen2PDF - Document Extraction
1. Upload PDF, PowerPoint, or image files
2. AI extracts and structures the content
3. Edit in the markdown editor
4. Export to PDF, DOCX, or Markdown

### Notes Generator
1. Upload study materials
2. Select AI model (Gemini, LongCat, etc.)
3. Generate structured notes
4. Save to a folder in your library

### AI Assistant (Isabella)
- Ask questions about your notes
- RAG system automatically searches your document library
- Add specific notes as context
- Get answers with source citations

### Timetable
- Add classes manually or import from CSV
- View weekly schedule
- Edit inline
- Track class types (Theory/Lab)

### Todo List
- Create todo cards
- Add subtasks to each card
- Pin important tasks
- Mark as complete

## 🏗️ Project Structure

```
StudyBuddy/
├── backend/
│   ├── app/
│   │   ├── models/        # Database schemas
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # AI & RAG services
│   │   └── utils/         # Helper functions
│   ├── data/              # RAG document storage
│   ├── vector_store/      # FAISS index
│   └── main.py            # FastAPI app
├── src/
│   ├── components/        # React components
│   ├── pages/             # Page components
│   ├── services/          # API client
│   ├── types/             # TypeScript types
│   └── styles/            # Global styles
└── public/
```

## 🔧 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB with Motor (async)
- **AI Models**: Google Gemini, LongCat, GitHub Models
- **RAG**: FAISS + sentence-transformers
- **File Processing**: PyPDF2, python-docx, python-pptx

### Frontend
- **Framework**: React 19 + TypeScript
- **Routing**: React Router v6
- **Styling**: CSS Modules with CSS Variables
- **Markdown**: react-markdown + KaTeX
- **HTTP Client**: Axios

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8003/docs`
- ReDoc: `http://localhost:8003/redoc`

### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/folders` | GET, POST, PUT, DELETE | Folder management |
| `/api/notes` | GET, POST, PUT, DELETE | Notes CRUD |
| `/api/notes/generate` | POST | Generate notes with AI |
| `/api/timetable` | GET, POST, PUT, DELETE | Timetable management |
| `/api/timetable/import` | POST | Import from CSV |
| `/api/todos` | GET, POST, PUT, DELETE | Todo management |
| `/api/assistant/chat` | POST | Chat with AI assistant |
| `/api/pen2pdf/extract` | POST | Extract text from documents |
| `/api/pen2pdf/export` | POST | Export to PDF/DOCX/MD |

## 🎯 RAG System

The RAG (Retrieval Augmented Generation) system:
1. Monitors `backend/data/` for documents
2. Automatically indexes new files on startup
3. Saves notes as `.txt` files for indexing
4. Uses FAISS for vector search
5. Integrates with AI Assistant for context-aware responses

## 🔐 Security

- API keys stored in `.env` (not committed)
- CORS configured for local development
- Input validation on all endpoints
- MongoDB connection with authentication support

## 📦 Build for Production

### Frontend
```bash
npm run build
npm run preview  # Test production build
```

### Backend
```bash
# Use production ASGI server
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8003
```

## 🤝 Contributing

This is a student productivity project. Feel free to fork and customize for your needs!

## 📄 License

MIT License - feel free to use for personal or educational purposes.

## 🐛 Known Issues

- Large file uploads (>50MB) may timeout
- Some AI models require specific API access
- MongoDB must be running for backend to start

## 💡 Tips

- Use Gemini models for document processing (supports images/PDFs)
- LongCat models are fast for text-only tasks
- Pin frequently used todos for quick access
- Organize notes into subject folders for better RAG results

---

Built with ❤️ for students by students
