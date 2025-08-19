from flask import Flask, request, redirect, url_for, render_template, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize database with vulnerable tables
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Create users table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  password TEXT)''')
    
    # Insert some db.sqlite3 users if they don't exist
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                 ('admin', 'admin123'))
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                 ('user1', 'password1'))
    except sqlite3.IntegrityError:
        pass  # Users already exist
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def list_view():
    return render_template('listview.html')

def sanitize_username(username):
    if '--' in username:
        return username.split('--')[0].strip()
    return username

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # This is the vulnerable query - susceptible to SQL injection
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        c.execute(query)
        
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user'] = sanitize_username(username)
            return redirect(url_for('list_view'))
        else:
            return render_template('accounts/login.html', 
                                message="Invalid credentials!",
                                success=False)
    
    return render_template('accounts/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Vulnerable SQL query - susceptible to SQL injection
        try:
            c.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
            conn.commit()
            conn.close()
            session['user'] = username
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('accounts/login.html', 
                                message="Username already exists!",
                                success=False)
    
    return render_template('accounts/login.html', register=True)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)