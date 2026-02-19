# Study Buddy 🎓

<p align="center">
  <img src="https://img.shields.io/github/license/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=blue" alt="License">
  <img src="https://img.shields.io/github/stars/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=yellow" alt="Stars">
  <img src="https://img.shields.io/github/forks/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=green" alt="Forks">
  <img src="https://img.shields.io/github/issues/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=red" alt="Issues">
  <img src="https://img.shields.io/github/issues-pr/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=orange" alt="Pull Requests">
</p>

<p align="center">
  <img src="https://img.shields.io/github/last-commit/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=purple" alt="Last Commit">
  <img src="https://img.shields.io/github/commit-activity/m/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=brightgreen" alt="Commit Activity">
  <img src="https://img.shields.io/github/languages/top/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=blueviolet" alt="Top Language">
  <img src="https://img.shields.io/github/languages/count/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=ff69b4" alt="Languages">
</p>

<p align="center">
  <img src="https://img.shields.io/github/repo-size/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=important" alt="Repo Size">
  <img src="https://img.shields.io/github/contributors/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=success" alt="Contributors">
  <img src="https://img.shields.io/github/watchers/H0NEYP0T-466/StudyBuddy?style=for-the-badge&color=informational" alt="Watchers">
  <img src="https://img.shields.io/github/downloads/H0NEYP0T-466/StudyBuddy/total?style=for-the-badge&color=blue" alt="Downloads">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/code%20style-standard-brightgreen?style=for-the-badge" alt="Code Style">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge" alt="PRs Welcome">
  <img src="https://img.shields.io/badge/maintained-yes-green.svg?style=for-the-badge" alt="Maintained">
  <img src="https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red.svg?style=for-the-badge" alt="Open Source Love">
</p>

---

<h3 align="center">🎯 A Complete AI-Powered Productivity Suite for Students</h3>

<p align="center">
  <strong>Study Buddy</strong> is your ultimate companion for academic success, combining cutting-edge AI technology with intuitive organization tools. Transform your study materials into structured notes, manage your schedule effortlessly, and get intelligent assistance powered by advanced language models.
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

### Backend Technologies

<p align="left">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB">
  <img src="https://img.shields.io/badge/Uvicorn-009688?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Uvicorn">
</p>

<p align="left">
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini">
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI">
  <img src="https://img.shields.io/badge/Anthropic-191919?style=for-the-badge&logo=anthropic&logoColor=white" alt="Anthropic">
  <img src="https://img.shields.io/badge/LangChain-121212?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain">
</p>

<p align="left">
  <img src="https://img.shields.io/badge/FAISS-0467DF?style=for-the-badge&logo=meta&logoColor=white" alt="FAISS">
  <img src="https://img.shields.io/badge/Sentence_Transformers-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="Sentence Transformers">
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Pillow-EE4C2C?style=for-the-badge&logo=python&logoColor=white" alt="Pillow">
</p>

**Core Framework:**
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: Lightning-fast ASGI server
- **Python-multipart**: Form and file upload handling

**Database:**
- **MongoDB**: NoSQL database for flexible document storage
- **Motor**: Async MongoDB driver for Python
- **PyMongo**: Official MongoDB Python driver

**AI & Machine Learning:**
- **Google Generative AI**: Gemini models for text and multimodal processing
- **OpenAI**: GPT models via GitHub Models
- **Anthropic**: Claude models via GitHub Models
- **LangCat**: Fast text generation models

**RAG (Retrieval Augmented Generation):**
- **FAISS**: Facebook AI Similarity Search for efficient vector retrieval
- **Sentence Transformers**: State-of-the-art text embeddings
- **LangChain**: Framework for developing LLM applications

**File Processing:**
- **PyPDF2 & pypdf**: PDF parsing and text extraction
- **python-docx**: Word document processing
- **python-pptx**: PowerPoint file handling
- **openpyxl**: Excel file processing
- **Pillow**: Image processing and manipulation

**Text & Export:**
- **Markdown**: Markdown processing
- **BeautifulSoup4**: HTML parsing
- **ReportLab**: PDF generation
- **Matplotlib**: Chart generation for exports

### Frontend Technologies

<p align="left">
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/React_Router-CA4245?style=for-the-badge&logo=react-router&logoColor=white" alt="React Router">
</p>

<p align="left">
  <img src="https://img.shields.io/badge/Axios-5A29E4?style=for-the-badge&logo=axios&logoColor=white" alt="Axios">
  <img src="https://img.shields.io/badge/Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white" alt="Markdown">
  <img src="https://img.shields.io/badge/KaTeX-008080?style=for-the-badge&logo=latex&logoColor=white" alt="KaTeX">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3">
</p>

<p align="left">
  <img src="https://img.shields.io/badge/ESLint-4B32C3?style=for-the-badge&logo=eslint&logoColor=white" alt="ESLint">
  <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=node.js&logoColor=white" alt="Node.js">
  <img src="https://img.shields.io/badge/npm-CB3837?style=for-the-badge&logo=npm&logoColor=white" alt="npm">
</p>

**Core Framework:**
- **React 19**: Latest React with improved performance and features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Next-generation frontend build tool for blazing fast development

**Routing & Navigation:**
- **React Router v7**: Declarative routing for React applications

**Styling & UI:**
- **CSS Modules**: Component-scoped CSS
- **CSS Variables**: Dynamic theming support
- **Dark Theme**: Optimized for extended study sessions

**Markdown & Math:**
- **react-markdown**: Render Markdown content in React
- **KaTeX**: Fast math typesetting for the web
- **react-katex**: React components for KaTeX
- **rehype-katex**: Rehype plugin to render math with KaTeX
- **remark-gfm**: GitHub Flavored Markdown support
- **remark-math**: Math support in Markdown

**HTTP & API:**
- **Axios**: Promise-based HTTP client for API requests

**Development Tools:**
- **ESLint**: JavaScript/TypeScript linting
- **@vitejs/plugin-react**: Official Vite plugin for React
- **typescript-eslint**: TypeScript support for ESLint

### 📦 Dependencies

#### Backend Dependencies (Python)

**Core Framework & Server:**
<p align="left">
  <img src="https://img.shields.io/pypi/v/fastapi?style=for-the-badge&label=fastapi&logo=fastapi&color=009688" alt="FastAPI">
  <img src="https://img.shields.io/pypi/v/uvicorn?style=for-the-badge&label=uvicorn&color=009688" alt="Uvicorn">
  <img src="https://img.shields.io/pypi/v/python-multipart?style=for-the-badge&label=python-multipart&color=blue" alt="Python Multipart">
  <img src="https://img.shields.io/pypi/v/python-dotenv?style=for-the-badge&label=python-dotenv&color=yellow" alt="Python Dotenv">
</p>

**Database:**
<p align="left">
  <img src="https://img.shields.io/pypi/v/motor?style=for-the-badge&label=motor&logo=mongodb&color=47A248" alt="Motor">
  <img src="https://img.shields.io/pypi/v/pymongo?style=for-the-badge&label=pymongo&logo=mongodb&color=47A248" alt="PyMongo">
</p>

**File Processing:**
<p align="left">
  <img src="https://img.shields.io/pypi/v/PyPDF2?style=for-the-badge&label=PyPDF2&color=red" alt="PyPDF2">
  <img src="https://img.shields.io/pypi/v/pypdf?style=for-the-badge&label=pypdf&color=red" alt="pypdf">
  <img src="https://img.shields.io/pypi/v/python-docx?style=for-the-badge&label=python-docx&color=blue" alt="python-docx">
  <img src="https://img.shields.io/pypi/v/python-pptx?style=for-the-badge&label=python-pptx&color=orange" alt="python-pptx">
</p>

<p align="left">
  <img src="https://img.shields.io/pypi/v/openpyxl?style=for-the-badge&label=openpyxl&color=green" alt="openpyxl">
  <img src="https://img.shields.io/pypi/v/pandas?style=for-the-badge&label=pandas&logo=pandas&color=150458" alt="pandas">
  <img src="https://img.shields.io/pypi/v/Pillow?style=for-the-badge&label=Pillow&color=yellow" alt="Pillow">
</p>

**AI Models:**
<p align="left">
  <img src="https://img.shields.io/pypi/v/google-generativeai?style=for-the-badge&label=google-generativeai&logo=google&color=4285F4" alt="Google Generative AI">
  <img src="https://img.shields.io/pypi/v/openai?style=for-the-badge&label=openai&logo=openai&color=412991" alt="OpenAI">
  <img src="https://img.shields.io/pypi/v/anthropic?style=for-the-badge&label=anthropic&color=191919" alt="Anthropic">
</p>

**RAG & Embeddings:**
<p align="left">
  <img src="https://img.shields.io/pypi/v/faiss-cpu?style=for-the-badge&label=faiss-cpu&logo=meta&color=0467DF" alt="FAISS CPU">
  <img src="https://img.shields.io/pypi/v/sentence-transformers?style=for-the-badge&label=sentence-transformers&logo=pytorch&color=EE4C2C" alt="Sentence Transformers">
  <img src="https://img.shields.io/pypi/v/langchain?style=for-the-badge&label=langchain&color=121212" alt="LangChain">
  <img src="https://img.shields.io/pypi/v/langchain-community?style=for-the-badge&label=langchain-community&color=121212" alt="LangChain Community">
</p>

**Text Processing & Export:**
<p align="left">
  <img src="https://img.shields.io/pypi/v/markdown?style=for-the-badge&label=markdown&color=000000" alt="Markdown">
  <img src="https://img.shields.io/pypi/v/beautifulsoup4?style=for-the-badge&label=beautifulsoup4&color=green" alt="BeautifulSoup4">
  <img src="https://img.shields.io/pypi/v/lxml?style=for-the-badge&label=lxml&color=orange" alt="lxml">
  <img src="https://img.shields.io/pypi/v/reportlab?style=for-the-badge&label=reportlab&color=red" alt="ReportLab">
</p>

<p align="left">
  <img src="https://img.shields.io/pypi/v/markdown2?style=for-the-badge&label=markdown2&color=000000" alt="Markdown2">
  <img src="https://img.shields.io/pypi/v/matplotlib?style=for-the-badge&label=matplotlib&color=11557c" alt="Matplotlib">
</p>

**Utilities:**
<p align="left">
  <img src="https://img.shields.io/pypi/v/aiofiles?style=for-the-badge&label=aiofiles&color=blue" alt="aiofiles">
  <img src="https://img.shields.io/pypi/v/httpx?style=for-the-badge&label=httpx&color=5A29E4" alt="httpx">
  <img src="https://img.shields.io/pypi/v/pydantic?style=for-the-badge&label=pydantic&logo=pydantic&color=E92063" alt="Pydantic">
  <img src="https://img.shields.io/pypi/v/pydantic-settings?style=for-the-badge&label=pydantic-settings&color=E92063" alt="Pydantic Settings">
</p>

#### Frontend Dependencies (npm)

**Runtime Dependencies:**
<p align="left">
  <img src="https://img.shields.io/npm/v/react?style=for-the-badge&label=react&logo=react&color=61DAFB" alt="React">
  <img src="https://img.shields.io/npm/v/react-dom?style=for-the-badge&label=react-dom&logo=react&color=61DAFB" alt="React DOM">
  <img src="https://img.shields.io/npm/v/react-router-dom?style=for-the-badge&label=react-router-dom&logo=react-router&color=CA4245" alt="React Router DOM">
</p>

<p align="left">
  <img src="https://img.shields.io/npm/v/axios?style=for-the-badge&label=axios&logo=axios&color=5A29E4" alt="Axios">
  <img src="https://img.shields.io/npm/v/react-markdown?style=for-the-badge&label=react-markdown&color=000000" alt="React Markdown">
  <img src="https://img.shields.io/npm/v/katex?style=for-the-badge&label=katex&color=008080" alt="KaTeX">
  <img src="https://img.shields.io/npm/v/react-katex?style=for-the-badge&label=react-katex&color=008080" alt="React KaTeX">
</p>

<p align="left">
  <img src="https://img.shields.io/npm/v/rehype-katex?style=for-the-badge&label=rehype-katex&color=blue" alt="Rehype KaTeX">
  <img src="https://img.shields.io/npm/v/remark-gfm?style=for-the-badge&label=remark-gfm&color=green" alt="Remark GFM">
  <img src="https://img.shields.io/npm/v/remark-math?style=for-the-badge&label=remark-math&color=yellow" alt="Remark Math">
</p>

**Development Dependencies:**
<p align="left">
  <img src="https://img.shields.io/npm/v/typescript?style=for-the-badge&label=typescript&logo=typescript&color=3178C6" alt="TypeScript">
  <img src="https://img.shields.io/npm/v/vite?style=for-the-badge&label=vite&logo=vite&color=646CFF" alt="Vite">
  <img src="https://img.shields.io/npm/v/eslint?style=for-the-badge&label=eslint&logo=eslint&color=4B32C3" alt="ESLint">
</p>

<p align="left">
  <img src="https://img.shields.io/npm/v/@vitejs/plugin-react?style=for-the-badge&label=@vitejs/plugin-react&color=61DAFB" alt="Vite Plugin React">
  <img src="https://img.shields.io/npm/v/typescript-eslint?style=for-the-badge&label=typescript-eslint&color=3178C6" alt="TypeScript ESLint">
  <img src="https://img.shields.io/npm/v/eslint-plugin-react-hooks?style=for-the-badge&label=eslint-plugin-react-hooks&color=61DAFB" alt="ESLint Plugin React Hooks">
</p>

<p align="left">
  <img src="https://img.shields.io/npm/v/eslint-plugin-react-refresh?style=for-the-badge&label=eslint-plugin-react-refresh&color=61DAFB" alt="ESLint Plugin React Refresh">
  <img src="https://img.shields.io/npm/v/@types/react?style=for-the-badge&label=@types/react&color=61DAFB" alt="Types React">
  <img src="https://img.shields.io/npm/v/@types/react-dom?style=for-the-badge&label=@types/react-dom&color=61DAFB" alt="Types React DOM">
  <img src="https://img.shields.io/npm/v/@types/node?style=for-the-badge&label=@types/node&logo=node.js&color=339933" alt="Types Node">
</p>

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

<p align="center">Made with love by H0NEYP0T-466 ❤️</p>
