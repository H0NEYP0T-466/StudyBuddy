import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { generateNotes, getFolders, createNote, exportPen2PDF } from '../services/api';
import type { Folder } from '../types';
import 'katex/dist/katex.min.css';
import './NotesGenerator.css';

const GEMINI_MODELS = [
  { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' },
  { value: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro' },
];

const NotesGenerator = () => {
  const [file, setFile] = useState<File | null>(null);
  const [model, setModel] = useState(GEMINI_MODELS[0].value);
  const [markdown, setMarkdown] = useState('');
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [saveModalStep, setSaveModalStep] = useState<'folder' | 'title'>('folder');
  const [selectedFolderId, setSelectedFolderId] = useState<number | undefined>();
  const [noteTitle, setNoteTitle] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const editorRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (showSaveModal && saveModalStep === 'folder') {
      fetchFoldersList();
    }
  }, [showSaveModal, saveModalStep]);

  const fetchFoldersList = async () => {
    try {
      const response = await getFolders();
      setFolders(response.data);
    } catch (error) {
      console.error('Failed to fetch folders:', error);
      setErrorMessage('Failed to load folders. Please try again.');
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
    setErrorMessage('');
    try {
      const formData = new FormData();
      formData.append('files', file);
      formData.append('model', model);
      
      const response = await generateNotes(formData);
      setMarkdown(response.data.notes || response.data.markdown || '');
      setErrorMessage('Notes generated successfully!');
      setTimeout(() => setErrorMessage(''), 3000);
    } catch (error) {
      console.error('Generation failed:', error);
      setErrorMessage('Failed to generate notes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const insertMarkdown = (syntax: string) => {
    const textarea = editorRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
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

    setMarkdown(newText);
    
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(newPosition, newPosition);
    }, 0);
  };

  const handleExport = async (format: 'pdf' | 'docx' | 'markdown') => {
    if (!markdown) return;
    
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('content', markdown);
      formData.append('title', file?.name.replace(/\.[^/.]+$/, '') || 'notes');
      formData.append('format', format);

      const response = await exportPen2PDF(formData);
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const extension = format === 'markdown' ? 'md' : format;
      link.setAttribute('download', `${file?.name.replace(/\.[^/.]+$/, '') || 'notes'}.${extension}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setErrorMessage('Export successful!');
      setTimeout(() => setErrorMessage(''), 3000);
    } catch (error) {
      console.error('Export failed:', error);
      setErrorMessage('Failed to export document. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveToNotes = () => {
    if (!markdown) return;
    setShowSaveModal(true);
    setSaveModalStep('folder');
    setErrorMessage('');
    setNoteTitle('');
  };

  const handleFolderSelect = (folderId?: number) => {
    setSelectedFolderId(folderId);
    setSaveModalStep('title');
  };

  const handleSaveNote = async () => {
    if (!noteTitle.trim()) {
      setErrorMessage('Please enter a note title.');
      return;
    }

    setLoading(true);
    try {
      await createNote({
        title: noteTitle,
        content: markdown,
        folder_id: selectedFolderId,
      });
      
      setShowSaveModal(false);
      setNoteTitle('');
      setSelectedFolderId(undefined);
      setSaveModalStep('folder');
      
      setErrorMessage('Note saved successfully!');
      setTimeout(() => setErrorMessage(''), 3000);
    } catch (error) {
      console.error('Failed to save note:', error);
      setErrorMessage('Failed to save note. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const closeSaveModal = () => {
    setShowSaveModal(false);
    setNoteTitle('');
    setSelectedFolderId(undefined);
    setSaveModalStep('folder');
    setErrorMessage('');
  };

  return (
    <div className="notes-generator">
      <div className="notes-generator-header">
        <h1>✨ Notes Generator</h1>
        <p className="subtitle">Upload a document to automatically generate structured notes</p>
      </div>

      {errorMessage && (
        <div className={`message ${errorMessage.includes('success') ? 'success' : 'error'}`}>
          {errorMessage}
        </div>
      )}

      <div className="notes-generator-content">
        <div className="upload-section">
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

          <div className="options-row">
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="model-select"
            >
              {GEMINI_MODELS.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>

            <button
              onClick={handleGenerate}
              disabled={!file || loading}
              className="generate-button"
            >
              {loading ? '⏳ Generating...' : '✨ Generate Notes'}
            </button>
          </div>
        </div>

        {markdown && (
          <div className="editor-section">
            <div className="editor-toolbar">
              <div className="toolbar-left">
                <button
                  onClick={() => setPreviewMode(false)}
                  className={`toolbar-button ${!previewMode ? 'active' : ''}`}
                >
                  ✏️ Edit
                </button>
                <button
                  onClick={() => setPreviewMode(true)}
                  className={`toolbar-button ${previewMode ? 'active' : ''}`}
                >
                  👁️ Preview
                </button>
              </div>
              
              {!previewMode && (
                <div className="toolbar-center">
                  <button onClick={() => insertMarkdown('h1')} className="format-button" title="Heading 1">
                    H1
                  </button>
                  <button onClick={() => insertMarkdown('h2')} className="format-button" title="Heading 2">
                    H2
                  </button>
                  <button onClick={() => insertMarkdown('h3')} className="format-button" title="Heading 3">
                    H3
                  </button>
                  <div className="toolbar-divider" />
                  <button onClick={() => insertMarkdown('bold')} className="format-button" title="Bold">
                    <strong>B</strong>
                  </button>
                  <button onClick={() => insertMarkdown('italic')} className="format-button" title="Italic">
                    <em>I</em>
                  </button>
                  <div className="toolbar-divider" />
                  <button onClick={() => insertMarkdown('bullet')} className="format-button" title="Bullet List">
                    ⦿
                  </button>
                  <button onClick={() => insertMarkdown('numbered')} className="format-button" title="Numbered List">
                    ⒈
                  </button>
                  <button onClick={() => insertMarkdown('code')} className="format-button" title="Code Block">
                    {'</>'}
                  </button>
                </div>
              )}

              <div className="toolbar-right">
                <button onClick={handleSaveToNotes} className="save-notes-button" disabled={loading}>
                  💾 Save to Notes
                </button>
                <button onClick={() => handleExport('markdown')} className="export-button" disabled={loading}>
                  Export MD
                </button>
                <button onClick={() => handleExport('docx')} className="export-button" disabled={loading}>
                  Export DOCX
                </button>
                <button onClick={() => handleExport('pdf')} className="export-button" disabled={loading}>
                  Export PDF
                </button>
              </div>
            </div>

            {previewMode ? (
              <div className="markdown-preview">
                <ReactMarkdown
                  remarkPlugins={[remarkMath, remarkGfm]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {markdown}
                </ReactMarkdown>
              </div>
            ) : (
              <textarea
                ref={editorRef}
                value={markdown}
                onChange={(e) => setMarkdown(e.target.value)}
                className="markdown-editor"
                placeholder="Generated notes will appear here..."
              />
            )}
          </div>
        )}
      </div>

      {showSaveModal && (
        <div className="modal-overlay" onClick={closeSaveModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{saveModalStep === 'folder' ? 'Select Folder' : 'Enter Note Title'}</h2>
              <button onClick={closeSaveModal} className="modal-close">×</button>
            </div>

            {saveModalStep === 'folder' ? (
              <div className="modal-content">
                {folders.length === 0 ? (
                  <div className="empty-folders">
                    <p>No folders found. Please create a folder first.</p>
                    <a href="/notes" className="link-button">Go to Notes Library</a>
                  </div>
                ) : (
                  <>
                    <p className="modal-description">Choose a folder to save this note:</p>
                    <div className="folder-list">
                      <button
                        onClick={() => handleFolderSelect(undefined)}
                        className={`folder-item ${selectedFolderId === undefined ? 'selected' : ''}`}
                      >
                        <span className="folder-icon">📁</span>
                        <span>No Folder (Root)</span>
                      </button>
                      {folders.map((folder) => (
                        <button
                          key={folder.id}
                          onClick={() => handleFolderSelect(folder.id)}
                          className={`folder-item ${selectedFolderId === folder.id ? 'selected' : ''}`}
                          style={{ borderLeftColor: folder.color }}
                        >
                          <span className="folder-icon">📁</span>
                          <span>{folder.name}</span>
                        </button>
                      ))}
                    </div>
                    <div className="modal-actions">
                      <button onClick={closeSaveModal} className="cancel-button">
                        Cancel
                      </button>
                      <button
                        onClick={() => setSaveModalStep('title')}
                        className="submit-button"
                      >
                        Next
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="modal-content">
                <div className="form-group">
                  <label>Note Title</label>
                  <input
                    type="text"
                    value={noteTitle}
                    onChange={(e) => setNoteTitle(e.target.value)}
                    placeholder="Enter note title..."
                    autoFocus
                  />
                </div>
                {errorMessage && !errorMessage.includes('success') && (
                  <p className="error-text">{errorMessage}</p>
                )}
                <div className="modal-actions">
                  <button onClick={() => setSaveModalStep('folder')} className="cancel-button">
                    Back
                  </button>
                  <button
                    onClick={handleSaveNote}
                    className="submit-button"
                    disabled={!noteTitle.trim() || loading}
                  >
                    {loading ? 'Saving...' : 'Save Note'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotesGenerator;
