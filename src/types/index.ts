export interface Folder {
  id: string;
  name: string;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: string;
  title: string;
  content: string;
  folder_id?: string;
  created_at: string;
  updated_at: string;
  folder?: Folder;
  model_used?: string;
}

export interface TimetableEntry {
  id: number;
  day: string;
  start_time: string;
  end_time: string;
  subject: string;
  type: string;
  location: string;
  created_at: string;
  updated_at: string;
}

export interface Todo {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  pinned: boolean;
  due_date: string | null;
  created_at: string;
  updated_at: string;
  subtasks: Subtask[];
}

export interface Subtask {
  id: number;
  todo_id: number;
  title: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface AssistantChatRequest {
  message: string;
  conversation_history: ChatMessage[];
  model?: string;
  use_rag?: boolean;
  folder_ids?: string[];
  isolate_message?: boolean;
}

export interface AssistantChatResponse {
  response: string;
  model: string;
  sources?: Note[];
}

// Change this to match your backend return key
export interface Pen2PDFExtractResponse {
  content: string; // Not 'text'
  files_processed: number;
}

export interface Pen2PDFExtractResponse {
  markdown: string;
  images_extracted: number;
  pages_processed: number;
}

export interface Pen2PDFExportRequest {
  markdown: string;
  format: 'pdf' | 'docx' | 'markdown';
  title?: string;
}

export interface NoteGenerateRequest {
  file: File;
  model: string;
  folder_id?: number;
  title?: string;
}

export interface NoteGenerateResponse {
  note: Note;
  processing_time: number;
}

export type Day = 'Monday' | 'Tuesday' | 'Wednesday' | 'Thursday' | 'Friday' | 'Saturday' | 'Sunday';

export const DAYS: Day[] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export const AI_MODELS = [
  // Gemini Models (support file upload)
  { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash', supportsFiles: true },
  { value: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro', supportsFiles: true },
  
  // LongCat Models
  { value: 'longcat-flash-lite', label: 'LongCat-Flash-Lite', supportsFiles: false },
  { value: 'longcat-flash-chat', label: 'LongCat-Flash-Chat', supportsFiles: false },
  { value: 'longcat-flash-thinking', label: 'LongCat-Flash-Thinking', supportsFiles: false },
  { value: 'longcat-flash-thinking-2601', label: 'LongCat-Flash-Thinking-2601', supportsFiles: false },
  
  // GitHub Models
  { value: 'gpt-4o', label: 'gpt-4o', supportsFiles: false },
  { value: 'gpt-4o-mini', label: 'gpt-4o-mini', supportsFiles: false },
  { value: 'gpt-5', label: 'gpt-5', supportsFiles: false },
  { value: 'o1-mini', label: 'o1-mini', supportsFiles: false },
  { value: 'llama-3.2-90b-vision-instruct', label: 'llama-3.2-90b-vision-instruct', supportsFiles: false },
  { value: 'llama-3.2-11b-vision-instruct', label: 'llama-3.2-11b-vision-instruct', supportsFiles: false },
  { value: 'mistral-large-2411', label: 'mistral-large-2411', supportsFiles: false },
  { value: 'mistral-small', label: 'mistral-small', supportsFiles: false },
  { value: 'mistral-nemo', label: 'mistral-nemo', supportsFiles: false },
  { value: 'phi-4', label: 'phi-4', supportsFiles: false },
];
