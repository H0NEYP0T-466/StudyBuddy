import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { chatWithAssistant, getFolders, getNotes } from '../services/api';
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
  const [folders, setFolders] = useState<Folder[]>([]);
  const [selectedFolders, setSelectedFolders] = useState<number[]>([]);
  const [showContextPanel, setShowContextPanel] = useState(false);
  const [contextNotes, setContextNotes] = useState<Note[]>([]);
  const [sources, setSources] = useState<Note[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadFolders();
  }, []);

  useEffect(() => {
    if (selectedFolders.length > 0) {
      loadContextNotes();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedFolders]);

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

  const loadContextNotes = async () => {
    try {
      const notesPromises = selectedFolders.map((folderId) => getNotes(folderId));
      const notesResponses = await Promise.all(notesPromises);
      const allNotes = notesResponses.flatMap((res) => res.data);
      setContextNotes(allNotes);
    } catch (error) {
      console.error('Failed to load context notes:', error);
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
      const response = await chatWithAssistant({
        message: input,
        conversation_history: messages,
        model,
        use_rag: useRAG,
        folder_ids: useRAG ? selectedFolders : undefined,
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
    if (confirm('Clear chat history?')) {
      setMessages([]);
      setSources([]);
    }
  };

  return (
    <div className="ai-assistant">
      <div className="assistant-header">
        <div>
          <h1>🤖 Isabella AI Assistant</h1>
          <p className="subtitle">Your personal study assistant with RAG support</p>
        </div>
        <div className="header-controls">
          <button onClick={clearChat} className="clear-button">
            🗑️ Clear
          </button>
          <button
            onClick={() => setShowContextPanel(!showContextPanel)}
            className={`context-button ${showContextPanel ? 'active' : ''}`}
          >
            📚 Context
          </button>
        </div>
      </div>

      <div className="assistant-container">
        <div className="assistant-main">
          <div className="assistant-settings">
            <div className="setting-group">
              <label>Model</label>
              <select value={model} onChange={(e) => setModel(e.target.value)} className="model-select">
                {AI_MODELS.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="setting-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={useRAG}
                  onChange={(e) => setUseRAG(e.target.checked)}
                />
                <span>Use RAG (Search Notes)</span>
              </label>
            </div>

            {useRAG && (
              <div className="setting-group">
                <label>Selected Folders: {selectedFolders.length}</label>
              </div>
            )}
          </div>

          <div className="chat-container">
            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="empty-chat">
                  <span className="empty-icon">🤖</span>
                  <h3>Hi! I'm Isabella</h3>
                  <p>Ask me anything about your notes or any study-related questions!</p>
                  <div className="suggestions">
                    <button onClick={() => setInput('Summarize my recent notes')} className="suggestion">
                      Summarize my notes
                    </button>
                    <button onClick={() => setInput('Explain quantum mechanics')} className="suggestion">
                      Explain a concept
                    </button>
                    <button onClick={() => setInput('Help me with this problem')} className="suggestion">
                      Solve a problem
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((message, index) => (
                    <div key={index} className={`message ${message.role}`}>
                      <div className="message-avatar">
                        {message.role === 'user' ? '👤' : '🤖'}
                      </div>
                      <div className="message-content">
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
                    <div className="message assistant">
                      <div className="message-avatar">🤖</div>
                      <div className="message-content loading-dots">
                        <span></span><span></span><span></span>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {sources.length > 0 && (
              <div className="sources-panel">
                <h4>📚 Sources Used</h4>
                <div className="sources-list">
                  {sources.map((note) => (
                    <div key={note.id} className="source-item">
                      <span className="source-icon">📄</span>
                      <span className="source-title">{note.title}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="input-container">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask Isabella anything... (Shift+Enter for new line)"
                className="chat-input"
                rows={2}
              />
              <button onClick={handleSend} disabled={!input.trim() || loading} className="send-button">
                ▲
              </button>
            </div>
          </div>
        </div>

        {showContextPanel && (
          <div className="context-panel">
            <h3>RAG Context</h3>
            <p className="context-description">
              Select folders to give Isabella context from your notes
            </p>
            
            <div className="folders-list">
              {folders.map((folder) => (
                <label key={folder.id} className="folder-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedFolders.includes(folder.id)}
                    onChange={() => toggleFolder(folder.id)}
                  />
                  <span style={{ color: folder.color }}>📁</span>
                  <span>{folder.name}</span>
                </label>
              ))}
            </div>

            {contextNotes.length > 0 && (
              <div className="context-info">
                <h4>📄 {contextNotes.length} notes available</h4>
                <div className="context-notes-list">
                  {contextNotes.slice(0, 10).map((note) => (
                    <div key={note.id} className="context-note-item">
                      {note.title}
                    </div>
                  ))}
                  {contextNotes.length > 10 && (
                    <div className="context-note-item muted">
                      +{contextNotes.length - 10} more
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AIAssistant;
