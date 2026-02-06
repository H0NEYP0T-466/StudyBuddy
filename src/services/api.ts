import axios from 'axios';
import type {
  Folder,
  Note,
  TimetableEntry,
  Todo,
  Subtask,
  AssistantChatRequest,
  AssistantChatResponse,
  Pen2PDFExtractResponse,
  NoteGenerateResponse,
} from '../types';

const API_BASE_URL = 'http://localhost:8003';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Folders
export const getFolders = () => api.get<Folder[]>('/api/folders');
export const createFolder = (data: { name: string; color: string }) => 
  api.post<Folder>('/api/folders', data);
export const updateFolder = (id: number, data: { name?: string; color?: string }) => 
  api.put<Folder>(`/api/folders/${id}`, data);
export const deleteFolder = (id: number) => api.delete(`/api/folders/${id}`);

// Notes
export const getNotes = (folderId?: number) => 
  api.get<Note[]>('/api/notes', { params: { folder_id: folderId } });
export const getNoteById = (id: number) => api.get<Note>(`/api/notes/${id}`);
export const createNote = (data: { title: string; content: string; folder_id?: number }) => 
  api.post<Note>('/api/notes', data);
export const updateNote = (id: number, data: { title?: string; content?: string; folder_id?: number }) => 
  api.put<Note>(`/api/notes/${id}`, data);
export const deleteNote = (id: number) => api.delete(`/api/notes/${id}`);
export const generateNotes = (formData: FormData) => 
  api.post<NoteGenerateResponse>('/api/notes/generate', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
export const searchNotes = (query: string) => 
  api.get<Note[]>('/api/notes/search', { params: { q: query } });

// Timetable
export const getTimetable = () => api.get<TimetableEntry[]>('/api/timetable');
export const createTimetableEntry = (data: {
  day: string;
  start_time: string;
  end_time: string;
  subject: string;
  type: string;
  location: string;
}) => api.post<TimetableEntry>('/api/timetable', data);
export const updateTimetableEntry = (id: number, data: Partial<TimetableEntry>) => 
  api.put<TimetableEntry>(`/api/timetable/${id}`, data);
export const deleteTimetableEntry = (id: number) => api.delete(`/api/timetable/${id}`);
export const importTimetable = (formData: FormData) => 
  api.post<{ message: string; entries_created: number }>('/api/timetable/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

// Todos
export const getTodos = () => api.get<Todo[]>('/api/todos');
export const createTodo = (data: { 
  title: string; 
  description?: string; 
  due_date?: string | null;
}) => api.post<Todo>('/api/todos', data);
export const updateTodo = (id: number, data: Partial<Todo>) => 
  api.put<Todo>(`/api/todos/${id}`, data);
export const deleteTodo = (id: number) => api.delete(`/api/todos/${id}`);

// Subtasks
export const createSubtask = (todoId: number, data: { title: string }) => 
  api.post<Subtask>(`/api/todos/${todoId}/subtasks`, data);
export const updateSubtask = (todoId: number, subtaskId: number, data: { title?: string; completed?: boolean }) => 
  api.put<Subtask>(`/api/todos/${todoId}/subtasks/${subtaskId}`, data);
export const deleteSubtask = (todoId: number, subtaskId: number) => 
  api.delete(`/api/todos/${todoId}/subtasks/${subtaskId}`);

// Assistant
export const chatWithAssistant = (data: AssistantChatRequest) => {
  const formData = new FormData();
  formData.append('message', data.message);
  formData.append('model', data.model || 'gemini-2.5-flash');
  formData.append('chat_history', JSON.stringify(data.conversation_history));
  formData.append('use_rag', String(data.use_rag ?? false));
  formData.append('isolate_message', String(data.isolate_message ?? false));
  
  // Add folder context notes if provided
  if (data.folder_ids && data.folder_ids.length > 0) {
    formData.append('folder_ids', JSON.stringify(data.folder_ids));
  }
  
  return api.post<AssistantChatResponse>('/api/assistant/chat', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Pen2PDF
export const extractPen2PDF = (formData: FormData) => 
  api.post<Pen2PDFExtractResponse>('/api/pen2pdf/extract', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const exportPen2PDF = (formData: FormData) => api.post('/api/pen2pdf/export', formData, {
  responseType: 'blob',
  headers: { 'Content-Type': 'multipart/form-data' },
});

export default api;
