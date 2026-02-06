import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getFolders, createFolder, updateFolder, deleteFolder } from '../services/api';
import type { Folder } from '../types';
import './NotesLibrary.css';

const PRESET_COLORS = [
  '#4a9eff', '#10b981', '#f59e0b', '#ef4444', 
  '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'
];

const NotesLibrary = () => {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingFolder, setEditingFolder] = useState<Folder | null>(null);
  const [deletingFolder, setDeletingFolder] = useState<Folder | null>(null);
  const [formData, setFormData] = useState({ name: '', color: PRESET_COLORS[0] });
  const navigate = useNavigate();

  useEffect(() => {
    loadFolders();
  }, []);

  const loadFolders = async () => {
    try {
      const response = await getFolders();
      setFolders(response.data);
    } catch (error) {
      console.error('Failed to load folders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.name.trim()) return;
    
    try {
      await createFolder(formData);
      setShowCreateModal(false);
      setFormData({ name: '', color: PRESET_COLORS[0] });
      loadFolders();
    } catch (error) {
      console.error('Failed to create folder:', error);
    }
  };

  const handleUpdate = async () => {
    if (!editingFolder || !formData.name.trim()) return;
    
    try {
      await updateFolder(editingFolder.id, formData);
      setEditingFolder(null);
      setFormData({ name: '', color: PRESET_COLORS[0] });
      loadFolders();
    } catch (error) {
      console.error('Failed to update folder:', error);
    }
  };

  const handleDelete = async () => {
    if (!deletingFolder) return;
    
    try {
      await deleteFolder(deletingFolder.id);
      setDeletingFolder(null);
      loadFolders();
    } catch (error) {
      console.error('Failed to delete folder:', error);
    }
  };

  const openEditModal = (folder: Folder) => {
    setEditingFolder(folder);
    setFormData({ name: folder.name, color: folder.color });
  };

  if (loading) {
    return <div className="loading">Loading folders...</div>;
  }

  return (
    <div className="notes-library">
      <div className="library-header">
        <div>
          <h1>📚 Notes Library</h1>
          <p className="subtitle">Organize your notes into folders</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="create-folder-button">
          ➕ New Folder
        </button>
      </div>

      {folders.length === 0 ? (
        <div className="empty-library">
          <span className="empty-icon">📁</span>
          <h3>No folders yet</h3>
          <p>Create a folder to organize your notes</p>
        </div>
      ) : (
        <div className="folders-grid">
          {folders.map((folder) => (
            <div
              key={folder.id}
              className="folder-card"
              style={{ borderTop: `4px solid ${folder.color}` }}
            >
              <div
                className="folder-card-content"
                onClick={() => navigate(`/notes-library/folder/${folder.id}`)}
              >
                <span className="folder-icon">📁</span>
                <h3 className="folder-name">{folder.name}</h3>
                <p className="folder-date">
                  Created {new Date(folder.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="folder-actions">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    openEditModal(folder);
                  }}
                  className="folder-action-button"
                >
                  ✏️
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeletingFolder(folder);
                  }}
                  className="folder-action-button delete"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {(showCreateModal || editingFolder) && (
        <div className="modal-overlay" onClick={() => {
          setShowCreateModal(false);
          setEditingFolder(null);
          setFormData({ name: '', color: PRESET_COLORS[0] });
        }}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingFolder ? 'Edit Folder' : 'Create Folder'}</h2>
            <div className="form-group">
              <label>Folder Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter folder name"
                autoFocus
              />
            </div>
            <div className="form-group">
              <label>Folder Color</label>
              <div className="color-picker">
                {PRESET_COLORS.map((color) => (
                  <button
                    key={color}
                    className={`color-option ${formData.color === color ? 'selected' : ''}`}
                    style={{ background: color }}
                    onClick={() => setFormData({ ...formData, color })}
                    title={color}
                  />
                ))}
              </div>
            </div>
            <div className="modal-actions">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setEditingFolder(null);
                  setFormData({ name: '', color: PRESET_COLORS[0] });
                }}
                className="cancel-button"
              >
                Cancel
              </button>
              <button
                onClick={editingFolder ? handleUpdate : handleCreate}
                className="submit-button"
                disabled={!formData.name.trim()}
              >
                {editingFolder ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {deletingFolder && (
        <div className="modal-overlay" onClick={() => setDeletingFolder(null)}>
          <div className="modal confirm-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Delete Folder?</h2>
            <p className="confirm-message">
              Are you sure you want to delete <strong>{deletingFolder.name}</strong> and all its notes? This action cannot be undone.
            </p>
            <div className="modal-actions">
              <button
                onClick={() => setDeletingFolder(null)}
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

export default NotesLibrary;
