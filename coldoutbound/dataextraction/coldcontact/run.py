"""
Run script for Contact Bot

This script provides a simple way to start the Contact Bot application.
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import flask
        import selenium
        import supabase
        print("All required packages are installed.")
        return True
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install the required packages using: pip install -r requirements.txt")
        return False

def start_app():
    """Start the Flask application"""
    print("Starting Contact Bot application...")
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("=" * 50)
    print("Contact Bot - Automated Contact Form Filling and LinkedIn Outreach")
    print("=" * 50)
    
    # Check if requirements are installed
    if not check_requirements():
        install = input("Would you like to install the required packages now? (y/n): ")
        if install.lower() == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        else:
            print("Exiting. Please install the required packages and try again.")
            sys.exit(1)
    
    # Start the application
    start_app()

if __name__ == "__main__":
    main()
