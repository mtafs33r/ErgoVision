"""
Simplified ErgoVision launcher with better error handling
"""

import sys
import os
import traceback
from tkinter import messagebox

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Simplified main function with better error handling"""
    try:
        print("Starting ErgoVision...")
        
        # Import required modules
        import customtkinter as ctk
        from database import DatabaseManager
        from auth import AuthWindow
        from dashboard import DashboardWindow
        
        print("✅ All modules imported successfully")
        
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize database
        print("Initializing database...")
        db_manager = DatabaseManager()
        print("✅ Database initialized")
        
        # Create a simple test user for demo
        print("Setting up demo user...")
        demo_user = {
            'id': 1,
            'username': 'demo',
            'email': 'demo@ergovision.com',
            'remember_me': False
        }
        
        # Try to authenticate demo user, create if doesn't exist
        user_data = db_manager.authenticate_user("demo", "demo123")
        if not user_data:
            print("Creating demo user...")
            db_manager.create_user("demo", "demo@ergovision.com", "demo123")
            user_data = db_manager.authenticate_user("demo", "demo123")
        
        if user_data:
            print(f"✅ Demo user ready: {user_data['username']}")
            
            # Show dashboard directly
            print("Opening dashboard...")
            dashboard = DashboardWindow(user_data, db_manager)
            print("✅ Dashboard opened successfully")
            
            # Start the main loop
            dashboard.mainloop()
        else:
            print("❌ Failed to setup demo user")
            messagebox.showerror("Error", "Failed to setup demo user")
            
    except Exception as e:
        error_msg = f"Failed to start application: {str(e)}"
        print(f"❌ {error_msg}")
        print("\nFull error traceback:")
        traceback.print_exc()
        
        # Show error message
        try:
            messagebox.showerror("ErgoVision Error", error_msg)
        except:
            print("Could not show error dialog")
        
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()



