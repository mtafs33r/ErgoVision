"""
ErgoVision - AI Posture & Health Coach Desktop Application
Main entry point for the application
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth import AuthWindow
from dashboard import DashboardWindow
from database import DatabaseManager
from voice_assistant import voice_assistant
from daily_quotes import daily_quotes

class ErgoVisionApp:
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue") # We will override specific colors in dashboard.py
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Check if user is already logged in (remember me functionality)
        self.current_user = self.check_remembered_user()
        
        if self.current_user:
            self.show_dashboard()
        else:
            self.show_auth()
    
    def check_remembered_user(self):
        """Check if there's a remembered user session"""
        try:
            # Check for remember me token or session
            # This is a simplified implementation
            return None
        except:
            return None
    
    def show_auth(self):
        """Show authentication window"""
        self.auth_window = AuthWindow(self.on_auth_success)
    
    def show_dashboard(self):
        """Show dashboard window after successful authentication"""
        print(f"Creating dashboard for user: {self.current_user['username']}")
        self.dashboard_window = DashboardWindow(self.current_user, self.db_manager)
        print("Dashboard window created successfully")
    
    def on_auth_success(self, user_data):
        """Callback for successful authentication"""
        self.current_user = user_data
        if hasattr(self, 'auth_window'):
            self.auth_window.destroy()
        
        # Welcome message with voice
        if voice_assistant.is_available():
            voice_assistant.speak_welcome(user_data['username'])
        
        self.show_dashboard()

def main():
    """Main function to run the application"""
    try:
        app = ErgoVisionApp()
        
        # Start the appropriate mainloop based on which window is active
        if hasattr(app, 'dashboard_window') and app.dashboard_window:
            print("Starting dashboard mainloop...")
            app.dashboard_window.mainloop()
        elif hasattr(app, 'auth_window') and app.auth_window:
            print("Starting auth window mainloop...")
            app.auth_window.mainloop()
        else:
            print("No active window found, creating fallback...")
            # Create a temporary window to keep the app running
            temp_window = ctk.CTk()
            temp_window.withdraw()  # Hide the window
            temp_window.mainloop()
    except Exception as e:
        print(f"Error in main: {e}")
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()
