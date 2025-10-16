"""
Reports and Analytics for ErgoVision application
Handles data visualization and report generation
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from typing import List, Dict

class ReportsWindow:
    def __init__(self, user_data, db_manager):
        """Initialize reports window"""
        self.user_data = user_data
        self.db_manager = db_manager
        
        # Create window
        self.window = ctk.CTkToplevel()
        self.window.title("ErgoVision - Reports & Analytics")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Center window
        self.center_window()
        
        # Setup UI
        self.setup_ui()
        
        # Load data
        self.load_data()
        
        # Create initial charts
        self.create_charts()
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup the reports UI"""
        # Main container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="Posture Analytics & Reports",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))
        
        # Controls frame
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        # Time period selection
        ctk.CTkLabel(
            controls_frame,
            text="Time Period:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        self.period_var = tk.StringVar(value="7 days")
        self.period_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=["7 days", "30 days", "90 days", "All time"],
            variable=self.period_var,
            command=self.on_period_change
        )
        self.period_dropdown.pack(side="left", padx=10, pady=10)
        
        # Export buttons
        self.export_csv_btn = ctk.CTkButton(
            controls_frame,
            text="Export CSV",
            width=100,
            height=30,
            command=self.export_csv
        )
        self.export_csv_btn.pack(side="right", padx=5, pady=10)
        
        self.export_pdf_btn = ctk.CTkButton(
            controls_frame,
            text="Export PDF",
            width=100,
            height=30,
            command=self.export_pdf
        )
        self.export_pdf_btn.pack(side="right", padx=5, pady=10)
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            controls_frame,
            text="Refresh",
            width=100,
            height=30,
            command=self.refresh_data
        )
        self.refresh_btn.pack(side="right", padx=5, pady=10)
        
        # Content frame with scrollbar
        self.content_frame = ctk.CTkScrollableFrame(main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Statistics frame
        self.stats_frame = ctk.CTkFrame(self.content_frame)
        self.stats_frame.pack(fill="x", pady=(0, 20))
        
        # Charts frame
        self.charts_frame = ctk.CTkFrame(self.content_frame)
        self.charts_frame.pack(fill="both", expand=True)
    
    def load_data(self):
        """Load session data from database"""
        # Get all sessions
        all_sessions = self.db_manager.get_posture_sessions(self.user_data['id'], limit=1000)
        
        # Filter by selected period
        period = self.period_var.get()
        cutoff_date = self.get_cutoff_date(period)
        
        self.sessions = [
            session for session in all_sessions
            if datetime.fromisoformat(session['date'].replace('Z', '+00:00')).date() >= cutoff_date
        ]
        
        # Convert to DataFrame for easier manipulation
        if self.sessions:
            self.df = pd.DataFrame(self.sessions)
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df = self.df.sort_values('date')
        else:
            self.df = pd.DataFrame()
    
    def get_cutoff_date(self, period: str):
        """Get cutoff date for selected period"""
        today = datetime.now().date()
        
        if period == "7 days":
            return today - timedelta(days=7)
        elif period == "30 days":
            return today - timedelta(days=30)
        elif period == "90 days":
            return today - timedelta(days=90)
        else:  # All time
            return datetime.min.date()
    
    def create_charts(self):
        """Create and display charts"""
        # Clear existing charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        if self.df.empty:
            # Show no data message
            no_data_label = ctk.CTkLabel(
                self.charts_frame,
                text="No data available for the selected period.\nStart monitoring to generate reports!",
                font=ctk.CTkFont(size=16)
            )
            no_data_label.pack(expand=True)
            return
        
        # Create matplotlib figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f'Posture Analytics - {self.period_var.get()}', fontsize=16, fontweight='bold')
        
        # Chart 1: Score trend over time
        ax1.plot(self.df['date'], self.df['score'], marker='o', linewidth=2, markersize=4)
        ax1.set_title('Posture Score Trend')
        ax1.set_ylabel('Score')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 100)
        
        # Format x-axis dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(self.df) // 10)))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Chart 2: Score distribution
        score_ranges = ['0-20', '21-40', '41-60', '61-80', '81-100']
        score_counts = [
            len(self.df[(self.df['score'] >= 0) & (self.df['score'] <= 20)]),
            len(self.df[(self.df['score'] >= 21) & (self.df['score'] <= 40)]),
            len(self.df[(self.df['score'] >= 41) & (self.df['score'] <= 60)]),
            len(self.df[(self.df['score'] >= 61) & (self.df['score'] <= 80)]),
            len(self.df[(self.df['score'] >= 81) & (self.df['score'] <= 100)])
        ]
        
        colors = ['#FF6B6B', '#FFA500', '#FFD700', '#90EE90', '#38E54D']
        ax2.bar(score_ranges, score_counts, color=colors)
        ax2.set_title('Score Distribution')
        ax2.set_ylabel('Number of Sessions')
        ax2.set_xlabel('Score Range')
        
        # Chart 3: Rating pie chart
        rating_counts = self.df['rating'].value_counts()
        ax3.pie(rating_counts.values, labels=rating_counts.index, autopct='%1.1f%%', startangle=90)
        ax3.set_title('Posture Ratings')
        
        # Chart 4: Session duration trend
        ax4.plot(self.df['date'], self.df['duration'], marker='s', linewidth=2, markersize=4, color='purple')
        ax4.set_title('Session Duration Trend')
        ax4.set_ylabel('Duration (minutes)')
        ax4.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax4.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(self.df) // 10)))
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
        
        # Adjust layout
        plt.tight_layout()
        
        # Embed chart in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Update statistics
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics display"""
        # Clear existing stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        if self.df.empty:
            return
        
        # Calculate statistics
        total_sessions = len(self.df)
        avg_score = self.df['score'].mean()
        best_score = self.df['score'].max()
        worst_score = self.df['score'].min()
        total_time = self.df['duration'].sum()
        avg_duration = self.df['duration'].mean()
        
        # Calculate improvement
        if len(self.df) > 1:
            first_half = self.df.iloc[:len(self.df)//2]['score'].mean()
            second_half = self.df.iloc[len(self.df)//2:]['score'].mean()
            improvement = second_half - first_half
        else:
            improvement = 0
        
        # Create stats grid
        stats_grid = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        stats_grid.pack(pady=20)
        
        # Configure grid
        for i in range(3):
            stats_grid.grid_columnconfigure(i, weight=1)
        
        # Session count
        sessions_frame = ctk.CTkFrame(stats_grid)
        sessions_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(sessions_frame, text="Total Sessions", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        ctk.CTkLabel(sessions_frame, text=str(total_sessions), font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 10))
        
        # Average score
        avg_frame = ctk.CTkFrame(stats_grid)
        avg_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(avg_frame, text="Average Score", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        ctk.CTkLabel(avg_frame, text=f"{avg_score:.1f}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 10))
        
        # Best score
        best_frame = ctk.CTkFrame(stats_grid)
        best_frame.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(best_frame, text="Best Score", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        ctk.CTkLabel(best_frame, text=str(best_score), font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 10))
        
        # Total time
        time_frame = ctk.CTkFrame(stats_grid)
        time_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(time_frame, text="Total Time", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        ctk.CTkLabel(time_frame, text=f"{total_time:.1f} min", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 10))
        
        # Average duration
        duration_frame = ctk.CTkFrame(stats_grid)
        duration_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(duration_frame, text="Avg Duration", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        ctk.CTkLabel(duration_frame, text=f"{avg_duration:.1f} min", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 10))
        
        # Improvement
        improvement_frame = ctk.CTkFrame(stats_grid)
        improvement_frame.grid(row=1, column=2, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(improvement_frame, text="Improvement", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        color = "#38E54D" if improvement >= 0 else "#FF6B6B"
        sign = "+" if improvement >= 0 else ""
        ctk.CTkLabel(improvement_frame, text=f"{sign}{improvement:.1f}", font=ctk.CTkFont(size=24, weight="bold"), text_color=color).pack(pady=(0, 10))
    
    def on_period_change(self, period):
        """Handle period selection change"""
        self.load_data()
        self.create_charts()
    
    def refresh_data(self):
        """Refresh data and charts"""
        self.load_data()
        self.create_charts()
        messagebox.showinfo("Success", "Data refreshed successfully!")
    
    def export_csv(self):
        """Export data to CSV file"""
        if self.df.empty:
            messagebox.showwarning("Warning", "No data to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV Report"
        )
        
        if filename:
            try:
                # Prepare data for export
                export_df = self.df.copy()
                export_df['date'] = export_df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
                export_df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def export_pdf(self):
        """Export report to PDF file"""
        if self.df.empty:
            messagebox.showwarning("Warning", "No data to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Save PDF Report"
        )
        
        if filename:
            try:
                self.create_pdf_report(filename)
                messagebox.showinfo("Success", f"Report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
    
    def create_pdf_report(self, filename):
        """Create PDF report"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("ErgoVision Posture Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # User info
        user_info = f"User: {self.user_data['username']}<br/>"
        user_info += f"Report Period: {self.period_var.get()}<br/>"
        user_info += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(user_info, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Statistics
        if not self.df.empty:
            avg_score = self.df['score'].mean()
            best_score = self.df['score'].max()
            total_sessions = len(self.df)
            total_time = self.df['duration'].sum()
            
            stats_data = [
                ['Metric', 'Value'],
                ['Total Sessions', str(total_sessions)],
                ['Average Score', f"{avg_score:.1f}"],
                ['Best Score', str(best_score)],
                ['Total Time (minutes)', f"{total_time:.1f}"]
            ]
            
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(Paragraph("Statistics Summary", styles['Heading2']))
            story.append(stats_table)
            story.append(Spacer(1, 20))
        
        # Recent sessions table
        if not self.df.empty:
            recent_sessions = self.df.tail(10)
            
            session_data = [['Date', 'Score', 'Rating', 'Duration (min)']]
            for _, session in recent_sessions.iterrows():
                session_data.append([
                    session['date'].strftime('%Y-%m-%d %H:%M'),
                    str(session['score']),
                    session['rating'],
                    f"{session['duration']:.1f}"
                ])
            
            sessions_table = Table(session_data)
            sessions_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10)
            ]))
            
            story.append(Paragraph("Recent Sessions", styles['Heading2']))
            story.append(sessions_table)
        
        # Build PDF
        doc.build(story)
