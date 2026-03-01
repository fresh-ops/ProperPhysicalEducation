import time

import cv2
import mediapipe as mp

from poses import create_video_pose_landmarker, draw_landmarks_on_image, get_camera

INFERENCE_WIDTH = 320
INFERENCE_HEIGHT = 180


def main() -> None:
    pose_landmarker = create_video_pose_landmarker()
    camera = get_camera(0)

    if not camera.isOpened():
        raise RuntimeError("Failed to open webcam")

    try:
        while True:
            ok, frame_bgr = camera.read()
            if not ok:
                continue

            inference_bgr = cv2.resize(
                frame_bgr,
                (INFERENCE_WIDTH, INFERENCE_HEIGHT),
                interpolation=cv2.INTER_AREA,
            )
            frame_rgb = cv2.cvtColor(inference_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            timestamp_ms = int(time.monotonic() * 1000)
            result = pose_landmarker.detect_for_video(mp_image, timestamp_ms)

            poses_count = len(result.pose_landmarks)
            cv2.putText(
                frame_bgr,
                f"Poses: {poses_count}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            annotated_image = draw_landmarks_on_image(frame_bgr, result)
            cv2.imshow("Pose detection", annotated_image)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        pose_landmarker.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
