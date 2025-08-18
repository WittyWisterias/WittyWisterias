import asyncio
import base64

import cv2
import reflex as rx
from reflex.utils.console import LogLevel, set_log_level

from frontend.app_config import app

# Filer race condition warnings, which can occur when the websocket is disconnected
# This is not an issue as the WebcamStateMixin is designed to handle disconnections gracefully
# Note: Reflex Console is very bad so our only option is to raise the log level to ERROR
set_log_level(LogLevel.ERROR)

# Opening/PreLoading Webcam Video Capture for faster Load times
webcam_cap = cv2.VideoCapture(0)
webcam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
webcam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
webcam_cap.set(cv2.CAP_PROP_FPS, 60)
webcam_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)


class WebcamStateMixin(rx.State, mixin=True):  # type: ignore[call-arg]
    """Mixin for managing webcam state in the application."""

    frame_data: str | None = None
    recording: bool = False

    @rx.event
    def disable_webcam(self) -> None:
        """Stop the webcam capture loop."""
        self.recording = False

    @rx.event(background=True)
    async def capture_loop(self) -> None:
        """Continuously capture frames from the webcam and update the frame data."""
        if not webcam_cap or not webcam_cap.isOpened():
            raise RuntimeError("Cannot open webcam at index 0")

        # While should record and Tab is open
        while self.recording and self.router.session.client_token in app.event_namespace.token_to_sid:
            ok, frame = webcam_cap.read()
            if not ok:
                await asyncio.sleep(0.1)
                continue

            # Taking a 480p grayscale frame for better performance
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # encode JPEG with lower quality
            _, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 20])
            data_url = "data:image/jpeg;base64," + base64.b64encode(buf).decode()

            async with self:
                self.frame_data = data_url
