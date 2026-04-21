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
from PIL import Image

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

            # ---- Premium Design UI Tokens ----
            self.colors = {
                "bg_dark": "#0B0E14",         # Deep Navy background
                "bg_panel": "#14181F",        # Sidebar/Panel background
                "bg_card": "#1E2430",         # Metric cards
                "accent": "#FF6B6B",          # Coral accent
                "accent_soft": "#4E2C2C",     # Soft accent for highlights
                "neon_blue": "#3A7FF6",       # Primary blue
                "neon_cyan": "#00F2FF",       # High impact cyan
                "neon_green": "#38E54D",      # Success green
                "text_primary": "#FFFFFF",
                "text_secondary": "#A0AEC0",
                "border": "#2D3748"
            }
            self.padding = 20
            self.corner_radius = 16
            self.font_family = "Inter" # Standard premium choice, falls back gracefully
            
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
        self.window.grid_rowconfigure(1, weight=1)
        
        # Sidebar
        self.create_sidebar()
        
        # Main content area
        self.create_main_content()
        
        # Top bar
        self.create_top_bar()
    
    def create_sidebar(self):
        """Create sidebar navigation with premium styling"""
        self.sidebar = ctk.CTkFrame(
            self.window, 
            width=220, 
            corner_radius=0, 
            fg_color=self.colors["bg_panel"]
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)
        
        # App logo/title area
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=20, pady=(40, 40))
        
        self.logo_label = ctk.CTkLabel(
            self.logo_frame,
            text="ErgoVision",
            text_color=self.colors["accent"],
            font=ctk.CTkFont(family=self.font_family, size=24, weight="bold")
        )
        self.logo_label.pack()
        
        self.logo_subtitle = ctk.CTkLabel(
            self.logo_frame,
            text="AI POSTURE COACH",
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(family=self.font_family, size=10, weight="bold")
        )
        self.logo_subtitle.pack()
        
        # Navigation buttons
        nav_items = [
            ("🏠 Home", "home"),
            ("📷 Monitoring", "monitoring"),
            ("🤖 AI Coach", "ai_coach"),
            ("💧 Hydration", "hydration"),
            ("📊 Reports", "reports"),
            ("⚙️ Settings", "settings")
        ]
        
        self.nav_buttons = {}
        for i, (text, view) in enumerate(nav_items, 1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=180,
                height=45,
                corner_radius=self.corner_radius,
                fg_color="transparent",
                text_color=self.colors["text_secondary"],
                hover_color=self.colors["bg_card"],
                anchor="w",
                font=ctk.CTkFont(family=self.font_family, size=14, weight="bold"),
                command=lambda v=view: self.switch_view(v)
            )
            btn.grid(row=i, column=0, padx=20, pady=8)
            self.nav_buttons[view] = btn
        
        # Logout button
        self.logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            width=180,
            height=45,
            corner_radius=self.corner_radius,
            fg_color=self.colors["accent_soft"],
            text_color=self.colors["accent"],
            hover_color="#5E3535",
            font=ctk.CTkFont(family=self.font_family, size=14, weight="bold"),
            command=self.logout
        )
        self.logout_btn.grid(row=8, column=0, padx=20, pady=40)
    
    def create_top_bar(self):
        """Create premium top navigation bar"""
        self.top_bar = ctk.CTkFrame(self.window, height=80, corner_radius=0, fg_color="transparent")
        self.top_bar.grid(row=0, column=1, sticky="ew", padx=30, pady=(20, 0))
        self.top_bar.grid_columnconfigure(1, weight=1)
        
        # Current date and time
        self.datetime_label = ctk.CTkLabel(
            self.top_bar,
            text="",
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(family=self.font_family, size=14)
        )
        self.datetime_label.grid(row=0, column=0, sticky="w")
        
        # User info
        self.user_label = ctk.CTkLabel(
            self.top_bar,
            text=f"Welcome back, {self.user_data['username']} 👋",
            text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family=self.font_family, size=18, weight="bold")
        )
        self.user_label.grid(row=0, column=2, sticky="e")
        
        # Update datetime
        self.update_datetime()
    
    def create_main_content(self):
        """Create main content area with premium background"""
        self.content_frame = ctk.CTkFrame(self.window, fg_color=self.colors["bg_dark"], corner_radius=0)
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        
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
        """Create a premium home view with card-based dashboard"""
        home_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        
        # Header Metrics Row
        metrics_frame = ctk.CTkFrame(home_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=30, pady=(30, 20))
        metrics_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # 1. Posture Score Card
        score_card = self.create_metric_card(
            metrics_frame, "Posture Score", "85%", "target", self.colors["neon_cyan"]
        )
        score_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.metric_posture_score = score_card.metric_label # reference for updates

        # 2. Hours Tracked Card
        hours_card = self.create_metric_card(
            metrics_frame, "Hours Today", "6.2h", "clock", self.colors["neon_blue"]
        )
        hours_card.grid(row=0, column=1, padx=10, sticky="nsew")
        self.metric_hours_tracked = hours_card.metric_label

        # 3. Breaks Taken Card
        breaks_card = self.create_metric_card(
            metrics_frame, "Breaks Taken", "4", "coffee", self.colors["neon_green"]
        )
        breaks_card.grid(row=0, column=2, padx=(10, 0), sticky="nsew")
        self.metric_breaks_taken = breaks_card.metric_label

        # Middle Row: Quick Stats & Profile
        mid_row = ctk.CTkFrame(home_frame, fg_color="transparent")
        mid_row.pack(fill="x", padx=30, pady=20)
        mid_row.grid_columnconfigure(0, weight=2)
        mid_row.grid_columnconfigure(1, weight=1)

        # Profile Section Card
        profile_card = ctk.CTkFrame(mid_row, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        profile_card.grid(row=0, column=0, padx=(0, 20), sticky="nsew")
        
        ctk.CTkLabel(
            profile_card,
            text="👤 Personal Information",
            text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family=self.font_family, size=18, weight="bold")
        ).pack(pady=(20, 15), padx=20, anchor="w")
        
        form_grid = ctk.CTkFrame(profile_card, fg_color="transparent")
        form_grid.pack(fill="x", padx=20, pady=(0, 10))
        form_grid.columnconfigure((0, 1), weight=1)

        # Row 1: Name, Age
        self.name_entry = self.create_styled_entry(form_grid, "Full Name", 0, 0)
        self.age_entry = self.create_styled_entry(form_grid, "Age", 0, 1)

        # Row 2: Height, Weight
        self.height_entry = self.create_styled_entry(form_grid, "Height (cm)", 1, 0)
        self.weight_entry = self.create_styled_entry(form_grid, "Weight (kg)", 1, 1)

        # Row 3: Gender, Setup
        self.gender_var = tk.StringVar(value="Male")
        self.gender_dropdown = ctk.CTkOptionMenu(
            form_grid, values=["Male", "Female", "Other"], variable=self.gender_var,
            fg_color=self.colors["bg_card"], button_color=self.colors["neon_blue"],
            corner_radius=10, height=40
        )
        self.gender_dropdown.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.setup_var = tk.StringVar(value="Desktop")
        self.setup_dropdown = ctk.CTkOptionMenu(
            form_grid, values=["Laptop", "Desktop", "Standing Desk"], variable=self.setup_var,
            fg_color=self.colors["bg_card"], button_color=self.colors["neon_blue"],
            corner_radius=10, height=40
        )
        self.setup_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.save_btn = ctk.CTkButton(
            profile_card, text="Update Profile", fg_color=self.colors["neon_blue"],
            hover_color="#2A6CD6", corner_radius=10, height=40, font=ctk.CTkFont(weight="bold"),
            command=self.save_profile
        )
        self.save_btn.pack(pady=20, padx=20, fill="x")

        # BMI & Daily Inspiration Card (Right Side)
        right_panel = ctk.CTkFrame(mid_row, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew")

        # BMI Card
        bmi_card = ctk.CTkFrame(right_panel, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        bmi_card.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            bmi_card, text="⚖️ Health Index", text_color=self.colors["accent"],
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold")
        ).pack(pady=(15, 5), padx=20, anchor="w")
        
        self.bmi_label = ctk.CTkLabel(
            bmi_card, text="BMI: Calculating...", text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family=self.font_family, size=22, weight="bold")
        )
        self.bmi_label.pack(pady=(5, 15))

        # Inspiration Card
        quote_card = ctk.CTkFrame(right_panel, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        quote_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            quote_card, text="✨ Daily Focus", text_color=self.colors["neon_cyan"],
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold")
        ).pack(pady=(15, 5), padx=20, anchor="w")

        self.daily_quote_label = ctk.CTkLabel(
            quote_card, text="", text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(family=self.font_family, size=12, slant="italic"),
            wraplength=250, justify="center"
        )
        self.daily_quote_label.pack(pady=15, padx=20)
        
        # Bind BMI triggers
        self.height_entry.bind('<KeyRelease>', self.calculate_bmi)
        self.weight_entry.bind('<KeyRelease>', self.calculate_bmi)

        self.load_daily_quote()
        self.views["home"] = home_frame

    def create_metric_card(self, parent, title, value, icon_name, color):
        """Helper to create a premium metric card"""
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        
        title_lbl = ctk.CTkLabel(
            card, text=title, text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(family=self.font_family, size=12, weight="bold")
        )
        title_lbl.pack(pady=(15, 0), padx=20, anchor="w")
        
        metric_val = ctk.CTkLabel(
            card, text=value, text_color=color,
            font=ctk.CTkFont(family=self.font_family, size=32, weight="bold")
        )
        metric_val.pack(pady=(5, 15), padx=20, anchor="w")
        card.metric_label = metric_val
        return card

    def create_styled_entry(self, parent, placeholder, row, col):
        """Helper to create a themed entry field"""
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder, height=40,
            fg_color=self.colors["bg_card"], border_color=self.colors["border"],
            corner_radius=10, font=ctk.CTkFont(family=self.font_family, size=13)
        )
        entry.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        return entry
    
    def create_monitoring_view(self):
        """Create a premium posture monitoring view"""
        monitoring_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Camera preview frame with subtle border
        self.camera_frame = ctk.CTkFrame(
            monitoring_frame, width=640, height=480, 
            fg_color=self.colors["bg_panel"], border_color=self.colors["border"], border_width=2
        )
        self.camera_frame.pack(pady=(30, 20))
        
        # Camera placeholder
        self.camera_placeholder = ctk.CTkLabel(
            self.camera_frame,
            text="📷 Camera Feed Placeholder",
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(family=self.font_family, size=18, weight="bold"),
            width=640,
            height=480
        )
        self.camera_placeholder.pack(expand=True)
        
        # Controls & Status Container
        info_container = ctk.CTkFrame(monitoring_frame, fg_color="transparent")
        info_container.pack(fill="x", padx=30, pady=10)
        info_container.columnconfigure((0, 1), weight=1)

        # 1. Controls Card
        controls_card = ctk.CTkFrame(info_container, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        controls_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.monitor_btn = ctk.CTkButton(
            controls_card, text="🚀 Start Session", width=200, height=50,
            fg_color=self.colors["neon_blue"], hover_color="#2A6CD6",
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold"),
            command=self.toggle_monitoring
        )
        self.monitor_btn.pack(pady=30, padx=20)

        # 2. Status & Metrics Card
        status_card = ctk.CTkFrame(info_container, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        status_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        self.status_label = ctk.CTkLabel(
            status_card, text="Posture: Not Monitoring", text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family=self.font_family, size=18, weight="bold")
        )
        self.status_label.pack(pady=(20, 5))

        self.duration_label = ctk.CTkLabel(
            status_card, text="Duration: 00:00", text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(family=self.font_family, size=14)
        )
        self.duration_label.pack(pady=2)

        self.score_label = ctk.CTkLabel(
            status_card, text="Current Score: --", text_color=self.colors["neon_cyan"],
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold")
        )
        self.score_label.pack(pady=(2, 20))
        
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
        """Create a premium AI coach view with health tips and visual guides"""
        coach_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        
        # --- Top Section: AI Insights ---
        tips_card = ctk.CTkFrame(coach_frame, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        tips_card.pack(fill="x", padx=30, pady=(30, 20))
        
        header_frame = ctk.CTkFrame(tips_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(25, 15))
        
        ctk.CTkLabel(
            header_frame, text="🤖 AI Health Insights", text_color=self.colors["neon_cyan"],
            font=ctk.CTkFont(family=self.font_family, size=22, weight="bold")
        ).pack(side="left")

        self.new_tip_btn = ctk.CTkButton(
            header_frame, text="Generate New Tip", width=140, height=32,
            fg_color=self.colors["accent_soft"], text_color=self.colors["accent"],
            hover_color="#5E3535", corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"),
            command=self.get_new_tip
        )
        self.new_tip_btn.pack(side="right")

        self.tip_text = ctk.CTkTextbox(
            tips_card, height=180, fg_color=self.colors["bg_card"],
            text_color=self.colors["text_primary"], border_width=0,
            font=ctk.CTkFont(family=self.font_family, size=15), corner_radius=12
        )
        self.tip_text.pack(fill="x", padx=25, pady=(0, 25))

        # --- Middle Section: Visual Guide Library ---
        visuals_header = ctk.CTkLabel(
            coach_frame, text="📚 Posture Mastery Library", text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family=self.font_family, size=20, weight="bold")
        )
        visuals_header.pack(padx=30, pady=(20, 10), anchor="w")

        visuals_grid = ctk.CTkFrame(coach_frame, fg_color="transparent")
        visuals_grid.pack(fill="x", padx=30, pady=(0, 30))
        visuals_grid.columnconfigure((0, 1, 2), weight=1)

        # Guide Cards
        guides = [
            ("Ideal Setup", "ideal_posture.png", "• Keep screen at eye level\n• Feet flat on floor\n• Elbows at 90 degrees\n• Shoulders relaxed"),
            ("Comparison", "posture_comparison.png", "• Avoid 'Tech Neck'\n• Pull chin back\n• Keep ears over shoulders\n• Stack spine vertically"),
            ("Stretches", "posture_stretches.png", "• Tilt head side-to-side\n• Roll shoulders back\n• Stretch wrists daily\n• Stand up every 30m")
        ]

        assets_path = os.path.join(os.path.dirname(__file__), "assets", "posture_guide")
        
        self.guide_images = [] # Store references
        for i, (title, filename, desc) in enumerate(guides):
            card = ctk.CTkFrame(visuals_grid, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
            card.grid(row=0, column=i, padx=10 if i == 1 else (0, 10) if i == 0 else (10, 0), sticky="nsew")
            
            # Load and display image
            img_path = os.path.join(assets_path, filename)
            if os.path.exists(img_path):
                img = Image.open(img_path)
                # Create CTK Image for scaling
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(240, 160))
                img_lbl = ctk.CTkLabel(card, image=ctk_img, text="")
                img_lbl.pack(pady=(15, 10), padx=15)
                self.guide_images.append(ctk_img) # keep reference

            ctk.CTkLabel(
                card, text=title, text_color=self.colors["text_primary"],
                font=ctk.CTkFont(family=self.font_family, size=16, weight="bold")
            ).pack(padx=15, anchor="w")

            ctk.CTkLabel(
                card, text=desc, text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(family=self.font_family, size=12),
                wraplength=220, justify="left"
            ).pack(padx=15, pady=(5, 20), anchor="w")
        
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
        """Create premium reports and analytics view"""
        reports_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Stats Overview Grid
        stats_container = ctk.CTkFrame(reports_frame, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        stats_container.pack(fill="x", padx=30, pady=30)
        
        ctk.CTkLabel(
            stats_container, text="📈 Session History Analytics", text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family=self.font_family, size=22, weight="bold")
        ).pack(pady=(25, 20), padx=25, anchor="w")

        self.view_reports_btn = ctk.CTkButton(
            stats_container, text="View Detailed Visual Reports", width=240, height=45,
            fg_color=self.colors["neon_blue"], hover_color="#2A6CD6",
            font=ctk.CTkFont(family=self.font_family, size=14, weight="bold"),
            command=self.open_reports_window
        )
        self.view_reports_btn.pack(pady=(0, 30))
        
        # Quick metrics placeholder
        self.stats_display_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
        self.stats_display_frame.pack(pady=(0, 25), padx=25, fill="x")
        
        self.views["reports"] = reports_frame
    
    def create_settings_view(self):
        """Create premium settings view"""
        settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        card = ctk.CTkFrame(settings_frame, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        card.pack(pady=50, padx=30)

        ctk.CTkLabel(
            card, text="⚙️ Preferences & Configuration", text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family=self.font_family, size=22, weight="bold")
        ).pack(pady=(30, 10), padx=40)

        ctk.CTkLabel(
            card, text="Manage your notification thresholds and interface theme.", 
            text_color=self.colors["text_secondary"], font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 30), padx=40)

        self.open_settings_btn = ctk.CTkButton(
            card, text="Open Settings Panel", width=220, height=45,
            fg_color=self.colors["accent_soft"], text_color=self.colors["accent"],
            hover_color="#5E3535", font=ctk.CTkFont(family=self.font_family, size=14, weight="bold"),
            command=self.open_settings_window
        )
        self.open_settings_btn.pack(pady=(0, 40))
        
        self.views["settings"] = settings_frame
    
    def switch_view(self, view_name):
        """Switch between different views with active navigation styling"""
        # Hide all views
        for view in self.views.values():
            view.pack_forget()
        
        # Show selected view
        self.views[view_name].pack(fill="both", expand=True)
        
        # Update navigation buttons styling
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(
                    fg_color=self.colors["neon_blue"],
                    text_color=self.colors["text_primary"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.colors["text_secondary"]
                )
        
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
        # Read current notification settings
        mobile_notif_enabled = self.settings.get('mobile_notifications_enabled', True)
        alert_threshold = self.settings.get('posture_alert_threshold_minutes', 2)

        self.posture_monitor = PostureMonitor(
            self.camera_frame,
            self.user_data['id'],
            self.db_manager,
            self.on_posture_update,
            self.on_session_end,
            mobile_notifications_enabled=mobile_notif_enabled,
            alert_threshold_minutes=float(alert_threshold),
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
