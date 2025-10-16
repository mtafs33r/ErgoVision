"""
Test script to debug ErgoVision application issues
"""

import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        import customtkinter as ctk
        print("✅ CustomTkinter imported successfully")
    except Exception as e:
        print(f"❌ CustomTkinter import failed: {e}")
        return False
    
    try:
        from database import DatabaseManager
        print("✅ DatabaseManager imported successfully")
    except Exception as e:
        print(f"❌ DatabaseManager import failed: {e}")
        return False
    
    try:
        from auth import AuthWindow
        print("✅ AuthWindow imported successfully")
    except Exception as e:
        print(f"❌ AuthWindow import failed: {e}")
        return False
    
    try:
        from dashboard import DashboardWindow
        print("✅ DashboardWindow imported successfully")
    except Exception as e:
        print(f"❌ DashboardWindow import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database functionality"""
    print("\nTesting database...")
    
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        print("✅ Database initialized successfully")
        
        # Test creating a test user
        success = db.create_user("testuser", "test@example.com", "testpass")
        if success:
            print("✅ User creation test successful")
            
            # Test authentication
            user_data = db.authenticate_user("testuser", "testpass")
            if user_data:
                print("✅ User authentication test successful")
                print(f"User data: {user_data}")
                return user_data
            else:
                print("❌ User authentication test failed")
        else:
            print("❌ User creation test failed")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        traceback.print_exc()
    
    return None

def test_auth_window():
    """Test authentication window"""
    print("\nTesting authentication window...")
    
    try:
        from auth import AuthWindow
        import customtkinter as ctk
        
        def dummy_callback(user_data):
            print(f"Auth callback received: {user_data}")
        
        # Create auth window
        auth = AuthWindow(dummy_callback)
        print("✅ Auth window created successfully")
        
        # Don't actually show it, just test creation
        auth.window.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Auth window test failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_window():
    """Test dashboard window"""
    print("\nTesting dashboard window...")
    
    try:
        from dashboard import DashboardWindow
        from database import DatabaseManager
        
        # Create test user data
        user_data = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'remember_me': False
        }
        
        db = DatabaseManager()
        
        # Create dashboard window
        dashboard = DashboardWindow(user_data, db)
        print("✅ Dashboard window created successfully")
        
        # Don't actually show it, just test creation
        dashboard.window.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Dashboard window test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("ErgoVision Application Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check your dependencies.")
        return
    
    # Test database
    user_data = test_database()
    if not user_data:
        print("\n❌ Database tests failed. Check database setup.")
        return
    
    # Test auth window
    if not test_auth_window():
        print("\n❌ Auth window test failed.")
        return
    
    # Test dashboard window
    if not test_dashboard_window():
        print("\n❌ Dashboard window test failed.")
        return
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! The application should work correctly.")
    print("=" * 50)
    
    print("\nTo run the full application:")
    print("python main.py")

if __name__ == "__main__":
    main()

