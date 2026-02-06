import { useState, useEffect, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { chatWithAssistant, getFolders, getNotes, exportPen2PDF } from '../services/api';
import type { ChatMessage, Folder, Note } from '../types';
import { AI_MODELS } from '../types';
import 'katex/dist/katex.min.css';
import './AIAssistant.css';

const AIAssistant = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState(AI_MODELS[0].value);
  const [useRAG, setUseRAG] = useState(false);
  const [isolateMessage, setIsolateMessage] = useState(false);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [selectedFolders, setSelectedFolders] = useState<number[]>([]);
  const [showContextPanel, setShowContextPanel] = useState(false);
  const [contextNotes, setContextNotes] = useState<Note[]>([]);
  const [sources, setSources] = useState<Note[]>([]);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportFilename, setExportFilename] = useState('conversation');
  const [exportFormat, setExportFormat] = useState<'pdf' | 'docx' | 'md'>('pdf');
  const [exportLoading, setExportLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadFolders();
  }, []);

  const loadContextNotes = useCallback(async () => {
    try {
      const notesPromises = selectedFolders.map((folderId) => getNotes(folderId));
      const notesResponses = await Promise.all(notesPromises);
      const allNotes = notesResponses.flatMap((res) => res.data);
      setContextNotes(allNotes);
    } catch (error) {
      console.error('Failed to load context notes:', error);
    }
  }, [selectedFolders]);

  useEffect(() => {
    if (selectedFolders.length > 0) {
      loadContextNotes();
    }
  }, [selectedFolders, loadContextNotes]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadFolders = async () => {
    try {
      const response = await getFolders();
      setFolders(response.data);
    } catch (error) {
      console.error('Failed to load folders:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    const userMessage: ChatMessage = { role: 'user', content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      // Prepare conversation history based on isolate_message setting
      const conversationHistory = isolateMessage ? [] : messages.slice(-10);
      
      const response = await chatWithAssistant({
        message: input,
        conversation_history: conversationHistory,
        model,
        use_rag: useRAG,
        folder_ids: useRAG ? selectedFolders : undefined,
        isolate_message: isolateMessage,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.response,
      };
      setMessages([...newMessages, assistantMessage]);
      
      if (response.data.sources) {
        setSources(response.data.sources);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      };
      setMessages([...newMessages, errorMessage]);
    } finally {
      setLoading(false);
      setUploadedFile(null);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleFolder = (folderId: number) => {
    setSelectedFolders((prev) =>
      prev.includes(folderId)
        ? prev.filter((id) => id !== folderId)
        : [...prev, folderId]
    );
  };

  const clearChat = () => {
    setMessages([]);
    setSources([]);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedModel = AI_MODELS.find(m => m.value === model);
      if (selectedModel?.supportsFiles) {
        setUploadedFile(e.target.files[0]);
      }
    }
  };

  const removeUploadedFile = () => {
    setUploadedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleExportConversation = async () => {
    if (messages.length === 0) return;
    
    setExportLoading(true);
    try {
      // Convert conversation to markdown
      let markdown = `# ${exportFilename}\n\n`;
      markdown += `**Date:** ${new Date().toLocaleDateString()}\n\n`;
      markdown += `**Model:** ${model}\n\n`;
      markdown += `---\n\n`;
      
      messages.forEach((msg) => {
        const role = msg.role === 'user' ? '**You:**' : '**Isabella:**';
        markdown += `${role}\n\n${msg.content}\n\n---\n\n`;
      });

      const formData = new FormData();
      formData.append('content', markdown);
      formData.append('title', exportFilename);
      formData.append('format', exportFormat === 'md' ? 'markdown' : exportFormat);

      const response = await exportPen2PDF(formData);
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const extension = exportFormat === 'md' ? 'md' : exportFormat;
      link.setAttribute('download', `${exportFilename}.${extension}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setShowExportModal(false);
      setExportFilename('conversation');
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export conversation. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const selectedModelObj = AI_MODELS.find(m => m.value === model);
  const supportsFiles = selectedModelObj?.supportsFiles || false;

  return (
    <div className="ai-assistant-new">
      {/* Minimalist Header */}
      <div className="assistant-header-minimal">
        <button
          onClick={() => setShowContextPanel(!showContextPanel)}
          className={`icon-button ${showContextPanel ? 'active' : ''}`}
          title="Show Notes"
        >
          📚
        </button>
        <button onClick={clearChat} className="icon-button" title="Clear Chat">
          🗑️
        </button>
        <button 
          onClick={() => setShowExportModal(true)} 
          className="icon-button"
          disabled={messages.length === 0}
          title="Export Conversation"
        >
          💾
        </button>
      </div>

      <div className="assistant-layout">
        {/* Main Chat Area */}
        <div className="chat-main">
          <div className="messages-container-new">
            {messages.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🤖</div>
                <h2>Isabella AI Assistant</h2>
                <p>Ask me anything about your notes or any study-related questions</p>
                <div className="quick-actions">
                  <button onClick={() => setInput('Summarize my recent notes')} className="quick-btn">
                    📝 Summarize notes
                  </button>
                  <button onClick={() => setInput('Explain quantum mechanics')} className="quick-btn">
                    🧠 Explain concept
                  </button>
                  <button onClick={() => setInput('Help me solve this problem')} className="quick-btn">
                    ✏️ Solve problem
                  </button>
                </div>
              </div>
            ) : (
              <>
                {messages.map((message, index) => (
                  <div key={index} className={`chat-message ${message.role}`}>
                    <div className="message-bubble">
                      <ReactMarkdown
                        remarkPlugins={[remarkMath, remarkGfm]}
                        rehypePlugins={[rehypeKatex]}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="chat-message assistant">
                    <div className="message-bubble loading">
                      <div className="typing-indicator">
                        <span></span><span></span><span></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Sources Panel */}
          {sources.length > 0 && (
            <div className="sources-compact">
              <span className="sources-label">📚 Sources:</span>
              {sources.map((note) => (
                <span key={note.id} className="source-tag">
                  {note.title}
                </span>
              ))}
            </div>
          )}

          {/* Controls (Bottom) */}
          <div className="controls-bottom">
            <div className="control-row">
              <select 
                value={model} 
                onChange={(e) => setModel(e.target.value)} 
                className="model-select-compact"
              >
                {AI_MODELS.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>

              <label className="checkbox-compact">
                <input
                  type="checkbox"
                  checked={useRAG}
                  onChange={(e) => setUseRAG(e.target.checked)}
                />
                <span>Use RAG</span>
              </label>

              <label className="checkbox-compact">
                <input
                  type="checkbox"
                  checked={isolateMessage}
                  onChange={(e) => setIsolateMessage(e.target.checked)}
                />
                <span>Isolate Message</span>
              </label>

              {useRAG && (
                <span className="info-text">
                  {selectedFolders.length} folder{selectedFolders.length !== 1 ? 's' : ''} selected
                </span>
              )}
            </div>

            {/* File Upload Preview */}
            {uploadedFile && (
              <div className="file-preview">
                <span className="file-icon">📎</span>
                <span className="file-name">{uploadedFile.name}</span>
                <button onClick={removeUploadedFile} className="file-remove">×</button>
              </div>
            )}

            {/* Input Area */}
            <div className="input-area">
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
                accept="image/*"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className={`attach-button ${!supportsFiles ? 'disabled' : ''}`}
                disabled={!supportsFiles}
                title={supportsFiles ? 'Attach file' : 'File upload only available for Gemini models'}
              >
                📎
              </button>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Message Isabella..."
                className="input-field"
                rows={1}
              />
              <button 
                onClick={handleSend} 
                disabled={!input.trim() || loading} 
                className="send-button-new"
              >
                ▲
              </button>
            </div>
          </div>
        </div>

        {/* Context Panel (Notes) */}
        {showContextPanel && (
          <div className="context-panel-new">
            <h3>📚 Notes Context</h3>
            <p className="panel-description">
              Select folders to include notes in conversation
            </p>
            
            <div className="folders-grid">
              {folders.map((folder) => (
                <label key={folder.id} className="folder-item">
                  <input
                    type="checkbox"
                    checked={selectedFolders.includes(folder.id)}
                    onChange={() => toggleFolder(folder.id)}
                  />
                  <span className="folder-icon" style={{ color: folder.color }}>📁</span>
                  <span className="folder-name">{folder.name}</span>
                </label>
              ))}
            </div>

            {contextNotes.length > 0 && (
              <div className="notes-preview">
                <h4>📄 Available Notes ({contextNotes.length})</h4>
                <div className="notes-list">
                  {contextNotes.slice(0, 10).map((note) => (
                    <div key={note.id} className="note-item">
                      {note.title}
                    </div>
                  ))}
                  {contextNotes.length > 10 && (
                    <div className="note-item more">
                      +{contextNotes.length - 10} more
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Export Modal */}
      {showExportModal && (
        <div className="modal-overlay" onClick={() => setShowExportModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Export Conversation</h2>
            
            <div className="modal-form">
              <label>
                Filename
                <input
                  type="text"
                  value={exportFilename}
                  onChange={(e) => setExportFilename(e.target.value)}
                  placeholder="conversation"
                  className="modal-input"
                />
              </label>

              <label>
                Format
                <select 
                  value={exportFormat} 
                  onChange={(e) => setExportFormat(e.target.value as 'pdf' | 'docx' | 'md')}
                  className="modal-select"
                >
                  <option value="pdf">PDF</option>
                  <option value="docx">DOCX</option>
                  <option value="md">Markdown</option>
                </select>
              </label>
            </div>

            <div className="modal-actions">
              <button 
                onClick={() => setShowExportModal(false)} 
                className="modal-button secondary"
                disabled={exportLoading}
              >
                Cancel
              </button>
              <button 
                onClick={handleExportConversation} 
                className="modal-button primary"
                disabled={exportLoading || !exportFilename.trim()}
              >
                {exportLoading ? 'Exporting...' : 'Export'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAssistant;
