# Tasks + Comments Application

This project implements a task management system with comments functionality, built with a Python Flask backend and a React frontend, as per the Associate Software Engineer (Python React) assessment requirements.

## Project Overview

The application enables users to perform CRUD (Create, Read, Update, Delete) operations on tasks and their associated comments. It prioritizes clean architecture, maintainability, and robust error handling. The backend provides RESTful APIs, while the frontend offers a responsive UI to interact with these APIs.

## Folder Structure

- `backend/`: Flask application with SQLite database, SQLAlchemy models, and Pytest suite.
- `frontend/`: Create React App with function components, hooks, and a proxy to the backend.

## Requirements

### Backend
- Python 3.8+
- Flask, SQLAlchemy, Pytest

### Frontend
- Node.js 16+
- React 18, Create React App

## Setup Instructions

### Backend
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the Flask app:
   ```bash
   python backend/app.py
   ```
4. Verify the server is running:
   ```bash
   curl http://127.0.0.1:5000/health
   ```
   Expected output: `{"status":"ok"}`

### Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```
   The app runs at `http://localhost:3000`, with API requests proxied to `http://127.0.0.1:5000`.

## API Endpoints

### Tasks
- `GET /api/tasks`: List all tasks
- `POST /api/tasks`: Create a task
- `GET /api/tasks/:id`: Get a task
- `PUT /api/tasks/:id`: Update a task
- `DELETE /api/tasks/:id`: Delete a task

### Comments
- `GET /api/tasks/:taskId/comments`: List comments for a task
- `POST /api/tasks/:taskId/comments`: Create a comment
- `PUT /api/tasks/:taskId/comments/:commentId`: Update a comment
- `DELETE /api/tasks/:taskId/comments/:commentId`: Delete a comment

## Running Tests

### Backend Tests
Run the Pytest suite:
```bash
cd backend
pytest
```
Tests cover task and comment CRUD operations, validation, and error cases (e.g., 404s).

## Key Features

### Backend
- Flask app factory pattern for testability.
- SQLAlchemy models with `TimestampMixin` for consistent timestamps.
- Cascade deletes for comments when tasks are removed.
- JSON error responses (400/404/500) with logging.
- SQLite database in Flask instance folder, with `DATABASE_URL` override support.

### Frontend
- React function components with hooks for state management.
- `api.js` layer for clean API calls and error handling.
- Proxy setup to avoid CORS issues.
- Responsive UI with task list, task details, and comment management.
- Validation feedback and error messaging.

## Troubleshooting

- **Proxy error (ECONNREFUSED)**: Ensure the backend is running on `http://127.0.0.1:5000` and the health endpoint returns `{"status":"ok"}`.
- **Database issues**: The SQLite DB is in the Flask instance folder. Delete it to reset or restart the app to recreate it.
- **Port conflicts**: Ensure no other process is using port 5000 (backend) or 3000 (frontend).

## Next Steps

- **Frontend**: Implement pagination, search, optimistic updates, and component tests.
- **Backend**: Add authentication, pagination, filtering, CORS, and Dockerization.
- **Deployment**: Containerize with Docker Compose or deploy to a PaaS.

## Assumptions

- SQLite is sufficient for the assessment; a production app might use PostgreSQL.
- Authentication was not implemented, as it wasn’t specified.
- Basic styling is used for clarity; a production app would include a design system (e.g., Tailwind CSS).

## Video Walkthrough

A 6–7 minute video is provided, covering:
- Project architecture and key decisions.
- Running the backend and frontend.
- End-to-end demo (task/comment CRUD, error handling).
- Code quality, testing, and maintainability.
- Troubleshooting and next steps.
https://www.loom.com/share/ed423b69e9a847aba6f2636c27a643ba?sid=1d7bcc8c-f159-4f11-ae19-8258dcd78c0f
