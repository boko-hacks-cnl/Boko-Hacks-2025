from datetime import datetime

import bleach  # Add this import for XSS protection
from flask import Blueprint, jsonify, render_template, request, session
from sqlalchemy import text

from extensions import db
from models.note import Note
from models.user import User

notes_bp = Blueprint("notes", __name__, url_prefix="/apps/notes")


@notes_bp.route("/")
def notes():
    """Render notes page with all notes"""
    if "user" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    current_user = User.query.filter_by(username=session["user"]).first()
    if not current_user:
        return jsonify({"success": False, "error": "User not found"}), 404

    user_id = request.args.get("user_id", current_user.id)

    try:
        user_id = int(user_id)
        # Fix: Add access control - only allow viewing own notes or admin access
        if user_id != current_user.id and not current_user.is_admin():
            return jsonify({"success": False, "error": "Unauthorized access"}), 403
    except (TypeError, ValueError):
        user_id = current_user.id

    all_notes = (
        Note.query.filter_by(user_id=user_id).order_by(Note.created_at.desc()).all()
    )
    print(f"Loading notes page - Found {len(all_notes)} notes for user {user_id}")

    return render_template(
        "notes.html", notes=all_notes, current_user_id=current_user.id
    )


@notes_bp.route("/create", methods=["POST"])
def create_note():
    """Create a new note - Fixed XSS vulnerability"""
    if "user" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    current_user = User.query.filter_by(username=session["user"]).first()
    if not current_user:
        return jsonify({"success": False, "error": "User not found"}), 404

    # Fix: Sanitize user input to prevent XSS
    title = bleach.clean(request.form.get("title", ""))
    content = bleach.clean(request.form.get("content", ""))

    if not title or not content:
        return jsonify(
            {"success": False, "error": "Title and content are required"}
        ), 400

    try:
        print(f"Creating note - Title: {title}, Content: {content}")

        # Validate title and content length
        max_title_length = 100
        max_content_length = 5000

        if len(title) > max_title_length:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Title exceeds maximum length of {max_title_length} characters",
                    }
                ),
                400,
            )

        if len(content) > max_content_length:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Content exceeds maximum length of {max_content_length} characters",
                    }
                ),
                400,
            )

        note = Note(
            title=title,
            content=content,
            created_at=datetime.now(),
            user_id=current_user.id,
        )

        db.session.add(note)
        db.session.commit()

        print(f"Note created with ID: {note.id}")

        return jsonify(
            {
                "success": True,
                "message": "Note created successfully",
                "note": {
                    "id": note.id,
                    "title": note.title,
                    "content": note.content,
                    "created_at": note.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "user_id": note.user_id,
                },
            }
        )
    except Exception as e:
        print(f"Error creating note: {e}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notes_bp.route("/search")
def search_notes():
    """Search notes - Fixed SQL injection vulnerability and user access control"""
    if "user" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    current_user = User.query.filter_by(username=session["user"]).first()
    if not current_user:
        return jsonify({"success": False, "error": "User not found"}), 404

    query = request.args.get("q", "")
    print(f"Search query: {query}")

    try:
        # Fix: Use parameterized query and add user_id filter for proper access control
        sql = text(
            "SELECT * FROM notes WHERE (title LIKE :query OR content LIKE :query) AND user_id = :user_id"
        )
        result = db.session.execute(
            sql, {"query": f"%{query}%", "user_id": current_user.id}
        )

        notes = []
        for row in result:
            # Handle created_at formatting properly - could be a string or datetime
            created_at = row[3]
            if isinstance(created_at, str):
                created_at_str = created_at
            else:
                try:
                    created_at_str = (
                        created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None
                    )
                except AttributeError:
                    created_at_str = str(created_at) if created_at else None

            note = {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "created_at": created_at_str,
                "user_id": row[4],
            }
            notes.append(note)

        print(f"Found {len(notes)} matching notes")
        return jsonify({"success": True, "notes": notes})
    except Exception as e:
        print(f"Error searching notes: {e}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notes_bp.route("/delete/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    """Delete a note - Fixed access control vulnerability"""
    if "user" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    current_user = User.query.filter_by(username=session["user"]).first()
    if not current_user:
        return jsonify({"success": False, "error": "User not found"}), 404

    try:
        note = Note.query.get(note_id)
        if not note:
            print(f"Note not found: {note_id}")
            return jsonify(
                {"success": False, "error": f"Note with ID {note_id} not found"}
            ), 404

        # Fix: Add proper authorization check
        if note.user_id != current_user.id and not current_user.is_admin():
            print(
                f"Unauthorized deletion attempt of note {note_id} by user {current_user.id}"
            )
            return jsonify({"success": False, "error": "Unauthorized"}), 403

        print(
            f"Deleting note ID: {note_id}, Title: {note.title}, Owner: {note.user_id}"
        )

        db.session.delete(note)
        db.session.commit()

        print(f"Note {note_id} deleted successfully")
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error deleting note: {e}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notes_bp.route("/debug")
def debug_database():
    """Debug route to check database contents - Fixed information disclosure"""
    # Fix: Add admin-only check
    if "user" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    current_user = User.query.filter_by(username=session["user"]).first()
    if not current_user or not current_user.is_admin():
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    try:
        users = User.query.all()
        print("\nAll Users:")
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}")

        notes = Note.query.all()
        print("\nAll Notes:")
        for note in notes:
            print(f"ID: {note.id}, Title: {note.title}, User ID: {note.user_id}")

        sql = text("SELECT * FROM notes")
        result = db.session.execute(sql)
        rows = result.fetchall()
        print("\nRaw SQL Notes Query Result:")
        for row in rows:
            print(row)

        return jsonify(
            {
                "users": [{"id": u.id, "username": u.username} for u in users],
                "notes": [note.to_dict() for note in notes],
            }
        )
    except Exception as e:
        print(f"Debug Error: {e}")
        return jsonify({"error": str(e)}), 500
