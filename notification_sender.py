"""
Notification sender for ErgoVision desktop application.

Sends push notifications to the user's mobile app (via the Node.js relay
server) when bad posture is detected for a sustained period.
Runs HTTP requests in a background thread so the Tk UI is never blocked.
"""

import threading
import time
import urllib.request
import urllib.error
import json
from datetime import datetime


class NotificationSender:
    """
    Sends posture-alert push notifications to the ErgoVision mobile app
    by POSTing to the local Node.js server endpoint.
    """

    # Adjust this if the server runs on a different host/port
    SERVER_URL = "http://localhost:3000"
    ENDPOINT = "/api/notify-posture"

    def __init__(self, user_id: int, server_url: str = None):
        """
        Parameters
        ----------
        user_id : int
            The numeric ID of the currently logged-in user.
        server_url : str, optional
            Override the default server URL (e.g. for LAN setups).
        """
        self.user_id = user_id
        if server_url:
            self.SERVER_URL = server_url

        # Timestamp of the last successfully sent notification
        self._last_sent_at: datetime | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send_posture_alert(
        self,
        message: str = "Your posture has been poor for too long. Sit up straight! 🪑",
        severity: str = "warning",
    ) -> None:
        """
        Fire-and-forget: send a posture alert in a background thread.

        This is safe to call from the Tk main loop without any blocking.
        """
        thread = threading.Thread(
            target=self._post_alert,
            args=(message, severity),
            daemon=True,
        )
        thread.start()
        self._last_sent_at = datetime.now()

    def can_send(self, cooldown_seconds: int) -> bool:
        """
        Returns True if enough time has passed since the last notification
        was sent, preventing alert spam.

        Parameters
        ----------
        cooldown_seconds : int
            Minimum number of seconds that must elapse between alerts.
        """
        if self._last_sent_at is None:
            return True
        elapsed = (datetime.now() - self._last_sent_at).total_seconds()
        return elapsed >= cooldown_seconds

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _post_alert(self, message: str, severity: str) -> None:
        """POST the alert to the relay server (runs in background thread)."""
        url = f"{self.SERVER_URL}{self.ENDPOINT}"
        payload = json.dumps(
            {
                "userId": str(self.user_id),
                "message": message,
                "severity": severity,
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                body = response.read().decode()
                result = json.loads(body)
                if result.get("status") == "success":
                    print(
                        f"[ErgoVision] Push notification sent to user {self.user_id}"
                    )
                else:
                    print(
                        f"[ErgoVision] Notification skipped/failed: {result.get('message', body)}"
                    )
        except urllib.error.URLError as exc:
            # Server may not be running — log but never crash the app
            print(
                f"[ErgoVision] Could not reach notification server: {exc.reason}"
            )
        except Exception as exc:
            print(f"[ErgoVision] Notification error: {exc}")
