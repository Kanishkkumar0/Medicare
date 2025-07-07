from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
import bcrypt
import re
from difflib import get_close_matches
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="alucard@69420",
        database="hospital_management"
    )

def insert_sample_doctors():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First, check for existing doctors in the doctors table
        cursor.execute('SELECT * FROM doctors')
        existing_doctors = cursor.fetchall()
        
        # If there are existing doctors, add them to users table if they don't exist
        for doctor in existing_doctors:
            cursor.execute('SELECT id FROM users WHERE id = %s', (doctor[1],))  # doctor[1] is user_id
            existing_user = cursor.fetchone()
            
            if not existing_user:
                # Create a username from first and last name
                username = f"{doctor[2].lower()}.{doctor[3].lower()}"  # doctor[2] is first_name, doctor[3] is last_name
                email = f"{username}@hospital.com"
                
                # Insert into users table
                cursor.execute('''
                    INSERT INTO users (username, password, email, role)
                    VALUES (%s, %s, %s, 'doctor')
                ''', (username, bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()), email))
                
                # Update the doctor's user_id
                cursor.execute('UPDATE doctors SET user_id = %s WHERE id = %s', 
                             (cursor.lastrowid, doctor[0]))
        
        # Check if doctors table is empty
        cursor.execute('SELECT COUNT(*) as count FROM doctors')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Sample doctor data with usernames and passwords
            doctors = [
                {
                    'username': 'john.smith',
                    'password': 'password123',
                    'email': 'john.smith@hospital.com',
                    'first_name': 'John',
                    'last_name': 'Smith',
                    'specialization': 'Cardiology',
                    'qualification': 'MD, FACC',
                    'experience': 15,
                    'phone': '+1 234 567 8901'
                },
                {
                    'username': 'sarah.davis',
                    'password': 'password123',
                    'email': 'sarah.davis@hospital.com',
                    'first_name': 'Sarah',
                    'last_name': 'Davis',
                    'specialization': 'Dermatology',
                    'qualification': 'MD, FAAD',
                    'experience': 10,
                    'phone': '+1 234 567 8902'
                },
                {
                    'username': 'robert.wilson',
                    'password': 'password123',
                    'email': 'robert.wilson@hospital.com',
                    'first_name': 'Robert',
                    'last_name': 'Wilson',
                    'specialization': 'Neurology',
                    'qualification': 'MD, PhD',
                    'experience': 20,
                    'phone': '+1 234 567 8903'
                },
                {
                    'username': 'emily.johnson',
                    'password': 'password123',
                    'email': 'emily.johnson@hospital.com',
                    'first_name': 'Emily',
                    'last_name': 'Johnson',
                    'specialization': 'Pediatrics',
                    'qualification': 'MD, FAAP',
                    'experience': 8,
                    'phone': '+1 234 567 8904'
                },
                {
                    'username': 'michael.brown',
                    'password': 'password123',
                    'email': 'michael.brown@hospital.com',
                    'first_name': 'Michael',
                    'last_name': 'Brown',
                    'specialization': 'Orthopedics',
                    'qualification': 'MD, FAAOS',
                    'experience': 12,
                    'phone': '+1 234 567 8905'
                },
                {
                    'username': 'jennifer.lee',
                    'password': 'password123',
                    'email': 'jennifer.lee@hospital.com',
                    'first_name': 'Jennifer',
                    'last_name': 'Lee',
                    'specialization': 'Ophthalmology',
                    'qualification': 'MD, FACS',
                    'experience': 9,
                    'phone': '+1 234 567 8906'
                },
                {
                    'username': 'david.martinez',
                    'password': 'password123',
                    'email': 'david.martinez@hospital.com',
                    'first_name': 'David',
                    'last_name': 'Martinez',
                    'specialization': 'General Surgery',
                    'qualification': 'MD, FACS',
                    'experience': 14,
                    'phone': '+1 234 567 8907'
                },
                {
                    'username': 'lisa.anderson',
                    'password': 'password123',
                    'email': 'lisa.anderson@hospital.com',
                    'first_name': 'Lisa',
                    'last_name': 'Anderson',
                    'specialization': 'Internal Medicine',
                    'qualification': 'MD, FACP',
                    'experience': 11,
                    'phone': '+1 234 567 8908'
                }
            ]
            
            # Insert each doctor
            for doctor in doctors:
                # Check if user already exists
                cursor.execute('SELECT id FROM users WHERE username = %s', (doctor['username'],))
                existing_user = cursor.fetchone()
                
                if not existing_user:
                    # Hash the password
                    hashed_password = bcrypt.hashpw(doctor['password'].encode('utf-8'), bcrypt.gensalt())
                    
                    # Insert into users table
                    cursor.execute('''
                        INSERT INTO users (username, password, email, role)
                        VALUES (%s, %s, %s, 'doctor')
                    ''', (doctor['username'], hashed_password, doctor['email']))
                    
                    user_id = cursor.lastrowid
                    
                    # Insert into doctors table
                    cursor.execute('''
                        INSERT INTO doctors 
                        (user_id, first_name, last_name, specialization, qualification, experience, phone)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        user_id,
                        doctor['first_name'],
                        doctor['last_name'],
                        doctor['specialization'],
                        doctor['qualification'],
                        doctor['experience'],
                        doctor['phone']
                    ))
            
            print("Successfully inserted sample doctors data")
        
        conn.commit()
        
    except Exception as e:
        print(f"Error inserting sample doctors: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def insert_sample_chatbot_questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if chatbot_questions table is empty
    cursor.execute('SELECT COUNT(*) as count FROM chatbot_questions')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Sample chatbot questions and answers
        qa_pairs = [
            ("What are your visiting hours?", "Our visiting hours are from 9 AM to 8 PM every day."),
            ("How do I schedule an appointment?", "You can schedule an appointment through our website or by calling our reception at 555-123-4567."),
            ("What insurance do you accept?", "We accept most major insurance plans including Medicare, Medicaid, Blue Cross Blue Shield, UnitedHealthcare, and Aetna."),
            ("How do I find a doctor?", "You can browse our 'Find a Doctor' section on the website or call our helpdesk for assistance."),
            ("Where are you located?", "Our main hospital is located at 123 Health Avenue, Medical City. We also have satellite clinics throughout the city."),
            ("What should I bring to my appointment?", "Please bring your ID, insurance card, list of current medications, and any relevant medical records or test results."),
            ("Do you have emergency services?", "Yes, our emergency department is open 24/7.")
        ]
        
        # Insert questions and answers
        cursor.executemany('''
            INSERT INTO chatbot_questions (question, answer)
            VALUES (%s, %s)
        ''', qa_pairs)
        
        conn.commit()
    
    conn.close()

# Initialize database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS hospital_management")
        cursor.execute("USE hospital_management")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                role ENUM('admin', 'doctor', 'nurse', 'patient', 'staff') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create rooms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_number VARCHAR(10) UNIQUE NOT NULL,
                room_type ENUM('consultation', 'examination', 'treatment', 'emergency') NOT NULL,
                status ENUM('available', 'occupied', 'maintenance') DEFAULT 'available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                dob DATE NOT NULL,
                gender ENUM('male', 'female', 'other') NOT NULL,
                blood_group VARCHAR(5),
                address TEXT,
                phone VARCHAR(15),
                emergency_contact VARCHAR(15),
                medical_history TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create doctors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                specialization VARCHAR(50) NOT NULL,
                qualification VARCHAR(100) NOT NULL,
                experience INT,
                phone VARCHAR(15),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create appointments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                reason TEXT,
                status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
            )
        """)
        
        # Create medical_records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NOT NULL,
                diagnosis TEXT,
                prescription TEXT,
                notes TEXT,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
            )
        """)
        
        # Create chatbot_questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatbot_questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        """)
        
        # Create unanswered_queries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unanswered_queries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                query TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Add room_id to appointments table if it doesn't exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'appointments' 
            AND column_name = 'room_id'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE appointments 
                ADD COLUMN room_id INT,
                ADD CONSTRAINT fk_room
                FOREIGN KEY (room_id) REFERENCES rooms(id)
            """)
        
        # Insert sample data
        insert_sample_doctors()
        insert_sample_chatbot_questions()
        
        # Insert sample rooms if table is empty
        cursor.execute("SELECT COUNT(*) FROM rooms")
        if cursor.fetchone()[0] == 0:
            sample_rooms = [
                ('C101', 'consultation'),
                ('C102', 'consultation'),
                ('E201', 'examination'),
                ('E202', 'examination'),
                ('T301', 'treatment'),
                ('T302', 'treatment'),
                ('ER01', 'emergency')
            ]
            cursor.executemany("""
                INSERT INTO rooms (room_number, room_type)
                VALUES (%s, %s)
            """, sample_rooms)
        
        conn.commit()
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

# Initialize the database when the app starts
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return render_template('signup.html', msg='Invalid email address!')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        account = cursor.fetchone()
        
        if account:
            conn.close()
            return render_template('signup.html', msg='Account already exists!')
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute('INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)', 
                      (username, hashed_password, email, role))
        conn.commit()
        conn.close()
        
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            conn.close()
            return render_template('login.html', msg='Incorrect username/password!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    role = session['role']
    user_id = session['id']
    
    if role == 'patient':
        return redirect(url_for('patient_dashboard'))
    elif role == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'nurse':
        return redirect(url_for('nurse_dashboard'))
    else:
        return redirect(url_for('staff_dashboard'))

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'loggedin' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))
    
    user_id = session['id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if patient profile exists
    cursor.execute('SELECT * FROM patients WHERE user_id = %s', (user_id,))
    patient = cursor.fetchone()
    
    # Get appointments
    if patient:
        cursor.execute('''
            SELECT a.*, d.first_name, d.last_name, d.specialization 
            FROM appointments a 
            JOIN doctors d ON a.doctor_id = d.id 
            WHERE a.patient_id = %s
        ''', (patient['id'],))
        appointments = cursor.fetchall()
        
        # Get medical records
        cursor.execute('''
            SELECT mr.*, d.first_name, d.last_name 
            FROM medical_records mr 
            JOIN doctors d ON mr.doctor_id = d.id 
            WHERE mr.patient_id = %s
        ''', (patient['id'],))
        medical_records = cursor.fetchall()
    else:
        appointments = []
        medical_records = []
    
    conn.close()
    
    return render_template('patient_dashboard.html', 
                          patient=patient, 
                          appointments=appointments, 
                          medical_records=medical_records,
                          username=session['username'])

@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'loggedin' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    user_id = session['id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get doctor's information
        cursor.execute('''
            SELECT d.*, u.username, u.email
            FROM doctors d
            JOIN users u ON d.user_id = u.id
            WHERE d.user_id = %s
        ''', (user_id,))
        doctor = cursor.fetchone()
        
        if not doctor:
            return redirect(url_for('add_doctor_profile'))
        
        # Get today's appointments with detailed patient information
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT a.*, 
                   p.first_name as patient_first_name, 
                   p.last_name as patient_last_name,
                   p.dob, p.gender, p.blood_group, p.phone,
                   p.emergency_contact, p.medical_history,
                   p.address
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.doctor_id = %s AND a.appointment_date = %s
            ORDER BY a.appointment_time
        ''', (doctor['id'], today))
        today_appointments = cursor.fetchall()
        
        # Calculate patient ages for today's appointments
        for appointment in today_appointments:
            if appointment['dob']:
                dob = datetime.strptime(str(appointment['dob']), '%Y-%m-%d')
                age = (datetime.now() - dob).days // 365
                appointment['patient_age'] = age
        
        # Get upcoming appointments for next 7 days with detailed patient information
        week_end = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT a.*, 
                   p.first_name as patient_first_name, 
                   p.last_name as patient_last_name,
                   p.dob, p.gender, p.blood_group, p.phone,
                   p.emergency_contact, p.medical_history,
                   p.address
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.doctor_id = %s 
            AND a.appointment_date > %s 
            AND a.appointment_date <= %s
            ORDER BY a.appointment_date, a.appointment_time
        ''', (doctor['id'], today, week_end))
        upcoming_appointments = cursor.fetchall()
        
        # Calculate patient ages for upcoming appointments
        for appointment in upcoming_appointments:
            if appointment['dob']:
                dob = datetime.strptime(str(appointment['dob']), '%Y-%m-%d')
                age = (datetime.now() - dob).days // 365
                appointment['patient_age'] = age
        
        # Get total patients count
        cursor.execute('''
            SELECT COUNT(DISTINCT patient_id) as total_patients
            FROM appointments
            WHERE doctor_id = %s
        ''', (doctor['id'],))
        total_patients = cursor.fetchone()['total_patients']
        
        # Get new patients this week
        week_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(DISTINCT patient_id) as new_patients
            FROM appointments
            WHERE doctor_id = %s AND appointment_date >= %s
        ''', (doctor['id'], week_start))
        new_patients_this_week = cursor.fetchone()['new_patients']
        
        # Get recent patients with their last visit
        cursor.execute('''
            SELECT p.*, 
                   TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) as age,
                   MAX(a.appointment_date) as last_visit
            FROM patients p
            JOIN appointments a ON p.id = a.patient_id
            WHERE a.doctor_id = %s
            GROUP BY p.id
            ORDER BY last_visit DESC
            LIMIT 5
        ''', (doctor['id'],))
        recent_patients = cursor.fetchall()
        
        # Get tasks (appointments that need attention)
        cursor.execute('''
            SELECT COUNT(*) as total_tasks,
                   SUM(CASE WHEN status = 'scheduled' AND appointment_date = %s THEN 1 ELSE 0 END) as urgent_tasks
            FROM appointments
            WHERE doctor_id = %s
        ''', (today, doctor['id']))
        tasks = cursor.fetchone()
        
        return render_template('doctor_dashboard.html', 
                             doctor=doctor,
                             today_appointments=today_appointments,
                             upcoming_appointments=upcoming_appointments,
                             total_patients=total_patients,
                             new_patients_this_week=new_patients_this_week,
                             recent_patients=recent_patients,
                             total_tasks=tasks['total_tasks'],
                             urgent_tasks=tasks['urgent_tasks'],
                             username=session['username'])
                             
    except Exception as e:
        print(f"Error in doctor dashboard: {str(e)}")
        return render_template('doctor_dashboard.html', 
                             error="An error occurred while loading the dashboard")
    finally:
        conn.close()

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'loggedin' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get counts
    cursor.execute('SELECT COUNT(*) as doctor_count FROM doctors')
    doctor_count = cursor.fetchone()['doctor_count']
    
    cursor.execute('SELECT COUNT(*) as patient_count FROM patients')
    patient_count = cursor.fetchone()['patient_count']
    
    cursor.execute('SELECT COUNT(*) as appointment_count FROM appointments')
    appointment_count = cursor.fetchone()['appointment_count']
    
    # Get recent users
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC LIMIT 5')
    recent_users = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                          doctor_count=doctor_count,
                          patient_count=patient_count,
                          appointment_count=appointment_count,
                          recent_users=recent_users,
                          username=session['username'])

@app.route('/nurse_dashboard')
def nurse_dashboard():
    if 'loggedin' not in session or session['role'] != 'nurse':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get today's appointments
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT a.*, p.first_name as patient_first_name, p.last_name as patient_last_name,
        d.first_name as doctor_first_name, d.last_name as doctor_last_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.appointment_date = %s
    ''', (today,))
    
    todays_appointments = cursor.fetchall()
    conn.close()
    
    return render_template('nurse_dashboard.html', 
                          appointments=todays_appointments,
                          username=session['username'])

@app.route('/staff_dashboard')
def staff_dashboard():
    if 'loggedin' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))
    
    return render_template('staff_dashboard.html', username=session['username'])

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        user_message = request.form.get('message')
        if not user_message:
            return jsonify({'response': 'Please provide a message.'})

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch all questions and answers from the database
        cursor.execute("SELECT question, answer FROM chatbot_questions")
        qa_pairs = cursor.fetchall()

        if not qa_pairs:
            # Store unanswered query
            user_id = session.get('id')
            cursor.execute('''
                INSERT INTO unanswered_queries (query, user_id)
                VALUES (%s, %s)
            ''', (user_message, user_id))
            conn.commit()
            conn.close()
            return jsonify({'response': "I'm sorry, I'm still learning. Please contact our staff for assistance."})

        # Convert questions to lowercase for case-insensitive matching
        questions = [qa['question'].lower() for qa in qa_pairs]
        
        # Find the best match
        matches = get_close_matches(user_message.lower(), questions, n=1, cutoff=0.6)
        
        if matches:
            # Find the corresponding answer
            for qa in qa_pairs:
                if qa['question'].lower() == matches[0]:
                    conn.close()
                    return jsonify({'response': qa['answer']})
        
        # If no match found, store the unanswered query
        user_id = session.get('id')
        cursor.execute('''
            INSERT INTO unanswered_queries (query, user_id)
            VALUES (%s, %s)
        ''', (user_message, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({'response': "I'm sorry, I don't have information on that topic. Please contact our staff for assistance."})

    except Exception as e:
        print(f"Error in chatbot: {str(e)}")
        return jsonify({'response': "I'm sorry, I encountered an error. Please try again later."})

@app.route('/add_patient_profile', methods=['GET', 'POST'])
def add_patient_profile():
    if 'loggedin' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get form data
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            dob = request.form['dob']
            gender = request.form['gender']
            blood_group = request.form['blood_group']
            address = request.form['address']
            phone = request.form['phone']
            emergency_contact = request.form['emergency_contact']
            medical_history = request.form['medical_history']
            
            # Insert patient profile
            cursor.execute('''
                INSERT INTO patients 
                (user_id, first_name, last_name, dob, gender, blood_group, address, phone, emergency_contact, medical_history)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (session['id'], first_name, last_name, dob, gender, blood_group, address, phone, emergency_contact, medical_history))
            
            conn.commit()
            conn.close()
            
            return redirect(url_for('book_appointment'))
            
        except Exception as e:
            print(f"Error adding patient profile: {str(e)}")
            return render_template('add_patient_profile.html', error="Failed to add profile. Please try again.")
    
    return render_template('add_patient_profile.html')

@app.route('/add_doctor_profile', methods=['GET', 'POST'])
def add_doctor_profile():
    if 'loggedin' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session['id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        specialization = request.form['specialization']
        qualification = request.form['qualification']
        experience = request.form['experience']
        phone = request.form['phone']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO doctors 
            (user_id, first_name, last_name, specialization, qualification, experience, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, first_name, last_name, specialization, qualification, experience, phone))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('add_doctor_profile.html')

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'loggedin' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get patient ID or create new patient
            cursor.execute('SELECT id FROM patients WHERE user_id = %s', (session['id'],))
            patient = cursor.fetchone()
            
            if not patient:
                # Create new patient profile
                cursor.execute('''
                    INSERT INTO patients 
                    (user_id, first_name, last_name, dob, gender, blood_group, address, phone, emergency_contact, medical_history)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    session['id'],
                    request.form['first_name'],
                    request.form['last_name'],
                    request.form['dob'],
                    request.form['gender'],
                    request.form['blood_group'],
                    request.form['address'],
                    request.form['phone'],
                    request.form['emergency_contact'],
                    request.form['medical_history']
                ))
                patient_id = cursor.lastrowid
            else:
                patient_id = patient['id']
            
            # Book appointment
            cursor.execute('''
                INSERT INTO appointments 
                (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
                VALUES (%s, %s, %s, %s, %s, 'scheduled')
            ''', (
                patient_id,
                request.form['doctor_id'],
                request.form['appointment_date'],
                request.form['appointment_time'],
                request.form['reason']
            ))
            
            conn.commit()
            conn.close()
            
            return redirect(url_for('patient_dashboard'))
            
        except Exception as e:
            print(f"Error booking appointment: {str(e)}")
            return render_template('book_appointment.html', 
                                error="Failed to book appointment. Please try again.",
                                doctors=get_doctors())
    
    # GET request - show booking form
    return render_template('book_appointment.html', doctors=get_doctors())

def get_doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, first_name, last_name, specialization FROM doctors')
    doctors = cursor.fetchall()
    conn.close()
    return doctors

@app.route('/view_appointment/<int:appointment_id>')
def view_appointment(appointment_id):
    if 'loggedin' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.*, 
                   p.first_name as patient_first_name, 
                   p.last_name as patient_last_name,
                   p.dob as date_of_birth, 
                   p.gender, 
                   p.blood_group, 
                   p.phone as patient_phone,
                   p.emergency_contact as patient_emergency_contact, 
                   p.medical_history as patient_medical_history,
                   p.address as patient_address,
                   TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) as patient_age
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.id = %s AND a.doctor_id = %s
        """, (appointment_id, session['id']))
        appointment = cursor.fetchone()
        
        if not appointment:
            flash('Appointment not found or unauthorized access.', 'danger')
            return redirect(url_for('doctor_dashboard'))
            
        return render_template('view_appointment.html', appointment=appointment)
    except Exception as e:
        flash('An error occurred while fetching appointment details.', 'danger')
        return redirect(url_for('doctor_dashboard'))
    finally:
        conn.close()

@app.route('/update_appointment_status/<int:appointment_id>', methods=['POST'])
def update_appointment_status(appointment_id):
    if 'user_id' not in session or session['role'] != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE appointments 
            SET status = %s, notes = %s 
            WHERE id = %s AND doctor_id = %s
        """, (status, notes, appointment_id, session['user_id']))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@app.route('/add_medical_record/<int:appointment_id>', methods=['GET', 'POST'])
def add_medical_record(appointment_id):
    if 'loggedin' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get appointment details
    cursor.execute('''
        SELECT a.*, p.id as patient_id, d.id as doctor_id
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.id = %s
    ''', (appointment_id,))
    
    appointment = cursor.fetchone()
    
    if not appointment:
        conn.close()
        return "Appointment not found", 404
    
    if request.method == 'POST':
        diagnosis = request.form['diagnosis']
        prescription = request.form['prescription']
        notes = request.form['notes']
        
        cursor.execute('''
            INSERT INTO medical_records
            (patient_id, doctor_id, diagnosis, prescription, notes)
            VALUES (%s, %s, %s, %s, %s)
        ''', (appointment['patient_id'], appointment['doctor_id'], diagnosis, prescription, notes))
        
        # Update appointment status
        cursor.execute('UPDATE appointments SET status = %s WHERE id = %s', 
                      ('completed', appointment_id))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('doctor_dashboard'))
    
    conn.close()
    
    return render_template('add_medical_record.html', appointment=appointment)

@app.route('/appointment_details')
def appointment_details():
    return render_template('appointment_details.html')

@app.route('/prescription_details')
def prescription_details():
    return render_template('prescription_details.html')

@app.route('/medical_record_details')
def medical_record_details():
    return render_template('medical_record_details.html')

@app.route('/verify_chatbot_data')
def verify_chatbot_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'chatbot_questions'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            return "chatbot_questions table does not exist"
        
        # Check table structure
        cursor.execute("DESCRIBE chatbot_questions")
        structure = cursor.fetchall()
        
        # Check for data
        cursor.execute("SELECT COUNT(*) as count FROM chatbot_questions")
        count = cursor.fetchone()['count']
        
        # Get sample data
        cursor.execute("SELECT * FROM chatbot_questions LIMIT 5")
        sample_data = cursor.fetchall()
        
        return jsonify({
            "table_exists": True,
            "structure": structure,
            "count": count,
            "sample_data": sample_data
        })
        
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        conn.close()

@app.route('/view_upcoming_appointment/<int:appointment_id>')
def view_upcoming_appointment(appointment_id):
    if 'loggedin' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # First get the doctor's ID
        cursor.execute('SELECT id FROM doctors WHERE user_id = %s', (session['id'],))
        doctor = cursor.fetchone()
        
        if not doctor:
            flash('Doctor profile not found.', 'danger')
            return redirect(url_for('doctor_dashboard'))
            
        cursor.execute("""
            SELECT a.*, 
                   p.first_name as patient_first_name, 
                   p.last_name as patient_last_name,
                   p.dob as date_of_birth, 
                   p.gender, 
                   p.blood_group, 
                   p.phone as patient_phone,
                   p.emergency_contact as patient_emergency_contact, 
                   p.medical_history as patient_medical_history,
                   p.address as patient_address,
                   TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) as patient_age,
                   r.room_number,
                   r.room_type
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            LEFT JOIN rooms r ON a.room_id = r.id
            WHERE a.id = %s AND a.doctor_id = %s
        """, (appointment_id, doctor['id']))
        appointment = cursor.fetchone()
        
        if not appointment:
            flash('Appointment not found or unauthorized access.', 'danger')
            return redirect(url_for('doctor_dashboard'))
            
        return render_template('view_upcoming_appointment.html', appointment=appointment)
    except Exception as e:
        flash('An error occurred while fetching appointment details.', 'danger')
        return redirect(url_for('doctor_dashboard'))
    finally:
        conn.close()

@app.route('/allocate_room/<int:appointment_id>', methods=['GET', 'POST'])
def allocate_room(appointment_id):
    if 'loggedin' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get appointment details
        cursor.execute("""
            SELECT a.*, p.first_name as patient_first_name, p.last_name as patient_last_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.id = %s
        """, (appointment_id,))
        appointment = cursor.fetchone()
        
        if not appointment:
            flash('Appointment not found.', 'danger')
            return redirect(url_for('doctor_dashboard'))
        
        if request.method == 'POST':
            room_id = request.form.get('room_id')
            
            # Update appointment with room
            cursor.execute("""
                UPDATE appointments 
                SET room_id = %s 
                WHERE id = %s
            """, (room_id, appointment_id))
            
            # Update room status
            cursor.execute("""
                UPDATE rooms 
                SET status = 'occupied' 
                WHERE id = %s
            """, (room_id,))
            
            conn.commit()
            flash('Room allocated successfully!', 'success')
            return redirect(url_for('view_upcoming_appointment', appointment_id=appointment_id))
        
        # Get available rooms
        cursor.execute("""
            SELECT * FROM rooms 
            WHERE status = 'available' 
            ORDER BY room_number
        """)
        available_rooms = cursor.fetchall()
        
        return render_template('allocate_room.html', 
                             appointment=appointment,
                             available_rooms=available_rooms)
                             
    except Exception as e:
        print(f"Error in allocate_room: {str(e)}")
        flash('An error occurred while allocating the room.', 'danger')
        return redirect(url_for('doctor_dashboard'))
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
