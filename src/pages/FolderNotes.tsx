import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { getNotes, createNote, updateNote, deleteNote, getFolders } from '../services/api';
import type { Note, Folder } from '../types';
import 'katex/dist/katex.min.css';
import './FolderNotes.css';

const FolderNotes = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [notes, setNotes] = useState<Note[]>([]);
  const [folder, setFolder] = useState<Folder | null>(null);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({ title: '', content: '' });
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [notesRes, foldersRes] = await Promise.all([
        getNotes(Number(id)),
        getFolders(),
      ]);
      setNotes(notesRes.data);
      const currentFolder = foldersRes.data.find((f) => f.id === Number(id));
      setFolder(currentFolder || null);
    } catch (error) {
      console.error('Failed to load notes:', error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      loadData();
    }
  }, [id, loadData]);

  const handleCreate = async () => {
    if (!formData.title.trim()) return;
    
    try {
      await createNote({ ...formData, folder_id: Number(id) });
      setShowCreateModal(false);
      setFormData({ title: '', content: '' });
      loadData();
    } catch (error) {
      console.error('Failed to create note:', error);
    }
  };

  const handleUpdate = async () => {
    if (!selectedNote) return;
    
    try {
      await updateNote(selectedNote.id, formData);
      setIsEditing(false);
      loadData();
      const updatedNote = await (await getNotes(Number(id))).data.find((n) => n.id === selectedNote.id);
      if (updatedNote) setSelectedNote(updatedNote);
    } catch (error) {
      console.error('Failed to update note:', error);
    }
  };

  const handleDelete = async (noteId: number) => {
    if (!confirm('Delete this note?')) return;
    
    try {
      await deleteNote(noteId);
      if (selectedNote?.id === noteId) {
        setSelectedNote(null);
      }
      loadData();
    } catch (error) {
      console.error('Failed to delete note:', error);
    }
  };

  const selectNote = (note: Note) => {
    setSelectedNote(note);
    setFormData({ title: note.title, content: note.content });
    setIsEditing(false);
  };

  if (loading) {
    return <div className="loading">Loading notes...</div>;
  }

  if (!folder) {
    return (
      <div className="folder-not-found">
        <h2>Folder not found</h2>
        <Link to="/notes-library">Back to Library</Link>
      </div>
    );
  }

  return (
    <div className="folder-notes">
      <div className="folder-notes-header">
        <div className="folder-info">
          <button onClick={() => navigate('/notes-library')} className="back-button">
            ← Back
          </button>
          <div>
            <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ color: folder.color }}>📁</span>
              {folder.name}
            </h1>
            <p className="subtitle">{notes.length} notes</p>
          </div>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="create-note-button">
          ➕ New Note
        </button>
      </div>

      <div className="folder-notes-content">
        <div className="notes-sidebar">
          {notes.length === 0 ? (
            <div className="empty-notes">
              <p>No notes in this folder</p>
            </div>
          ) : (
            notes.map((note) => (
              <div
                key={note.id}
                className={`note-item ${selectedNote?.id === note.id ? 'active' : ''}`}
                onClick={() => selectNote(note)}
              >
                <h4 className="note-item-title">{note.title}</h4>
                <p className="note-item-date">
                  {new Date(note.updated_at).toLocaleDateString()}
                </p>
              </div>
            ))
          )}
        </div>

        <div className="note-viewer">
          {selectedNote ? (
            <>
              <div className="note-viewer-header">
                <h2>{isEditing ? 'Edit Note' : selectedNote.title}</h2>
                <div className="note-actions">
                  {isEditing ? (
                    <>
                      <button onClick={() => setIsEditing(false)} className="action-btn">
                        Cancel
                      </button>
                      <button onClick={handleUpdate} className="action-btn save">
                        💾 Save
                      </button>
                    </>
                  ) : (
                    <>
                      <button onClick={() => setIsEditing(true)} className="action-btn">
                        ✏️ Edit
                      </button>
                      <button
                        onClick={() => handleDelete(selectedNote.id)}
                        className="action-btn delete"
                      >
                        🗑️ Delete
                      </button>
                    </>
                  )}
                </div>
              </div>

              {isEditing ? (
                <div className="note-editor">
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="note-title-input"
                    placeholder="Note title"
                  />
                  <textarea
                    value={formData.content}
                    onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                    className="note-content-editor"
                    placeholder="Write your note content in markdown..."
                  />
                </div>
              ) : (
                <div className="note-content">
                  <ReactMarkdown
                    remarkPlugins={[remarkMath, remarkGfm]}
                    rehypePlugins={[rehypeKatex]}
                  >
                    {selectedNote.content || '*No content*'}
                  </ReactMarkdown>
                </div>
              )}
            </>
          ) : (
            <div className="no-note-selected">
              <span className="empty-icon">📄</span>
              <p>Select a note to view</p>
            </div>
          )}
        </div>
      </div>

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create Note</h2>
            <div className="form-group">
              <label>Title</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Enter note title"
                autoFocus
              />
            </div>
            <div className="form-group">
              <label>Content</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                placeholder="Write note content in markdown..."
                rows={10}
              />
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowCreateModal(false)} className="cancel-button">
                Cancel
              </button>
              <button
                onClick={handleCreate}
                className="submit-button"
                disabled={!formData.title.trim()}
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FolderNotes;
