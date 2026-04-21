"""
Database management for ErgoVision application
Handles MongoDB database operations for users, sessions, and settings
"""

import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseManager:
    def __init__(self, db_name: str = "ergovision"):
        """Initialize database connection to MongoDB"""
        self.db_name = db_name
        self.client = None
        self.db = None
        self.bypass_mode = False # Add bypass mode flag
        self.init_database()
    
    def get_connection(self):
        """Get MongoDB database instance"""
        if self.bypass_mode:
            return None
            
        if self.db is None:
            # Connect using the connection string from environment variables, or default to localhost
            uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
            try:
                self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
                self.db = self.client[self.db_name]
                # Force a connection check
                self.client.admin.command('ping')
            except Exception as e:
                error_msg = str(e)
                if "dnspython" in error_msg:
                    print("\n[ERROR] Missing 'dnspython' package. This is required for 'mongodb+srv://' connection strings.")
                    print("Please run: pip install dnspython\n")
                elif "DNS query name does not exist" in error_msg:
                    print(f"\n[ERROR] DNS Resolution Failed: {e}")
                    print("This usually happens when your internal DNS doesn't support SRV records.")
                    print("Try changing your DNS to Google (8.8.8.8) or Cloudflare (1.1.1.1).\n")
                else:
                    print(f"\n[ERROR] Could not connect to MongoDB: {e}\n")
                raise e
        return self.db
    
    def init_database(self):
        """Initialize database collections and indexes"""
        try:
            db = self.get_connection()
            
            # Create indexes to ensure uniqueness like SQLite UNIQUE constraints
            db.users.create_index("username", unique=True)
            db.users.create_index("email", unique=True)
            
            # Additional indexes for performance (optional but good mimicking SQLite foreign keys/queries)
            db.user_profiles.create_index("user_id", unique=True)
            db.user_settings.create_index("user_id", unique=True)
            db.posture_sessions.create_index("user_id")
            db.posture_sessions.create_index("session_date")
            db.hydration_logs.create_index("user_id")
            db.hydration_logs.create_index("timestamp")
            
        except Exception as e:
            print(f"Error initializing MongoDB database: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, remember_me: bool = False) -> bool:
        """Create a new user account"""
        try:
            db = self.get_connection()
            password_hash = self.hash_password(password)
            
            # In MongoDB, we'll store user_id as a string (the stringified ObjectId)
            # but for backwards compatibility with parts expecting integers, 
            # we'll use a sequence generator if we wanted perfect matching,
            # or we can just return the stringified ObjectId and rely on the consumers to handle it.
            # Upon inspecting typical usage, string IDs usually work fine if passed transparently.
            # To be very safe and keep integer IDs, we can use a counter collection.
            
            # Let's generate a unique integer ID
            seq_doc = db.counters.find_one_and_update(
                {"_id": "userid"},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=True
            )
            user_id = seq_doc["seq"]

            user_doc = {
                "id": user_id,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.now(),
                "remember_me": remember_me
            }
            
            db.users.insert_one(user_doc)
            
            # Create default settings for user
            settings_doc = {
                "user_id": user_id,
                "dark_mode": True,
                "reminder_interval": 30,
                "notifications_enabled": True,
                "hydration_reminders": True,
                "hydration_goal": 2000,
                "mobile_notifications_enabled": True,
                "posture_alert_threshold_minutes": 2,
            }
            db.user_settings.insert_one(settings_doc)
            
            return True
        except DuplicateKeyError:
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data if successful"""
        try:
            db = self.get_connection()
            password_hash = self.hash_password(password)
            
            result = db.users.find_one({
                "username": username,
                "password_hash": password_hash
            })
            
            if result:
                return {
                    'id': result['id'],
                    'username': result['username'],
                    'email': result['email'],
                    'remember_me': result.get('remember_me', False)
                }
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def update_user_profile(self, user_id: int, profile_data: Dict) -> bool:
        """Update user profile information"""
        try:
            db = self.get_connection()
            
            update_data = {
                "name": profile_data.get('name'),
                "age": profile_data.get('age'),
                "height": profile_data.get('height'),
                "weight": profile_data.get('weight'),
                "gender": profile_data.get('gender'),
                "desktop_setup": profile_data.get('desktop_setup'),
                "updated_at": datetime.now()
            }
            
            # Upsert (update if exists, insert if not)
            db.user_profiles.update_one(
                {"user_id": user_id},
                {"$set": update_data},
                upsert=True
            )
            
            return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile information"""
        if self.bypass_mode:
            return {
                'name': 'Demo User',
                'age': 30,
                'height': 180,
                'weight': 75,
                'gender': 'Male',
                'desktop_setup': 'Standing Desk'
            }
            
        try:
            db = self.get_connection()
            if not db: return None
            
            result = db.user_profiles.find_one({"user_id": user_id})
            
            if result:
                return {
                    'name': result.get('name'),
                    'age': result.get('age'),
                    'height': result.get('height'),
                    'weight': result.get('weight'),
                    'gender': result.get('gender'),
                    'desktop_setup': result.get('desktop_setup')
                }
            return None
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    def save_posture_session(self, user_id: int, duration: float, score: int, rating: str, notes: str = "") -> bool:
        """Save posture monitoring session data"""
        try:
            db = self.get_connection()
            
            session_doc = {
                "user_id": user_id,
                "session_date": datetime.now(),
                "duration_minutes": duration,
                "score": score,
                "rating": rating,
                "notes": notes
            }
            
            db.posture_sessions.insert_one(session_doc)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_posture_sessions(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's posture sessions"""
        try:
            db = self.get_connection()
            
            # Find and sort by session_date descending, then limit
            cursor = db.posture_sessions.find({"user_id": user_id}).sort("session_date", -1).limit(limit)
            
            sessions = []
            for result in cursor:
                # Need to convert datetime to string if the original logic expects str (SQLite timestamp usually returns as string in default connect)
                # SQLite usually returns "YYYY-MM-DD HH:MM:SS" style string
                dt_str = result['session_date'].strftime("%Y-%m-%d %H:%M:%S") if isinstance(result['session_date'], datetime) else result['session_date']
                
                sessions.append({
                    'date': dt_str,
                    'duration': result.get('duration_minutes', 0),
                    'score': result.get('score', 0),
                    'rating': result.get('rating', ''),
                    'notes': result.get('notes', '')
                })
            
            return sessions
        except Exception as e:
            print(f"Error getting sessions: {e}")
            return []
    
    def get_user_settings(self, user_id: int) -> Dict:
        """Get user settings"""
        default_settings = {
            'dark_mode': True,
            'reminder_interval': 30,
            'notifications_enabled': True,
            'hydration_reminders': True,
            'hydration_goal': 2000,
            'mobile_notifications_enabled': True,
            'posture_alert_threshold_minutes': 2,
        }
        
        if self.bypass_mode:
            return default_settings
            
        try:
            db = self.get_connection()
            if not db: return default_settings
            result = db.user_settings.find_one({"user_id": user_id})
            
            if result:
                return {
                    'dark_mode': result.get('dark_mode', True),
                    'reminder_interval': result.get('reminder_interval', 30),
                    'notifications_enabled': result.get('notifications_enabled', True),
                    'hydration_reminders': result.get('hydration_reminders', True),
                    'hydration_goal': result.get('hydration_goal', 2000),
                    'mobile_notifications_enabled': result.get('mobile_notifications_enabled', True),
                    'posture_alert_threshold_minutes': result.get('posture_alert_threshold_minutes', 2),
                }
            else:
                return default_settings
        except Exception as e:
            print(f"Error getting settings: {e}")
            return default_settings
    
    def update_user_settings(self, user_id: int, settings: Dict) -> bool:
        """Update user settings"""
        try:
            db = self.get_connection()
            
            update_data = {
                "dark_mode": settings.get('dark_mode', True),
                "reminder_interval": settings.get('reminder_interval', 30),
                "notifications_enabled": settings.get('notifications_enabled', True),
                "hydration_reminders": settings.get('hydration_reminders', True),
                "hydration_goal": settings.get('hydration_goal', 2000),
                "mobile_notifications_enabled": settings.get('mobile_notifications_enabled', True),
                "posture_alert_threshold_minutes": settings.get('posture_alert_threshold_minutes', 2),
            }
            
            db.user_settings.update_one(
                {"user_id": user_id},
                {"$set": update_data},
                upsert=True
            )
            
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
            db = self.get_connection()
            
            log_doc = {
                "user_id": user_id,
                "amount_ml": amount_ml,
                "drink_type": drink_type,
                "notes": notes,
                "timestamp": datetime.now()
            }
            
            db.hydration_logs.insert_one(log_doc)
            return True
        except Exception as e:
            print(f"Error logging hydration: {e}")
            return False
    
    def get_today_hydration(self, user_id: int) -> Dict:
        """Get today's hydration data"""
        try:
            db = self.get_connection()
            
            # Get start of today
            today = datetime.now()
            start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Aggregate for today's logs
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": start_of_day}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_ml": {"$sum": "$amount_ml"},
                        "entries": {"$sum": 1}
                    }
                }
            ]
            
            logs_agg = list(db.hydration_logs.aggregate(pipeline))
            
            if logs_agg:
                total_ml = logs_agg[0]["total_ml"]
                entries = logs_agg[0]["entries"]
            else:
                total_ml = 0
                entries = 0
                
            # Get user's hydration goal
            settings = db.user_settings.find_one({"user_id": user_id})
            goal_ml = settings.get("hydration_goal", 2000) if settings else 2000
            
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
            db = self.get_connection()
            
            seven_days_ago = datetime.now() - timedelta(days=7)
            start_of_day = seven_days_ago.replace(hour=0, minute=0, second=0, microsecond=0)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": start_of_day}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
                        },
                        "total_ml": {"$sum": "$amount_ml"}
                    }
                },
                {
                    "$sort": {"_id": 1} # sort by date ascending
                }
            ]
            
            results = list(db.hydration_logs.aggregate(pipeline))
            
            return [{'date': row["_id"], 'total_ml': row["total_ml"]} for row in results]
        except Exception as e:
            print(f"Error getting weekly hydration: {e}")
            return []
    
    def update_hydration_goal(self, user_id: int, goal_ml: int) -> bool:
        """Update user's daily hydration goal"""
        try:
            db = self.get_connection()
            
            db.user_settings.update_one(
                {"user_id": user_id},
                {"$set": {"hydration_goal": goal_ml}},
                upsert=True
            )
            
            return True
        except Exception as e:
            print(f"Error updating hydration goal: {e}")
            return False

