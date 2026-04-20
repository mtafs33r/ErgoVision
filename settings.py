"""
Settings panel for ErgoVision application
Handles user preferences and configuration
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime
from typing import Dict, Callable

class SettingsWindow:
    def __init__(self, user_data, db_manager, dashboard_callback=None):
        """Initialize settings window"""
        self.user_data = user_data
        self.db_manager = db_manager
        self.dashboard_callback = dashboard_callback
        
        # Load current settings
        self.current_settings = self.db_manager.get_user_settings(user_data['id'])
        
        # Create window
        self.window = ctk.CTkToplevel()
        self.window.title("ErgoVision - Settings")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Setup UI
        self.setup_ui()
        
        # Load settings into UI
        self.load_settings()
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup the settings UI"""
        # Main container
        main_frame = ctk.CTkScrollableFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="Settings",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(0, 30))
        
        # Appearance section
        self.create_appearance_section(main_frame)
        
        # Notifications section
        self.create_notifications_section(main_frame)
        
        # Mobile Notifications section
        self.create_mobile_notifications_section(main_frame)
        
        # Profile section
        self.create_profile_section(main_frame)
        
        # Account section
        self.create_account_section(main_frame)
        
        # About section
        self.create_about_section(main_frame)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=30)
        
        # Save button
        self.save_btn = ctk.CTkButton(
            buttons_frame,
            text="Save Settings",
            width=150,
            height=40,
            command=self.save_settings
        )
        self.save_btn.pack(side="left", padx=(0, 10))
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            width=150,
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=self.window.destroy
        )
        self.cancel_btn.pack(side="left", padx=(0, 10))
        
        # Reset button
        self.reset_btn = ctk.CTkButton(
            buttons_frame,
            text="Reset to Defaults",
            width=150,
            height=40,
            fg_color="#FF6B6B",
            hover_color="#FF5252",
            command=self.reset_settings
        )
        self.reset_btn.pack(side="right")
    
    def create_appearance_section(self, parent):
        """Create appearance settings section"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Section title
        ctk.CTkLabel(
            section_frame,
            text="Appearance",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))
        
        # Dark mode toggle
        dark_mode_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        dark_mode_frame.pack(fill="x", padx=20, pady=5)
        
        self.dark_mode_var = tk.BooleanVar()
        self.dark_mode_checkbox = ctk.CTkCheckBox(
            dark_mode_frame,
            text="Dark Mode",
            variable=self.dark_mode_var
        )
        self.dark_mode_checkbox.pack(side="left")
        
        ctk.CTkLabel(
            dark_mode_frame,
            text="Toggle between light and dark theme",
            font=ctk.CTkFont(size=12)
        ).pack(side="right")
        
        section_frame.pack_configure(pady=(0, 20))
    
    def create_notifications_section(self, parent):
        """Create notifications settings section"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Section title
        ctk.CTkLabel(
            section_frame,
            text="Notifications",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))
        
        # Enable notifications
        notifications_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        notifications_frame.pack(fill="x", padx=20, pady=5)
        
        self.notifications_var = tk.BooleanVar()
        self.notifications_checkbox = ctk.CTkCheckBox(
            notifications_frame,
            text="Enable Notifications",
            variable=self.notifications_var
        )
        self.notifications_checkbox.pack(side="left")
        
        ctk.CTkLabel(
            notifications_frame,
            text="Receive posture reminders",
            font=ctk.CTkFont(size=12)
        ).pack(side="right")
        
        # Reminder interval
        interval_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        interval_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            interval_frame,
            text="Reminder Interval:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")
        
        self.interval_var = tk.StringVar()
        self.interval_dropdown = ctk.CTkOptionMenu(
            interval_frame,
            values=["15 minutes", "30 minutes", "45 minutes", "60 minutes", "90 minutes"],
            variable=self.interval_var
        )
        self.interval_dropdown.pack(side="right")
    
    def create_mobile_notifications_section(self, parent):
        """Create mobile push notifications settings section"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 20))

        # Section title
        ctk.CTkLabel(
            section_frame,
            text="📱 Mobile Push Notifications",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            section_frame,
            text="Sends an alert to your phone when poor posture persists",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 15))

        # Enable toggle
        mobile_notif_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        mobile_notif_frame.pack(fill="x", padx=20, pady=5)

        self.mobile_notifications_var = tk.BooleanVar()
        self.mobile_notifications_checkbox = ctk.CTkCheckBox(
            mobile_notif_frame,
            text="Enable Mobile Push Alerts",
            variable=self.mobile_notifications_var
        )
        self.mobile_notifications_checkbox.pack(side="left")

        ctk.CTkLabel(
            mobile_notif_frame,
            text="Notify my phone via Expo",
            font=ctk.CTkFont(size=12)
        ).pack(side="right")

        # Threshold dropdown
        threshold_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        threshold_frame.pack(fill="x", padx=20, pady=(5, 20))

        ctk.CTkLabel(
            threshold_frame,
            text="Alert After Bad Posture for:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")

        self.posture_threshold_var = tk.StringVar()
        self.posture_threshold_dropdown = ctk.CTkOptionMenu(
            threshold_frame,
            values=["1 minute", "2 minutes", "3 minutes", "5 minutes"],
            variable=self.posture_threshold_var
        )
        self.posture_threshold_dropdown.pack(side="right")
    
    def create_profile_section(self, parent):
        """Create profile settings section"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Section title
        ctk.CTkLabel(
            section_frame,
            text="Profile Information",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))
        
        # Load profile data
        profile = self.db_manager.get_user_profile(self.user_data['id'])
        
        # Name
        name_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            name_frame,
            text="Full Name:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")
        
        self.profile_name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="Enter your full name",
            width=200
        )
        self.profile_name_entry.pack(side="right")
        
        if profile and profile.get('name'):
            self.profile_name_entry.insert(0, profile['name'])
        
        # Email (read-only)
        email_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        email_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            email_frame,
            text="Email:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")
        
        email_label = ctk.CTkLabel(
            email_frame,
            text=self.user_data['email'],
            font=ctk.CTkFont(size=14)
        )
        email_label.pack(side="right")
    
    def create_account_section(self, parent):
        """Create account settings section"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Section title
        ctk.CTkLabel(
            section_frame,
            text="Account Security",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))
        
        # Change password button
        self.change_password_btn = ctk.CTkButton(
            section_frame,
            text="Change Password",
            width=200,
            height=35,
            command=self.change_password
        )
        self.change_password_btn.pack(pady=(0, 20))
        
        # Export data button
        self.export_data_btn = ctk.CTkButton(
            section_frame,
            text="Export My Data",
            width=200,
            height=35,
            command=self.export_user_data
        )
        self.export_data_btn.pack(pady=(0, 20))
        
        # Delete account button
        self.delete_account_btn = ctk.CTkButton(
            section_frame,
            text="Delete Account",
            width=200,
            height=35,
            fg_color="#FF6B6B",
            hover_color="#FF5252",
            command=self.delete_account
        )
        self.delete_account_btn.pack(pady=(0, 20))
    
    def create_about_section(self, parent):
        """Create about section"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Section title
        ctk.CTkLabel(
            section_frame,
            text="About",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))
        
        # App info
        info_text = """ErgoVision - AI Posture & Health Coach
        
Version: 1.0.0
Developed with Python and CustomTkinter

Features:
• Real-time posture monitoring
• AI-powered health coaching
• Comprehensive analytics
• Smart reminders
• Personalized tips

For support or feedback, please contact us."""
        
        info_label = ctk.CTkLabel(
            section_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.pack(padx=20, pady=(0, 20))
    
    def load_settings(self):
        """Load current settings into UI"""
        # Appearance
        self.dark_mode_var.set(self.current_settings['dark_mode'])
        
        # Notifications
        self.notifications_var.set(self.current_settings['notifications_enabled'])
        
        # Reminder interval
        interval_minutes = self.current_settings['reminder_interval']
        interval_options = {
            15: "15 minutes",
            30: "30 minutes", 
            45: "45 minutes",
            60: "60 minutes",
            90: "90 minutes"
        }
        self.interval_var.set(interval_options.get(interval_minutes, "30 minutes"))

        # Mobile push notifications
        self.mobile_notifications_var.set(
            self.current_settings.get('mobile_notifications_enabled', True)
        )
        threshold_minutes = self.current_settings.get('posture_alert_threshold_minutes', 2)
        threshold_options = {
            1: "1 minute",
            2: "2 minutes",
            3: "3 minutes",
            5: "5 minutes",
        }
        self.posture_threshold_var.set(
            threshold_options.get(threshold_minutes, "2 minutes")
        )
    
    def save_settings(self):
        """Save settings to database"""
        try:
            # Parse threshold string back to int
            threshold_str = self.posture_threshold_var.get()  # e.g. "2 minutes"
            threshold_minutes = int(threshold_str.split()[0])

            # Collect settings
            new_settings = {
                'dark_mode': self.dark_mode_var.get(),
                'notifications_enabled': self.notifications_var.get(),
                'reminder_interval': int(self.interval_var.get().split()[0]),
                'mobile_notifications_enabled': self.mobile_notifications_var.get(),
                'posture_alert_threshold_minutes': threshold_minutes,
            }
            
            # Save to database
            success = self.db_manager.update_user_settings(self.user_data['id'], new_settings)
            
            if success:
                # Update profile if name changed
                new_name = self.profile_name_entry.get().strip()
                if new_name:
                    profile_data = {'name': new_name}
                    self.db_manager.update_user_profile(self.user_data['id'], profile_data)
                
                # Notify dashboard of changes
                if self.dashboard_callback:
                    self.dashboard_callback.update_settings(new_settings)
                
                messagebox.showinfo("Success", "Settings saved successfully!")
                self.window.destroy()
            else:
                messagebox.showerror("Error", "Failed to save settings")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        result = messagebox.askyesno(
            "Confirm Reset",
            "Are you sure you want to reset all settings to default values?"
        )
        
        if result:
            # Reset to defaults
            self.dark_mode_var.set(True)
            self.notifications_var.set(True)
            self.interval_var.set("30 minutes")
            
            messagebox.showinfo("Success", "Settings reset to defaults")
    
    def change_password(self):
        """Open change password dialog"""
        dialog = ChangePasswordDialog(self.window, self.user_data, self.db_manager)
        self.window.wait_window(dialog.window)
    
    def export_user_data(self):
        """Export user data"""
        try:
            from tkinter import filedialog
            import json
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export User Data"
            )
            
            if filename:
                # Collect user data
                profile = self.db_manager.get_user_profile(self.user_data['id'])
                sessions = self.db_manager.get_posture_sessions(self.user_data['id'])
                settings = self.db_manager.get_user_settings(self.user_data['id'])
                
                export_data = {
                    'user_info': {
                        'username': self.user_data['username'],
                        'email': self.user_data['email']
                    },
                    'profile': profile,
                    'sessions': sessions,
                    'settings': settings,
                    'export_date': str(datetime.now())
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def delete_account(self):
        """Delete user account"""
        result = messagebox.askyesno(
            "Confirm Account Deletion",
            "Are you sure you want to delete your account?\n\nThis action cannot be undone and all your data will be permanently lost.",
            icon="warning"
        )
        
        if result:
            # Additional confirmation
            confirm_result = messagebox.askyesno(
                "Final Confirmation",
                "This is your final warning. Your account and all data will be permanently deleted. Are you absolutely sure?",
                icon="error"
            )
            
            if confirm_result:
                messagebox.showinfo(
                    "Account Deletion",
                    "Account deletion functionality would be implemented here.\n\nFor security reasons, please contact support to delete your account."
                )

class ChangePasswordDialog:
    def __init__(self, parent, user_data, db_manager):
        """Initialize change password dialog"""
        self.user_data = user_data
        self.db_manager = db_manager
        
        # Create dialog window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Change Password")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center window
        self.center_window()
        
        # Setup UI
        self.setup_ui()
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="Change Password",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Current password
        ctk.CTkLabel(
            main_frame,
            text="Current Password:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 5))
        
        self.current_password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter current password",
            width=300,
            height=35,
            show="*"
        )
        self.current_password_entry.pack(pady=(0, 15))
        
        # New password
        ctk.CTkLabel(
            main_frame,
            text="New Password:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 5))
        
        self.new_password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter new password",
            width=300,
            height=35,
            show="*"
        )
        self.new_password_entry.pack(pady=(0, 15))
        
        # Confirm password
        ctk.CTkLabel(
            main_frame,
            text="Confirm New Password:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 5))
        
        self.confirm_password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Confirm new password",
            width=300,
            height=35,
            show="*"
        )
        self.confirm_password_entry.pack(pady=(0, 20))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 20))
        
        # Change button
        self.change_btn = ctk.CTkButton(
            buttons_frame,
            text="Change Password",
            width=150,
            height=35,
            command=self.change_password
        )
        self.change_btn.pack(side="left", padx=(0, 10))
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            width=150,
            height=35,
            fg_color="gray",
            hover_color="darkgray",
            command=self.window.destroy
        )
        self.cancel_btn.pack(side="left")
    
    def change_password(self):
        """Handle password change"""
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if len(new_password) < 6:
            messagebox.showerror("Error", "New password must be at least 6 characters long")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords do not match")
            return
        
        # Verify current password
        user_data = self.db_manager.authenticate_user(self.user_data['username'], current_password)
        if not user_data:
            messagebox.showerror("Error", "Current password is incorrect")
            return
        
        # Update password (this would require a new method in database.py)
        # For now, show a message that this feature needs to be implemented
        messagebox.showinfo(
            "Password Change",
            "Password change functionality needs to be implemented in the database layer.\n\nFor now, please contact support to change your password."
        )
        
        self.window.destroy()
