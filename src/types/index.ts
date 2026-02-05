export interface Folder {
  id: number;
  name: string;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: number;
  title: string;
  content: string;
  folder_id: number;
  created_at: string;
  updated_at: string;
  folder?: Folder;
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
  folder_ids?: number[];
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
  { value: 'gpt-4o', label: 'GPT-4o (Best)' },
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini (Fast)' },
  { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet' },
  { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' },
];
