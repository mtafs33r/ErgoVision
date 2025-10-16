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

class PostureMonitor:
    def __init__(self, camera_frame, user_id, db_manager, posture_callback, session_callback):
        """Initialize posture monitor"""
        self.camera_frame = camera_frame
        self.user_id = user_id
        self.db_manager = db_manager
        self.posture_callback = posture_callback
        self.session_callback = session_callback
        
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
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
        # Aim for ~30 FPS
        try:
            self._after_job = self.camera_frame.after(33, self._schedule_next_frame)
        except Exception:
            # If scheduling fails, stop monitoring gracefully
            self.is_monitoring = False
    
    def analyze_posture(self, frame):
        """Analyze posture in the given frame"""
        # Convert to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # This is a simplified posture detection algorithm
        # In a real implementation, you would use pose estimation libraries like MediaPipe
        
        # For demonstration, we'll simulate posture detection based on image characteristics
        # This is a placeholder implementation
        
        # Calculate image variance (rough measure of movement/stability)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate brightness (can indicate head position relative to light)
        brightness = np.mean(gray)
        
        # Calculate edge density (can indicate posture alignment)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges) / (frame.shape[0] * frame.shape[1])
        
        # Simulate posture score based on these factors
        # This is a simplified algorithm - real implementation would be much more sophisticated
        
        # Normalize factors (these values are arbitrary for demonstration)
        variance_score = min(variance / 1000, 1.0)  # Higher variance = more movement = worse posture
        brightness_score = 1.0 - abs(brightness - 127) / 127  # Optimal brightness around middle
        edge_score = min(edge_density * 100, 1.0)  # Moderate edge density is good
        
        # Combine scores (weights are arbitrary)
        posture_score = (variance_score * 0.3 + brightness_score * 0.4 + edge_score * 0.3) * 100
        
        # Add some randomness to make it more realistic
        posture_score += np.random.normal(0, 5)
        posture_score = max(0, min(100, posture_score))  # Clamp to 0-100
        
        # Determine posture status
        if posture_score >= 80:
            posture_status = "Good"
        elif posture_score >= 60:
            posture_status = "Average"
        else:
            posture_status = "Poor"
        
        return posture_score, posture_status
    
    def draw_posture_analysis(self, frame, score, status):
        """Draw posture analysis overlay on frame"""
        # Define colors for different posture states
        colors = {
            "Good": (0, 255, 0),      # Green
            "Average": (0, 165, 255),  # Orange
            "Poor": (0, 0, 255)       # Red
        }
        
        color = colors.get(status, (255, 255, 255))
        
        # Draw posture status
        cv2.putText(frame, f"Posture: {status}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Draw score
        cv2.putText(frame, f"Score: {int(score)}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Draw posture indicator circle
        center = (frame.shape[1] - 50, 50)
        radius = 20
        
        # Circle color based on posture
        cv2.circle(frame, center, radius, color, -1)
        
        # Add status text next to circle
        cv2.putText(frame, status, (center[0] + 35, center[1] + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Draw posture guidelines (simplified)
        height, width = frame.shape[:2]
        
        # Draw center line
        cv2.line(frame, (width//2, 0), (width//2, height), (128, 128, 128), 1)
        
        # Draw horizontal guideline at 1/3 height (suggested eye level)
        guideline_y = height // 3
        cv2.line(frame, (0, guideline_y), (width, guideline_y), (128, 128, 128), 1)
        
        # Draw posture feedback text
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
