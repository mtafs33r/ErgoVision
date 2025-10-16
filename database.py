"""
Database management for ErgoVision application
Handles SQLite database operations for users, sessions, and settings
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime
from typing import Optional, Dict, List, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "ergovision.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                remember_me BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT,
                age INTEGER,
                height REAL,
                weight REAL,
                gender TEXT,
                desktop_setup TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Posture sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posture_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_minutes REAL,
                score INTEGER,
                rating TEXT,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                dark_mode BOOLEAN DEFAULT TRUE,
                reminder_interval INTEGER DEFAULT 30,
                notifications_enabled BOOLEAN DEFAULT TRUE,
                hydration_reminders BOOLEAN DEFAULT TRUE,
                hydration_goal INTEGER DEFAULT 2000,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Hydration tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hydration_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount_ml INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                drink_type TEXT DEFAULT 'water',
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Migrate existing user_settings table to include new hydration columns
        try:
            # Check if hydration_reminders column exists
            cursor.execute("PRAGMA table_info(user_settings)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'hydration_reminders' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN hydration_reminders BOOLEAN DEFAULT TRUE')
                print("Added hydration_reminders column to user_settings")
            
            if 'hydration_goal' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN hydration_goal INTEGER DEFAULT 2000')
                print("Added hydration_goal column to user_settings")
                
        except Exception as e:
            print(f"Error migrating user_settings table: {e}")
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, remember_me: bool = False) -> bool:
        """Create a new user account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, remember_me)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, remember_me))
            
            user_id = cursor.lastrowid
            
            # Create default settings for user
            cursor.execute('''
                INSERT INTO user_settings (user_id)
                VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data if successful"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, username, email, remember_me
                FROM users
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'email': result[2],
                    'remember_me': result[3]
                }
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def update_user_profile(self, user_id: int, profile_data: Dict) -> bool:
        """Update user profile information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if profile exists
            cursor.execute('SELECT id FROM user_profiles WHERE user_id = ?', (user_id,))
            existing_profile = cursor.fetchone()
            
            if existing_profile:
                # Update existing profile
                cursor.execute('''
                    UPDATE user_profiles
                    SET name = ?, age = ?, height = ?, weight = ?, 
                        gender = ?, desktop_setup = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (
                    profile_data.get('name'),
                    profile_data.get('age'),
                    profile_data.get('height'),
                    profile_data.get('weight'),
                    profile_data.get('gender'),
                    profile_data.get('desktop_setup'),
                    user_id
                ))
            else:
                # Create new profile
                cursor.execute('''
                    INSERT INTO user_profiles (user_id, name, age, height, weight, gender, desktop_setup)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    profile_data.get('name'),
                    profile_data.get('age'),
                    profile_data.get('height'),
                    profile_data.get('weight'),
                    profile_data.get('gender'),
                    profile_data.get('desktop_setup')
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, age, height, weight, gender, desktop_setup
                FROM user_profiles
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'name': result[0],
                    'age': result[1],
                    'height': result[2],
                    'weight': result[3],
                    'gender': result[4],
                    'desktop_setup': result[5]
                }
            return None
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    def save_posture_session(self, user_id: int, duration: float, score: int, rating: str, notes: str = "") -> bool:
        """Save posture monitoring session data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO posture_sessions (user_id, duration_minutes, score, rating, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, duration, score, rating, notes))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_posture_sessions(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's posture sessions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_date, duration_minutes, score, rating, notes
                FROM posture_sessions
                WHERE user_id = ?
                ORDER BY session_date DESC
                LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            sessions = []
            for result in results:
                sessions.append({
                    'date': result[0],
                    'duration': result[1],
                    'score': result[2],
                    'rating': result[3],
                    'notes': result[4]
                })
            
            return sessions
        except Exception as e:
            print(f"Error getting sessions: {e}")
            return []
    
    def get_user_settings(self, user_id: int) -> Dict:
        """Get user settings"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dark_mode, reminder_interval, notifications_enabled, 
                       hydration_reminders, hydration_goal
                FROM user_settings
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'dark_mode': result[0],
                    'reminder_interval': result[1],
                    'notifications_enabled': result[2],
                    'hydration_reminders': result[3] if result[3] is not None else True,
                    'hydration_goal': result[4] if result[4] is not None else 2000
                }
            else:
                # Return default settings
                return {
                    'dark_mode': True,
                    'reminder_interval': 30,
                    'notifications_enabled': True,
                    'hydration_reminders': True,
                    'hydration_goal': 2000
                }
        except Exception as e:
            print(f"Error getting settings: {e}")
            return {
                'dark_mode': True,
                'reminder_interval': 30,
                'notifications_enabled': True,
                'hydration_reminders': True,
                'hydration_goal': 2000
            }
    
    def update_user_settings(self, user_id: int, settings: Dict) -> bool:
        """Update user settings"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_settings
                SET dark_mode = ?, reminder_interval = ?, notifications_enabled = ?, 
                    hydration_reminders = ?, hydration_goal = ?
                WHERE user_id = ?
            ''', (
                settings.get('dark_mode', True),
                settings.get('reminder_interval', 30),
                settings.get('notifications_enabled', True),
                settings.get('hydration_reminders', True),
                settings.get('hydration_goal', 2000),
                user_id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False
    
    def calculate_bmi(self, height: float, weight: float) -> Tuple[float, str]:
        """Calculate BMI and category"""
        if height <= 0 or weight <= 0:
            return 0, "Invalid"
        
        # Convert height from cm to meters
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
        
        return round(bmi, 1), category
    
    def log_hydration(self, user_id: int, amount_ml: int, drink_type: str = 'water', notes: str = '') -> bool:
        """Log a hydration entry"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO hydration_logs (user_id, amount_ml, drink_type, notes)
                VALUES (?, ?, ?, ?)
            ''', (user_id, amount_ml, drink_type, notes))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging hydration: {e}")
            return False
    
    def get_today_hydration(self, user_id: int) -> Dict:
        """Get today's hydration data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get today's hydration logs
            cursor.execute('''
                SELECT SUM(amount_ml) as total_ml, COUNT(*) as entries
                FROM hydration_logs 
                WHERE user_id = ? AND DATE(timestamp) = DATE('now')
            ''', (user_id,))
            
            result = cursor.fetchone()
            total_ml = result[0] if result[0] else 0
            entries = result[1] if result[1] else 0
            
            # Get user's hydration goal
            cursor.execute('''
                SELECT hydration_goal FROM user_settings WHERE user_id = ?
            ''', (user_id,))
            
            goal_result = cursor.fetchone()
            goal_ml = goal_result[0] if goal_result and goal_result[0] else 2000
            
            conn.close()
            
            return {
                'total_ml': total_ml,
                'goal_ml': goal_ml,
                'entries': entries,
                'percentage': round((total_ml / goal_ml) * 100, 1) if goal_ml > 0 else 0
            }
        except Exception as e:
            print(f"Error getting today's hydration: {e}")
            return {'total_ml': 0, 'goal_ml': 2000, 'entries': 0, 'percentage': 0}
    
    def get_weekly_hydration(self, user_id: int) -> List[Dict]:
        """Get weekly hydration data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DATE(timestamp) as date, SUM(amount_ml) as total_ml
                FROM hydration_logs 
                WHERE user_id = ? AND timestamp >= DATE('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (user_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [{'date': row[0], 'total_ml': row[1] or 0} for row in results]
        except Exception as e:
            print(f"Error getting weekly hydration: {e}")
            return []
    
    def update_hydration_goal(self, user_id: int, goal_ml: int) -> bool:
        """Update user's daily hydration goal"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_settings 
                SET hydration_goal = ? 
                WHERE user_id = ?
            ''', (goal_ml, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating hydration goal: {e}")
            return False
