import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateNotes, getFolders } from '../services/api';
import type { Folder } from '../types';
import { AI_MODELS } from '../types';
import './NotesGenerator.css';

const NotesGenerator = () => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [model, setModel] = useState(AI_MODELS[0].value);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<number | null>(null);
  const [showFolderModal, setShowFolderModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
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
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleGenerate = async () => {
    if (!file) return;
    
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('model', model);
      if (title) formData.append('title', title);
      if (selectedFolder) formData.append('folder_id', selectedFolder.toString());
      
      const response = await generateNotes(formData);
      alert(`Notes generated successfully in ${response.data.processing_time.toFixed(2)}s!`);
      
      if (selectedFolder) {
        navigate(`/notes-library/folder/${selectedFolder}`);
      } else {
        navigate('/notes-library');
      }
    } catch (error) {
      console.error('Generation failed:', error);
      alert('Failed to generate notes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const selectedFolderObj = folders.find((f) => f.id === selectedFolder);

  return (
    <div className="notes-generator">
      <div className="generator-header">
        <h1>✨ Notes Generator</h1>
        <p className="subtitle">Upload a document to automatically generate structured notes</p>
      </div>

      <div className="generator-content">
        <div className="generator-card">
          <h3>📁 Upload Document</h3>
          <div
            className={`dropzone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.txt,.md"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            {file ? (
              <div className="file-selected">
                <span className="file-icon">📄</span>
                <span className="file-name">{file.name}</span>
                <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
              </div>
            ) : (
              <div className="dropzone-placeholder">
                <span className="upload-icon">📁</span>
                <p>Drag and drop a file here, or click to browse</p>
                <p className="dropzone-hint">Supported: PDF, Images, Text, Markdown</p>
              </div>
            )}
          </div>
        </div>

        <div className="generator-card">
          <h3>⚙️ Configuration</h3>
          
          <div className="form-group">
            <label>Note Title (Optional)</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Leave empty to auto-generate from content"
              className="config-input"
            />
          </div>

          <div className="form-group">
            <label>AI Model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="config-select"
            >
              {AI_MODELS.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Target Folder</label>
            <button
              onClick={() => setShowFolderModal(true)}
              className="folder-select-button"
            >
              {selectedFolderObj ? (
                <>
                  <span style={{ color: selectedFolderObj.color }}>📁</span>
                  {selectedFolderObj.name}
                </>
              ) : (
                '📂 Select Folder (Optional)'
              )}
            </button>
          </div>

          <button
            onClick={handleGenerate}
            disabled={!file || loading}
            className="generate-button"
          >
            {loading ? '⏳ Generating...' : '✨ Generate Notes'}
          </button>
        </div>

        <div className="generator-card info-card">
          <h3>ℹ️ How it works</h3>
          <ul className="info-list">
            <li>Upload a document (PDF, image, or text file)</li>
            <li>AI extracts and structures the content</li>
            <li>Notes are automatically formatted in markdown</li>
            <li>Mathematical expressions are converted to LaTeX</li>
            <li>Generated notes are saved to your library</li>
          </ul>
          <div className="model-info">
            <strong>Model Recommendations:</strong>
            <p>• GPT-4o: Best quality, slower</p>
            <p>• GPT-4o Mini: Fast, good quality</p>
            <p>• Claude 3.5: Creative, detailed</p>
            <p>• Gemini 2.0: Fastest, good for simple docs</p>
          </div>
        </div>
      </div>

      {showFolderModal && (
        <div className="modal-overlay" onClick={() => setShowFolderModal(false)}>
          <div className="modal folder-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Select Folder</h2>
            <div className="folders-list">
              <div
                className={`folder-option ${selectedFolder === null ? 'selected' : ''}`}
                onClick={() => {
                  setSelectedFolder(null);
                  setShowFolderModal(false);
                }}
              >
                <span className="folder-icon">📂</span>
                <span className="folder-name">No Folder (Root)</span>
              </div>
              {folders.map((folder) => (
                <div
                  key={folder.id}
                  className={`folder-option ${selectedFolder === folder.id ? 'selected' : ''}`}
                  onClick={() => {
                    setSelectedFolder(folder.id);
                    setShowFolderModal(false);
                  }}
                  style={{ borderLeft: `3px solid ${folder.color}` }}
                >
                  <span className="folder-icon" style={{ color: folder.color }}>📁</span>
                  <span className="folder-name">{folder.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotesGenerator;
