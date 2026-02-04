import { useState, useEffect } from 'react';
import './WeekCounter.css';

const WeekCounter = () => {
  const [weekNumber, setWeekNumber] = useState(1);
  const [semesterStart, setSemesterStart] = useState<string>('');
  const [isEditing, setIsEditing] = useState(false);

  const calculateWeek = (startDate: string) => {
    const start = new Date(startDate);
    const today = new Date();
    const diff = Math.floor((today.getTime() - start.getTime()) / (1000 * 60 * 60 * 24 * 7));
    setWeekNumber(Math.max(1, diff + 1));
  };

  useEffect(() => {
    const stored = localStorage.getItem('semesterStart');
    if (stored) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSemesterStart(stored);
    }
  }, []);

  useEffect(() => {
    if (semesterStart) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      calculateWeek(semesterStart);
    }
  }, [semesterStart]);

  const handleSave = () => {
    localStorage.setItem('semesterStart', semesterStart);
    setIsEditing(false);
  };

  if (!semesterStart && !isEditing) {
    return (
      <button className="week-counter-setup" onClick={() => setIsEditing(true)}>
        Set Semester Start
      </button>
    );
  }

  if (isEditing) {
    return (
      <div className="week-counter-edit">
        <input
          type="date"
          value={semesterStart}
          onChange={(e) => setSemesterStart(e.target.value)}
          className="week-counter-input"
        />
        <button onClick={handleSave} className="week-counter-save">
          Save
        </button>
      </div>
    );
  }

  return (
    <div className="week-counter" onClick={() => setIsEditing(true)}>
      <span className="week-label">Week</span>
      <span className="week-number">{weekNumber}</span>
    </div>
  );
};

export default WeekCounter;
