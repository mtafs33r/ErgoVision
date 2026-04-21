"""
Hydration tracking module for ErgoVision application
Handles hydration logging, reminders, and analytics
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
# at top of hydration_tracker.py
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

class HydrationTracker:
    def __init__(self, parent_frame, user_data, db_manager):
        """Initialize hydration tracker"""
        self.user_data = user_data
        self.db_manager = db_manager
        self.parent_frame = parent_frame
        self.current_goal = 2000  # Default goal in ml
        
        # Premium Colors (Synced with Dashboard)
        self.colors = {
            "bg_dark": "#0B0E14",
            "bg_panel": "#14181F",
            "bg_card": "#1E2430",
            "neon_blue": "#3A7FF6",
            "neon_cyan": "#00F2FF",
            "neon_green": "#38E54D",
            "accent": "#FF6B6B",
            "text_primary": "#FFFFFF",
            "text_secondary": "#A0AEC0",
            "border": "#2D3748"
        }
        self.padding = 20
        self.corner_radius = 16
        self.font_family = "Inter"

        self.setup_ui()
        self.load_hydration_data()
    
    def setup_ui(self):
        """Setup the hydration tracker UI with premium styling"""
        # Main container with scroll
        self.scroll_frame = ctk.CTkScrollableFrame(self.parent_frame, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.main_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Title Section
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(
            header_frame,
            text="💧 Hydration Intelligence",
            text_color=self.colors["neon_cyan"],
            font=ctk.CTkFont(family=self.font_family, size=28, weight="bold")
        ).pack(side="left")

        # Top section - Today's Analytics Card
        self.create_progress_section()
        
        # Middle section - Interaction Cards
        mid_row = ctk.CTkFrame(self.main_container, fg_color="transparent")
        mid_row.pack(fill="x", pady=(0, 30))
        mid_row.columnconfigure(0, weight=1)
        mid_row.columnconfigure(1, weight=1)

        self.create_log_section(mid_row)
        self.create_tips_section(mid_row)
        
        # Bottom section - Visual Analytics Card
        self.create_charts_section()
    
    def create_progress_section(self):
        """Create today's high-impact progress card"""
        card = ctk.CTkFrame(self.main_container, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        card.pack(fill="x", pady=(0, 30))
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=30, pady=30)

        # Left side: Progress Info
        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(
            info_frame, text="DAILY PROGRESS", text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(family=self.font_family, size=12, weight="bold")
        ).pack(anchor="w")

        self.progress_info = ctk.CTkLabel(
            info_frame, text="0 ml / 2000 ml (0%)", text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family=self.font_family, size=28, weight="bold")
        )
        self.progress_info.pack(anchor="w", pady=(5, 15))
        
        self.progress_bar = ctk.CTkProgressBar(
            info_frame, width=500, height=12, corner_radius=6,
            fg_color=self.colors["bg_card"], progress_color=self.colors["neon_blue"]
        )
        self.progress_bar.pack(anchor="w")
        self.progress_bar.set(0)

        # Right side: Goal Settings
        goal_frame = ctk.CTkFrame(inner, fg_color=self.colors["bg_card"], corner_radius=12)
        goal_frame.grid(row=0, column=1, padx=(40, 0), sticky="nsew")
        
        ctk.CTkLabel(
            goal_frame, text="SET TARGET (ML)", text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(family=self.font_family, size=10, weight="bold")
        ).pack(pady=(15, 5), padx=20)

        entry_frame = ctk.CTkFrame(goal_frame, fg_color="transparent")
        entry_frame.pack(padx=20, pady=(0, 15))

        self.goal_entry = ctk.CTkEntry(
            entry_frame, width=100, height=35, placeholder_text="2000",
            fg_color=self.colors["bg_panel"], border_color=self.colors["border"], corner_radius=8
        )
        self.goal_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            entry_frame, text="Update", width=80, height=35, corner_radius=8,
            fg_color=self.colors["neon_blue"], hover_color="#2A6CD6",
            font=ctk.CTkFont(family=self.font_family, size=13, weight="bold"),
            command=self.update_goal
        ).pack(side="left")
    
    def create_log_section(self, parent):
        """Create premium hydration logging card"""
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        card.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        
        ctk.CTkLabel(
            card, text="💧 QUICK LOG", text_color=self.colors["neon_cyan"],
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold")
        ).pack(pady=(20, 15), padx=25, anchor="w")

        # Quick log buttons
        quick_frame = ctk.CTkFrame(card, fg_color="transparent")
        quick_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        quick_amounts = [250, 500, 750, 1000]
        # Grid for buttons to look cleaner
        for i, amount in enumerate(quick_amounts):
            btn = ctk.CTkButton(
                quick_frame, text=f"+{amount}ml", width=85, height=35, corner_radius=8,
                fg_color=self.colors["bg_card"], hover_color=self.colors["border"],
                font=ctk.CTkFont(family=self.font_family, size=12, weight="bold"),
                command=lambda a=amount: self.log_hydration(a)
            )
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        quick_frame.columnconfigure((0, 1), weight=1)

        # Custom log
        ctk.CTkLabel(
            card, text="CUSTOM LOG", text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(family=self.font_family, size=10, weight="bold")
        ).pack(pady=(15, 5), padx=25, anchor="w")

        custom_frame = ctk.CTkFrame(card, fg_color="transparent")
        custom_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.custom_amount_entry = ctk.CTkEntry(
            custom_frame, width=100, height=35, placeholder_text="ml",
            fg_color=self.colors["bg_card"], border_color=self.colors["border"], corner_radius=8
        )
        self.custom_amount_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.drink_type_var = tk.StringVar(value="water")
        drink_type_menu = ctk.CTkOptionMenu(
            custom_frame, values=["water", "tea", "coffee", "juice", "other"],
            variable=self.drink_type_var, width=120, height=35, corner_radius=8,
            fg_color=self.colors["bg_card"], button_color=self.colors["neon_blue"]
        )
        drink_type_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(
            card, text="LOG TRANSACTION", fg_color=self.colors["neon_green"],
            text_color="#000000", hover_color="#2EB43B", corner_radius=10, height=40,
            font=ctk.CTkFont(family=self.font_family, size=14, weight="bold"),
            command=self.log_custom_hydration
        ).pack(fill="x", padx=25, pady=(5, 25))

    def create_tips_section(self, parent):
        """Create premium hydration tips card"""
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        card.grid(row=0, column=1, padx=(15, 0), sticky="nsew")

        ctk.CTkLabel(
            card, text="💡 SMART TIPS", text_color=self.colors["neon_cyan"],
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold")
        ).pack(pady=(20, 15), padx=25, anchor="w")

        tips_text = (
            "• Start your day with a glass of water\n"
            "• Keep a bottle visible on your desk\n"
            "• Set hourly reminders to drink\n"
            "• Eat water-rich foods\n"
            "• Listen to your thirst signals"
        )
        
        ctk.CTkLabel(
            card, text=tips_text, text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(family=self.font_family, size=14), justify="left"
        ).pack(padx=25, pady=(0, 20), anchor="w")
    
    def create_charts_section(self):
        """Create premium charts and history section"""
        card = ctk.CTkFrame(self.main_container, fg_color=self.colors["bg_panel"], corner_radius=self.corner_radius)
        card.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            card, text="📊 WEEKLY ANALYTICS", text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold")
        ).pack(pady=(20, 10), padx=30, anchor="w")
        
        # Create matplotlib figure with premium theme
        self.fig, self.ax = plt.subplots(figsize=(8, 4), facecolor=self.colors["bg_panel"])
        self.ax.set_facecolor(self.colors["bg_card"])
        self.canvas = FigureCanvasTkAgg(self.fig, card)

        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=30, pady=(0, 30))
    
    def load_hydration_data(self):
        """Load and display current hydration data"""
        try:
            # Get today's hydration data
            today_data = self.db_manager.get_today_hydration(self.user_data['id'])
            
            # Update progress
            progress = today_data['percentage'] / 100
            self.progress_bar.set(min(progress, 1.0))
            
            # Update progress info
            self.progress_info.configure(
                text=f"{today_data['total_ml']} ml / {today_data['goal_ml']} ml ({today_data['percentage']}%)"
            )
            
            # Set current goal
            self.current_goal = today_data['goal_ml']
            self.goal_entry.delete(0, 'end')
            self.goal_entry.insert(0, str(self.current_goal))
            
            # Update chart
            self.update_chart()
            
        except Exception as e:
            print(f"Error loading hydration data: {e}")
    
    def log_hydration(self, amount_ml: int):
        """Log a hydration entry"""
        try:
            success = self.db_manager.log_hydration(
                self.user_data['id'], 
                amount_ml, 
                'water', 
                f'Quick log - {datetime.now().strftime("%H:%M")}'
            )
            
            if success:
                self.load_hydration_data()  # Refresh data
                messagebox.showinfo("Success", f"Logged {amount_ml}ml of water!")
            else:
                messagebox.showerror("Error", "Failed to log hydration entry")
                
        except Exception as e:
            print(f"Error logging hydration: {e}")
            messagebox.showerror("Error", f"Failed to log hydration: {str(e)}")
    
    def log_custom_hydration(self):
        """Log custom hydration amount"""
        try:
            amount_text = self.custom_amount_entry.get()
            if not amount_text:
                messagebox.showwarning("Warning", "Please enter an amount")
                return
            
            amount_ml = int(amount_text)
            drink_type = self.drink_type_var.get()
            
            success = self.db_manager.log_hydration(
                self.user_data['id'], 
                amount_ml, 
                drink_type, 
                f'Custom log - {datetime.now().strftime("%H:%M")}'
            )
            
            if success:
                self.custom_amount_entry.delete(0, 'end')
                self.load_hydration_data()  # Refresh data
                messagebox.showinfo("Success", f"Logged {amount_ml}ml of {drink_type}!")
            else:
                messagebox.showerror("Error", "Failed to log hydration entry")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            print(f"Error logging custom hydration: {e}")
            messagebox.showerror("Error", f"Failed to log hydration: {str(e)}")
    
    def update_goal(self):
        """Update daily hydration goal"""
        try:
            goal_text = self.goal_entry.get()
            if not goal_text:
                messagebox.showwarning("Warning", "Please enter a goal amount")
                return
            
            goal_ml = int(goal_text)
            
            success = self.db_manager.update_hydration_goal(self.user_data['id'], goal_ml)
            
            if success:
                self.current_goal = goal_ml
                self.load_hydration_data()  # Refresh data
                messagebox.showinfo("Success", f"Updated daily goal to {goal_ml}ml!")
            else:
                messagebox.showerror("Error", "Failed to update goal")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            print(f"Error updating goal: {e}")
            messagebox.showerror("Error", f"Failed to update goal: {str(e)}")
    
    def update_chart(self):
        """Update the weekly hydration chart"""
        try:
            # Get weekly data
            weekly_data = self.db_manager.get_weekly_hydration(self.user_data['id'])
            
            # Clear previous chart
            self.ax.clear()
            
            if weekly_data:
                # Prepare data for chart
                dates = []
                amounts = []
                
                # Get last 7 days
                today = datetime.now().date()
                for i in range(7):
                    date = today - timedelta(days=6-i)
                    date_str = date.strftime('%Y-%m-%d')
                    
                    # Find data for this date
                    day_data = next((d for d in weekly_data if d['date'] == date_str), {'total_ml': 0})
                    
                    dates.append(date.strftime('%a'))
                    amounts.append(day_data['total_ml'])
                
                # Create bar chart with neon styling
                bars = self.ax.bar(dates, amounts, color=self.colors["neon_blue"], alpha=0.8, edgecolor=self.colors["neon_cyan"], linewidth=1)
                
                # Customize chart
                self.ax.set_ylabel('Water (ml)', color=self.colors["text_secondary"], fontname=self.font_family)
                self.ax.set_title('WEEKLY HYDRATION', color=self.colors["text_primary"], fontsize=14, fontweight='bold', fontname=self.font_family)
                self.ax.tick_params(colors=self.colors["text_secondary"])
                
                # Add goal line
                self.ax.axhline(y=self.current_goal, color=self.colors["accent"], linestyle='--', alpha=0.7, label=f'Goal ({self.current_goal}ml)')
                leg = self.ax.legend(facecolor=self.colors["bg_card"], edgecolor=self.colors["border"])
                for text in leg.get_texts():
                    text.set_color(self.colors["text_primary"])
                
                # Add value labels on bars
                for bar, amount in zip(bars, amounts):
                    height = bar.get_height()
                    self.ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                               f'{amount}ml', ha='center', va='bottom', color=self.colors["text_primary"], fontsize=10, fontname=self.font_family)
                
            else:
                self.ax.text(0.5, 0.5, 'No hydration data available', 
                           ha='center', va='center', transform=self.ax.transAxes, 
                           color=self.colors["text_secondary"], fontsize=14, fontname=self.font_family)
            
            # Style the chart
            self.ax.spines['bottom'].set_color(self.colors["border"])
            self.ax.spines['left'].set_color(self.colors["border"])
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            
            # Refresh canvas
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating chart: {e}")
    
    def refresh(self):
        """Refresh all hydration data"""
        self.load_hydration_data()
