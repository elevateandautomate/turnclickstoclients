"""
Flask web application for Contact Bot

This application provides a web interface for:
1. Uploading CSV files with contact information
2. Viewing progress of contact processing
3. Managing the contact bot
"""

import os
import csv
import json
import threading
from typing import Dict, List, Any, Optional
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename
from supabase import create_client, Client

# Import the ContactBot class
from contact_bot import ContactBot

# Constants
SUPABASE_URL = "https://eumhqssfvkyuepyrtlqj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjU2MTQwMSwiZXhwIjoyMDYyMTM3NDAxfQ.hpiGyFGfFOhkbrfLNnp9uapkICXeeBY-md6QCV0C0ck"
TABLE_NAME = "core_data"  # Using the core_data table (renamed from dentist)

# Flask app setup
app = Flask(__name__)
app.secret_key = "your-secret-key"  # Change this to a secure random key in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
ALLOWED_EXTENSIONS = {'csv'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Supabase client
supabase: Optional[Client] = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully initialized Supabase client.")
    else:
        print("CRITICAL: Supabase URL or Key is missing.")
except Exception as e:
    print(f"Error initializing Supabase client: {e}")

# Global bot instance and processing thread
bot_thread = None
is_processing = False

def allowed_file(filename: str) -> bool:
    """Check if file has an allowed extension

    Args:
        filename: Name of the file

    Returns:
        True if file has an allowed extension
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_contacts_thread(csv_path: Optional[str] = None, limit: int = 10) -> None:
    """Process contacts in a separate thread

    Args:
        csv_path: Path to CSV file (optional)
        limit: Maximum number of contacts to process
    """
    global is_processing
    is_processing = True

    try:
        bot = ContactBot(headless=True)

        try:
            if csv_path:
                bot.process_csv(csv_path)
            else:
                bot.process_contacts_from_supabase(limit=limit)
        finally:
            bot.close()

    except Exception as e:
        print(f"Error in processing thread: {e}")
    finally:
        is_processing = False

@app.route('/')
def index():
    """Home page with CSV upload form"""
    return render_template('index.html', is_processing=is_processing)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload"""
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Start processing in a separate thread
        global bot_thread
        if bot_thread is not None and bot_thread.is_alive():
            flash('Processing already in progress')
            return redirect(url_for('index'))

        bot_thread = threading.Thread(target=process_contacts_thread, args=(file_path,))
        bot_thread.daemon = True
        bot_thread.start()

        flash(f'File {filename} uploaded and processing started')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid file type. Please upload a CSV file.')
        return redirect(request.url)

@app.route('/process')
def process():
    """Start processing contacts from Supabase"""
    global bot_thread

    # Debug logging
    print(f"Process route called in coldcontact/app.py with table name: {TABLE_NAME}")

    # Test Supabase connection
    try:
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if supabase_url and supabase_key:
            print(f"Connecting to Supabase at {supabase_url}")
            supabase = create_client(supabase_url, supabase_key)
            print("Testing Supabase connection...")
            data = supabase.table(TABLE_NAME).select("*").limit(1).execute()
            print(f"Supabase test query result: {data}")
        else:
            print("Supabase URL or Key is missing")
    except Exception as e:
        print(f"Error connecting to Supabase: {str(e)}")
        import traceback
        traceback.print_exc()

    if bot_thread is not None and bot_thread.is_alive():
        flash('Processing already in progress')
        return redirect(url_for('dashboard'))

    limit = request.args.get('limit', 10, type=int)
    bot_thread = threading.Thread(target=process_contacts_thread, args=(None, limit))
    bot_thread.daemon = True
    bot_thread.start()

    flash(f'Processing started for up to {limit} contacts')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Dashboard for viewing progress"""
    contacts = []

    if supabase:
        try:
            response = supabase.table(TABLE_NAME).select("*").order('created_at', desc=True).limit(100).execute()
            contacts = response.data
        except Exception as e:
            print(f"Error fetching contacts: {e}")

    return render_template('dashboard.html', contacts=contacts, is_processing=is_processing)

@app.route('/api/contacts')
def api_contacts():
    """API endpoint for getting contacts data"""
    if not supabase:
        return jsonify({"error": "Supabase client not initialized"}), 500

    try:
        response = supabase.table(TABLE_NAME).select("*").order('created_at', desc=True).limit(100).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status')
def api_status():
    """API endpoint for getting processing status"""
    return jsonify({"is_processing": is_processing})

@app.route('/api/retry/<contact_id>')
def api_retry(contact_id):
    """API endpoint for retrying a contact"""
    if not supabase:
        return jsonify({"error": "Supabase client not initialized"}), 500

    try:
        # Reset status fields
        update_data = {
            "website_visited": None,
            "website_visited_message": None,
            "contact_form_found": None,
            "contact_form_found_message": None,
            "contact_form_submitted": None,
            "contact_form_submitted_message": None,
            "linkedin_connected": None,
            "linkedin_connected_message": None,
            "error": None
        }

        supabase.table(TABLE_NAME).update(update_data).eq("id", contact_id).execute()

        # Start processing in a separate thread if not already running
        global bot_thread
        if bot_thread is None or not bot_thread.is_alive():
            bot_thread = threading.Thread(target=process_contacts_thread)
            bot_thread.daemon = True
            bot_thread.start()

        return jsonify({"success": True, "message": f"Contact {contact_id} queued for retry"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
