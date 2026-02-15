# Notes Selection Feature

## Overview
Enhanced the AI Assistant to allow users to select specific notes as context for their conversations, providing more precise and relevant AI responses.

## Changes Made

### 1. Fixed 307 Temporary Redirects
- **Issue**: API requests to `/api/folders`, `/api/notes`, `/api/timetable`, and `/api/todos` were receiving 307 redirects
- **Solution**: Added trailing slashes to all GET and POST requests in the frontend API service
- **Files Modified**: 
  - `src/services/api.ts`

### 2. RAG Checkbox Default State
- **Issue**: RAG (Retrieval Augmented Generation) was disabled by default
- **Solution**: Changed initial state of `useRAG` from `false` to `true`
- **Files Modified**: 
  - `src/pages/AIAssistant.tsx` (line 23)

### 3. Enhanced Notes Selection UI
- **Features Added**:
  - Two-step selection process:
    1. Select subject folders
    2. Select specific notes from those folders
  - "Select All" and "Clear" buttons for bulk operations
  - Search functionality to filter notes by title or content
  - Visual count of selected folders and notes
  - Note preview showing first 60 characters

- **Files Modified**:
  - `src/pages/AIAssistant.tsx`
  - `src/pages/AIAssistant.css`
  - `src/types/index.ts`
  - `src/services/api.ts`

### 4. Backend Note Context Integration
- **Features Added**:
  - New `note_ids` parameter in chat endpoint
  - Fetches selected notes from MongoDB by ID
  - Includes full note content as context in the AI prompt
  - Maintains backward compatibility with legacy `context_notes` parameter

- **Files Modified**:
  - `backend/app/routes/assistant.py`

## Usage

### For Users

1. **Open AI Assistant** (Isabella icon in navigation)
2. **Enable RAG** (checked by default)
3. **Click the 📚 button** to open the Notes Context panel
4. **Select Subject Folders**:
   - Check the folders/subjects you want to include
   - All notes in selected folders will be loaded
5. **Select Specific Notes**:
   - Use the search box to filter notes by title or content
   - Check individual notes you want to include as context
   - Use "Select All" to quickly select all visible notes
   - Use "Clear" to deselect all notes
6. **Ask Questions**: Your selected notes will be included as context in the AI's response

### For Developers

#### Frontend Integration

```typescript
// In your component
const [selectedNotes, setSelectedNotes] = useState<string[]>([]);

// Toggle individual note
const toggleNote = (noteId: string) => {
  setSelectedNotes(prev =>
    prev.includes(noteId) ? prev.filter(id => id !== noteId) : [...prev, noteId]
  );
};

// Send chat request with note context
const response = await chatWithAssistant({
  message: userMessage,
  model: selectedModel,
  use_rag: true,
  note_ids: selectedNotes,  // Array of note IDs
  conversation_history: chatHistory
});
```

#### Backend Integration

```python
@router.post("/chat")
async def chat_with_assistant(
    message: str = Form(...),
    model: str = Form(...),
    note_ids: Optional[str] = Form(None),  # JSON stringified array
    ...
):
    # Parse note IDs
    note_id_list = json.loads(note_ids) if note_ids else []
    
    # Fetch notes from database
    db = get_database()
    selected_notes = []
    for note_id in note_id_list:
        note = await db.notes.find_one({"_id": ObjectId(note_id)})
        if note:
            selected_notes.append(note)
    
    # Build context
    notes_context = ""
    for note in selected_notes:
        notes_context += f"\n[Note: {note['title']}]\n{note['content']}\n"
    
    # Include in prompt
    final_prompt = f"{notes_context}\n\nUser question: {message}"
```

## Technical Details

### State Management
- `selectedFolders: string[]` - IDs of selected folders
- `selectedNotes: string[]` - IDs of individually selected notes
- `contextNotes: Note[]` - All notes loaded from selected folders
- `noteSearchQuery: string` - Current search filter

### Search Implementation
- Case-insensitive search
- Searches both title and content fields
- Real-time filtering as user types

### API Changes
- Added `note_ids?: string[]` to `AssistantChatRequest` type
- Backend accepts `note_ids` as JSON-stringified array in FormData
- Backend fetches notes by ObjectId from MongoDB
- Note content is prepended to the AI prompt with clear markers

## Benefits

1. **More Precise Context**: Users can select exactly which notes are relevant
2. **Better AI Responses**: AI has access to complete note content, not just RAG chunks
3. **User Control**: Clear visibility into what context the AI is using
4. **Flexible**: Works alongside existing RAG system for best results
5. **Searchable**: Easy to find specific notes even with many in a folder

## Future Enhancements

- [ ] Save/load note selection presets
- [ ] Automatic note relevance scoring
- [ ] Folder-level select all
- [ ] Recent notes quick access
- [ ] Note content preview on hover
- [ ] Export conversation with referenced notes
