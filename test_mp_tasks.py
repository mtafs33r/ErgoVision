import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

try:
    base_options = python.BaseOptions(model_asset_path='pose_landmarker_lite.task')
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=False)
    detector = vision.PoseLandmarker.create_from_options(options)
    print("SUCCESS: create_from_options")
    
    # Test on dummy image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
    detection_result = detector.detect(mp_image)
    print(f"SUCCESS: detect. landmarks size: {len(detection_result.pose_landmarks)}")
except Exception as e:
    print(f"ERROR: {e}")
