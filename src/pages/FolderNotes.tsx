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
  const [deletingNote, setDeletingNote] = useState<Note | null>(null);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [formData, setFormData] = useState({ title: '', content: '' });
  const [loading, setLoading] = useState(true);
  const editorRef = useCallback((node: HTMLTextAreaElement | null) => {
    if (node) {
      (window as any).__noteEditorRef = node;
    }
  }, []);

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

  const handleDelete = async () => {
    if (!deletingNote) return;
    
    try {
      await deleteNote(deletingNote.id);
      if (selectedNote?.id === deletingNote.id) {
        setSelectedNote(null);
      }
      setDeletingNote(null);
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

  const insertMarkdown = (syntax: string) => {
    const textareaRef = (window as any).__noteEditorRef;
    if (!textareaRef) return;

    const start = textareaRef.selectionStart;
    const end = textareaRef.selectionEnd;
    const text = textareaRef.value;
    const selectedText = text.substring(start, end);

    let newText = '';
    let newPosition = start;

    switch (syntax) {
      case 'h1':
        newText = text.substring(0, start) + '# ' + selectedText + text.substring(end);
        newPosition = selectedText ? end + 2 : start + 2;
        break;
      case 'h2':
        newText = text.substring(0, start) + '## ' + selectedText + text.substring(end);
        newPosition = selectedText ? end + 3 : start + 3;
        break;
      case 'h3':
        newText = text.substring(0, start) + '### ' + selectedText + text.substring(end);
        newPosition = selectedText ? end + 4 : start + 4;
        break;
      case 'bold':
        newText = text.substring(0, start) + '**' + selectedText + '**' + text.substring(end);
        newPosition = selectedText ? end + 4 : start + 2;
        break;
      case 'italic':
        newText = text.substring(0, start) + '*' + selectedText + '*' + text.substring(end);
        newPosition = selectedText ? end + 2 : start + 1;
        break;
      case 'bullet':
        newText = text.substring(0, start) + '- ' + selectedText + text.substring(end);
        newPosition = selectedText ? end + 2 : start + 2;
        break;
      case 'numbered':
        newText = text.substring(0, start) + '1. ' + selectedText + text.substring(end);
        newPosition = selectedText ? end + 3 : start + 3;
        break;
      case 'code':
        newText = text.substring(0, start) + '```\n' + selectedText + '\n```' + text.substring(end);
        newPosition = selectedText ? end + 9 : start + 4;
        break;
      default:
        return;
    }

    setFormData({ ...formData, content: newText });
    
    setTimeout(() => {
      textareaRef.focus();
      textareaRef.setSelectionRange(newPosition, newPosition);
    }, 0);
  };

  const handleExport = async (format: 'pdf' | 'docx' | 'md') => {
    if (!selectedNote) return;
    
    setLoading(true);
    try {
      const { exportPen2PDF } = await import('../services/api');
      const formData = new FormData();
      formData.append('content', selectedNote.content);
      formData.append('title', selectedNote.title);
      formData.append('format', format === 'md' ? 'markdown' : format);

      const response = await exportPen2PDF(formData);
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${selectedNote.title}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setShowExportMenu(false);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setLoading(false);
    }
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
              <span className="empty-icon">📄</span>
              <p>This folder is empty</p>
              <button 
                onClick={() => setShowCreateModal(true)} 
                className="empty-create-button"
              >
                Create your first note!
              </button>
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
                      <div className="export-dropdown">
                        <button 
                          onClick={() => setShowExportMenu(!showExportMenu)} 
                          className="action-btn"
                        >
                          📥 Export
                        </button>
                        {showExportMenu && (
                          <div className="export-menu">
                            <button onClick={() => handleExport('pdf')} className="export-option">
                              📄 Export as PDF
                            </button>
                            <button onClick={() => handleExport('docx')} className="export-option">
                              📝 Export as DOCX
                            </button>
                            <button onClick={() => handleExport('md')} className="export-option">
                              📋 Export as Markdown
                            </button>
                          </div>
                        )}
                      </div>
                      <button onClick={() => setIsEditing(true)} className="action-btn">
                        ✏️ Edit
                      </button>
                      <button
                        onClick={() => setDeletingNote(selectedNote)}
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
                  <div className="editor-toolbar">
                    <button 
                      onClick={() => insertMarkdown('h1')}
                      className="toolbar-btn"
                      title="Heading 1"
                    >
                      H1
                    </button>
                    <button 
                      onClick={() => insertMarkdown('h2')}
                      className="toolbar-btn"
                      title="Heading 2"
                    >
                      H2
                    </button>
                    <button 
                      onClick={() => insertMarkdown('h3')}
                      className="toolbar-btn"
                      title="Heading 3"
                    >
                      H3
                    </button>
                    <div className="toolbar-divider" />
                    <button 
                      onClick={() => insertMarkdown('bold')}
                      className="toolbar-btn"
                      title="Bold"
                    >
                      <strong>B</strong>
                    </button>
                    <button 
                      onClick={() => insertMarkdown('italic')}
                      className="toolbar-btn"
                      title="Italic"
                    >
                      <em>I</em>
                    </button>
                    <div className="toolbar-divider" />
                    <button 
                      onClick={() => insertMarkdown('bullet')}
                      className="toolbar-btn"
                      title="Bullet List"
                    >
                      •
                    </button>
                    <button 
                      onClick={() => insertMarkdown('numbered')}
                      className="toolbar-btn"
                      title="Numbered List"
                    >
                      1.
                    </button>
                    <button 
                      onClick={() => insertMarkdown('code')}
                      className="toolbar-btn"
                      title="Code Block"
                    >
                      {'</>'}
                    </button>
                  </div>
                  <textarea
                    ref={editorRef}
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

      {deletingNote && (
        <div className="modal-overlay" onClick={() => setDeletingNote(null)}>
          <div className="modal confirm-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Delete Note?</h2>
            <p className="confirm-message">
              Are you sure you want to delete <strong>{deletingNote.title}</strong>? This action cannot be undone.
            </p>
            <div className="modal-actions">
              <button
                onClick={() => setDeletingNote(null)}
                className="cancel-button"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="delete-button"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FolderNotes;
