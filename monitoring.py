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
        alert_threshold_minutes: float = 2.0,
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
        
        # Setup MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
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
                self._poor_posture_start = datetime.now()
            else:
                streak_seconds = (
                    datetime.now() - self._poor_posture_start
                ).total_seconds()

                if streak_seconds >= self.alert_threshold_seconds:
                    # Cooldown = same as threshold so we don't spam
                    if self._notification_sender.can_send(
                        int(self.alert_threshold_seconds)
                    ):
                        minutes = int(self.alert_threshold_seconds // 60)
                        self._notification_sender.send_posture_alert(
                            message=(
                                f"Your posture has been poor for {minutes} minute"
                                f"{'s' if minutes != 1 else ''}. "
                                "Sit up straight and take a break! 🪑"
                            ),
                            severity="warning",
                        )
                        # Reset streak so the timer restarts after the alert
                        self._poor_posture_start = datetime.now()
        else:
            # Posture is Good or Average — reset the streak
            self._poor_posture_start = None
    def analyze_posture(self, frame):
        """Analyze posture in the given frame using MediaPipe"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.pose.process(rgb_frame)
        self.last_results = results
        rgb_frame.flags.writeable = True

        posture_score = 100.0

        if not results.pose_landmarks:
            return 0, "Poor"
        
        landmarks = results.pose_landmarks.landmark
        
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]

        # 1. Shoulder Level (y-axis alignment)
        shoulder_y_diff = abs(left_shoulder.y - right_shoulder.y)
        if shoulder_y_diff > 0.03:
            posture_score -= (shoulder_y_diff - 0.03) * 500

        # 2. Neck alignment (nose x vs mid-shoulder x)
        mid_shoulder_x = (left_shoulder.x + right_shoulder.x) / 2.0
        neck_x_diff = abs(nose.x - mid_shoulder_x)
        if neck_x_diff > 0.05:
            posture_score -= (neck_x_diff - 0.05) * 400
            
        # 3. Forward head tracking (Z depth)
        mid_shoulder_z = (left_shoulder.z + right_shoulder.z) / 2.0
        head_depth = nose.z - mid_shoulder_z
        if head_depth < -0.15:
            posture_score -= (abs(head_depth) - 0.15) * 200

        posture_score = max(0, min(100, posture_score))

        if posture_score >= 80:
            posture_status = "Good"
        elif posture_score >= 60:
            posture_status = "Average"
        else:
            posture_status = "Poor"

        return posture_score, posture_status
    
    def draw_posture_analysis(self, frame, score, status):
        """Draw posture analysis overlay on frame"""
        colors = {
            "Good": (0, 255, 0),      # Green
            "Average": (0, 165, 255),  # Orange
            "Poor": (0, 0, 255)       # Red
        }
        
        color = colors.get(status, (255, 255, 255))
        
        # Draw MediaPipe landmarks if available
        if hasattr(self, 'last_results') and self.last_results and self.last_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                self.last_results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(255,255,255), thickness=2, circle_radius=2),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(color=color, thickness=2)
            )

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
        else:
            feedback_text = "Please adjust your posture"
        
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
