from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists('uploads'):
    os.makedirs('uploads')

# SQLite DB setup
def init_db():
    conn = sqlite3.connect('qms.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            owner TEXT,
            revision TEXT,
            upload_date TEXT,
            filename TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect('qms.db')
    c = conn.cursor()
    c.execute("SELECT * FROM documents")
    docs = c.fetchall()
    conn.close()
    return render_template('dashboard.html', documents=docs)

@app.route('/upload', methods=['POST'])
def upload():
    title = request.form['title']
    owner = request.form['owner']
    revision = request.form['revision']
    file = request.files['file']

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        conn = sqlite3.connect('qms.db')
        c = conn.cursor()
        c.execute("INSERT INTO documents (title, owner, revision, upload_date, filename) VALUES (?, ?, ?, DATE('now'), ?)",
                  (title, owner, revision, filename))
        conn.commit()
        conn.close()
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
