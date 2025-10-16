# ErgoVision - AI Posture & Health Coach

A modern desktop application built with Python and CustomTkinter that helps users improve their posture and health through AI-powered monitoring, camera detection, and personalized health tips.

## Features

### 🏠 Authentication System
- Secure login and signup with SQLite database
- Password hashing for security
- "Remember Me" functionality
- Forgot password support

### 📊 User Dashboard
- Clean and responsive layout with sidebar navigation
- Personal information management
- Real-time BMI calculation
- Quick statistics overview
- Daily inspirational quotes

### 🎥 Posture Monitoring System
- Real-time camera detection using OpenCV
- Live posture analysis and feedback
- Posture scoring system (0-100)
- Session tracking and duration monitoring
- Visual posture guidelines and feedback

### 💬 AI Health Coach
- Personalized health and posture tips
- Dynamic recommendations based on:
  - Posture scores
  - BMI category
  - Desktop setup type
  - Session history
- Context-aware advice

### 📈 Reports & Analytics
- Comprehensive session history
- Interactive charts and graphs using matplotlib
- Data export to CSV and PDF
- Progress tracking over time
- Statistical analysis

### ⚙️ Settings Panel
- Profile management
- Theme customization (Dark/Light mode)
- Notification preferences
- Reminder interval settings
- Password change functionality
- Data export options

### 🔔 Smart Reminders
- Configurable posture break reminders
- Audio and visual notifications
- Intelligent timing based on user preferences

### 🎤 Voice Assistant (Bonus Feature)
- Text-to-speech feedback
- Posture status announcements
- Session summaries
- Motivational messages
- Welcome and goodbye messages

### 📝 Daily Quotes (Bonus Feature)
- Inspirational daily quotes
- Context-aware motivational messages
- Achievement-based encouragement

## Installation

### Prerequisites
- Python 3.10 or higher
- Webcam/Camera access
- Windows 10/11 (tested on Windows)

### Setup
1. Clone or download the project files
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

### Dependencies
- `customtkinter` - Modern GUI framework
- `opencv-python` - Camera and image processing
- `matplotlib` - Charts and data visualization
- `numpy` - Numerical computing
- `Pillow` - Image processing
- `pyttsx3` - Text-to-speech functionality
- `reportlab` - PDF generation
- `pandas` - Data manipulation and analysis

## Usage

### First Time Setup
1. Launch the application
2. Create a new account or login
3. Complete your profile information in the Dashboard
4. Start your first posture monitoring session

### Posture Monitoring
1. Navigate to the "Monitoring" tab
2. Click "Start Monitoring" to begin camera detection
3. Follow the visual feedback to maintain good posture
4. Stop monitoring when your session is complete
5. View your session results and statistics

### AI Coaching
1. Visit the "AI Coach" tab for personalized tips
2. Click "Get New Tip" for fresh recommendations
3. Tips are generated based on your profile and session data

### Reports & Analytics
1. Access the "Reports" tab to view detailed analytics
2. Filter data by time period (7 days, 30 days, 90 days, All time)
3. Export data to CSV or PDF formats
4. View progress charts and statistics

### Settings
1. Open the "Settings" panel to customize preferences
2. Adjust theme, notifications, and reminder intervals
3. Update profile information
4. Change password or export data

## File Structure

```
ErgoVision/
├── main.py                 # Main application entry point
├── auth.py                 # Authentication system
├── dashboard.py            # Main dashboard interface
├── database.py             # Database management
├── monitoring.py           # Posture monitoring system
├── ai_coach.py             # AI health coaching
├── reports.py              # Reports and analytics
├── settings.py             # Settings panel
├── voice_assistant.py      # Voice assistant (bonus)
├── daily_quotes.py         # Daily quotes system (bonus)
├── config.json             # Application configuration
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── build.py               # Build script for packaging
```

## Configuration

The application uses `config.json` for configuration settings including:
- Default UI theme and colors
- Camera resolution settings
- Posture scoring thresholds
- Feature toggles
- Database settings

## Building for Distribution

To create an executable file:

```bash
python build.py
```

This will create a standalone executable using PyInstaller.

## Technical Details

### Posture Detection Algorithm
The application uses a simplified posture detection algorithm that analyzes:
- Image variance (movement/stability)
- Brightness levels (head position)
- Edge density (alignment)

*Note: This is a demonstration implementation. A production version would use advanced pose estimation libraries like MediaPipe.*

### Database Schema
- **users**: User accounts and authentication
- **user_profiles**: Personal information and preferences
- **posture_sessions**: Monitoring session data
- **user_settings**: Application preferences

### Architecture
- Modular design with separate components
- Event-driven UI updates
- Threaded camera processing
- Voice assistant integration
- Configurable reminder system

## Troubleshooting

### Common Issues

**Camera not working:**
- Ensure camera is not being used by another application
- Check camera permissions
- Try restarting the application

**Voice assistant not working:**
- Install additional TTS engines if needed
- Check system audio settings
- Voice can be disabled in settings

**Performance issues:**
- Close other camera applications
- Reduce camera resolution in config
- Ensure adequate system resources

## Future Enhancements

- Advanced pose estimation using MediaPipe
- Machine learning-based posture analysis
- Cloud synchronization
- Mobile companion app
- Integration with fitness trackers
- Advanced analytics and insights

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions, please check the troubleshooting section or review the code documentation.

---

**ErgoVision** - Transforming workspace health through AI-powered posture monitoring and coaching.
