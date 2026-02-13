import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/pen2pdf', label: 'Pen2PDF', icon: '📝' },
    { path: '/notes-library', label: 'Notes', icon: '📚' },
    { path: '/notes-generator', label: 'Generate', icon: '✨' },
    { path: '/timetable', label: 'Timetable', icon: '📅' },
    { path: '/todos', label: 'Todos', icon: '✓' },
    { path: '/assistant', label: 'Isabella', icon: '🤖' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h2>StudyBuddy</h2>
      </div>
      <div className="navbar-links">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
};

export default Navbar;
