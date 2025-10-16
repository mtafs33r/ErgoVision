"""
Voice Assistant for ErgoVision application
Provides audio feedback and notifications
"""

import pyttsx3
import threading
import queue
import time
from typing import Optional

class VoiceAssistant:
    def __init__(self):
        """Initialize voice assistant"""
        self.engine = None
        self.is_enabled = True
        self.voice_queue = queue.Queue()
        self.speaking_thread = None
        self.is_speaking = False
        
        # Initialize TTS engine
        try:
            self.engine = pyttsx3.init()
            self.setup_voice()
            self.start_speaking_thread()
        except Exception as e:
            print(f"Failed to initialize voice assistant: {e}")
            self.is_enabled = False
    
    def setup_voice(self):
        """Setup voice properties"""
        if not self.engine:
            return
        
        # Get available voices
        voices = self.engine.getProperty('voices')
        
        # Try to set a female voice if available
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        self.engine.setProperty('rate', 180)  # Speed of speech
        self.engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
    
    def start_speaking_thread(self):
        """Start the speaking thread"""
        if not self.is_enabled:
            return
        
        self.speaking_thread = threading.Thread(target=self.speaking_worker, daemon=True)
        self.speaking_thread.start()
    
    def speaking_worker(self):
        """Worker thread for speaking"""
        while True:
            try:
                # Get next message from queue
                message = self.voice_queue.get(timeout=1)
                
                if message is None:  # Shutdown signal
                    break
                
                self.speak_immediate(message)
                self.voice_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in speaking worker: {e}")
    
    def speak(self, text: str, priority: str = "normal"):
        """Add text to speaking queue"""
        if not self.is_enabled or not self.engine:
            return
        
        try:
            self.voice_queue.put(text)
        except Exception as e:
            print(f"Error adding text to voice queue: {e}")
    
    def speak_immediate(self, text: str):
        """Speak text immediately (blocking)"""
        if not self.is_enabled or not self.engine:
            return
        
        try:
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.is_speaking = False
        except Exception as e:
            print(f"Error speaking text: {e}")
            self.is_speaking = False
    
    def speak_posture_feedback(self, status: str, score: int):
        """Provide posture-specific feedback"""
        if not self.is_enabled:
            return
        
        if status == "Good":
            messages = [
                "Excellent posture! Keep it up!",
                "Great job maintaining good posture!",
                "Your posture looks perfect today!",
                "Outstanding! You're setting a great example!",
                "Perfect alignment! You're doing amazing!"
            ]
        elif status == "Average":
            messages = [
                "Good posture with room for improvement.",
                "You're doing well, just a small adjustment needed.",
                "Almost perfect! Just straighten up a bit.",
                "Good effort! Let's make it even better.",
                "You're on the right track! Just a little more."
            ]
        else:  # Poor
            messages = [
                "Time for a posture check! Please sit up straight.",
                "Let's improve that posture. Straighten your back.",
                "Remember to keep your shoulders back and spine straight.",
                "Posture reminder: Sit tall and proud!",
                "You've got this! Just adjust your position slightly."
            ]
        
        import random
        message = random.choice(messages)
        self.speak(message)
    
    def speak_session_summary(self, duration: str, score: int, rating: str):
        """Provide session summary feedback"""
        if not self.is_enabled:
            return
        
        if rating == "Excellent":
            message = f"Fantastic session! You maintained excellent posture for {duration} with a score of {score}. You're a posture champion!"
        elif rating == "Average":
            message = f"Good session! You monitored your posture for {duration} with a score of {score}. Keep practicing to improve!"
        else:  # Poor
            message = f"Session completed. You monitored for {duration} with a score of {score}. Don't worry, every session is progress!"
        
        self.speak(message)
    
    def speak_reminder(self):
        """Speak posture reminder"""
        if not self.is_enabled:
            return
        
        reminders = [
            "Time for a posture break! Stand up and stretch.",
            "Posture reminder: Take a moment to adjust your position.",
            "Break time! Stand up, stretch, and check your posture.",
            "Remember to maintain good posture and take breaks.",
            "It's time to move around and stretch your muscles!"
        ]
        
        import random
        message = random.choice(reminders)
        self.speak(message)
    
    def speak_daily_quote(self, quote: str):
        """Speak daily motivational quote"""
        if not self.is_enabled:
            return
        
        self.speak(f"Today's motivation: {quote}")
    
    def speak_tip(self, tip: str):
        """Speak health tip"""
        if not self.is_enabled:
            return
        
        # Extract just the main tip text (remove emojis and formatting)
        clean_tip = tip.replace("💡", "").replace("🌟", "").replace("👍", "").replace("💪", "")
        lines = clean_tip.split('\n')
        main_tip = lines[-1] if lines else tip
        
        self.speak(f"Health tip: {main_tip}")
    
    def speak_welcome(self, username: str):
        """Speak welcome message"""
        if not self.is_enabled:
            return
        
        welcome_messages = [
            f"Welcome back, {username}! Ready to improve your posture?",
            f"Hello {username}! Let's start another great posture session.",
            f"Good to see you, {username}! Time to focus on your health.",
            f"Welcome, {username}! Your posture journey continues today."
        ]
        
        import random
        message = random.choice(welcome_messages)
        self.speak(message)
    
    def speak_goodbye(self, username: str):
        """Speak goodbye message"""
        if not self.is_enabled:
            return
        
        goodbye_messages = [
            f"Take care, {username}! Remember to maintain good posture throughout your day.",
            f"See you next time, {username}! Keep up the great posture work.",
            f"Goodbye, {username}! Your health and posture are in good hands.",
            f"Until next time, {username}! Stay mindful of your posture."
        ]
        
        import random
        message = random.choice(goodbye_messages)
        self.speak(message)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable voice assistant"""
        self.is_enabled = enabled
        
        if not enabled and self.is_speaking:
            # Stop current speech
            try:
                self.engine.stop()
            except:
                pass
    
    def is_available(self) -> bool:
        """Check if voice assistant is available"""
        return self.is_enabled and self.engine is not None
    
    def shutdown(self):
        """Shutdown voice assistant"""
        self.is_enabled = False
        
        if self.engine:
            try:
                self.engine.stop()
                self.engine = None
            except:
                pass
        
        # Signal speaking thread to stop
        try:
            self.voice_queue.put(None)
        except:
            pass

# Global voice assistant instance
voice_assistant = VoiceAssistant()
