from typing import Dict, Any, Union, BinaryIO
import cv2 as cv
import numpy as np
import tempfile
import os
import fitz
from app.config import PDF_RENDER_SCALE, BLUR_RADIUS
from app.core.scanner import Scanner
from app.core.embedder import Embedder
from app.core.privacy import PrivacyEngine
from app.core.vision import VisionEngine
from app.processors.audio import AudioProcessor
from app.processors.text import TextProcessor
from app.processors.form import FormProcessor
from app.processors.document_blur import DocumentProcessorBlur
from app.processors.face_blur import FaceDetection


class SecurePipeline:
    def __init__(self):
        self.scanner = Scanner()
        self.embedder = Embedder()
        self.privacy_engine = PrivacyEngine()
        self.vision_engine = VisionEngine()
        self.audio_proc = AudioProcessor()
        self.text_proc = TextProcessor()
        self.form_proc = FormProcessor()
        self.doc_proc = DocumentProcessorBlur(
            self.scanner,
            scale=PDF_RENDER_SCALE,
            blur_radius=BLUR_RADIUS
        )

        self.face_proc = FaceDetection()

    def _apply_standard_security(self, raw_text: str, epsilon: float) -> Dict[str, Any]:
        """The 'Universal' Security Wrapper"""
        self.privacy_engine.epsilon = epsilon
        findings = self.scanner.scan(raw_text)
        safe_text = self.scanner.redact(raw_text, findings)
        boomerang_map = self.scanner.create_boomerang_map(findings)
        raw_vector = self.embedder.get_vector(safe_text)
        safe_vector = self.privacy_engine.add_noise(raw_vector)
        return {
            "safe_content": safe_text,
            "boomerang_map": boomerang_map,
            "audit_log": findings,
            "safe_vector": safe_vector.tolist(),
            "full_vector_shape": safe_vector.shape,
            "raw_vector": raw_vector.tolist()
        }

    def run_document_pipeline(self, temp_path: str, epsilon: float) -> Dict[str, Any]:
        """Processes all pages and returns a consistent response"""
        doc_result = self.doc_proc.process(temp_path, epsilon)

        doc = fitz.open(doc_result.get('safe_pdf_path'))
        all_descriptions = []
        try:
            for page in doc:
                pix = page.get_pixmap()
                all_descriptions.append(self.vision_engine.describe_pdf_content(pix.tobytes()))
        finally:
            doc.close()

        full_description = "\n".join(all_descriptions)
        security = self._apply_standard_security(full_description, epsilon)

        return {**doc_result, **security,"description": full_description}

    def run_image_pipeline(self, file_obj: BinaryIO, epsilon: float) -> Dict[str, Any]:
        """Standardizes image response"""
        file_bytes = file_obj.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            cv.imwrite(tmp.name, img)
            blurred_img = self.face_proc.blur_faces(tmp.name)
            os.remove(tmp.name)

        _, buffer = cv.imencode('.png', blurred_img)
        description = self.vision_engine.describe_image(buffer.tobytes())
        security = self._apply_standard_security(description, epsilon)

        return {"blurred_image_bytes": buffer.tobytes(), "description": description, **security}

    def run_audio_pipeline(self, file_obj: BinaryIO, epsilon: float):
        """Standardizes audio response"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(file_obj.read())
            tmp_path = tmp.name

        try:
            raw_text = self.audio_proc.extract_text(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return self._apply_standard_security(raw_text, epsilon)

    def run_text_pipeline(self, text: str, epsilon: float):
        """Standardizes text response"""
        return self._apply_standard_security(text, epsilon)

    def run_form_pipeline(self, json_data: Dict, epsilon: float):
        """Standardizes form response"""
        flattened = ". ".join([f"{k}: {v}" for k, v in json_data.items()])
        return self._apply_standard_security(flattened, epsilon)