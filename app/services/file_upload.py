import os
from werkzeug.utils import secure_filename
from app.utils.logger import logger

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "txt", "csv"}

# Create upload folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename: str):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """
    Save the uploaded file to the upload folder
    """
    if not allowed_file(file.filename):
        logger.warning(f"Attempted to upload invalid file type: {file.filename}")
        return None, "File type not allowed"

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    logger.info(f"File uploaded successfully: {filename}")
    return file_path, None
