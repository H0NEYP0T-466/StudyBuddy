# 🤝 Contributing to StudyBuddy

Thank you for your interest in contributing to StudyBuddy! This document provides guidelines for contributing to the project.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Branch Naming Conventions](#branch-naming-conventions)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)

## 🚀 Getting Started

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/YOUR-USERNAME/StudyBuddy.git
cd StudyBuddy
```

3. Add the upstream repository:
```bash
git remote add upstream https://github.com/H0NEYP0T-466/StudyBuddy.git
```

4. Keep your fork in sync:
```bash
git fetch upstream
git checkout main
git merge upstream/main
```

## 🛠 Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Start backend server:
```bash
cd ..
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8003 --reload
```

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Run linter:
```bash
npm run lint
```

## 🌿 Branch Naming Conventions

Use the following prefixes for your branch names:

- `feat/` - New features (e.g., `feat/add-calendar-view`)
- `fix/` - Bug fixes (e.g., `fix/timetable-export-bug`)
- `docs/` - Documentation changes (e.g., `docs/update-api-guide`)
- `refactor/` - Code refactoring (e.g., `refactor/simplify-rag-service`)
- `test/` - Test additions or changes (e.g., `test/add-notes-api-tests`)
- `chore/` - Maintenance tasks (e.g., `chore/update-dependencies`)
- `perf/` - Performance improvements (e.g., `perf/optimize-vector-search`)
- `style/` - Code style changes (e.g., `style/format-components`)

## 💬 Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no code change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions or modifications
- `chore`: Build process or auxiliary tool changes

### Examples
```
feat(notes): add markdown export option

Add ability to export notes as plain markdown files.
Includes download trigger and file generation.

Closes #123
```

```
fix(timetable): resolve CSV import parsing error

Fix bug where CSV files with empty cells caused import to fail.
Now handles empty cells gracefully.
```

## 🔄 Pull Request Process

1. **Create a feature branch** from `main`:
```bash
git checkout -b feat/your-feature-name
```

2. **Make your changes** following the code style guidelines

3. **Test your changes** thoroughly:
```bash
# Frontend
npm run lint
npm run build

# Backend (if applicable)
# Run any existing tests
```

4. **Commit your changes** using conventional commit messages

5. **Push to your fork**:
```bash
git push origin feat/your-feature-name
```

6. **Create a Pull Request**:
   - Use the PR template
   - Link related issues
   - Provide a clear description
   - Add screenshots for UI changes
   - Wait for review

7. **Address review feedback**:
   - Make requested changes
   - Push additional commits
   - Request re-review when ready

8. **Merge**: Once approved, your PR will be merged by a maintainer

## 📝 Code Style Guidelines

### TypeScript/React

- Follow the existing ESLint configuration (`eslint.config.js`)
- Use functional components with hooks
- Use TypeScript interfaces for props and types
- Keep components focused and single-purpose
- Use CSS modules for component styling
- Follow existing naming conventions

#### Example Component Structure
```tsx
import React from 'react';
import styles from './MyComponent.module.css';

interface MyComponentProps {
  title: string;
  onAction: () => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, onAction }) => {
  return (
    <div className={styles.container}>
      <h2>{title}</h2>
      <button onClick={onAction}>Action</button>
    </div>
  );
};
```

### Python/FastAPI

- Follow PEP 8 style guide
- Use type hints for function parameters and returns
- Keep functions focused and well-documented
- Use async/await for database operations
- Follow existing project structure

#### Example Endpoint
```python
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/items", response_model=List[ItemResponse])
async def get_items() -> List[ItemResponse]:
    """
    Retrieve all items from the database.
    
    Returns:
        List of items
    """
    try:
        items = await db.items.find().to_list(None)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## ✅ Testing Requirements

### Frontend Testing
- Manually test your changes in the browser
- Ensure no console errors or warnings
- Test responsive design on different screen sizes
- Verify accessibility (keyboard navigation, screen readers)

### Backend Testing
- Test API endpoints using the Swagger UI (`/docs`)
- Verify database operations don't cause errors
- Test error handling with invalid inputs
- Check API responses match expected schemas

### Integration Testing
- Test the full workflow from frontend to backend
- Verify file uploads work correctly
- Test AI model integrations if applicable
- Ensure RAG system functions properly

## 🐛 Reporting Bugs

If you find a bug, please create an issue using the bug report template. Include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, browser, versions)

## 💡 Suggesting Features

Feature suggestions are welcome! Please:
- Create an issue using the feature request template
- Explain the problem it solves
- Describe your proposed solution
- Consider alternatives
- Be open to discussion

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)

## 🙏 Thank You!

Your contributions help make StudyBuddy better for everyone. We appreciate your time and effort!

---

Questions? Feel free to open a discussion or reach out to the maintainers.
