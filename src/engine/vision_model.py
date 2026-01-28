import cv2
import numpy as np
import mediapipe as mp

# src/engine/vision_model.py
import cv2
import numpy as np
import mediapipe as mp

class SkinAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.3
        )
        self.ZONE_INDICES = {'forehead': 10, 'left_cheek': 234, 'right_cheek': 454}

    def _get_roi_stats(self, img_rgb, landmark, w, h):
        cx, cy = int(landmark.x * w), int(landmark.y * h)
        size = 20
        y1, y2 = max(0, cy-size), min(h, cy+size)
        x1, x2 = max(0, cx-size), min(w, cx+size)
        
        roi = img_rgb[y1:y2, x1:x2]
        if roi.size == 0: return None
        
        lab_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2Lab)
        avg_a = np.mean(lab_roi[:, :, 1])
        
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        v_channel = hsv_roi[:, :, 2]
        glare_score = np.mean(v_channel > 200)
        
        return {"redness": avg_a, "oiliness": glare_score}

    def analyze_process(self, image_bytes):
        """
        [수정] Streamlit에서 넘겨준 바이트 데이터를 직접 처리하도록 변경
        """
        try:
            # 1. 바이트 데이터를 numpy 배열로 변환
            nparr = np.frombuffer(image_bytes, np.uint8)
            # 2. 이미지로 디코딩
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            return {"status": "fail", "message": f"이미지 디코딩 에러: {e}"}

        if image is None: 
            return {"status": "fail", "message": "이미지 로드 실패"}
        
        h, w, _ = image.shape
        rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_img)

        if not results.multi_face_landmarks:
            return {"status": "fail", "message": "얼굴 감지 실패"}

        landmarks = results.multi_face_landmarks[0].landmark
        zones = {}
        for name, idx in self.ZONE_INDICES.items():
            res = self._get_roi_stats(rgb_img, landmarks[idx], w, h)
            if res: zones[name] = res

        if not zones:
            return {"status": "fail", "message": "ROI 영역 분석 실패"}

        avg_red = np.mean([z['redness'] for z in zones.values()])
        avg_oil = np.mean([z['oiliness'] for z in zones.values()])

        return {
            "status": "success",
            "metrics": {
                "redness_level": round(max(0, (avg_red - 128) / 20) * 100, 1),
                "oiliness_level": round(avg_oil * 100, 1)
            }
        }