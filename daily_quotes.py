"""
Daily motivational quotes for ErgoVision application
Provides inspirational messages for users
"""

import random
from datetime import datetime, date
from typing import List

class DailyQuotes:
    def __init__(self):
        """Initialize daily quotes system"""
        self.quotes = [
            "Good posture is not just about looking confident—it's about feeling confident!",
            "Every small step towards better posture is a step towards better health.",
            "Your future self will thank you for taking care of your posture today.",
            "Consistency is key—small daily improvements lead to big results.",
            "Remember: Rome wasn't built in a day, and neither is perfect posture!",
            "You're investing in your health every time you adjust your posture.",
            "The best time to start improving your posture was yesterday. The second best time is now.",
            "Your spine is your lifeline—treat it with care and respect.",
            "Small changes today lead to big improvements tomorrow.",
            "You have the power to transform your workspace into a health-promoting environment.",
            "Posture is the foundation of confidence and health.",
            "Stand tall, sit straight, and let your posture reflect your inner strength.",
            "Every moment of good posture is an investment in your future wellness.",
            "Your body is your temple—honor it with proper posture.",
            "Good posture is a habit that pays dividends for life.",
            "The way you hold yourself affects how you feel about yourself.",
            "Posture is not just physical—it's a reflection of your mental state.",
            "Take pride in your posture, and your posture will take pride in you.",
            "Healthy posture leads to a healthy mind and body.",
            "You are stronger than you think—let your posture show it.",
            "Every correction is progress, every day is a new opportunity.",
            "Posture is the silent language of confidence.",
            "Your spine carries you through life—give it the respect it deserves.",
            "Good posture is the foundation of good health.",
            "Stand up straight and let your posture speak of your determination.",
            "The way you sit affects the way you think and feel.",
            "Posture is not about perfection—it's about progress.",
            "Your posture tells a story—make it a story of strength and health.",
            "Every time you straighten up, you're choosing health over habit.",
            "Good posture is a gift you give yourself every day.",
            "Let your posture reflect the champion that you are.",
            "Healthy posture is the foundation of a healthy life.",
            "Your posture is your power—use it wisely.",
            "Stand tall, breathe deep, and let your posture inspire others.",
            "Posture is not just about appearance—it's about function and health.",
            "Every moment of awareness is a moment of improvement.",
            "Your posture is a reflection of your self-respect.",
            "Good posture is the cornerstone of physical and mental wellness.",
            "Stand up for your health—literally and figuratively.",
            "Posture is the silent partner in your health journey.",
            "Your spine is the backbone of your health—treat it well.",
            "Good posture is a habit that creates other good habits.",
            "Let your posture be a testament to your commitment to health.",
            "Every adjustment is a step towards better health.",
            "Posture is the foundation upon which health is built.",
            "Stand tall, sit proud, and let your posture show your determination.",
            "Your posture is your personal statement about your health.",
            "Good posture is not a luxury—it's a necessity for a healthy life.",
            "Every moment of good posture is a moment of self-care.",
            "Let your posture reflect the care you have for yourself."
        ]
        
        # Special quotes for different contexts
        self.morning_quotes = [
            "Start your day with intention and good posture!",
            "Good morning! Let's begin this day with healthy habits.",
            "Rise and shine! Time to align your spine and your mind.",
            "Morning is the perfect time to set your posture intentions.",
            "A good day starts with good posture!"
        ]
        
        self.evening_quotes = [
            "End your day with gratitude for taking care of your posture.",
            "Well done on another day of mindful posture practice!",
            "Your spine thanks you for the care you showed today.",
            "Rest well, knowing you've taken care of your posture today.",
            "Tomorrow is another opportunity to practice good posture."
        ]
        
        self.encouragement_quotes = [
            "You're doing better than you think—keep going!",
            "Every expert was once a beginner—you're on the right path.",
            "Progress, not perfection—you're making great strides!",
            "Your dedication to good posture is inspiring!",
            "Small steps lead to big changes—you're doing amazing!"
        ]
        
        self.achievement_quotes = [
            "Congratulations on your posture progress!",
            "Your commitment to health is paying off!",
            "Well done on maintaining excellent posture!",
            "You're becoming a posture champion!",
            "Your dedication is transforming your health!"
        ]
    
    def get_daily_quote(self, user_date: date = None) -> str:
        """Get a daily quote based on the date"""
        if user_date is None:
            user_date = date.today()
        
        # Use date to seed random for consistent daily quotes
        random.seed(user_date.toordinal())
        quote = random.choice(self.quotes)
        random.seed()  # Reset seed
        
        return quote
    
    def get_quote_of_the_day(self) -> str:
        """Get today's quote"""
        return self.get_daily_quote(date.today())
    
    def get_morning_quote(self) -> str:
        """Get a morning-specific quote"""
        return random.choice(self.morning_quotes)
    
    def get_evening_quote(self) -> str:
        """Get an evening-specific quote"""
        return random.choice(self.evening_quotes)
    
    def get_encouragement_quote(self) -> str:
        """Get an encouragement quote"""
        return random.choice(self.encouragement_quotes)
    
    def get_achievement_quote(self) -> str:
        """Get an achievement quote"""
        return random.choice(self.achievement_quotes)
    
    def get_contextual_quote(self, context: str) -> str:
        """Get a quote based on context"""
        context_lower = context.lower()
        
        if 'morning' in context_lower or 'start' in context_lower:
            return self.get_morning_quote()
        elif 'evening' in context_lower or 'end' in context_lower:
            return self.get_evening_quote()
        elif 'encourage' in context_lower or 'motivate' in context_lower:
            return self.get_encouragement_quote()
        elif 'achievement' in context_lower or 'success' in context_lower:
            return self.get_achievement_quote()
        else:
            return self.get_quote_of_the_day()
    
    def get_random_quote(self) -> str:
        """Get a random quote"""
        return random.choice(self.quotes)
    
    def get_quote_for_score(self, score: int) -> str:
        """Get a quote based on posture score"""
        if score >= 80:
            return f"🌟 Outstanding score of {score}! {self.get_achievement_quote()}"
        elif score >= 60:
            return f"👍 Great score of {score}! {self.get_encouragement_quote()}"
        else:
            return f"💪 Score of {score} - {self.get_encouragement_quote()}"
    
    def get_quote_for_rating(self, rating: str) -> str:
        """Get a quote based on posture rating"""
        rating_lower = rating.lower()
        
        if 'excellent' in rating_lower:
            return f"🏆 {rating} posture! {self.get_achievement_quote()}"
        elif 'average' in rating_lower:
            return f"📈 {rating} posture - {self.get_encouragement_quote()}"
        else:
            return f"💪 {rating} posture - {self.get_encouragement_quote()}"
    
    def get_bmi_quote(self, bmi_category: str) -> str:
        """Get a quote based on BMI category"""
        if bmi_category == "Normal":
            return "🎯 Perfect BMI! Your healthy lifestyle is showing in your posture too!"
        elif bmi_category in ["Overweight", "Obese"]:
            return "💪 Every step towards better health counts! Good posture is a great start!"
        else:
            return "🌱 Focus on building strength and maintaining good posture!"
    
    def get_session_quote(self, session_count: int, avg_score: float) -> str:
        """Get a quote based on session statistics"""
        if session_count == 0:
            return "🚀 Ready to start your posture improvement journey? Every expert was once a beginner!"
        elif session_count < 5:
            return f"📚 {session_count} sessions in! You're building great habits. Keep going!"
        elif session_count < 20:
            return f"🎯 {session_count} sessions completed! Your dedication is paying off!"
        else:
            return f"🏆 {session_count} sessions! You're a true posture champion!"
    
    def get_time_based_quote(self) -> str:
        """Get a quote based on current time of day"""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:  # Morning
            return self.get_morning_quote()
        elif 18 <= current_hour < 22:  # Evening
            return self.get_evening_quote()
        else:  # Afternoon/Night
            return self.get_random_quote()
    
    def add_custom_quote(self, quote: str):
        """Add a custom quote to the collection"""
        if quote and quote.strip():
            self.quotes.append(quote.strip())
    
    def get_quote_count(self) -> int:
        """Get total number of quotes available"""
        return len(self.quotes)

# Global quotes instance
daily_quotes = DailyQuotes()
