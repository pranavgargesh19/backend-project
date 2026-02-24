from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
from flask_migrate import Migrate
from app.routes.user import user_bp
from app.routes.file_upload import file_bp
from app.routes.scheduler import manual_bp
from app.routes.roles import role_bp
from app.db import db
from app.extentions import mail
from app.utils.logger import logger
from app.utils.decorators import get_user_id_for_limiter
from app.utils.scheduler import start_scheduler  # <-- import here

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # ------------------ DB and Mail ------------------
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # ------------------ Upload Folder -----------------
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # ------------------ Flask-Limiter -----------------
    # Create limiter WITHOUT app
    limiter = Limiter(
    key_func=get_user_id_for_limiter,
    default_limits=[]
    )

# Later, bind to app
    limiter.init_app(app)

# Save it in app
    app.limiter = limiter


    # ------------------ Register Blueprints -----------------
    app.register_blueprint(user_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(manual_bp)
    app.register_blueprint(role_bp)

    # ------------------ Logger -----------------
    @app.before_request
    def log_request_info():
        body = None
        try:
            if request.is_json:  # ✅ only parse JSON if Content-Type is application/json
               body = request.get_json()
            elif request.form:  # ✅ handle form data (like file uploads)
               body = dict(request.form)
            else:
               body = None
        except Exception:
                body = None

        logger.info(
            f"[REQUEST] {request.method} {request.path} IP: {request.remote_addr} Body: {body}"
        )

    @app.after_request
    def log_response_info(response):
        logger.info(f"[RESPONSE] {request.method} {request.path} Status: {response.status}")
        return response

    # ------------------ Rate Limit Error -----------------
    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(e):
        return jsonify({
            "status": False,
            "message": f"Rate limit exceeded: {e.description}",
            "data": None
        }), 429

    # ------------------ Create DB Tables -----------------
    with app.app_context():
        db.create_all()
        start_scheduler(app)  # <-- start scheduler safely within app context

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "Backend is running successfully"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
