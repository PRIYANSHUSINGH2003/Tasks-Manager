import { useEffect, useMemo, useState } from 'react';
import './App.css';
import {
  listTasks,
  createTask,
  updateTask,
  deleteTask,
  listComments,
  createComment,
  updateComment,
  deleteComment,
} from './api';

function useAsync(asyncFn, deps = []) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const run = async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await asyncFn(...args);
      setData(result);
      return result;
    } catch (e) {
      setError(e);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useMemo(() => ({ run, loading, error, data, setData }), [loading, error, data]);
}

function TaskList({ tasks, onSelect, selectedId, onCreate, onDelete }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [err, setErr] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setErr('');
    try {
      await onCreate({ title, description: description || undefined });
      setTitle('');
      setDescription('');
    } catch (e) {
      setErr(e.message || 'Failed to create task');
    }
  };

  return (
    <div className="task-list">
      <h2>Tasks</h2>
      <form onSubmit={submit} className="task-form">
        <input
          placeholder="Task title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <input
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button type="submit">Add</button>
      </form>
      {err && <div className="error" role="alert">{err}</div>}
      <ul>
        {tasks.map((t) => (
          <li key={t.id} className={t.id === selectedId ? 'selected' : ''}>
            <button className="link" onClick={() => onSelect(t.id)}>{t.title}</button>
            <button className="danger" onClick={() => onDelete(t.id)} aria-label={`Delete ${t.title}`}>×</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function TaskDetail({ task, onUpdate }) {
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [message, setMessage] = useState('');
  const [err, setErr] = useState('');

  useEffect(() => {
    setTitle(task?.title || '');
    setDescription(task?.description || '');
    setMessage('');
    setErr('');
  }, [task]);

  if (!task) return <div className="task-detail"><em>Select a task</em></div>;

  const submit = async (e) => {
    e.preventDefault();
    setErr('');
    try {
      await onUpdate(task.id, { title, description });
      setMessage('Saved');
      setTimeout(() => setMessage(''), 1500);
    } catch (e) {
      setErr(e.message || 'Failed to save');
    }
  };

  return (
    <div className="task-detail">
      <h2>Task Detail</h2>
      <form onSubmit={submit} className="task-form">
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
        <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" />
        <button type="submit">Save</button>
      </form>
      {message && <div className="success" role="status">{message}</div>}
      {err && <div className="error" role="alert">{err}</div>}
      <small>
        Created: {task.created_at?.replace('T', ' ').slice(0, 19) || '-'} | Updated: {task.updated_at?.replace('T', ' ').slice(0, 19) || '-'}
      </small>
    </div>
  );
}

function CommentList({ taskId }) {
  const [comments, setComments] = useState([]);
  const [content, setContent] = useState('');
  const [author, setAuthor] = useState('');
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');

  const fetchComments = async () => {
    setLoading(true);
    setErr('');
    try {
      const res = await listComments(taskId);
      setComments(res.data);
    } catch (e) {
      setErr(e.message || 'Failed to load comments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (taskId) fetchComments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  const add = async (e) => {
    e.preventDefault();
    setErr('');
    try {
      await createComment(taskId, { content, author: author || undefined });
      setContent('');
      setAuthor('');
      await fetchComments();
    } catch (e) {
      setErr(e.message || 'Failed to add comment');
    }
  };

  const save = async (id, body) => {
    setErr('');
    try {
      await updateComment(taskId, id, body);
      await fetchComments();
    } catch (e) {
      setErr(e.message || 'Failed to update comment');
    }
  };

  const remove = async (id) => {
    setErr('');
    try {
      await deleteComment(taskId, id);
      await fetchComments();
    } catch (e) {
      setErr(e.message || 'Failed to delete comment');
    }
  };

  return (
    <div className="comments">
      <h3>Comments</h3>
      <form onSubmit={add} className="comment-form">
        <input
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Add a comment"
          maxLength={1000}
          required
        />
        <input
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          placeholder="Author (optional)"
        />
        <button type="submit">Add</button>
      </form>
      {err && <div className="error" role="alert">{err}</div>}
      {loading ? (
        <div>Loading...</div>
      ) : (
        <ul>
          {comments.map((c) => (
            <EditableComment key={c.id} c={c} onSave={save} onDelete={remove} />
          ))}
        </ul>
      )}
    </div>
  );
}

function EditableComment({ c, onSave, onDelete }) {
  const [isEditing, setEditing] = useState(false);
  const [content, setContent] = useState(c.content);
  const [author, setAuthor] = useState(c.author || '');

  const save = async () => {
    await onSave(c.id, { content, author: author || null });
    setEditing(false);
  };

  return (
    <li>
      {isEditing ? (
        <div className="comment-edit">
          <input value={content} onChange={(e) => setContent(e.target.value)} maxLength={1000} required />
          <input value={author} onChange={(e) => setAuthor(e.target.value)} placeholder="Author (optional)" />
          <button onClick={save}>Save</button>
          <button className="secondary" onClick={() => setEditing(false)}>Cancel</button>
        </div>
      ) : (
        <div className="comment">
          <div>
            <strong>{c.author || 'Anonymous'}</strong>: {c.content}
          </div>
          <div className="comment-actions">
            <button onClick={() => setEditing(true)}>Edit</button>
            <button className="danger" onClick={() => onDelete(c.id)}>Delete</button>
          </div>
        </div>
      )}
    </li>
  );
}

function App() {
  const [tasks, setTasks] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');

  const selectedTask = tasks.find((t) => t.id === selectedId) || null;

  const fetchTasks = async () => {
    setLoading(true);
    setErr('');
    try {
      const res = await listTasks();
      setTasks(res.data);
      if (res.data.length && !selectedId) setSelectedId(res.data[0].id);
    } catch (e) {
      setErr(e.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const addTask = async (body) => {
    const res = await createTask(body);
    const newTask = res.data;
    setTasks((prev) => [...prev, newTask]);
    setSelectedId(newTask.id);
  };

  const removeTask = async (id) => {
    await deleteTask(id);
    setTasks((prev) => prev.filter((t) => t.id !== id));
    if (selectedId === id) setSelectedId(null);
  };

  const saveTask = async (id, body) => {
    const res = await updateTask(id, body);
    const updated = res.data;
    setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
  };

  return (
    <div className="App">
      <h1>Tasks Manager</h1>
      {err && <div className="error" role="alert">{err}</div>}
      <div className="grid">
        <TaskList
          tasks={tasks}
          selectedId={selectedId}
          onSelect={setSelectedId}
          onCreate={addTask}
          onDelete={removeTask}
        />
        <div>
          {loading ? (
            <div>Loading...</div>
          ) : (
            <TaskDetail task={selectedTask} onUpdate={saveTask} />
          )}
          {selectedId && <CommentList taskId={selectedId} />}
        </div>
      </div>
    </div>
  );
}

export default App;
