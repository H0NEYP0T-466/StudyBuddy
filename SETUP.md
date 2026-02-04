# Pen2PDF v2.0 - Setup Guide

## Prerequisites Installation

### 1. Python 3.10+
```bash
# Check Python version
python3 --version

# If not installed:
# macOS: brew install python3
# Ubuntu: sudo apt install python3 python3-pip python3-venv
# Windows: Download from python.org
```

### 2. Node.js 18+
```bash
# Check Node version
node --version

# If not installed:
# macOS: brew install node
# Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install nodejs
# Windows: Download from nodejs.org
```

### 3. MongoDB
```bash
# Option 1: Local Installation
# macOS: brew tap mongodb/brew && brew install mongodb-community
# Ubuntu: Follow official MongoDB installation guide
# Windows: Download from mongodb.com

# Option 2: MongoDB Atlas (Cloud)
# Sign up at mongodb.com/cloud/atlas
# Create free tier cluster
# Get connection string
```

## Step-by-Step Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/H0NEYP0T-466/StudyBuddy.git
cd StudyBuddy
```

### Step 2: Backend Setup

#### Create Virtual Environment
```bash
cd backend
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (Web framework)
- Motor & PyMongo (MongoDB)
- Google GenAI (Gemini)
- OpenAI (for various models)
- FAISS (Vector search)
- Sentence Transformers (Embeddings)
- PDF/Document processors
- And more...

#### Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Required configuration:
```env
# MongoDB - Local
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=pen2pdf

# MongoDB - Atlas (Cloud)
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

# AI Models (Get from respective providers)
GEMINI_API_KEY=your_gemini_api_key_here
LONGCAT_API_KEY=your_longcat_api_key_here  # Optional
GITHUB_TOKEN=your_github_token_here  # Optional

# Server
PORT=8003
HOST=0.0.0.0

# CORS
FRONTEND_URL=http://localhost:5173
```

#### Get API Keys

**Google Gemini**:
1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy to `.env` as `GEMINI_API_KEY`

**LongCat** (Optional):
1. Visit https://longcat.chat
2. Sign up and get API key
3. Copy to `.env` as `LONGCAT_API_KEY`

**GitHub Models** (Optional):
1. Go to https://github.com/settings/tokens
2. Generate new Personal Access Token
3. Copy to `.env` as `GITHUB_TOKEN`

#### Start MongoDB (if using local)
```bash
# macOS/Linux
mongod --config /usr/local/etc/mongod.conf

# Or in separate terminal:
mongod --dbpath ~/data/db

# Windows
net start MongoDB
```

#### Start Backend Server
```bash
# Make sure you're in backend directory with venv activated
cd /path/to/StudyBuddy/backend
source venv/bin/activate  # if not already activated

# Option 1: Using the run script
./run.sh

# Option 2: Manual start
cd ..
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8003 --reload
```

Backend will be available at: http://localhost:8003
API docs at: http://localhost:8003/docs

### Step 3: Frontend Setup

Open a new terminal (keep backend running):

```bash
cd /path/to/StudyBuddy

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## Verification

### Test Backend
```bash
# In a new terminal
curl http://localhost:8003/health

# Should return: {"status":"healthy"}
```

### Test Frontend
Open browser to http://localhost:5173
- You should see the Pen2PDF dashboard
- Navigation should work
- Dark theme should be applied

### Test RAG System
1. Place some `.txt` or `.md` files in `backend/data/`
2. Restart backend server
3. Go to AI Assistant page
4. Ask a question related to your documents
5. Should see sources cited in response

## Troubleshooting

### Backend Issues

**Error: "ModuleNotFoundError"**
```bash
# Make sure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Error: "Connection refused" (MongoDB)**
```bash
# Start MongoDB
# Check if running:
ps aux | grep mongod

# If not, start it:
mongod --dbpath ~/data/db
```

**Error: "GEMINI_API_KEY not found"**
```bash
# Check .env file exists
ls -la backend/.env

# Verify API key is set
cat backend/.env | grep GEMINI
```

### Frontend Issues

**Error: "Cannot connect to backend"**
- Ensure backend is running on port 8003
- Check browser console for CORS errors
- Verify `FRONTEND_URL` in backend `.env`

**Error: "Module not found"**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### RAG System Issues

**RAG not finding documents**
- Ensure files are in `backend/data/` directory
- Restart backend to re-index
- Check backend logs for indexing messages
- Supported formats: .pdf, .txt, .md, .docx

**Vector store errors**
```bash
# Delete existing index and restart
rm -rf backend/vector_store/*
# Restart backend - will rebuild index
```

## Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- Frontend: Changes auto-refresh in browser
- Backend: Add `--reload` flag to uvicorn

### Debug Mode
```bash
# Backend with debug logs
DEBUG=true python -m uvicorn backend.main:app --reload

# Frontend with source maps (default in dev)
npm run dev
```

### Database Management
```bash
# MongoDB Shell
mongosh

# Use database
use pen2pdf

# List collections
show collections

# Query notes
db.notes.find().pretty()

# Clear all data (careful!)
db.dropDatabase()
```

## Production Deployment

### Backend
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn backend.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8003 \
  --access-logfile - \
  --error-logfile -
```

### Frontend
```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Deploy dist/ folder to your hosting service
# (Vercel, Netlify, AWS S3, etc.)
```

## Next Steps

1. **Create Folders**: Start by creating subject folders in Notes Library
2. **Upload Documents**: Add study materials to Pen2PDF or Notes Generator
3. **Generate Notes**: Use AI to create structured notes
4. **Set Up Timetable**: Import or manually add your class schedule
5. **Create Todos**: Add tasks and break them into subtasks
6. **Ask Isabella**: Start chatting with AI assistant

## Support

For issues or questions:
- Check the main README.md
- Review API documentation at /docs
- Check backend logs for errors
- Review browser console for frontend issues

Happy studying! 🎓
