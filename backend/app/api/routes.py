import io
import json
import os

from flask import Blueprint, jsonify, request, send_file, send_from_directory

from app.config import UPLOAD_DIR
from app.core.pipeline import SecurePipeline

api = Blueprint('api', __name__)
pipeline = SecurePipeline()


@api.route('/process/text', methods=['POST'])
def process_text():
    data = request.json
    text = data.get('text', '')
    epsilon = float(data.get('epsilon', 1.0))

    try:
        result = pipeline.run_text_pipeline(text, epsilon)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/process/form', methods=['POST'])
def process_form():
    body = request.json
    form_data = body.get('data', {})
    epsilon = float(body.get('epsilon', 1.0))
    try:
        result = pipeline.run_form_pipeline(form_data, epsilon)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/process/audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files['file']
    epsilon = float(request.form.get('epsilon', 1.0))
    try:
        result = pipeline.run_audio_pipeline(file, epsilon)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/process/image/blur', methods=['POST'])
def process_image_blur():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    epsilon = float(request.form.get('epsilon', 1.0))
    try:
        result = pipeline.run_image_pipeline(file, epsilon)
        output_stream = io.BytesIO(result["blurred_image_bytes"])
        response = send_file(
            output_stream,
            mimetype='image/png',
            as_attachment=True,
            download_name="blurred_image.png"
        )
        metadata = {
            "description": result.get("description"),
            "unsafe_words": result.get("audit_log"),
            "safe_description": result.get("safe_content"),
            "safe_vector": result.get("safe_vector")

        }
        response.headers['X-Privacy-Metadata'] = json.dumps(metadata)
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/process/document/blur', methods=['POST'])
def process_document_blur():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    epsilon = float(request.form.get('epsilon', 1.0))
    temp_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(temp_path)
    try:
        result = pipeline.run_document_pipeline(temp_path, epsilon)
        response = send_file(
            result['safe_pdf_path'],
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"blurred_{file.filename}"
        )

        response.headers['X-Document-Metadata'] = json.dumps({
            "description": result.get("description", "No description available."),
            "unsafe_words": result.get("unsafe_words", []),
            "safe_description": result.get("safe_content"),
            "safe_vector": result.get("safe_vector", [])
        })
        return response
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@api.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@api.route('/status', methods=['GET'])
def health():
    return jsonify({"status": "online", "message": "Secure Pipeline Active"})