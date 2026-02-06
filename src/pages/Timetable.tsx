import { useEffect, useState, useRef } from 'react';
import {
  getTimetable,
  createTimetableEntry,
  updateTimetableEntry,
  deleteTimetableEntry,
  importTimetable,
} from '../services/api';
import type { TimetableEntry, Day } from '../types';
import { DAYS } from '../types';
import './Timetable.css';

const TIME_SLOTS = Array.from({ length: 13 }, (_, i) => {
  const hour = i + 8;
  return `${hour.toString().padStart(2, '0')}:00`;
});

const Timetable = () => {
  const [entries, setEntries] = useState<TimetableEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingEntry, setEditingEntry] = useState<TimetableEntry | null>(null);
  const [deletingEntry, setDeletingEntry] = useState<TimetableEntry | null>(null);
  const [formData, setFormData] = useState({
    day: 'Monday' as Day,
    start_time: '09:00',
    end_time: '10:00',
    subject: '',
    type: 'Lecture',
    location: '',
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadTimetable();
  }, []);

  const loadTimetable = async () => {
    try {
      const response = await getTimetable();
      setEntries(response.data);
    } catch (error) {
      console.error('Failed to load timetable:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.subject.trim()) return;
    
    try {
      await createTimetableEntry(formData);
      setShowModal(false);
      resetForm();
      loadTimetable();
    } catch (error) {
      console.error('Failed to create entry:', error);
    }
  };

  const handleUpdate = async () => {
    if (!editingEntry || !formData.subject.trim()) return;
    
    try {
      await updateTimetableEntry(editingEntry.id, formData);
      setEditingEntry(null);
      setShowModal(false);
      resetForm();
      loadTimetable();
    } catch (error) {
      console.error('Failed to update entry:', error);
    }
  };

  const handleDelete = async (id: number) => {
    const entryToDelete = entries.find(e => e.id === id);
    if (entryToDelete) {
      setDeletingEntry(entryToDelete);
    }
  };

  const confirmDelete = async () => {
    if (!deletingEntry) return;
    
    try {
      await deleteTimetableEntry(deletingEntry.id);
      setDeletingEntry(null);
      loadTimetable();
    } catch (error) {
      console.error('Failed to delete entry:', error);
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      await importTimetable(formData);
      alert('Timetable imported successfully!');
      loadTimetable();
    } catch (error) {
      console.error('Failed to import timetable:', error);
      alert('Failed to import timetable. Please check the CSV format.');
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const openEditModal = (entry: TimetableEntry) => {
    setEditingEntry(entry);
    setFormData({
      day: entry.day as Day,
      start_time: entry.start_time,
      end_time: entry.end_time,
      subject: entry.subject,
      type: entry.type,
      location: entry.location,
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      day: 'Monday',
      start_time: '09:00',
      end_time: '10:00',
      subject: '',
      type: 'Lecture',
      location: '',
    });
    setEditingEntry(null);
  };

  const getEntriesForDayAndTime = (day: Day, time: string) => {
    return entries.filter((entry) => {
      return entry.day === day && entry.start_time <= time && entry.end_time > time;
    });
  };

  if (loading) {
    return <div className="loading">Loading timetable...</div>;
  }

  return (
    <div className="timetable-page">
      <div className="timetable-header">
        <div>
          <h1>📅 Timetable</h1>
          <p className="subtitle">Manage your weekly schedule</p>
        </div>
        <div className="header-actions">
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleImport}
            style={{ display: 'none' }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="import-button"
          >
            📤 Import CSV
          </button>
          <button
            onClick={() => {
              resetForm();
              setShowModal(true);
            }}
            className="add-button"
          >
            ➕ Add Entry
          </button>
        </div>
      </div>

      <div className="timetable-container">
        <div className="timetable-grid">
          <div className="timetable-corner-cell"></div>
          {TIME_SLOTS.map((time) => (
            <div key={`time-${time}`} className="timetable-header-cell time-header">
              {time}
            </div>
          ))}

          {DAYS.map((day) => (
            <>
              <div key={`day-${day}`} className="timetable-header-cell day-header">
                {day}
              </div>
              {TIME_SLOTS.map((time) => {
                const dayEntries = getEntriesForDayAndTime(day, time);
                return (
                  <div key={`${day}-${time}`} className="timetable-cell">
                    {dayEntries.map((entry) => (
                      <div
                        key={entry.id}
                        className="timetable-entry"
                        onClick={() => openEditModal(entry)}
                      >
                        <div className="entry-subject">{entry.subject}</div>
                        <div className="entry-time">
                          {entry.start_time} - {entry.end_time}
                        </div>
                        <div className="entry-details">
                          {entry.type} • {entry.location}
                        </div>
                      </div>
                    ))}
                  </div>
                );
              })}
            </>
          ))}
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => {
          setShowModal(false);
          resetForm();
        }}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingEntry ? 'Edit Entry' : 'Add Entry'}</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label>Day</label>
                <select
                  value={formData.day}
                  onChange={(e) => setFormData({ ...formData, day: e.target.value as Day })}
                >
                  {DAYS.map((day) => (
                    <option key={day} value={day}>{day}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Subject</label>
                <input
                  type="text"
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  placeholder="e.g., Mathematics"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Start Time</label>
                <input
                  type="time"
                  value={formData.start_time}
                  onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>End Time</label>
                <input
                  type="time"
                  value={formData.end_time}
                  onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Type</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                >
                  <option value="Lecture">Lecture</option>
                  <option value="Tutorial">Tutorial</option>
                  <option value="Lab">Lab</option>
                  <option value="Seminar">Seminar</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="form-group">
                <label>Location</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="e.g., Room 101"
                />
              </div>
            </div>

            <div className="modal-actions">
              {editingEntry && (
                <button
                  onClick={() => handleDelete(editingEntry.id)}
                  className="delete-button"
                >
                  Delete
                </button>
              )}
              <div className="modal-actions-right">
                <button
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="cancel-button"
                >
                  Cancel
                </button>
                <button
                  onClick={editingEntry ? handleUpdate : handleCreate}
                  className="submit-button"
                  disabled={!formData.subject.trim()}
                >
                  {editingEntry ? 'Update' : 'Create'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {deletingEntry && (
        <div className="modal-overlay" onClick={() => setDeletingEntry(null)}>
          <div className="modal confirm-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Delete Timetable Entry?</h2>
            <p className="confirm-message">
              Are you sure you want to delete <strong>{deletingEntry.subject}</strong> ({deletingEntry.day} {deletingEntry.start_time})? This action cannot be undone.
            </p>
            <div className="modal-actions">
              <button onClick={() => setDeletingEntry(null)} className="cancel-button">
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

export default Timetable;
