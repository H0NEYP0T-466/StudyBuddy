import { useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { extractPen2PDF, exportPen2PDF } from '../services/api';
import 'katex/dist/katex.min.css';
import './Pen2PDF.css';

const Pen2PDF = () => {
  const [file, setFile] = useState<File | null>(null);
  const [markdown, setMarkdown] = useState('');
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [pages, setPages] = useState('');
  const [previewMode, setPreviewMode] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const handleExtract = async () => {
    if (!file) return;
    
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (pages) formData.append('pages', pages);
      
      const response = await extractPen2PDF(formData);
      setMarkdown(response.data.markdown);
    } catch (error) {
      console.error('Extraction failed:', error);
      alert('Failed to extract document. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'pdf' | 'docx' | 'markdown') => {
    if (!markdown) return;
    
    setLoading(true);
    try {
      const response = await exportPen2PDF({
        markdown,
        format,
        title: file?.name.replace(/\.[^/.]+$/, '') || 'document',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const extension = format === 'markdown' ? 'md' : format;
      link.setAttribute('download', `${file?.name.replace(/\.[^/.]+$/, '') || 'document'}.${extension}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export document. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pen2pdf">
      <div className="pen2pdf-header">
        <h1>📝 Pen2PDF Document Extractor</h1>
        <p className="subtitle">Upload a PDF or image to extract text and convert to markdown</p>
      </div>

      <div className="pen2pdf-content">
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
              accept=".pdf,.png,.jpg,.jpeg"
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
                <p className="dropzone-hint">Supported: PDF, PNG, JPG</p>
              </div>
            )}
          </div>

          <div className="options-row">
            <input
              type="text"
              placeholder="Pages (e.g., 1-5, 7, 9-12)"
              value={pages}
              onChange={(e) => setPages(e.target.value)}
              className="pages-input"
            />
            <button
              onClick={handleExtract}
              disabled={!file || loading}
              className="extract-button"
            >
              {loading ? 'Extracting...' : 'Extract'}
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
              <div className="toolbar-right">
                <button onClick={() => handleExport('markdown')} className="export-button">
                  Export MD
                </button>
                <button onClick={() => handleExport('docx')} className="export-button">
                  Export DOCX
                </button>
                <button onClick={() => handleExport('pdf')} className="export-button">
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
                value={markdown}
                onChange={(e) => setMarkdown(e.target.value)}
                className="markdown-editor"
                placeholder="Extracted markdown will appear here..."
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Pen2PDF;
