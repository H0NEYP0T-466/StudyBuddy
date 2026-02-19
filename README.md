# Pen2PDF v2.0 🎓

<p align="center">
  <img src="https://img.shields.io/github/license/H0NEYP0T-466/StudyBuddy?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/github/stars/H0NEYP0T-466/StudyBuddy?style=for-the-badge" alt="Stars">
  <img src="https://img.shields.io/github/forks/H0NEYP0T-466/StudyBuddy?style=for-the-badge" alt="Forks">
  <img src="https://img.shields.io/github/issues/H0NEYP0T-466/StudyBuddy?style=for-the-badge" alt="Issues">
  <img src="https://img.shields.io/github/issues-pr/H0NEYP0T-466/StudyBuddy?style=for-the-badge" alt="Pull Requests">
</p>

<p align="center">
  <img src="https://img.shields.io/github/last-commit/H0NEYP0T-466/StudyBuddy?style=for-the-badge" alt="Last Commit">
  <img src="https://img.shields.io/github/commit-activity/m/H0NEYP0T-466/StudyBuddy?style=for-the-badge" alt="Commit Activity">
  <img src="https://img.shields.io/github/languages/top/H0NEYP0T-466/StudyBuddy?style=for-the-badge" alt="Top Language">
  <img src="https://img.shields.io/github/languages/count/H0NEYP0T-466/StudyBuddy?style=for-the-badge" alt="Languages">
</p>

A complete productivity suite for students with AI-powered document processing, intelligent note-taking, timetable management, and more.

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-api-documentation">API Docs</a> •
  <a href="https://github.com/H0NEYP0T-466/StudyBuddy/issues">Issues</a> •
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

---

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

# Install Playwright browsers (required for PDF export)
playwright install chromium
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

## 🛠 Tech Stack

### Backend
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Google AI](https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)

- **Framework**: FastAPI
- **Database**: MongoDB with Motor (async)
- **AI Models**: Google Gemini, LongCat, GitHub Models
- **RAG**: FAISS + sentence-transformers
- **File Processing**: PyPDF2, python-docx, python-pptx

### Frontend
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-CA4245?style=for-the-badge&logo=react-router&logoColor=white)

- **Framework**: React 19 + TypeScript
- **Routing**: React Router v6
- **Styling**: CSS Modules with CSS Variables
- **Markdown**: react-markdown + KaTeX
- **HTTP Client**: Axios

### 📦 Dependencies

#### Runtime Dependencies (Frontend)
![react](https://img.shields.io/npm/v/react?style=for-the-badge&label=react&logo=react&color=61DAFB)
![react-router-dom](https://img.shields.io/npm/v/react-router-dom?style=for-the-badge&label=react-router-dom&logo=react-router)
![axios](https://img.shields.io/npm/v/axios?style=for-the-badge&label=axios&logo=axios)
![katex](https://img.shields.io/npm/v/katex?style=for-the-badge&label=katex)
![react-markdown](https://img.shields.io/npm/v/react-markdown?style=for-the-badge&label=react-markdown)

#### Development Dependencies (Frontend)
![typescript](https://img.shields.io/npm/v/typescript?style=for-the-badge&label=typescript&logo=typescript)
![vite](https://img.shields.io/npm/v/vite?style=for-the-badge&label=vite&logo=vite)
![eslint](https://img.shields.io/npm/v/eslint?style=for-the-badge&label=eslint&logo=eslint)

#### Backend Dependencies (Python)
![fastapi](https://img.shields.io/pypi/v/fastapi?style=for-the-badge&label=fastapi&logo=fastapi)
![motor](https://img.shields.io/pypi/v/motor?style=for-the-badge&label=motor)
![langchain](https://img.shields.io/pypi/v/langchain?style=for-the-badge&label=langchain)
![faiss-cpu](https://img.shields.io/pypi/v/faiss-cpu?style=for-the-badge&label=faiss-cpu)
![sentence-transformers](https://img.shields.io/pypi/v/sentence-transformers?style=for-the-badge&label=sentence-transformers)

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

## 🔐 Security Considerations

- API keys stored in `.env` (not committed)
- CORS configured for local development
- Input validation on all endpoints
- MongoDB connection with authentication support

For detailed security information and vulnerability reporting, see [SECURITY.md](SECURITY.md).

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

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- How to fork and set up the project
- Code style guidelines
- Commit message format
- Pull request process

This is a student productivity project. Feel free to fork and customize for your needs!

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛡 Security

For information about reporting security vulnerabilities, please see our [Security Policy](SECURITY.md).

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
