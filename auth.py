"""
Authentication system for ErgoVision application
Handles login, signup, and user authentication
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import re
from database import DatabaseManager

class AuthWindow:
    def __init__(self, auth_callback):
        """Initialize authentication window"""
        self.auth_callback = auth_callback
        self.db_manager = DatabaseManager()
        
        # Create main window
        self.window = ctk.CTk()
        self.window.title("ErgoVision - AI Posture & Health Coach")
        self.window.geometry("400x600")
        self.window.resizable(False, False)
        
        # Center window on screen
        self.center_window()
        
        # Set window icon (if available)
        try:
            self.window.iconbitmap("icon.ico")
        except:
            pass
        
        # Initialize UI
        self.setup_ui()
        
        # Start with login screen
        self.show_login()
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup the main UI frame"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # App title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="ErgoVision",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.title_label.pack(pady=(20, 10))
        
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="AI Posture & Health Coach",
            font=ctk.CTkFont(size=16)
        )
        self.subtitle_label.pack(pady=(0, 30))
        
        # Content frame for forms
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True)
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_login(self):
        """Show login form"""
        self.clear_content()
        
        # Login form
        login_frame = ctk.CTkFrame(self.content_frame)
        login_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            login_frame,
            text="Welcome Back",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Username field
        self.username_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Username",
            width=250,
            height=40
        )
        self.username_entry.pack(pady=(0, 15))
        
        # Password field
        self.password_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Password",
            width=250,
            height=40,
            show="*"
        )
        self.password_entry.pack(pady=(0, 15))
        # Login button
        self.login_btn = ctk.CTkButton(
            login_frame,
            text="Login",
            width=250,
            height=40,
            command=self.handle_login
        )
        self.login_btn.pack(pady=(0, 15))
        
        # Demo Mode / Bypass button
        self.demo_btn = ctk.CTkButton(
            login_frame,
            text="🚀 Demo Mode (Bypass)",
            width=250,
            height=40,
            fg_color="#38E54D",
            hover_color="#2EB43B",
            text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            command=self.handle_demo_login
        )
        self.demo_btn.pack(pady=(0, 15))
        
        # Forgot password link
        self.forgot_link = ctk.CTkLabel(
            login_frame,
            text="Forgot Password?",
            text_color="#3A7FF6",
            cursor="hand2"
        )
        self.forgot_link.pack(pady=(0, 20))
        self.forgot_link.bind("<Button-1>", lambda e: self.show_forgot_password())
        
        # Switch to signup
        switch_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        switch_frame.pack(side="bottom", pady=(0, 20))
        
        ctk.CTkLabel(
            switch_frame,
            text="Don't have an account?"
        ).pack(side="left")
        
        self.signup_link = ctk.CTkLabel(
            switch_frame,
            text="Sign Up",
            text_color="#3A7FF6",
            cursor="hand2"
        )
        self.signup_link.pack(side="left", padx=(5, 0))
        self.signup_link.bind("<Button-1>", lambda e: self.show_signup())
        
        # Bind Enter key to login
        self.window.bind('<Return>', lambda e: self.handle_login())
    
    def show_signup(self):
        """Show signup form"""
        self.clear_content()
        
        # Signup form
        signup_frame = ctk.CTkFrame(self.content_frame)
        signup_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            signup_frame,
            text="Create Account",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Username field
        self.signup_username_entry = ctk.CTkEntry(
            signup_frame,
            placeholder_text="Username",
            width=250,
            height=40
        )
        self.signup_username_entry.pack(pady=(0, 15))
        
        # Email field
        self.email_entry = ctk.CTkEntry(
            signup_frame,
            placeholder_text="Email",
            width=250,
            height=40
        )
        self.email_entry.pack(pady=(0, 15))
        
        # Password field
        self.signup_password_entry = ctk.CTkEntry(
            signup_frame,
            placeholder_text="Password",
            width=250,
            height=40,
            show="*"
        )
        self.signup_password_entry.pack(pady=(0, 15))
        
        # Confirm password field
        self.confirm_password_entry = ctk.CTkEntry(
            signup_frame,
            placeholder_text="Confirm Password",
            width=250,
            height=40,
            show="*"
        )
        self.confirm_password_entry.pack(pady=(0, 15))
        
        # Terms checkbox
        self.terms_var = tk.BooleanVar()
        self.terms_checkbox = ctk.CTkCheckBox(
            signup_frame,
            text="I agree to the Terms and Conditions",
            variable=self.terms_var
        )
        self.terms_checkbox.pack(pady=(0, 15))
        
        # Signup button
        self.signup_btn = ctk.CTkButton(
            signup_frame,
            text="Create Account",
            width=250,
            height=40,
            command=self.handle_signup
        )
        self.signup_btn.pack(pady=(0, 20))
        
        # Switch to login
        switch_frame = ctk.CTkFrame(signup_frame, fg_color="transparent")
        switch_frame.pack(side="bottom", pady=(0, 20))
        
        ctk.CTkLabel(
            switch_frame,
            text="Already have an account?"
        ).pack(side="left")
        
        self.login_link = ctk.CTkLabel(
            switch_frame,
            text="Login",
            text_color="#3A7FF6",
            cursor="hand2"
        )
        self.login_link.pack(side="left", padx=(5, 0))
        self.login_link.bind("<Button-1>", lambda e: self.show_login())
        
        # Bind Enter key to signup
        self.window.bind('<Return>', lambda e: self.handle_signup())
    
    def show_forgot_password(self):
        """Show forgot password form"""
        self.clear_content()
        
        # Forgot password form
        forgot_frame = ctk.CTkFrame(self.content_frame)
        forgot_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            forgot_frame,
            text="Reset Password",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Email field
        self.reset_email_entry = ctk.CTkEntry(
            forgot_frame,
            placeholder_text="Enter your email",
            width=250,
            height=40
        )
        self.reset_email_entry.pack(pady=(0, 30))
        
        # Reset button
        self.reset_btn = ctk.CTkButton(
            forgot_frame,
            text="Send Reset Link",
            width=250,
            height=40,
            command=self.handle_forgot_password
        )
        self.reset_btn.pack(pady=(0, 20))
        
        # Back to login
        self.back_link = ctk.CTkLabel(
            forgot_frame,
            text="Back to Login",
            text_color="#3A7FF6",
            cursor="hand2"
        )
        self.back_link.pack(pady=(0, 20))
        self.back_link.bind("<Button-1>", lambda e: self.show_login())
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Authenticate user
        user_data = self.db_manager.authenticate_user(username, password)
        
        if user_data:
            messagebox.showinfo("Success", f"Welcome back, {username}!")
            self.auth_callback(user_data)
        else:
            messagebox.showerror("Error", "Invalid username or password")
            
    def handle_demo_login(self):
        """Handle demo/bypass login"""
        self.db_manager.bypass_mode = True
        demo_user = {
            'id': 999, 
            'username': 'DemoUser', 
            'email': 'demo@ergovision.ai',
            'remember_me': False
        }
        messagebox.showinfo("Demo Mode", "Entering Demo Mode. Database features will be simulated.")
        self.auth_callback(demo_user)
    
    def handle_signup(self):
        """Handle signup attempt"""
        username = self.signup_username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.signup_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not all([username, email, password, confirm_password]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if not self.terms_var.get():
            messagebox.showerror("Error", "Please agree to the Terms and Conditions")
            return
        
        # Create user
        success = self.db_manager.create_user(username, email, password)
        
        if success:
            messagebox.showinfo("Success", "Account created successfully! Please login.")
            self.show_login()
        else:
            messagebox.showerror("Error", "Username or email already exists")
    
    def handle_forgot_password(self):
        """Handle forgot password request"""
        email = self.reset_email_entry.get().strip()
        
        if not email:
            messagebox.showerror("Error", "Please enter your email address")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        # In a real application, this would send an email
        messagebox.showinfo("Reset Link Sent", 
                           "If an account exists with this email, a reset link has been sent.")
        self.show_login()
    
    def mainloop(self):
        """Start the window mainloop"""
        self.window.mainloop()
    
    def destroy(self):
        """Destroy the window"""
        self.window.destroy()
