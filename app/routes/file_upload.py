from flask import Blueprint, request, jsonify, current_app
from app.services.file_upload import save_file
from app.utils.decorators import token_required
from app.utils.helpers import rate_limit

file_bp = Blueprint("file_bp", __name__, url_prefix="/files")

# ----------------- Upload Route -----------------
@file_bp.route("/upload", methods=["POST"])
@token_required
@rate_limit("10 per minute")
def upload_file():
    try:
        # Access uploaded file
        file = request.files.get('file')  
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        # Optional: get additional form fields (not JSON)
        description = request.form.get('description')

        # Save file
        file.save(f"uploads/{file.filename}")

        return jsonify({"message": "File uploaded successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500