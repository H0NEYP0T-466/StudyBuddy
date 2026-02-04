import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Pen2PDF from './pages/Pen2PDF';
import NotesLibrary from './pages/NotesLibrary';
import FolderNotes from './pages/FolderNotes';
import NotesGenerator from './pages/NotesGenerator';
import Timetable from './pages/Timetable';
import TodoList from './pages/TodoList';
import AIAssistant from './pages/AIAssistant';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/pen2pdf" element={<Pen2PDF />} />
          <Route path="/notes-library" element={<NotesLibrary />} />
          <Route path="/notes-library/folder/:id" element={<FolderNotes />} />
          <Route path="/notes-generator" element={<NotesGenerator />} />
          <Route path="/timetable" element={<Timetable />} />
          <Route path="/todos" element={<TodoList />} />
          <Route path="/assistant" element={<AIAssistant />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
