from app.config import (
    DATA_DIR,
    FACE_DETECTION_MODEL_PATH,
    DEFAULT_TEST_IMAGE,
    DEFAULT_BLURRED_OUTPUT,
    FACE_CONFIDENCE_THRESHOLD,
    FACE_BLUR_KERNEL_SIZE
)
from download_models import download_model
import cv2 as cv
import numpy as np
import os


class YuNet:
    def __init__(self, modelPath, inputSize=[320, 320], confThreshold=0.6, nmsThreshold=0.3, topK=5000, backendId=0, targetId=0):
        self._modelPath = modelPath
        self._inputSize = tuple(inputSize) # [w, h]
        self._confThreshold = confThreshold
        self._nmsThreshold = nmsThreshold
        self._topK = topK
        self._backendId = backendId
        self._target_id = targetId

        self._model = cv.FaceDetectorYN.create(
            model=self._modelPath,
            config="",
            input_size=self._inputSize,
            score_threshold=self._confThreshold,
            nms_threshold=self._nmsThreshold,
            top_k=self._topK,
            backend_id=self._backendId,
            target_id=self._target_id
        )

    def setInputSize(self, input_size):
        self._model.setInputSize(tuple(input_size))

    def infer(self, image):
        faces = self._model.detect(image)
        return faces[1] if faces[1] is not None else np.empty(shape=(0, 15))

class FaceDetection:
    def __init__(self, model_path=FACE_DETECTION_MODEL_PATH,
                 conf_threshold=FACE_CONFIDENCE_THRESHOLD,
                 nms_threshold=0.3, top_k=5000,
                 backend_target_idx=0):

        backend_target_pairs = [
            [cv.dnn.DNN_BACKEND_OPENCV, cv.dnn.DNN_TARGET_CPU],
            [cv.dnn.DNN_BACKEND_CUDA,   cv.dnn.DNN_TARGET_CUDA],
            [cv.dnn.DNN_BACKEND_CUDA,   cv.dnn.DNN_TARGET_CUDA_FP16],
            [cv.dnn.DNN_BACKEND_TIMVX,  cv.dnn.DNN_TARGET_NPU],
            [cv.dnn.DNN_BACKEND_CANN,   cv.dnn.DNN_TARGET_NPU]
        ]

        backend_id = backend_target_pairs[backend_target_idx][0]
        target_id = backend_target_pairs[backend_target_idx][1]

        download_model(model_path)
        self.detector = YuNet(modelPath=model_path,
                              inputSize=[320, 320],
                              confThreshold=conf_threshold,
                              nmsThreshold=nms_threshold,
                              topK=top_k,
                              backendId=backend_id,
                              targetId=target_id)



    def blur_faces(self, image_path, blur_kernel=(FACE_BLUR_KERNEL_SIZE, FACE_BLUR_KERNEL_SIZE)):
        image = cv.imread(image_path)
        if image is None:
            print(f"Error: Could not read image at {image_path}")
            return None

        h, w, _ = image.shape
        self.detector.setInputSize([w, h])
        results = self.detector.infer(image)

        blurred_image = image.copy()
        for det in results:
            bbox = det[0:4].astype(np.int32)
            # Ensure bbox is within image boundaries
            bx, by, bw, bh = bbox
            bx = max(0, bx)
            by = max(0, by)
            bw = min(bw, w - bx)
            bh = min(bh, h - by)

            if bw > 0 and bh > 0:
                roi = blurred_image[by:by+bh, bx:bx+bw]
                roi = cv.GaussianBlur(roi, blur_kernel, 0)
                blurred_image[by:by+bh, bx:bx+bw] = roi

        return blurred_image

if __name__ == '__main__':
    fd = FaceDetection(conf_threshold=0.9)
    img_p = DEFAULT_TEST_IMAGE
    print("\n--- Face Blurring ---")
    blurred_img = fd.blur_faces(img_p)
    if blurred_img is not None:
        os.makedirs(os.path.join(DATA_DIR, "results"), exist_ok=True)
        output_path = DEFAULT_BLURRED_OUTPUT
        cv.imwrite(output_path, blurred_img)
        print(f"Saved blurred image to {output_path}")
    else:
        print("Failed to blur image; no output saved.")
