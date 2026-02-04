import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getTodos, getFolders, getTimetable } from '../services/api';
import type { Todo, Folder, TimetableEntry } from '../types';
import WeekCounter from '../components/WeekCounter';
import './Dashboard.css';

const Dashboard = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [timetable, setTimetable] = useState<TimetableEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [todosRes, foldersRes, timetableRes] = await Promise.all([
        getTodos(),
        getFolders(),
        getTimetable(),
      ]);
      setTodos(todosRes.data);
      setFolders(foldersRes.data);
      setTimetable(timetableRes.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const activeTodos = todos.filter((t) => !t.completed);
  const pinnedTodos = todos.filter((t) => t.pinned && !t.completed);

  const today = new Date().toLocaleDateString('en-US', { weekday: 'long' });
  const todayClasses = timetable.filter((entry) => entry.day === today);

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <WeekCounter />
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-header">
            <h3>📅 Today's Schedule</h3>
            <Link to="/timetable" className="card-link">View All →</Link>
          </div>
          <div className="card-content">
            {todayClasses.length === 0 ? (
              <p className="empty-state">No classes today</p>
            ) : (
              <div className="schedule-list">
                {todayClasses.map((entry) => (
                  <div key={entry.id} className="schedule-item">
                    <div className="schedule-time">
                      {entry.start_time} - {entry.end_time}
                    </div>
                    <div className="schedule-details">
                      <div className="schedule-subject">{entry.subject}</div>
                      <div className="schedule-meta">
                        {entry.type} • {entry.location}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>✓ Active Todos</h3>
            <Link to="/todos" className="card-link">View All →</Link>
          </div>
          <div className="card-content">
            {activeTodos.length === 0 ? (
              <p className="empty-state">No active todos</p>
            ) : (
              <div className="todo-list">
                {pinnedTodos.slice(0, 3).map((todo) => (
                  <div key={todo.id} className="todo-item pinned">
                    <span className="todo-pin">📌</span>
                    <span className="todo-title">{todo.title}</span>
                  </div>
                ))}
                {activeTodos.slice(0, 5).map((todo) => (
                  !todo.pinned && (
                    <div key={todo.id} className="todo-item">
                      <span className="todo-title">{todo.title}</span>
                    </div>
                  )
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>📚 Notes Library</h3>
            <Link to="/notes-library" className="card-link">View All →</Link>
          </div>
          <div className="card-content">
            {folders.length === 0 ? (
              <p className="empty-state">No folders created</p>
            ) : (
              <div className="folders-grid">
                {folders.slice(0, 6).map((folder) => (
                  <Link
                    key={folder.id}
                    to={`/notes-library/folder/${folder.id}`}
                    className="folder-mini"
                    style={{ borderLeft: `3px solid ${folder.color}` }}
                  >
                    <span className="folder-icon">📁</span>
                    <span className="folder-name">{folder.name}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="dashboard-card quick-actions">
          <div className="card-header">
            <h3>⚡ Quick Actions</h3>
          </div>
          <div className="card-content">
            <div className="actions-grid">
              <Link to="/pen2pdf" className="action-button">
                <span className="action-icon">📝</span>
                <span className="action-label">Extract Document</span>
              </Link>
              <Link to="/notes-generator" className="action-button">
                <span className="action-icon">✨</span>
                <span className="action-label">Generate Notes</span>
              </Link>
              <Link to="/assistant" className="action-button">
                <span className="action-icon">🤖</span>
                <span className="action-label">Ask Isabella</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
