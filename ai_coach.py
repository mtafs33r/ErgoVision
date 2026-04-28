"""
AI Health Coach for ErgoVision application
Provides personalized health and posture tips
"""

import random
import os
from typing import Dict, List, Optional
from database import DatabaseManager

try:
    from google import genai as google_genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

class AICoach:
    def __init__(self, db_manager: DatabaseManager):
        """Initialize AI coach"""
        self.db_manager = db_manager
        
        # Initialize Gemini API if available
        self.gemini_client = None
        api_key = os.getenv("GEMINI_API_KEY")
        if HAS_GEMINI and api_key:
            try:
                self.gemini_client = google_genai.Client(api_key=api_key)
            except Exception as e:
                print(f"Failed to initialize Gemini AI: {e}")
        
        # Health tips database
        self.posture_tips = [
            "Keep your feet flat on the floor and your back straight against the chair.",
            "Position your monitor at eye level to avoid neck strain.",
            "Take a 5-minute break every hour to stretch and move around.",
            "Adjust your chair height so your knees are at a 90-degree angle.",
            "Keep your shoulders relaxed and avoid hunching forward.",
            "Use a footrest if your feet don't comfortably reach the floor.",
            "Position your keyboard and mouse at elbow height.",
            "Look away from your screen every 20 minutes to focus on distant objects.",
            "Keep your wrists straight while typing, not bent up or down.",
            "Ensure your monitor is about an arm's length away from your eyes."
        ]
        
        self.exercise_tips = [
            "Try neck rolls: Slowly roll your head in a circle 5 times each direction.",
            "Shoulder shrugs: Lift your shoulders up to your ears, hold for 5 seconds, then release.",
            "Seated spinal twist: Sit tall and gently twist your torso to each side.",
            "Wrist stretches: Extend your arm and gently pull your fingers back with your other hand.",
            "Chest opener: Clasp your hands behind your back and lift your arms.",
            "Ankle circles: Lift your foot and rotate your ankle 10 times each direction.",
            "Seated forward fold: Sit tall and gently fold forward, letting your arms hang.",
            "Cat-cow stretch: Arch and round your back while seated.",
            "Leg extensions: Straighten one leg at a time and hold for 5 seconds.",
            "Deep breathing: Take 5 deep breaths, focusing on expanding your chest."
        ]
        
        self.ergonomic_tips = [
            "Invest in an ergonomic chair with proper lumbar support.",
            "Use a monitor stand to raise your screen to eye level.",
            "Consider a standing desk to alternate between sitting and standing.",
            "Use a wrist rest for your keyboard and mouse pad.",
            "Ensure adequate lighting to reduce eye strain.",
            "Keep frequently used items within easy reach.",
            "Use a document holder if you frequently reference papers.",
            "Consider blue light glasses for extended screen time.",
            "Organize your workspace to minimize reaching and twisting.",
            "Use an ergonomic keyboard and mouse if possible."
        ]
        
        self.nutrition_tips = [
            "Stay hydrated by drinking water throughout the day.",
            "Take breaks to eat healthy snacks like nuts or fruits.",
            "Avoid excessive caffeine, which can increase tension.",
            "Include foods rich in omega-3 fatty acids for brain health.",
            "Eat regular meals to maintain steady energy levels.",
            "Consider taking vitamin D supplements if you work indoors.",
            "Limit processed foods that can cause energy crashes.",
            "Include magnesium-rich foods to help with muscle relaxation.",
            "Stay away from sugary drinks that can cause energy spikes.",
            "Eat foods with anti-inflammatory properties like berries."
        ]
        
        self.motivational_quotes = [
            "Good posture is not just about looking confident—it's about feeling confident!",
            "Every small step towards better posture is a step towards better health.",
            "Your future self will thank you for taking care of your posture today.",
            "Consistency is key—small daily improvements lead to big results.",
            "Remember: Rome wasn't built in a day, and neither is perfect posture!",
            "You're investing in your health every time you adjust your posture.",
            "The best time to start improving your posture was yesterday. The second best time is now.",
            "Your spine is your lifeline—treat it with care and respect.",
            "Small changes today lead to big improvements tomorrow.",
            "You have the power to transform your workspace into a health-promoting environment."
        ]
    
    def _build_gemini_prompt(self, profile: Dict, sessions: List[Dict]) -> str:
        """Build prompt for Gemini AI based on user context"""
        name = profile.get('name', 'User')
        
        context = f"You are ErgoVision's AI Posture and Health Coach. Keep your response concise (3-4 sentences max), friendly, motivating, and personalized.\n\n"
        context += f"User Profile:\n- Name: {name}\n"
        
        if profile.get('height') and profile.get('weight'):
            bmi, category = self.db_manager.calculate_bmi(profile['height'], profile['weight'])
            context += f"- Health Check: BMI is {bmi:.1f} ({category})\n"
            
        if profile.get('desktop_setup'):
            context += f"- Setup: {profile['desktop_setup']}\n"
            
        if sessions:
            recent_scores = [s['score'] for s in sessions[:5] if s.get('score')]
            if recent_scores:
                avg_score = sum(recent_scores) / len(recent_scores)
                context += f"- Recent Posture Score Average: {avg_score:.1f}/100\n"
                
        context += "\nBased on this profile, provide ONE highly specific piece of actionable ergonomic, postural, or exercise advice. Use emojis, stay professional yet encouraging. Address them by their name!"
        return context

    def generate_tip(self, profile: Optional[Dict], sessions: List[Dict]) -> str:
        """Generate a personalized health tip based on user data"""
        # Try to use Gemini AI first
        if self.gemini_client and profile:
            try:
                prompt = self._build_gemini_prompt(profile, sessions)
                response = self.gemini_client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt
                )
                if response and response.text:
                    return f"🤖 GEMINI AI COACH:\n\n{response.text.strip()}"
            except Exception as e:
                print(f"Gemini generation failed, falling back to local tips: {e}")
                
        tip_categories = []
        
        # Analyze user profile
        if profile:
            # Check BMI
            if profile.get('height') and profile.get('weight'):
                bmi, category = self.db_manager.calculate_bmi(
                    profile['height'], profile['weight']
                )
                if category in ["Overweight", "Obese"]:
                    tip_categories.append("nutrition")
            
            # Check desktop setup
            setup = profile.get('desktop_setup', '') or ''
            setup = setup.lower() if setup else ''
            if 'laptop' in setup:
                tip_categories.extend(["posture", "ergonomic"])
            elif 'standing' in setup:
                tip_categories.extend(["exercise", "posture"])
            else:
                tip_categories.extend(["posture", "ergonomic"])
        
        # Analyze recent sessions
        if sessions:
            recent_scores = [s['score'] for s in sessions[:5] if s.get('score')]
            if recent_scores:
                avg_recent_score = sum(recent_scores) / len(recent_scores)
                
                if avg_recent_score < 60:
                    tip_categories.extend(["posture", "exercise"])
                elif avg_recent_score < 80:
                    tip_categories.extend(["posture", "exercise"])
                else:
                    tip_categories.extend(["exercise", "motivation"])
        
        # If no specific categories determined, provide general tips
        if not tip_categories:
            tip_categories = ["posture", "exercise", "ergonomic"]
        
        # Select random category from determined categories
        selected_category = random.choice(tip_categories)
        
        # Generate tip based on category
        if selected_category == "posture":
            tip = random.choice(self.posture_tips)
            category_title = "Posture Improvement"
        elif selected_category == "exercise":
            tip = random.choice(self.exercise_tips)
            category_title = "Desk Exercise"
        elif selected_category == "ergonomic":
            tip = random.choice(self.ergonomic_tips)
            category_title = "Ergonomic Setup"
        elif selected_category == "nutrition":
            tip = random.choice(self.nutrition_tips)
            category_title = "Health & Nutrition"
        else:  # motivation
            tip = random.choice(self.motivational_quotes)
            category_title = "Daily Motivation"
        
        # Format the tip
        formatted_tip = f"💡 {category_title}\n\n{tip}"
        
        # Add personalized context if available
        if profile and profile.get('name'):
            formatted_tip = f"Hello {profile['name']}!\n\n{formatted_tip}"
        
        # Add session-based encouragement
        if sessions:
            recent_sessions = [s for s in sessions[:3]]
            if recent_sessions:
                avg_score = sum(s['score'] for s in recent_sessions if s.get('score')) / len([s for s in recent_sessions if s.get('score')])
                if avg_score >= 80:
                    formatted_tip += "\n\n🌟 You're doing great! Keep up the excellent posture!"
                elif avg_score >= 60:
                    formatted_tip += "\n\n👍 You're making good progress! A few more adjustments and you'll be perfect!"
                else:
                    formatted_tip += "\n\n💪 Don't worry! Every expert was once a beginner. Keep practicing!"
        
        return formatted_tip
    
    def get_daily_quote(self) -> str:
        """Get a daily motivational quote"""
        return random.choice(self.motivational_quotes)
    
    def get_posture_advice(self, current_score: int, recent_scores: List[int]) -> str:
        """Get specific posture advice based on current and recent scores"""
        if current_score >= 80:
            return "Excellent posture! You're setting a great example. Keep maintaining this alignment and consider helping others improve their posture too."
        elif current_score >= 60:
            return "Good posture with room for improvement. Focus on keeping your shoulders relaxed and your spine aligned. Small adjustments can make a big difference."
        else:
            return "Time for a posture check! Try sitting up straight, relaxing your shoulders, and ensuring your feet are flat on the floor. You've got this!"
    
    def get_exercise_recommendation(self, setup_type: str, session_duration: float) -> str:
        """Get exercise recommendations based on setup and session duration"""
        if session_duration > 60:  # More than 1 hour
            return "You've been sitting for over an hour! Time for a movement break. Try standing up, walking around, and doing some light stretching."
        elif 'standing' in setup_type.lower():
            return "Great choice with the standing desk! Remember to alternate between sitting and standing every 30 minutes for optimal health."
        else:
            return "Consider taking a 2-minute movement break. Try some seated stretches or walk to get water to keep your body active."
    
    def get_ergonomic_advice(self, setup_type: str, profile: Dict) -> str:
        """Get ergonomic setup advice based on user's current setup"""
        advice = []
        
        if 'laptop' in setup_type.lower():
            advice.append("Consider using an external keyboard and mouse with your laptop to improve your working posture.")
            advice.append("Use a laptop stand to raise your screen to eye level.")
        
        if 'standing' in setup_type.lower():
            advice.append("Remember to alternate between sitting and standing every 30-60 minutes.")
            advice.append("Wear comfortable shoes and use an anti-fatigue mat when standing.")
        
        if profile.get('height'):
            height = profile['height']
            if height > 180:  # Tall person
                advice.append("Make sure your chair and desk height accommodate your taller frame.")
            elif height < 160:  # Shorter person
                advice.append("Consider a footrest if your feet don't comfortably reach the floor.")
        
        return " ".join(advice) if advice else "Your current setup looks good! Keep maintaining proper ergonomic practices."
    
    def generate_weekly_report(self, sessions: List[Dict]) -> str:
        """Generate a weekly progress report"""
        if not sessions:
            return "No sessions recorded this week. Start monitoring to track your posture improvement journey!"
        
        # Calculate weekly statistics
        weekly_scores = [s['score'] for s in sessions if s.get('score')]
        if not weekly_scores:
            return "Sessions recorded but no scores available. Make sure to complete some monitoring sessions!"
        
        avg_score = sum(weekly_scores) / len(weekly_scores)
        best_score = max(weekly_scores)
        improvement = weekly_scores[-1] - weekly_scores[0] if len(weekly_scores) > 1 else 0
        
        report = f"Weekly Posture Report\n\n"
        report += f"📊 Sessions Completed: {len(sessions)}\n"
        report += f"📈 Average Score: {avg_score:.1f}/100\n"
        report += f"🏆 Best Score: {best_score}/100\n"
        
        if improvement > 0:
            report += f"📈 Improvement: +{improvement:.1f} points\n"
        elif improvement < 0:
            report += f"📉 Decline: {improvement:.1f} points\n"
        else:
            report += f"📊 No change in score\n"
        
        # Add encouragement
        if avg_score >= 80:
            report += "\n🌟 Outstanding work! You're maintaining excellent posture consistently."
        elif avg_score >= 60:
            report += "\n👍 Good progress! Keep working on those small improvements."
        else:
            report += "\n💪 Room for improvement, but every session is a step forward!"
        
        return report
