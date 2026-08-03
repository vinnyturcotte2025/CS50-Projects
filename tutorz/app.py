from flask import Flask, render_template, redirect, url_for, request, flash, session
import sqlite3
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

DATABASE = 'users.db'
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Create users table if it does not exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')

    conn.commit()
    conn.close()

init_db()
def get_user_by_id(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    data = cursor.fetchone()
    conn.close()
    if data:
        return {'id': data[0], 'username': data[1], 'email': data[2], 'password': data[3]}
    return None

def get_user_by_email(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    data = cursor.fetchone()
    conn.close()
    if data:
        return {'id': data[0], 'username': data[1], 'email': data[2], 'password': data[3]}
    return None

def create_user(username, email, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return {'id': user_id, 'username': username, 'email': email, 'password': password}

@app.route('/')
def index():
    current_year = datetime.now().year
    return render_template('index.html', current_year=current_year)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')


# Route for contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Send email
        try:
            send_email(name, email, message)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred while sending your message: {e}', 'danger')

    return render_template('contact.html')


def send_email(name, email, message):
    from_email = 'turcottevinny@gmail.com'
    from_password = 'Butthead1!'  # Use app-specific password if 2-step verification is enabled
    to_email = 'turcottevinny@gmail.com'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'New Contact Form Submission'

    body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

@app.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Retrieve the user from the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):  # Assuming password is the third field
            # Login the user (you can set the user session here)
            return redirect(url_for('profile'))  # Redirect to the profile page

    return render_template('login.html')
# Route for signup page

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get the form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Hash the password with the correct method
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Save the user to the database (you need to have a `users` table)
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('signup.html')
# Route for EULA page
@app.route('/eula')
def eula():
    return render_template('eula.html')

@app.route('/plans')
def payment_plans():
    # Define your payment plans data (you can fetch this from a database or define it here)
    payment_plans = [
        {
            'title': 'Basic Plan',
            'description': 'Includes 5 hours of tutoring per month.',
            'price': '$50/month'
        },
        {
            'title': 'Standard Plan',
            'description': 'Includes 10 hours of tutoring per month.',
            'price': '$80/month'
        },
        {
            'title': 'Premium Plan',
            'description': 'Includes unlimited tutoring sessions per month.',
            'price': '$150/month'
        }
    ]
    return render_template('payment_plans.html', payment_plans=payment_plans)


# Route for profile page
@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        return redirect(url_for('login'))  # Redirect to login if user is not found or not logged in

    user = users.get(user_id)
    return render_template('profile.html', name=user['username'])

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    from database_setup import init_db
    init_db()
    app.run(debug=True)
