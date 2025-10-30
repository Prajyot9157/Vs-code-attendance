from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import sqlite3
import hashlib
from datetime import datetime, date
import pandas as pd
import os
from database import init_db, get_db_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize database
init_db()

# Subjects list
SUBJECTS = ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'Computer Science', 'English']

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        
        if user_type == 'student':
            student = conn.execute(
                'SELECT * FROM students WHERE username = ? AND password = ?',
                (username, hashed_password)
            ).fetchone()
            
            if student:
                session['user_id'] = student['id']
                session['username'] = student['username']
                session['name'] = student['name']
                session['class'] = student['class']
                session['user_type'] = 'student'
                conn.close()
                return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid student credentials!')
        
        elif user_type == 'admin':
            admin = conn.execute(
                'SELECT * FROM admin WHERE username = ? AND password = ?',
                (username, hashed_password)
            ).fetchone()
            
            if admin:
                session['user_id'] = admin['id']
                session['username'] = admin['username']
                session['user_type'] = 'admin'
                conn.close()
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials!')
        
        conn.close()
    
    return render_template('login.html')

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_type' not in session or session['user_type'] != 'student':
        return redirect(url_for('login'))
    
    # Check if student has already marked attendance for today
    conn = get_db_connection()
    today = date.today().isoformat()
    
    today_attendance = conn.execute('''
        SELECT subject FROM attendance 
        WHERE student_id = ? AND date = ?
    ''', (session['user_id'], today)).fetchall()
    
    attended_subjects = [row['subject'] for row in today_attendance]
    conn.close()
    
    return render_template('student_dashboard.html', 
                         subjects=SUBJECTS, 
                         attended_subjects=attended_subjects)

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'user_type' not in session or session['user_type'] != 'student':
        return redirect(url_for('login'))
    
    subject = request.form['subject']
    today = date.today().isoformat()
    current_time = datetime.now().strftime('%H:%M:%S')
    
    conn = get_db_connection()
    
    # Check if already marked for this subject today
    existing = conn.execute('''
        SELECT * FROM attendance 
        WHERE student_id = ? AND subject = ? AND date = ?
    ''', (session['user_id'], subject, today)).fetchone()
    
    if existing:
        flash(f'You have already marked attendance for {subject} today!')
        conn.close()
        return redirect(url_for('student_dashboard'))
    
    # Insert attendance record
    conn.execute('''
        INSERT INTO attendance (student_id, subject, date, time, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (session['user_id'], subject, today, current_time, 'Present'))
    
    conn.commit()
    conn.close()
    
    flash(f'Attendance marked successfully for {subject}!')
    return redirect(url_for('student_dashboard'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get filter parameters
    class_filter = request.args.get('class_filter', '')
    subject_filter = request.args.get('subject_filter', '')
    date_filter = request.args.get('date_filter', '')
    
    # Build query with filters
    query = '''
        SELECT a.*, s.name, s.class 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id 
        WHERE 1=1
    '''
    params = []
    
    if class_filter:
        query += ' AND s.class = ?'
        params.append(class_filter)
    
    if subject_filter:
        query += ' AND a.subject = ?'
        params.append(subject_filter)
    
    if date_filter:
        query += ' AND a.date = ?'
        params.append(date_filter)
    
    query += ' ORDER BY a.date DESC, a.time DESC'
    
    attendance_records = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         attendance_records=attendance_records,
                         subjects=SUBJECTS)

@app.route('/export_excel')
def export_excel():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get all attendance records
    records = conn.execute('''
        SELECT s.name, s.class, a.subject, a.date, a.time, a.status
        FROM attendance a 
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC, a.time DESC
    ''').fetchall()
    
    conn.close()
    
    # Convert to DataFrame
    df = pd.DataFrame(records, columns=['Name', 'Class', 'Subject', 'Date', 'Time', 'Status'])
    
    # Create Excel file
    filename = f"attendance_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    filepath = os.path.join('static', 'exports', filename)
    
    # Ensure exports directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    df.to_excel(filepath, index=False)
    
    return render_template('export_success.html', filename=filename)

@app.route('/download_excel/<filename>')
def download_excel(filename):
    return send_file(f'static/exports/{filename}', as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
