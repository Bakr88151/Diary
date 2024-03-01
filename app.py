from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Function to create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('diary.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to initialize the database
def initialize_database():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY, date TEXT, content TEXT)')
    conn.commit()
    conn.close()

# Initialize the database when the app starts
initialize_database()

# Route to display diary entries
@app.route('/')
def show_entries():
    conn = get_db_connection()
    entries = conn.execute('SELECT id, content, strftime("%d/%m/%Y", date) AS formatted_date FROM entries ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('show_entries.html', entries=entries)

# Route to display a single entry
@app.route('/entry/<int:entry_id>')
def show_entry(entry_id):
    conn = get_db_connection()
    entry = conn.execute('SELECT *, strftime("%d/%m/%Y", date) AS formatted_date FROM entries WHERE id = ?', (entry_id,)).fetchone()
    conn.close()

    # Calculate if it's the same day
    same_day = False
    if entry:
        entry_date = datetime.strptime(entry['date'], '%Y-%m-%d').date()
        today_date = datetime.now().date()
        same_day = entry_date == today_date

    return render_template('show_entry.html', entry=entry, same_day=same_day)

# Route to add a new entry
@app.route('/add', methods=['POST'])
def add_entry():
    date = datetime.now().strftime('%Y-%m-%d')
    content = request.form['content']
    
    # Check if an entry already exists for today
    conn = get_db_connection()
    existing_entry = conn.execute('SELECT * FROM entries WHERE date = ?', (date,)).fetchone()
    
    if existing_entry:
        return "You have already added an entry for today."
    
    conn.execute('INSERT INTO entries (date, content) VALUES (?, ?)', (date, content))
    conn.commit()
    conn.close()
    return redirect(url_for('show_entries'))

# Route to update an entry
@app.route('/update/<int:entry_id>', methods=['POST'])
def update_entry(entry_id):
    content = request.form['content']
    
    conn = get_db_connection()
    conn.execute('UPDATE entries SET content = ? WHERE id = ?', (content, entry_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('show_entry', entry_id=entry_id))

if __name__ == '__main__':
    app.run(debug=True)
