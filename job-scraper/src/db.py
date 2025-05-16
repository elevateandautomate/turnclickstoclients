import sqlite3
import os
import pandas as pd
from datetime import datetime
from config import DB_PATH

def ensure_db_exists():
    """Create the database and tables if they don't exist."""
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create jobs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        job_id TEXT UNIQUE,
        title TEXT,
        company TEXT,
        location TEXT,
        description TEXT,
        url TEXT,
        salary TEXT,
        date_posted TEXT,
        job_board TEXT,
        date_scraped TEXT,
        status TEXT DEFAULT 'new',
        notes TEXT,
        keywords TEXT
    )
    ''')
    
    # Create applications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY,
        job_id INTEGER,
        date_applied TEXT,
        status TEXT DEFAULT 'applied',
        response_date TEXT,
        follow_up_date TEXT,
        notes TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def save_job(job_data):
    """Save a job to the database."""
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO jobs (
            job_id, title, company, location, description, url, 
            salary, date_posted, job_board, date_scraped, status, keywords
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_data.get('job_id', ''),
            job_data.get('title', ''),
            job_data.get('company', ''),
            job_data.get('location', ''),
            job_data.get('description', ''),
            job_data.get('url', ''),
            job_data.get('salary', ''),
            job_data.get('date_posted', ''),
            job_data.get('job_board', ''),
            datetime.now().isoformat(),
            'new',
            job_data.get('keywords', '')
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def save_application(job_id, notes=""):
    """Record an application in the database."""
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Update job status
        cursor.execute("UPDATE jobs SET status = 'applied' WHERE id = ?", (job_id,))
        
        # Record application
        cursor.execute('''
        INSERT INTO applications (job_id, date_applied, status, notes)
        VALUES (?, ?, ?, ?)
        ''', (job_id, datetime.now().isoformat(), 'applied', notes))
        
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_jobs(status=None, job_board=None):
    """Get jobs with optional filtering."""
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if job_board:
        query += " AND job_board = ?"
        params.append(job_board)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_applications():
    """Get all applications with job details."""
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT a.*, j.title, j.company, j.url
    FROM applications a
    JOIN jobs j ON a.job_id = j.id
    ORDER BY a.date_applied DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_job_status(job_id, status, notes=None):
    """Update a job's status and optionally add notes."""
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        if notes:
            cursor.execute("UPDATE jobs SET status = ?, notes = ? WHERE id = ?", (status, notes, job_id))
        else:
            cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
        
        conn.commit()
    finally:
        conn.close()

def update_application_status(app_id, status, notes=None, response_date=None, follow_up_date=None):
    """Update an application's status and details."""
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        updates = ["status = ?"]
        params = [status]
        
        if notes:
            updates.append("notes = ?")
            params.append(notes)
        
        if response_date:
            updates.append("response_date = ?")
            params.append(response_date)
        
        if follow_up_date:
            updates.append("follow_up_date = ?")
            params.append(follow_up_date)
        
        query = f"UPDATE applications SET {', '.join(updates)} WHERE id = ?"
        params.append(app_id)
        
        cursor.execute(query, params)
        conn.commit()
    finally:
        conn.close()

def export_jobs_to_csv(file_path):
    """Export all jobs to a CSV file."""
    df = get_jobs()
    df.to_csv(file_path, index=False)
    return len(df)

def export_applications_to_csv(file_path):
    """Export all applications to a CSV file."""
    df = get_applications()
    df.to_csv(file_path, index=False)
    return len(df) 