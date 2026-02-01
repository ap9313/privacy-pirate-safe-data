import os

from flask import Flask, jsonify
from flask_cors import CORS

from app.api.routes import api
from app.config import UPLOAD_DIR


def create_app() -> Flask:
    app = Flask(__name__)

    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        expose_headers=["X-Privacy-Metadata", "X-Metadata", "X-Document-Metadata"],
    )
    app.register_blueprint(api, url_prefix="")

    @app.route("/status", methods=["GET"])
    def system_status():
        return jsonify({"status": "ok", "message": "Backend is online"})

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return app


if __name__ == "__main__":
    flask_app = create_app()
    print("Safe-Data Backend running on port 8000")
    flask_app.run(host="0.0.0.0", port=8000, debug=True)
