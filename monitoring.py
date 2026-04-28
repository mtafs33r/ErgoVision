"""
Posture monitoring system for ErgoVision application
Handles camera detection and posture analysis
"""

import cv2
import numpy as np
import threading
import time
from datetime import datetime, timedelta
import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
from notification_sender import NotificationSender
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import urllib.request
import math

class PostureMonitor:
    def __init__(
        self,
        camera_frame,
        user_id,
        db_manager,
        posture_callback,
        session_callback,
        mobile_notifications_enabled: bool = True,
        alert_threshold_minutes: float = 0.0833,  # 5 seconds default
        server_url: str = None,
    ):
        """Initialize posture monitor

        Parameters
        ----------
        mobile_notifications_enabled : bool
            Whether to send push alerts to the mobile app.
        alert_threshold_minutes : float
            Number of consecutive minutes of "Poor" posture before an alert fires.
        server_url : str, optional
            Override the relay server URL (e.g. if running on a different host).
        """
        self.camera_frame = camera_frame
        self.user_id = user_id
        self.db_manager = db_manager
        self.posture_callback = posture_callback
        self.session_callback = session_callback

        # Mobile notification settings
        self.mobile_notifications_enabled = mobile_notifications_enabled
        self.alert_threshold_seconds = alert_threshold_minutes * 60
        self._notification_sender = NotificationSender(user_id, server_url)

        # Bad-posture sustain tracker
        self._poor_posture_start: datetime | None = None  # when "Poor" streak began
        # Monitoring state
        self.is_monitoring = False
        self.cap = None
        self.monitor_thread = None
        self._after_job = None
        
        # Session tracking
        self.session_start_time = None
        self.posture_scores = []
        self.current_posture = "Unknown"
        
        # Posture detection parameters
        self.good_posture_threshold = 0.8
        self.average_posture_threshold = 0.6
        
        # Ensure model exists
        self.model_path = "pose_landmarker_lite.task"
        if not os.path.exists(self.model_path):
            print("Downloading Pose Landmarker model...")
            urllib.request.urlretrieve(
                'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task',
                self.model_path
            )
        
        # Setup MediaPipe Pose Tasks API
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            output_segmentation_masks=False)
        self.detector = vision.PoseLandmarker.create_from_options(options)
        self.last_results = None
        
        # Setup camera preview
        self.setup_camera_preview()
    
    def setup_camera_preview(self):
        """Setup camera preview display"""
        # Remove placeholder
        for widget in self.camera_frame.winfo_children():
            widget.destroy()
        
        # Create camera display
        self.camera_display = ctk.CTkLabel(
            self.camera_frame,
            text="Initializing Camera...",
            width=640,
            height=480
        )
        self.camera_display.pack(expand=True)
        
        # Status overlay
        self.status_overlay = ctk.CTkLabel(
            self.camera_frame,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="transparent"
        )
        self.status_overlay.place(x=10, y=10)
    
    def start(self):
        """Start posture monitoring"""
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Start monitoring
            self.is_monitoring = True
            self.session_start_time = datetime.now()
            self.posture_scores = []
            
            # Schedule first frame processing on Tk main loop
            self._schedule_next_frame()
            
            return True
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def stop(self):
        """Stop posture monitoring"""
        self.is_monitoring = False

        # Cancel scheduled callbacks
        try:
            if self._after_job is not None:
                self.camera_frame.after_cancel(self._after_job)
                self._after_job = None
        except Exception:
            pass
        
        if self.cap:
            self.cap.release()
        
        # Calculate session results
        if self.session_start_time and self.posture_scores:
            duration = datetime.now() - self.session_start_time
            duration_minutes = duration.total_seconds() / 60
            
            # Calculate average score
            avg_score = sum(self.posture_scores) / len(self.posture_scores)
            
            # Determine rating
            if avg_score >= 80:
                rating = "Excellent"
            elif avg_score >= 60:
                rating = "Average"
            else:
                rating = "Poor"
            
            # Save session to database
            self.db_manager.save_posture_session(
                self.user_id,
                duration_minutes,
                int(avg_score),
                rating
            )
            
            # Call session callback on the Tk thread
            if self.session_callback:
                self.camera_frame.after(0, lambda: self.session_callback(
                    f"{int(duration.total_seconds() // 60)}:{int(duration.total_seconds() % 60):02d}",
                    int(avg_score),
                    rating
                ))
        
        # Reset display via Tk thread
        try:
            self.camera_display.configure(text="Camera Stopped")
            self.status_overlay.configure(text="")
        except Exception:
            pass
    
    def _schedule_next_frame(self):
        """Schedule processing of the next frame on the Tk main loop."""
        if not self.is_monitoring:
            return
        try:
            ret, frame = self.cap.read()
            if ret:
                posture_score, posture_status = self.analyze_posture(frame)
                self.posture_scores.append(posture_score)
                self.current_posture = posture_status
                frame = self.draw_posture_analysis(frame, posture_score, posture_status)
                # Update UI directly (we are on Tk thread)
                self.update_camera_display(frame)
                if self.posture_callback:
                    self.posture_callback(posture_status, posture_score)

                # ---- Bad-posture sustain tracking & mobile alert ----
                self._check_and_send_posture_alert(posture_status)
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
        # Aim for ~30 FPS
        try:
            self._after_job = self.camera_frame.after(33, self._schedule_next_frame)
        except Exception:
            # If scheduling fails, stop monitoring gracefully
            self.is_monitoring = False

    def _check_and_send_posture_alert(self, posture_status: str) -> None:
        """Track consecutive poor-posture duration; fire mobile alert when threshold exceeded."""
        if not self.mobile_notifications_enabled:
            self._poor_posture_start = None
            return

        if posture_status == "Poor":
            if self._poor_posture_start is None:
                # Start of a new bad-posture streak
                print("[Monitor] Poor posture detected! Starting 5-second timer...")
                self._poor_posture_start = datetime.now()
            else:
                streak_seconds = (
                    datetime.now() - self._poor_posture_start
                ).total_seconds()
                
                # Log progress every second to debug
                if int(streak_seconds) > 0 and int(streak_seconds) > getattr(self, '_last_log_second', 0):
                    print(f"[Monitor] Slouching for {int(streak_seconds)}s...")
                    self._last_log_second = int(streak_seconds)

                if streak_seconds >= self.alert_threshold_seconds:
                    self._last_log_second = 0 # reset log counter
                    print(f"[Monitor] Poor posture threshold reached ({int(streak_seconds)}s). Triggering alert...")
                    # Cooldown = same as threshold so we don't spam
                    can = self._notification_sender.can_send(int(self.alert_threshold_seconds))
                    print(f"[Monitor] can_send check = {can} (last sent: {self._notification_sender._last_sent_at})")
                    if can:
                        threshold_s = int(self.alert_threshold_seconds)
                        if threshold_s < 60:
                            time_str = f"{threshold_s} seconds"
                        else:
                            minutes = threshold_s // 60
                            time_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
                        msg = f"You've had poor posture for {time_str}. Sit up straight! 🪑"
                        print(f"[Monitor] Calling send_posture_alert with user_id={self.user_id}")
                        self._notification_sender.send_posture_alert(message=msg, severity="warning")
                        # Reset streak so the timer restarts after the alert
                        self._poor_posture_start = datetime.now()
        else:
            # Posture is Good or Average — reset the streak
            if self._poor_posture_start is not None:
                print("[Monitor] Posture improved. Timer reset.")
                self._last_log_second = 0
            self._poor_posture_start = None
    def analyze_posture(self, frame):
        """Analyze posture in the given frame using MediaPipe"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # In VIDEO mode, we need to pass a monotonically increasing timestamp in ms
        timestamp_ms = int(time.time() * 1000)
        results = self.detector.detect_for_video(mp_image, timestamp_ms)
        self.last_results = results

        posture_score = 100.0

        if not results.pose_landmarks:
            return 0, "No Detection"
        
        # Take the first detected person
        landmarks = results.pose_landmarks[0]
        
        # MediaPipe landmark indices: 11 = LEFT_SHOULDER, 12 = RIGHT_SHOULDER, 0 = NOSE
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        nose = landmarks[0]

        # Normalize penalties against shoulder width to make scoring completely immune to camera distance
        shoulder_width = abs(left_shoulder.x - right_shoulder.x)
        shoulder_width = max(0.05, shoulder_width)  # Prevent division by zero if sideways

        # 1. Shoulder Level (y-axis tilt normalized)
        # Any deviation continuously drains points (no dead zones where score is perfect 100 if slightly tilted)
        shoulder_y_diff_ratio = abs(left_shoulder.y - right_shoulder.y) / shoulder_width
        posture_score -= (shoulder_y_diff_ratio * 100)

        # 2. Neck alignment (nose x vs mid-shoulder x to detect leaning sideways)
        mid_shoulder_x = (left_shoulder.x + right_shoulder.x) / 2.0
        neck_x_ratio = abs(nose.x - mid_shoulder_x) / shoulder_width
        posture_score -= (neck_x_ratio * 100)
            
        # 3. Forward slouch (Face drop on Y axis vs shoulder width)
        mid_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2.0
        neck_height = mid_shoulder_y - nose.y
        neck_height_ratio = neck_height / shoulder_width
        
        # Perfect upright posture has an average neck height ratio > 0.70.
        # Continuously and smoothly penalty as the head drops closer to shoulder level.
        slouch_amount = max(0.0, 0.70 - neck_height_ratio)
        posture_score -= (slouch_amount * 150)

        posture_score = max(0, min(100, int(posture_score)))

        # Symmetrical thresholds over the 0-100 range
        if posture_score >= 67:
            posture_status = "Good"
        elif posture_score >= 34:
            posture_status = "Average"
        else:
            posture_status = "Poor"

        return posture_score, posture_status
    
    def draw_posture_analysis(self, frame, score, status):
        """Draw posture analysis overlay on frame"""
        colors = {
            "Good": (0, 255, 0),      # Green
            "Average": (0, 165, 255),  # Orange
            "Poor": (0, 0, 255),      # Red
            "No Detection": (128, 128, 128) # Gray
        }
        
        color = colors.get(status, (255, 255, 255))
        
        # Draw key landmarks if available
        if hasattr(self, 'last_results') and self.last_results and self.last_results.pose_landmarks:
            landmarks = self.last_results.pose_landmarks[0]
            height, width = frame.shape[:2]
            
            # Draw circles on Nose, Left Shoulder, Right Shoulder
            for idx in [0, 11, 12]:
                if idx < len(landmarks):
                    lm = landmarks[idx]
                    # Ensure validity of x and y
                    if hasattr(lm, 'x') and hasattr(lm, 'y'):
                        cx, cy = int(lm.x * width), int(lm.y * height)
                        cv2.circle(frame, (cx, cy), 6, color, -1)
                        cv2.circle(frame, (cx, cy), 8, (255, 255, 255), 2)
            
            # Draw line between shoulders if both found
            if len(landmarks) > 12:
                ls = landmarks[11]
                rs = landmarks[12]
                if hasattr(ls, 'x') and hasattr(rs, 'x'):
                    cx1, cy1 = int(ls.x * width), int(ls.y * height)
                    cx2, cy2 = int(rs.x * width), int(rs.y * height)
                    cv2.line(frame, (cx1, cy1), (cx2, cy2), color, 3)

        cv2.putText(frame, f"Posture: {status}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        cv2.putText(frame, f"Score: {int(score)}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        height, width = frame.shape[:2]
        feedback_y = height - 30
        
        if status == "Good":
            feedback_text = "Keep it up! Great posture!"
        elif status == "Average":
            feedback_text = "Slight adjustment needed"
        elif status == "Poor":
            feedback_text = "Please adjust your posture"
        else:
            feedback_text = "Searching for posture..."
        
        cv2.putText(frame, feedback_text, (10, feedback_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return frame
    
    def update_camera_display(self, frame):
        """Update the camera display with the current frame"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image (safe in worker thread)
            pil_image = Image.fromarray(rgb_frame)
            # Resize to fit display (safe in worker thread)
            pil_image = pil_image.resize((640, 480), Image.Resampling.LANCZOS)
            # Create the PhotoImage and update UI (we are on Tk thread)
            photo_local = ImageTk.PhotoImage(pil_image)
            self.camera_display.configure(image=photo_local, text="")
            # Keep a reference on the widget to prevent GC
            self.camera_display.image = photo_local
            
        except Exception as e:
            print(f"Error updating camera display: {e}")
    
    def get_session_stats(self):
        """Get current session statistics"""
        if not self.session_start_time:
            return None
        
        duration = datetime.now() - self.session_start_time
        
        if not self.posture_scores:
            return {
                'duration': duration,
                'avg_score': 0,
                'current_status': 'Unknown'
            }
        
        return {
            'duration': duration,
            'avg_score': sum(self.posture_scores) / len(self.posture_scores),
            'current_status': self.current_posture,
            'score_count': len(self.posture_scores)
        }
