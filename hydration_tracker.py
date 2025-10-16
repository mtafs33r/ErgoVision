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
        
        self.setup_ui()
        self.load_hydration_data()
    
    def setup_ui(self):
        """Setup the hydration tracker UI"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.parent_frame)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="💧 Hydration Tracker",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Top section - Today's progress
        self.create_progress_section()
        
        # Middle section - Quick log
        self.create_log_section()
        
        # Bottom section - Charts and history
        self.create_charts_section()
    
    def create_progress_section(self):
        """Create today's hydration progress section"""
        progress_frame = ctk.CTkFrame(self.main_frame)
        progress_frame.pack(fill="x", pady=(0, 20))
        
        # Progress title
        ctk.CTkLabel(
            progress_frame,
            text="Today's Hydration Goal",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=400,
            height=20
        )
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar.set(0)
        
        # Progress info
        self.progress_info = ctk.CTkLabel(
            progress_frame,
            text="0 ml / 2000 ml (0%)",
            font=ctk.CTkFont(size=14)
        )
        self.progress_info.pack(pady=(0, 15))
        
        # Goal setting
        goal_frame = ctk.CTkFrame(progress_frame)
        goal_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            goal_frame,
            text="Daily Goal (ml):",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(10, 5))
        
        self.goal_entry = ctk.CTkEntry(
            goal_frame,
            width=100,
            placeholder_text="2000"
        )
        self.goal_entry.pack(side="left", padx=(0, 10))
        
        update_goal_btn = ctk.CTkButton(
            goal_frame,
            text="Update Goal",
            width=100,
            command=self.update_goal
        )
        update_goal_btn.pack(side="left", padx=(0, 10))
    
    def create_log_section(self):
        """Create hydration logging section"""
        log_frame = ctk.CTkFrame(self.main_frame)
        log_frame.pack(fill="x", pady=(0, 20))
        
        # Log title
        ctk.CTkLabel(
            log_frame,
            text="Log Hydration",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        # Quick log buttons
        quick_frame = ctk.CTkFrame(log_frame)
        quick_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        quick_amounts = [250, 500, 750, 1000]
        for amount in quick_amounts:
            btn = ctk.CTkButton(
                quick_frame,
                text=f"+{amount}ml",
                width=80,
                command=lambda a=amount: self.log_hydration(a)
            )
            btn.pack(side="left", padx=5)
        
        # Custom log
        custom_frame = ctk.CTkFrame(log_frame)
        custom_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        ctk.CTkLabel(
            custom_frame,
            text="Custom amount:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(10, 5))
        
        self.custom_amount_entry = ctk.CTkEntry(
            custom_frame,
            width=100,
            placeholder_text="ml"
        )
        self.custom_amount_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            custom_frame,
            text="Drink type:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(10, 5))
        
        self.drink_type_var = tk.StringVar(value="water")
        drink_type_menu = ctk.CTkOptionMenu(
            custom_frame,
            values=["water", "tea", "coffee", "juice", "sports drink", "other"],
            variable=self.drink_type_var,
            width=120
        )
        drink_type_menu.pack(side="left", padx=(0, 10))
        
        log_btn = ctk.CTkButton(
            custom_frame,
            text="Log Drink",
            width=100,
            command=self.log_custom_hydration
        )
        log_btn.pack(side="left", padx=(0, 10))
    
    def create_charts_section(self):
        """Create charts and history section"""
        charts_frame = ctk.CTkFrame(self.main_frame)
        charts_frame.pack(fill="both", expand=True)
        
        # Charts title
        ctk.CTkLabel(
            charts_frame,
            text="Weekly Hydration History",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 4), facecolor='#212121')
        self.ax.set_facecolor('#2b2b2b')
        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)

        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Tips section
        tips_frame = ctk.CTkFrame(charts_frame)
        tips_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            tips_frame,
            text="💡 Hydration Tips",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        tips_text = """• Start your day with a glass of water
• Keep a water bottle visible on your desk
• Set hourly reminders to drink water
• Eat water-rich foods like fruits and vegetables
• Listen to your body's thirst signals"""
        
        tips_label = ctk.CTkLabel(
            tips_frame,
            text=tips_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        tips_label.pack(pady=(0, 10))
    
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
                
                # Create bar chart
                bars = self.ax.bar(dates, amounts, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2'])
                
                # Customize chart
                self.ax.set_ylabel('Water (ml)', color='white')
                self.ax.set_title('Weekly Hydration', color='white', fontsize=14, fontweight='bold')
                self.ax.tick_params(colors='white')
                
                # Add goal line
                self.ax.axhline(y=self.current_goal, color='red', linestyle='--', alpha=0.7, label=f'Daily Goal ({self.current_goal}ml)')
                self.ax.legend()
                
                # Add value labels on bars
                for bar, amount in zip(bars, amounts):
                    height = bar.get_height()
                    self.ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                               f'{amount}ml', ha='center', va='bottom', color='white', fontsize=10)
                
            else:
                self.ax.text(0.5, 0.5, 'No hydration data available', 
                           ha='center', va='center', transform=self.ax.transAxes, 
                           color='white', fontsize=14)
            
            # Style the chart
            self.ax.spines['bottom'].set_color('white')
            self.ax.spines['left'].set_color('white')
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            
            # Refresh canvas
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating chart: {e}")
    
    def refresh(self):
        """Refresh all hydration data"""
        self.load_hydration_data()
