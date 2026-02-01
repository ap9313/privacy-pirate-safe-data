import os
import urllib.request
from gliner import GLiNER

from app.config import (DATA_DIR,
                        NER_MODEL_NAME,
                        GLINER_MODEL_NAME,
                        GLINER_LOCAL_DIR,
                        FACE_DETECTION_MODEL_PATH,
                        FACE_DETECTION_MODEL_DIR,
                        FACE_DETECTION_MODEL_NAME)



def download_gliner():
    model_path = os.path.join(DATA_DIR, "models", GLINER_LOCAL_DIR)
    if os.path.exists(model_path):
        print(f"✅ GLiNER model already downloaded at: {model_path}")
        return

    model_name = GLINER_MODEL_NAME or NER_MODEL_NAME
    print(f"⏳ Downloading GLiNER model: {model_name}...")
    model = GLiNER.from_pretrained(model_name)
    model.save_pretrained(model_path)
    print(f"✅ Model saved to: {model_path}")


def download_model(model_path: str = FACE_DETECTION_MODEL_PATH):
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    if os.path.exists(model_path):
        print(f"✅ YuNet model already downloaded at: {model_path}")
        return

    model_name = FACE_DETECTION_MODEL_NAME
    url = f"https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/{model_name}"
    print(f"Downloading model {model_name} from {url}...")
    try:
        urllib.request.urlretrieve(url, model_path)
        print(f"✅ Model saved to: {model_path}")
    except Exception as e:
        print(f"Error downloading model: {e}")

if __name__ == "__main__":
    download_gliner()
    download_model()
