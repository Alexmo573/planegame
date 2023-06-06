import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2


class mediapipe_gesture_helper():
    def __init__(self, confidence=0.3) -> None:
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.mp_drawing_styles = mp.solutions.drawing_styles
        base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
        options = vision.GestureRecognizerOptions(base_options=base_options)
        self.recognizer = vision.GestureRecognizer.create_from_options(options)
        self.cap = cv2.VideoCapture(0)
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=confidence)

        self.last_image = None

    # 需要先拍照,运行后修改之前的图片，加上辅助线和点，返回当前手的位置(几何中心)和动作
    def take_photo(self):
        success, image = self.cap.read()
        self.last_image = cv2.flip(image, 1)

    def get_last_hand_info(self, show_cord=True, show_landmark=True):
        # Convert the image to RGB format
        indexFingerTipLandmark = None
        detect_image = cv2.cvtColor(self.last_image, cv2.COLOR_BGR2RGB)
        recognition_result = self.recognizer.recognize(mp.Image(image_format=mp.ImageFormat.SRGB, data=detect_image))
        # Draw the hand landmarks on the image
        if len(recognition_result.hand_landmarks) > 0:
            multi_hand_landmarks_list = recognition_result.hand_landmarks
            for hand_landmarks in multi_hand_landmarks_list:
                hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                x = 0.0
                y = 0.0
                z = 0.0
                hand_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in
                    hand_landmarks
                ])
                indexFingerTipLandmark = hand_landmarks[8]
                for landmark in hand_landmarks:
                    x += landmark.x
                    y += landmark.y
                    z += landmark.z
                x /= len(hand_landmarks)
                y /= len(hand_landmarks)
                z /= len(hand_landmarks)
                if show_landmark:
                    self.mp_drawing.draw_landmarks(
                        detect_image,
                        hand_landmarks_proto,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())
            if show_cord:
                cv2.putText(detect_image, str(recognition_result.gestures[0][0].category_name), (10, 100),
                            cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                cv2.putText(detect_image, str(x), (10, 150), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                cv2.putText(detect_image, str(y), (10, 200), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                cv2.putText(detect_image, str(z), (10, 250), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
            self.last_image = cv2.cvtColor(detect_image, cv2.COLOR_RGB2BGR)
            return recognition_result.gestures[0][0].category_name, x, y, z, indexFingerTipLandmark

# cv2.destroyAllWindows()
