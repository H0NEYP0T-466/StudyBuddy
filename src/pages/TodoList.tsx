import { useEffect, useState } from 'react';
import {
  getTodos,
  createTodo,
  updateTodo,
  deleteTodo,
  createSubtask,
  updateSubtask,
  deleteSubtask,
} from '../services/api';
import type { Todo } from '../types';
import './TodoList.css';

const TodoList = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [deletingTodo, setDeletingTodo] = useState<Todo | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    due_date: '',
  });
  const [newSubtask, setNewSubtask] = useState<{ [key: number]: string }>({});

  useEffect(() => {
    loadTodos();
  }, []);

  const loadTodos = async () => {
    try {
      const response = await getTodos();
      setTodos(response.data);
    } catch (error) {
      console.error('Failed to load todos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.title.trim()) return;
    
    try {
      await createTodo({
        title: formData.title,
        description: formData.description,
        due_date: formData.due_date || null,
      });
      setShowModal(false);
      setFormData({ title: '', description: '', due_date: '' });
      loadTodos();
    } catch (error) {
      console.error('Failed to create todo:', error);
    }
  };

  const handleUpdate = async () => {
    if (!editingTodo || !formData.title.trim()) return;
    
    try {
      await updateTodo(editingTodo.id, {
        title: formData.title,
        description: formData.description,
        due_date: formData.due_date || null,
      });
      setEditingTodo(null);
      setShowModal(false);
      setFormData({ title: '', description: '', due_date: '' });
      loadTodos();
    } catch (error) {
      console.error('Failed to update todo:', error);
    }
  };

  const handleDelete = async (id: number) => {
    const todoToDelete = todos.find(t => t.id === id);
    if (todoToDelete) {
      setDeletingTodo(todoToDelete);
    }
  };
  
  const confirmDelete = async () => {
    if (!deletingTodo) return;
    
    try {
      await deleteTodo(deletingTodo.id);
      setDeletingTodo(null);
      loadTodos();
    } catch (error) {
      console.error('Failed to delete todo:', error);
    }
  };

  const toggleComplete = async (todo: Todo) => {
    try {
      await updateTodo(todo.id, { completed: !todo.completed });
      loadTodos();
    } catch (error) {
      console.error('Failed to toggle complete:', error);
    }
  };

  const togglePin = async (todo: Todo) => {
    try {
      await updateTodo(todo.id, { pinned: !todo.pinned });
      loadTodos();
    } catch (error) {
      console.error('Failed to toggle pin:', error);
    }
  };

  const handleAddSubtask = async (todoId: number) => {
    const title = newSubtask[todoId]?.trim();
    if (!title) return;
    
    try {
      await createSubtask(todoId, { title });
      setNewSubtask({ ...newSubtask, [todoId]: '' });
      loadTodos();
    } catch (error) {
      console.error('Failed to create subtask:', error);
    }
  };

  const toggleSubtask = async (todoId: number, subtaskId: number, completed: boolean) => {
    try {
      await updateSubtask(todoId, subtaskId, { completed: !completed });
      loadTodos();
    } catch (error) {
      console.error('Failed to toggle subtask:', error);
    }
  };

  const handleDeleteSubtask = async (todoId: number, subtaskId: number) => {
    try {
      await deleteSubtask(todoId, subtaskId);
      loadTodos();
    } catch (error) {
      console.error('Failed to delete subtask:', error);
    }
  };

  const openEditModal = (todo: Todo) => {
    setEditingTodo(todo);
    setFormData({
      title: todo.title,
      description: todo.description,
      due_date: todo.due_date || '',
    });
    setShowModal(true);
  };

  const activeTodos = todos.filter((t) => !t.completed);
  const completedTodos = todos.filter((t) => t.completed);

  if (loading) {
    return <div className="loading">Loading todos...</div>;
  }

  return (
    <div className="todo-list-page">
      <div className="todo-header">
        <div>
          <h1>✓ Todo List</h1>
          <p className="subtitle">
            {activeTodos.length} active, {completedTodos.length} completed
          </p>
        </div>
        <button
          onClick={() => {
            setEditingTodo(null);
            setFormData({ title: '', description: '', due_date: '' });
            setShowModal(true);
          }}
          className="create-todo-button"
        >
          ➕ New Todo
        </button>
      </div>

      <div className="todos-container">
        {activeTodos.length > 0 && (
          <div className="todos-section">
            <h3>Active Tasks</h3>
            {activeTodos
              .sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0))
              .map((todo) => (
                <div key={todo.id} className={`todo-card ${todo.pinned ? 'pinned' : ''}`}>
                  <div className="todo-header-row">
                    <div className="todo-checkbox-container">
                      <input
                        type="checkbox"
                        checked={todo.completed}
                        onChange={() => toggleComplete(todo)}
                        className="todo-checkbox"
                      />
                      <h3 className="todo-title">{todo.title}</h3>
                    </div>
                    <div className="todo-actions">
                      <button onClick={() => togglePin(todo)} className="icon-button">
                        {todo.pinned ? '📌' : '📍'}
                      </button>
                      <button onClick={() => openEditModal(todo)} className="icon-button">
                        ✏️
                      </button>
                      <button onClick={() => handleDelete(todo.id)} className="icon-button delete">
                        🗑️
                      </button>
                    </div>
                  </div>

                  {todo.description && (
                    <p className="todo-description">{todo.description}</p>
                  )}

                  {todo.due_date && (
                    <div className="todo-due-date">
                      📅 Due: {new Date(todo.due_date).toLocaleDateString()}
                    </div>
                  )}

                  {todo.subtasks.length > 0 && (
                    <div className="subtasks-list">
                      {todo.subtasks.map((subtask) => (
                        <div key={subtask.id} className="subtask-item">
                          <input
                            type="checkbox"
                            checked={subtask.completed}
                            onChange={() => toggleSubtask(todo.id, subtask.id, subtask.completed)}
                            className="subtask-checkbox"
                          />
                          <span className={`subtask-title ${subtask.completed ? 'completed' : ''}`}>
                            {subtask.title}
                          </span>
                          <button
                            onClick={() => handleDeleteSubtask(todo.id, subtask.id)}
                            className="subtask-delete"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="add-subtask">
                    <input
                      type="text"
                      value={newSubtask[todo.id] || ''}
                      onChange={(e) => setNewSubtask({ ...newSubtask, [todo.id]: e.target.value })}
                      onKeyPress={(e) => e.key === 'Enter' && handleAddSubtask(todo.id)}
                      placeholder="Add subtask..."
                      className="subtask-input"
                    />
                    <button onClick={() => handleAddSubtask(todo.id)} className="add-subtask-button">
                      +
                    </button>
                  </div>
                </div>
              ))}
          </div>
        )}

        {completedTodos.length > 0 && (
          <div className="todos-section">
            <h3>Completed</h3>
            {completedTodos.map((todo) => (
              <div key={todo.id} className="todo-card completed">
                <div className="todo-header-row">
                  <div className="todo-checkbox-container">
                    <input
                      type="checkbox"
                      checked={todo.completed}
                      onChange={() => toggleComplete(todo)}
                      className="todo-checkbox"
                    />
                    <h3 className="todo-title">{todo.title}</h3>
                  </div>
                  <button onClick={() => handleDelete(todo.id)} className="icon-button delete">
                    🗑️
                  </button>
                </div>
                
                {todo.description && (
                  <p className="todo-description">{todo.description}</p>
                )}

                {todo.subtasks.length > 0 && (
                  <div className="subtasks-list">
                    {todo.subtasks.map((subtask) => (
                      <div key={subtask.id} className="subtask-item">
                        <input
                          type="checkbox"
                          checked={subtask.completed}
                          onChange={() => toggleSubtask(todo.id, subtask.id, subtask.completed)}
                          className="subtask-checkbox"
                        />
                        <span className={`subtask-title ${subtask.completed ? 'completed' : ''}`}>
                          {subtask.title}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {todos.length === 0 && (
          <div className="empty-todos">
            <span className="empty-icon">✓</span>
            <h3>No todos yet</h3>
            <p>Create a todo to get started</p>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingTodo ? 'Edit Todo' : 'Create Todo'}</h2>
            
            <div className="form-group">
              <label>Title</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Enter todo title"
                autoFocus
              />
            </div>

            <div className="form-group">
              <label>Description (Optional)</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Add details..."
                rows={4}
              />
            </div>

            <div className="form-group">
              <label>Due Date (Optional)</label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              />
            </div>

            <div className="modal-actions">
              <button onClick={() => setShowModal(false)} className="cancel-button">
                Cancel
              </button>
              <button
                onClick={editingTodo ? handleUpdate : handleCreate}
                className="submit-button"
                disabled={!formData.title.trim()}
              >
                {editingTodo ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {deletingTodo && (
        <div className="modal-overlay" onClick={() => setDeletingTodo(null)}>
          <div className="modal confirm-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Delete Todo?</h2>
            <p className="confirm-message">
              Are you sure you want to delete <strong>{deletingTodo.title}</strong>? This action cannot be undone.
            </p>
            <div className="modal-actions">
              <button onClick={() => setDeletingTodo(null)} className="cancel-button">
                Cancel
              </button>
              <button onClick={confirmDelete} className="delete-button">
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TodoList;
