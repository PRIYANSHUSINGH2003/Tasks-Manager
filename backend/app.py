from __future__ import annotations

import os
from datetime import datetime
from typing import Dict, Any

from flask import Flask, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy without an app, bind in create_app
# This allows reuse in tests with a fresh app instance

db = SQLAlchemy()


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Task(db.Model, TimestampMixin):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    comments = db.relationship("Comment", back_populates="task", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Comment(db.Model, TimestampMixin):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    content = db.Column(db.String(1000), nullable=False)
    author = db.Column(db.String(120), nullable=True)

    task = db.relationship("Task", back_populates="comments")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "content": self.content,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# --------- App Factory ---------

def create_app(config: Dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)

    # Defaults suitable for local development; tests can override in fixture
    # Ensure instance folder exists and default DB is stored there to avoid path/permission issues
    os.makedirs(app.instance_path, exist_ok=True)
    default_db = os.path.join(app.instance_path, "app.db")
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", os.getenv("DATABASE_URL", f"sqlite:///{default_db}"))
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault("JSON_SORT_KEYS", False)

    if config:
        app.config.update(config)

    db.init_app(app)

    # Register blueprints
    api_bp = Blueprint("api", __name__, url_prefix="/api")

    @app.get("/health")
    def health() -> Any:
        return jsonify({"status": "ok"})

    # ---- Error handlers ----
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": {"message": "Not found"}}), 404

    @app.errorhandler(400)
    def bad_request(e):
        message = getattr(e, "description", "Bad request")
        return jsonify({"error": {"message": message}}), 400

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("Unhandled error: %s", e)
        return jsonify({"error": {"message": "Internal Server Error"}}), 500

    # ---- Helpers ----
    def json_error(message: str, code: int = 400):
        return jsonify({"error": {"message": message}}), code

    def get_json() -> Dict[str, Any]:
        if not request.is_json:
            return {}
        data = request.get_json(silent=True)
        return data or {}

    # ---- Task CRUD (supporting comments) ----
    @api_bp.get("/tasks")
    def list_tasks():
        tasks = Task.query.order_by(Task.id.asc()).all()
        return jsonify({"data": [t.to_dict() for t in tasks]})

    @api_bp.post("/tasks")
    def create_task():
        payload = get_json()
        title = (payload.get("title") or "").strip()
        if not title:
            return json_error("'title' is required", 400)
        description = payload.get("description")
        task = Task(title=title, description=description)
        db.session.add(task)
        db.session.commit()
        return jsonify({"data": task.to_dict()}), 201

    @api_bp.get("/tasks/<int:task_id>")
    def get_task(task_id: int):
        task = Task.query.get(task_id)
        if not task:
            return json_error("Task not found", 404)
        return jsonify({"data": task.to_dict()})

    @api_bp.put("/tasks/<int:task_id>")
    def update_task(task_id: int):
        task = Task.query.get(task_id)
        if not task:
            return json_error("Task not found", 404)
        payload = get_json()
        if "title" in payload:
            title = (payload.get("title") or "").strip()
            if not title:
                return json_error("'title' cannot be empty", 400)
            task.title = title
        if "description" in payload:
            task.description = payload.get("description")
        db.session.commit()
        return jsonify({"data": task.to_dict()})

    @api_bp.delete("/tasks/<int:task_id>")
    def delete_task(task_id: int):
        task = Task.query.get(task_id)
        if not task:
            return json_error("Task not found", 404)
        db.session.delete(task)
        db.session.commit()
        return jsonify({"data": {"deleted": True}})

    # ---- Comment CRUD (for a given task) ----
    @api_bp.get("/tasks/<int:task_id>/comments")
    def list_comments(task_id: int):
        task = Task.query.get(task_id)
        if not task:
            return json_error("Task not found", 404)
        comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.id.asc()).all()
        return jsonify({"data": [c.to_dict() for c in comments]})

    @api_bp.post("/tasks/<int:task_id>/comments")
    def create_comment(task_id: int):
        task = Task.query.get(task_id)
        if not task:
            return json_error("Task not found", 404)
        payload = get_json()
        content = (payload.get("content") or "").strip()
        if not content:
            return json_error("'content' is required", 400)
        if len(content) > 1000:
            return json_error("'content' must be <= 1000 characters", 400)
        author = (payload.get("author") or None)
        comment = Comment(task_id=task.id, content=content, author=author)
        db.session.add(comment)
        db.session.commit()
        return jsonify({"data": comment.to_dict()}), 201

    @api_bp.put("/tasks/<int:task_id>/comments/<int:comment_id>")
    def update_comment(task_id: int, comment_id: int):
        task = Task.query.get(task_id)
        if not task:
            return json_error("Task not found", 404)
        comment = Comment.query.filter_by(task_id=task_id, id=comment_id).first()
        if not comment:
            return json_error("Comment not found", 404)
        payload = get_json()
        if "content" in payload:
            content = (payload.get("content") or "").strip()
            if not content:
                return json_error("'content' cannot be empty", 400)
            if len(content) > 1000:
                return json_error("'content' must be <= 1000 characters", 400)
            comment.content = content
        if "author" in payload:
            author = payload.get("author")
            comment.author = (author or None)
        db.session.commit()
        return jsonify({"data": comment.to_dict()})

    @api_bp.delete("/tasks/<int:task_id>/comments/<int:comment_id>")
    def delete_comment(task_id: int, comment_id: int):
        task = Task.query.get(task_id)
        if not task:
            return json_error("Task not found", 404)
        comment = Comment.query.filter_by(task_id=task_id, id=comment_id).first()
        if not comment:
            return json_error("Comment not found", 404)
        db.session.delete(comment)
        db.session.commit()
        return jsonify({"data": {"deleted": True}})

    app.register_blueprint(api_bp)

    # Create DB tables if not present (local dev convenience)
    with app.app_context():
        db.create_all()

    return app


# --------- Entrypoint for local run ---------
if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
