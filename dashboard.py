"""
Dashboard window for ErgoVision application
Main interface with navigation and content areas
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
from datetime import datetime, timedelta
import json
import os

from monitoring import PostureMonitor
from ai_coach import AICoach
from reports import ReportsWindow
from settings import SettingsWindow
from hydration_tracker import HydrationTracker
from voice_assistant import voice_assistant
from daily_quotes import daily_quotes

class DashboardWindow:
    def __init__(self, user_data, db_manager):
        """Initialize dashboard window"""
        try:
            self.user_data = user_data
            self.db_manager = db_manager
            self.current_view = "home"
            
            # Create main window
            self.window = ctk.CTk()
            self.window.title("ErgoVision - Dashboard")
            self.window.geometry("1200x800")
            self.window.minsize(1000, 700)
            # Start maximized on Windows; otherwise center the window
            try:
                self.window.state("zoomed")
            except Exception:
                try:
                    self.center_window()
                except Exception:
                    pass
            
            # Load user settings
            try:
                self.settings = self.db_manager.get_user_settings(user_data['id'])
                if not self.settings:
                    # Default settings if none exist
                    self.settings = {
                        'dark_mode': True,
                        'notifications_enabled': True,
                        'reminder_interval': 30,
                        'hydration_reminders': True,
                        'hydration_goal': 2000
                    }
            except Exception as e:
                print(f"Error loading user settings: {e}")
                # Default settings if there's an error
                self.settings = {
                    'dark_mode': True,
                    'notifications_enabled': True,
                    'reminder_interval': 30,
                    'hydration_reminders': True,
                    'hydration_goal': 2000
                }
            
            self.apply_theme()
            
            # Initialize components
            self.posture_monitor = None
            self.ai_coach = AICoach(db_manager)
            self.reports_window = None
            self.settings_window = None
            
            # Setup UI
            self.setup_ui()
            
            # Load user profile
            self.load_user_profile()
            
            # Start reminder system
            self.start_reminder_system()
            
            # Show the window
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            
            print(f"Dashboard initialized successfully for user: {user_data['username']}")
            
        except Exception as e:
            print(f"Error initializing dashboard: {e}")
            import traceback
            traceback.print_exc()
            raise

    def center_window(self, width: int | None = None, height: int | None = None):
        """Center window on the screen with optional width/height.
        If width/height not provided, use current or default size.
        """
        try:
            self.window.update_idletasks()
            current_width = self.window.winfo_width() if self.window.winfo_width() > 1 else 1200
            current_height = self.window.winfo_height() if self.window.winfo_height() > 1 else 800
            win_w = width if width else current_width
            win_h = height if height else current_height
            screen_w = self.window.winfo_screenwidth()
            screen_h = self.window.winfo_screenheight()
            pos_x = max((screen_w - win_w) // 2, 0)
            pos_y = max((screen_h - win_h) // 2, 0)
            self.window.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        except Exception:
            pass
    
    def apply_theme(self):
        """Apply theme based on user settings"""
        try:
            if self.settings and self.settings.get('dark_mode', True):
                ctk.set_appearance_mode("dark")
            else:
                ctk.set_appearance_mode("light")
        except Exception as e:
            print(f"Error applying theme: {e}")
            # Default to dark mode if there's an error
            ctk.set_appearance_mode("dark")
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Configure grid weights
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.create_sidebar()
        
        # Main content area
        self.create_main_content()
        
        # Top bar
        self.create_top_bar()
    
    def create_sidebar(self):
        """Create sidebar navigation"""
        self.sidebar = ctk.CTkFrame(self.window, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)
        
        # App logo/title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="ErgoVision",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        # Navigation buttons
        nav_items = [
            ("Home", "home"),
            ("Monitoring", "monitoring"),
            ("AI Coach", "ai_coach"),
            ("Hydration", "hydration"),
            ("Reports", "reports"),
            ("Settings", "settings")
        ]
        
        self.nav_buttons = {}
        for i, (text, view) in enumerate(nav_items, 1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=160,
                height=40,
                command=lambda v=view: self.switch_view(v)
            )
            btn.grid(row=i, column=0, padx=20, pady=10)
            self.nav_buttons[view] = btn
        
        # Logout button
        self.logout_btn = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            width=160,
            height=40,
            fg_color="#FF6B6B",
            hover_color="#FF5252",
            command=self.logout
        )
        self.logout_btn.grid(row=8, column=0, padx=20, pady=20)
    
    def create_top_bar(self):
        """Create top navigation bar"""
        self.top_bar = ctk.CTkFrame(self.window, height=60, corner_radius=0)
        self.top_bar.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=(20, 0))
        self.top_bar.grid_columnconfigure(1, weight=1)
        
        # Current date and time
        self.datetime_label = ctk.CTkLabel(
            self.top_bar,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.datetime_label.grid(row=0, column=0, padx=20, pady=15)
        
        # User info
        self.user_label = ctk.CTkLabel(
            self.top_bar,
            text=f"Welcome, {self.user_data['username']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.user_label.grid(row=0, column=2, padx=20, pady=15)
        
        # Update datetime
        self.update_datetime()
    
    def create_main_content(self):
        """Create main content area"""
        self.content_frame = ctk.CTkFrame(self.window)
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=(0, 20))
        
        # Create different views
        self.views = {}
        self.create_home_view()
        self.create_monitoring_view()
        self.create_ai_coach_view()
        self.create_hydration_view()
        self.create_reports_view()
        self.create_settings_view()
        
        # Show home view by default
        self.switch_view("home")
    
    def create_home_view(self):
        """Create home/dashboard view"""
        home_frame = ctk.CTkFrame(self.content_frame)
        
        # Title
        title = ctk.CTkLabel(
            home_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(30, 20))
        
        # Profile form
        profile_frame = ctk.CTkFrame(home_frame)
        profile_frame.pack(pady=(0, 20), padx=30, fill="x")
        
        ctk.CTkLabel(
            profile_frame,
            text="Personal Information",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))
        
        # Form fields in grid
        form_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        form_frame.pack(pady=(0, 20), padx=20)
        
        # Row 1
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        self.name_entry = ctk.CTkEntry(
            row1,
            placeholder_text="Full Name",
            width=200,
            height=35
        )
        self.name_entry.pack(side="left", padx=(0, 10))
        
        self.age_entry = ctk.CTkEntry(
            row1,
            placeholder_text="Age",
            width=100,
            height=35
        )
        self.age_entry.pack(side="left", padx=(0, 10))
        
        # Row 2
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self.height_entry = ctk.CTkEntry(
            row2,
            placeholder_text="Height (cm)",
            width=150,
            height=35
        )
        self.height_entry.pack(side="left", padx=(0, 10))
        
        self.weight_entry = ctk.CTkEntry(
            row2,
            placeholder_text="Weight (kg)",
            width=150,
            height=35
        )
        self.weight_entry.pack(side="left", padx=(0, 10))
        
        # Row 3
        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        self.gender_var = tk.StringVar(value="Male")
        self.gender_dropdown = ctk.CTkOptionMenu(
            row3,
            values=["Male", "Female", "Other"],
            variable=self.gender_var,
            width=150,
            height=35
        )
        self.gender_dropdown.pack(side="left", padx=(0, 10))
        
        self.setup_var = tk.StringVar(value="Desktop")
        self.setup_dropdown = ctk.CTkOptionMenu(
            row3,
            values=["Laptop", "Desktop", "Standing Desk"],
            variable=self.setup_var,
            width=150,
            height=35
        )
        self.setup_dropdown.pack(side="left", padx=(0, 10))
        
        # Save button
        self.save_btn = ctk.CTkButton(
            profile_frame,
            text="Save Information",
            width=200,
            height=40,
            command=self.save_profile
        )
        self.save_btn.pack(pady=(0, 20))
        
        # BMI display
        self.bmi_frame = ctk.CTkFrame(home_frame)
        self.bmi_frame.pack(pady=(0, 20), padx=30, fill="x")
        
        ctk.CTkLabel(
            self.bmi_frame,
            text="BMI Information",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))
        
        self.bmi_label = ctk.CTkLabel(
            self.bmi_frame,
            text="Enter height and weight to calculate BMI",
            font=ctk.CTkFont(size=16)
        )
        self.bmi_label.pack(pady=(0, 20))
        
        # Bind BMI calculation to weight/height changes
        self.height_entry.bind('<KeyRelease>', self.calculate_bmi)
        self.weight_entry.bind('<KeyRelease>', self.calculate_bmi)
        
        # Stats overview
        stats_frame = ctk.CTkFrame(home_frame)
        stats_frame.pack(pady=(0, 20), padx=30, fill="x")
        
        ctk.CTkLabel(
            stats_frame,
            text="Quick Stats",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))
        
        # Stats grid
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(pady=(0, 20), padx=20)
        
        # Recent sessions
        self.recent_sessions_label = ctk.CTkLabel(
            stats_grid,
            text="Recent Sessions: 0",
            font=ctk.CTkFont(size=14)
        )
        self.recent_sessions_label.pack(pady=5)
        
        # Average score
        self.avg_score_label = ctk.CTkLabel(
            stats_grid,
            text="Average Score: N/A",
            font=ctk.CTkFont(size=14)
        )
        self.avg_score_label.pack(pady=5)
        
        # Best score
        self.best_score_label = ctk.CTkLabel(
            stats_grid,
            text="Best Score: N/A",
            font=ctk.CTkFont(size=14)
        )
        self.best_score_label.pack(pady=5)
        
        # Daily quote section
        quote_frame = ctk.CTkFrame(home_frame)
        quote_frame.pack(pady=(0, 20), padx=30, fill="x")
        
        ctk.CTkLabel(
            quote_frame,
            text="Daily Inspiration",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))
        
        self.daily_quote_label = ctk.CTkLabel(
            quote_frame,
            text="",
            font=ctk.CTkFont(size=14),
            wraplength=600,
            justify="center"
        )
        self.daily_quote_label.pack(pady=(0, 20))
        
        # Load daily quote
        self.load_daily_quote()
        
        self.views["home"] = home_frame
    
    def create_monitoring_view(self):
        """Create posture monitoring view"""
        monitoring_frame = ctk.CTkFrame(self.content_frame)
        
        # Title
        title = ctk.CTkLabel(
            monitoring_frame,
            text="Posture Monitoring",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(30, 20))
        
        # Camera preview frame
        self.camera_frame = ctk.CTkFrame(monitoring_frame, width=640, height=480)
        self.camera_frame.pack(pady=(0, 20))
        
        # Camera placeholder
        self.camera_placeholder = ctk.CTkLabel(
            self.camera_frame,
            text="Camera Preview\nWill appear here when monitoring starts",
            font=ctk.CTkFont(size=16),
            width=640,
            height=480
        )
        self.camera_placeholder.pack(expand=True)
        
        # Controls frame
        controls_frame = ctk.CTkFrame(monitoring_frame)
        controls_frame.pack(pady=(0, 20), padx=30, fill="x")
        
        # Start/Stop monitoring button
        self.monitor_btn = ctk.CTkButton(
            controls_frame,
            text="Start Monitoring",
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.toggle_monitoring
        )
        self.monitor_btn.pack(pady=20)
        
        # Status frame
        status_frame = ctk.CTkFrame(monitoring_frame)
        status_frame.pack(pady=(0, 20), padx=30, fill="x")
        
        ctk.CTkLabel(
            status_frame,
            text="Current Status",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Not Monitoring",
            font=ctk.CTkFont(size=16)
        )
        self.status_label.pack(pady=(0, 15))
        
        # Session info
        session_frame = ctk.CTkFrame(monitoring_frame)
        session_frame.pack(pady=(0, 20), padx=30, fill="x")
        
        ctk.CTkLabel(
            session_frame,
            text="Session Information",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        self.duration_label = ctk.CTkLabel(
            session_frame,
            text="Duration: 0:00",
            font=ctk.CTkFont(size=14)
        )
        self.duration_label.pack(pady=2)
        
        self.score_label = ctk.CTkLabel(
            session_frame,
            text="Current Score: N/A",
            font=ctk.CTkFont(size=14)
        )
        self.score_label.pack(pady=(2, 15))
        
        self.views["monitoring"] = monitoring_frame
    
    def create_ai_coach_view(self):
        """Create AI coach view"""
        coach_frame = ctk.CTkFrame(self.content_frame)
        
        # Title
        title = ctk.CTkLabel(
            coach_frame,
            text="AI Health Coach",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(30, 20))
        
        # Tips frame
        tips_frame = ctk.CTkFrame(coach_frame)
        tips_frame.pack(pady=(0, 20), padx=30, fill="both", expand=True)
        
        ctk.CTkLabel(
            tips_frame,
            text="Personalized Health Tips",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))
        
        # Tip display
        self.tip_text = ctk.CTkTextbox(
            tips_frame,
            width=600,
            height=300,
            font=ctk.CTkFont(size=14)
        )
        self.tip_text.pack(pady=(0, 20), padx=20)
        
        # Get new tip button
        self.new_tip_btn = ctk.CTkButton(
            tips_frame,
            text="Get New Tip",
            width=200,
            height=40,
            command=self.get_new_tip
        )
        self.new_tip_btn.pack(pady=(0, 20))
        
        # Load initial tip only if profile is available
        try:
            profile = self.db_manager.get_user_profile(self.user_data['id'])
            if profile and profile.get('height') and profile.get('weight'):
                self.get_new_tip()
            else:
                self.tip_text.delete("1.0", "end")
                self.tip_text.insert("1.0", "Please complete your profile in the Dashboard tab to get personalized AI tips!")
        except:
            self.tip_text.delete("1.0", "end")
            self.tip_text.insert("1.0", "Please complete your profile in the Dashboard tab to get personalized AI tips!")
        
        self.views["ai_coach"] = coach_frame
    
    def create_hydration_view(self):
        """Create hydration tracking view"""
        hydration_frame = ctk.CTkFrame(self.content_frame)
        
        # Initialize hydration tracker
        self.hydration_tracker = HydrationTracker(hydration_frame, self.user_data, self.db_manager)
        
        self.views["hydration"] = hydration_frame
    
    def create_reports_view(self):
        """Create reports and analytics view"""
        reports_frame = ctk.CTkFrame(self.content_frame)
        
        # Title
        title = ctk.CTkLabel(
            reports_frame,
            text="Reports & Analytics",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(30, 20))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(reports_frame)
        buttons_frame.pack(pady=(0, 20), padx=30, fill="x")
        
        self.view_reports_btn = ctk.CTkButton(
            buttons_frame,
            text="View Detailed Reports",
            width=200,
            height=40,
            command=self.open_reports_window
        )
        self.view_reports_btn.pack(pady=20)
        
        # Quick stats
        quick_stats_frame = ctk.CTkFrame(reports_frame)
        quick_stats_frame.pack(pady=(0, 20), padx=30, fill="x")
        
        ctk.CTkLabel(
            quick_stats_frame,
            text="Quick Overview",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))
        
        # Stats will be populated by load_stats method
        self.stats_display_frame = ctk.CTkFrame(quick_stats_frame, fg_color="transparent")
        self.stats_display_frame.pack(pady=(0, 20), padx=20)
        
        self.views["reports"] = reports_frame
    
    def create_settings_view(self):
        """Create settings view"""
        settings_frame = ctk.CTkFrame(self.content_frame)
        
        # Title
        title = ctk.CTkLabel(
            settings_frame,
            text="Settings",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(30, 20))
        
        # Open settings window button
        self.open_settings_btn = ctk.CTkButton(
            settings_frame,
            text="Open Settings Panel",
            width=200,
            height=40,
            command=self.open_settings_window
        )
        self.open_settings_btn.pack(pady=50)
        
        self.views["settings"] = settings_frame
    
    def switch_view(self, view_name):
        """Switch between different views"""
        # Hide all views
        for view in self.views.values():
            view.pack_forget()
        
        # Show selected view
        self.views[view_name].pack(fill="both", expand=True)
        
        # Update navigation buttons
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color="#3A7FF6")
            else:
                btn.configure(fg_color=("gray75", "gray25"))
        
        self.current_view = view_name
        
        # Load view-specific data
        if view_name == "home":
            self.load_stats()
        elif view_name == "reports":
            self.load_stats()
    
    def update_datetime(self):
        """Update date and time display"""
        now = datetime.now()
        self.datetime_label.configure(text=now.strftime("%B %d, %Y - %I:%M %p"))
        self.window.after(1000, self.update_datetime)
    
    def load_user_profile(self):
        """Load user profile data"""
        profile = self.db_manager.get_user_profile(self.user_data['id'])
        if profile:
            self.name_entry.insert(0, profile.get('name', ''))
            self.age_entry.insert(0, str(profile.get('age', '')) if profile.get('age') else '')
            self.height_entry.insert(0, str(profile.get('height', '')) if profile.get('height') else '')
            self.weight_entry.insert(0, str(profile.get('weight', '')) if profile.get('weight') else '')
            self.gender_var.set(profile.get('gender', 'Male'))
            self.setup_var.set(profile.get('desktop_setup', 'Desktop'))
            
            # Calculate BMI if height and weight are available
            if profile.get('height') and profile.get('weight'):
                self.calculate_bmi()
    
    def calculate_bmi(self, event=None):
        """Calculate and display BMI"""
        try:
            height = float(self.height_entry.get()) if self.height_entry.get() else 0
            weight = float(self.weight_entry.get()) if self.weight_entry.get() else 0
            
            if height > 0 and weight > 0:
                bmi, category = self.db_manager.calculate_bmi(height, weight)
                self.bmi_label.configure(
                    text=f"BMI: {bmi} ({category})",
                    text_color="#38E54D" if category == "Normal" else "#FF6B6B"
                )
            else:
                self.bmi_label.configure(text="Enter height and weight to calculate BMI")
        except ValueError:
            pass
    
    def save_profile(self):
        """Save user profile information"""
        profile_data = {
            'name': self.name_entry.get().strip(),
            'age': int(self.age_entry.get()) if self.age_entry.get().isdigit() else None,
            'height': float(self.height_entry.get()) if self.height_entry.get().replace('.', '').isdigit() else None,
            'weight': float(self.weight_entry.get()) if self.weight_entry.get().replace('.', '').isdigit() else None,
            'gender': self.gender_var.get(),
            'desktop_setup': self.setup_var.get()
        }
        
        success = self.db_manager.update_user_profile(self.user_data['id'], profile_data)
        
        if success:
            messagebox.showinfo("Success", "Profile information saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save profile information")
    
    def toggle_monitoring(self):
        """Toggle posture monitoring"""
        if self.posture_monitor is None or not self.posture_monitor.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start posture monitoring"""
        self.posture_monitor = PostureMonitor(
            self.camera_frame,
            self.user_data['id'],
            self.db_manager,
            self.on_posture_update,
            self.on_session_end
        )
        
        if self.posture_monitor.start():
            self.monitor_btn.configure(text="Stop Monitoring")
            self.status_label.configure(text="Monitoring Active")
        else:
            messagebox.showerror("Error", "Failed to start camera. Please check your camera connection.")
    
    def stop_monitoring(self):
        """Stop posture monitoring"""
        if self.posture_monitor:
            self.posture_monitor.stop()
            self.monitor_btn.configure(text="Start Monitoring")
            self.status_label.configure(text="Not Monitoring")
    
    def on_posture_update(self, status, score):
        """Callback for posture status updates"""
        colors = {
            "Good": "#38E54D",
            "Average": "#FFA500",
            "Poor": "#FF6B6B"
        }
        
        self.status_label.configure(
            text=f"Posture: {status}",
            text_color=colors.get(status, "#FFFFFF")
        )
        self.score_label.configure(text=f"Current Score: {score}")
        
        # Voice feedback for posture updates (throttled)
        if hasattr(self, 'last_voice_time'):
            time_since_last = datetime.now() - self.last_voice_time
            if time_since_last.total_seconds() > 30:  # Only speak every 30 seconds
                if voice_assistant.is_available():
                    voice_assistant.speak_posture_feedback(status, score)
                self.last_voice_time = datetime.now()
        else:
            self.last_voice_time = datetime.now()
    
    def on_session_end(self, duration, final_score, rating):
        """Callback for session end"""
        self.duration_label.configure(text=f"Duration: {duration}")
        self.score_label.configure(text=f"Final Score: {final_score} ({rating})")
        
        # Voice feedback for session summary
        if voice_assistant.is_available():
            voice_assistant.speak_session_summary(duration, final_score, rating)
        
        # Update stats
        self.load_stats()
    
    def get_new_tip(self):
        """Get new AI health tip"""
        try:
            profile = self.db_manager.get_user_profile(self.user_data['id'])
            sessions = self.db_manager.get_posture_sessions(self.user_data['id'], limit=10)
            
            # Ensure profile has required data
            if not profile or not profile.get('height') or not profile.get('weight'):
                self.tip_text.delete("1.0", "end")
                self.tip_text.insert("1.0", "Please complete your profile in the Dashboard tab to get personalized AI tips!")
                return
            
            tip = self.ai_coach.generate_tip(profile, sessions)
            
            self.tip_text.delete("1.0", "end")
            self.tip_text.insert("1.0", tip)
        except Exception as e:
            print(f"Error generating tip: {e}")
            self.tip_text.delete("1.0", "end")
            self.tip_text.insert("1.0", "Unable to generate tip at this time. Please try again later.")
    
    def load_stats(self):
        """Load and display quick stats"""
        sessions = self.db_manager.get_posture_sessions(self.user_data['id'], limit=50)
        
        if sessions:
            # Recent sessions count
            recent_count = len([s for s in sessions if 
                              datetime.fromisoformat(s['date'].replace('Z', '+00:00')).date() == datetime.now().date()])
            self.recent_sessions_label.configure(text=f"Recent Sessions: {recent_count}")
            
            # Average score
            scores = [s['score'] for s in sessions if s['score'] is not None]
            if scores:
                avg_score = sum(scores) / len(scores)
                self.avg_score_label.configure(text=f"Average Score: {avg_score:.1f}")
                
                # Best score
                best_score = max(scores)
                self.best_score_label.configure(text=f"Best Score: {best_score}")
        else:
            self.recent_sessions_label.configure(text="Recent Sessions: 0")
            self.avg_score_label.configure(text="Average Score: N/A")
            self.best_score_label.configure(text="Best Score: N/A")
    
    def open_reports_window(self):
        """Open detailed reports window"""
        if self.reports_window is None or not self.reports_window.window.winfo_exists():
            self.reports_window = ReportsWindow(self.user_data, self.db_manager)
        else:
            self.reports_window.window.lift()
    
    def open_settings_window(self):
        """Open settings window"""
        if self.settings_window is None or not self.settings_window.window.winfo_exists():
            self.settings_window = SettingsWindow(self.user_data, self.db_manager, self)
        else:
            self.settings_window.window.lift()
    
    def start_reminder_system(self):
        """Start the reminder system"""
        if self.settings['notifications_enabled']:
            self.schedule_next_reminder()
        
        # Start hydration reminders
        if self.settings.get('hydration_reminders', True):
            self.schedule_hydration_reminder()
    
    def schedule_next_reminder(self):
        """Schedule the next reminder"""
        interval = self.settings['reminder_interval'] * 60 * 1000  # Convert to milliseconds
        self.window.after(interval, self.show_reminder)
    
    def show_reminder(self):
        """Show posture reminder"""
        if self.settings['notifications_enabled']:
            messagebox.showwarning(
                "Posture Reminder",
                "⚠️ Time to stretch your neck and back!\n\nTake a break from your desk and do some gentle stretches."
            )
            
            # Voice reminder
            if voice_assistant.is_available():
                voice_assistant.speak_reminder()
            
            # Schedule next reminder
            self.schedule_next_reminder()
    
    def schedule_hydration_reminder(self):
        """Schedule hydration reminder"""
        # Hydration reminder every 2 hours (7200000 milliseconds)
        self.window.after(7200000, self.show_hydration_reminder)
    
    def show_hydration_reminder(self):
        """Show hydration reminder"""
        if self.settings.get('hydration_reminders', True):
            # Get today's hydration progress
            hydration_data = self.db_manager.get_today_hydration(self.user_data['id'])
            
            message = f"💧 Hydration Reminder!\n\n"
            message += f"You've consumed {hydration_data['total_ml']}ml today.\n"
            message += f"Goal: {hydration_data['goal_ml']}ml ({hydration_data['percentage']}%)\n\n"
            
            if hydration_data['percentage'] < 50:
                message += "You're behind on your hydration goal. Drink some water now!"
            elif hydration_data['percentage'] < 80:
                message += "Good progress! Keep drinking water throughout the day."
            else:
                message += "Great job staying hydrated! Keep it up!"
            
            messagebox.showinfo("Hydration Reminder", message)
            
            # Voice reminder
            if voice_assistant.is_available():
                voice_assistant.speak("Time for a hydration break! Drink some water to stay healthy.")
            
            # Schedule next hydration reminder
            self.schedule_hydration_reminder()
    
    def update_settings(self, new_settings):
        """Update settings and apply changes"""
        try:
            self.settings = new_settings
            
            # Save to database
            success = self.db_manager.update_user_settings(self.user_data['id'], self.settings)
            
            if not success:
                messagebox.showerror("Error", "Failed to save settings to database")
                return
            
            # Apply theme changes
            self.apply_theme()
            
            # Restart reminder system
            self.start_reminder_system()
            
        except Exception as e:
            print(f"Error updating settings: {e}")
            messagebox.showerror("Error", f"Failed to update settings: {str(e)}")
    
    def load_daily_quote(self):
        """Load and display daily quote"""
        try:
            quote = daily_quotes.get_quote_of_the_day()
            self.daily_quote_label.configure(text=quote)
        except Exception as e:
            print(f"Error loading daily quote: {e}")
            self.daily_quote_label.configure(text="Every small step towards better posture is a step towards better health.")
    
    def logout(self):
        """Logout user and return to auth"""
        # Goodbye message
        if voice_assistant.is_available():
            voice_assistant.speak_goodbye(self.user_data['username'])
        
        self.window.destroy()
        # In a real app, you might want to show auth window again
        # For now, just close the application
    
    def mainloop(self):
        """Start the window mainloop"""
        self.window.mainloop()
