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
export const getFolders = () => api.get<Folder[]>('/folders');
export const createFolder = (data: { name: string; color: string }) => 
  api.post<Folder>('/folders', data);
export const updateFolder = (id: number, data: { name?: string; color?: string }) => 
  api.put<Folder>(`/folders/${id}`, data);
export const deleteFolder = (id: number) => api.delete(`/folders/${id}`);

// Notes
export const getNotes = (folderId?: number) => 
  api.get<Note[]>('/notes', { params: { folder_id: folderId } });
export const getNoteById = (id: number) => api.get<Note>(`/notes/${id}`);
export const createNote = (data: { title: string; content: string; folder_id?: number }) => 
  api.post<Note>('/notes', data);
export const updateNote = (id: number, data: { title?: string; content?: string; folder_id?: number }) => 
  api.put<Note>(`/notes/${id}`, data);
export const deleteNote = (id: number) => api.delete(`/notes/${id}`);
export const generateNotes = (formData: FormData) => 
  api.post<NoteGenerateResponse>('/notes/generate', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
export const searchNotes = (query: string) => 
  api.get<Note[]>('/notes/search', { params: { q: query } });

// Timetable
export const getTimetable = () => api.get<TimetableEntry[]>('/timetable');
export const createTimetableEntry = (data: {
  day: string;
  start_time: string;
  end_time: string;
  subject: string;
  type: string;
  location: string;
}) => api.post<TimetableEntry>('/timetable', data);
export const updateTimetableEntry = (id: number, data: Partial<TimetableEntry>) => 
  api.put<TimetableEntry>(`/timetable/${id}`, data);
export const deleteTimetableEntry = (id: number) => api.delete(`/timetable/${id}`);
export const importTimetable = (formData: FormData) => 
  api.post<{ message: string; entries_created: number }>('/timetable/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

// Todos
export const getTodos = () => api.get<Todo[]>('/todos');
export const createTodo = (data: { 
  title: string; 
  description?: string; 
  due_date?: string | null;
}) => api.post<Todo>('/todos', data);
export const updateTodo = (id: number, data: Partial<Todo>) => 
  api.put<Todo>(`/todos/${id}`, data);
export const deleteTodo = (id: number) => api.delete(`/todos/${id}`);

// Subtasks
export const createSubtask = (todoId: number, data: { title: string }) => 
  api.post<Subtask>(`/todos/${todoId}/subtasks`, data);
export const updateSubtask = (todoId: number, subtaskId: number, data: { title?: string; completed?: boolean }) => 
  api.put<Subtask>(`/todos/${todoId}/subtasks/${subtaskId}`, data);
export const deleteSubtask = (todoId: number, subtaskId: number) => 
  api.delete(`/todos/${todoId}/subtasks/${subtaskId}`);

// Assistant
export const chatWithAssistant = (data: AssistantChatRequest) => 
  api.post<AssistantChatResponse>('/assistant/chat', data);

// Pen2PDF
export const extractPen2PDF = (formData: FormData) => 
  api.post<Pen2PDFExtractResponse>('/api/pen2pdf/extract', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const exportPen2PDF = (data: { 
  markdown: string; 
  format: 'pdf' | 'docx' | 'markdown';
  title?: string;
}) => api.post('/pen2pdf/export', data, {
  responseType: 'blob',
});

export default api;
