# Pen2PDF v2.0 Frontend

A complete React + TypeScript frontend for the Pen2PDF v2.0 productivity suite.

## Features

### 🏠 Dashboard
- Overview of today's schedule from timetable
- Active and pinned todos
- Quick access to notes folders
- Quick action buttons for common tasks
- Week counter widget

### 📝 Pen2PDF Document Extractor
- Drag-and-drop file upload
- Support for PDF, PNG, JPG files
- Page range selection
- Real-time markdown editor with live preview
- Export to PDF, DOCX, or Markdown
- KaTeX support for mathematical expressions

### 📚 Notes Library
- Folder-based organization
- Color-coded folders
- CRUD operations for folders and notes
- Markdown editor with preview
- Search functionality

### ✨ Notes Generator
- AI-powered note generation from documents
- Multiple AI model support (GPT-4o, Claude, Gemini)
- Folder selection for organization
- Support for PDF, images, text, and markdown files

### 📅 Timetable
- Weekly schedule view
- Add/edit/delete timetable entries
- CSV import for bulk updates
- Color-coded entries by day

### ✓ Todo List
- Create todos with descriptions and due dates
- Pin important todos
- Subtask support with completion tracking
- Separate active and completed sections

### 🤖 Isabella AI Assistant
- Conversational AI with chat interface
- RAG (Retrieval Augmented Generation) support
- Search through your notes for context
- Multiple AI model selection
- Markdown rendering with code syntax highlighting
- Source citation from notes

### 🎨 Design
- Dark theme with #111 background
- Minimalistic and modern UI
- Smooth animations and transitions
- Responsive layout for mobile and desktop
- Custom scrollbar styling
- Consistent color palette and spacing

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **React Router** - Navigation
- **Axios** - API requests
- **React Markdown** - Markdown rendering
- **KaTeX** - Mathematical expressions
- **Vite** - Build tool

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── Layout.tsx      # Main layout wrapper
│   ├── Navbar.tsx      # Navigation bar
│   └── WeekCounter.tsx # Semester week counter
├── pages/              # Page components
│   ├── Dashboard.tsx
│   ├── Pen2PDF.tsx
│   ├── NotesLibrary.tsx
│   ├── FolderNotes.tsx
│   ├── NotesGenerator.tsx
│   ├── Timetable.tsx
│   ├── TodoList.tsx
│   └── AIAssistant.tsx
├── services/           # API service layer
│   └── api.ts
├── types/             # TypeScript type definitions
│   └── index.ts
└── styles/            # Global styles
    └── global.css
```

## API Endpoints

The frontend connects to the backend running on `http://localhost:8003`:

- `/api/folders` - Folder management
- `/api/notes` - Notes CRUD and generation
- `/api/timetable` - Timetable management
- `/api/todos` - Todo list with subtasks
- `/api/assistant/chat` - AI assistant chat
- `/api/pen2pdf/extract` - Document extraction
- `/api/pen2pdf/export` - Document export

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

## Features by Page

### Dashboard
- Real-time week counter
- Today's timetable entries
- Active and pinned todos
- Folder overview
- Quick action shortcuts

### Pen2PDF
- File drag-and-drop upload
- Page range extraction
- Split-view editor/preview
- Live markdown rendering
- Multi-format export

### Notes Library
- Grid view of folders
- Color customization
- Folder creation/editing/deletion
- Navigate to folder contents

### Folder Notes
- Sidebar with note list
- Note editor with markdown
- CRUD operations
- Real-time preview
- Folder navigation

### Notes Generator
- Document upload
- AI model selection
- Folder targeting
- Progress tracking
- Auto-redirect after generation

### Timetable
- 8 AM - 8 PM time slots
- Monday to Sunday columns
- Drag-to-create functionality
- Entry editing modal
- CSV bulk import

### Todo List
- Title and description
- Due date tracking
- Pin important items
- Subtask management
- Completion tracking

### AI Assistant
- Chat interface
- Model selection
- RAG toggle
- Folder context selection
- Source citation
- Markdown message rendering

## Styling

The app uses CSS custom properties for consistent theming:

```css
--bg-primary: #111
--accent: #4a9eff
--success: #10b981
--danger: #ef4444
--warning: #f59e0b
```

All components follow the same spacing, border radius, and color conventions defined in `global.css`.

## Type Safety

Full TypeScript coverage with interfaces for:
- API request/response types
- Component props
- State management
- Route parameters

## Best Practices

- Functional components with hooks
- Proper error handling
- Loading states
- Responsive design
- Accessibility considerations
- Code organization
- Consistent naming conventions
