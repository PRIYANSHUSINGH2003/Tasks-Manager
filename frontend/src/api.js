const BASE = process.env.REACT_APP_API_URL || ""; // If proxy is set, relative paths will proxy to backend

async function http(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  let body = null;
  const text = await res.text();
  try {
    body = text ? JSON.parse(text) : null;
  } catch (e) {
    body = text;
  }
  if (!res.ok) {
    const message = body && body.error && body.error.message ? body.error.message : res.statusText;
    const err = new Error(message);
    err.status = res.status;
    err.payload = body;
    throw err;
  }
  return body;
}

// Tasks
export function listTasks() {
  return http("/api/tasks");
}
export function createTask({ title, description }) {
  return http("/api/tasks", { method: "POST", body: JSON.stringify({ title, description }) });
}
export function updateTask(id, body) {
  return http(`/api/tasks/${id}`, { method: "PUT", body: JSON.stringify(body) });
}
export function deleteTask(id) {
  return http(`/api/tasks/${id}`, { method: "DELETE" });
}

// Comments
export function listComments(taskId) {
  return http(`/api/tasks/${taskId}/comments`);
}
export function createComment(taskId, { content, author }) {
  return http(`/api/tasks/${taskId}/comments`, { method: "POST", body: JSON.stringify({ content, author }) });
}
export function updateComment(taskId, commentId, body) {
  return http(`/api/tasks/${taskId}/comments/${commentId}`, { method: "PUT", body: JSON.stringify(body) });
}
export function deleteComment(taskId, commentId) {
  return http(`/api/tasks/${taskId}/comments/${commentId}`, { method: "DELETE" });
}
