import os
import sqlite3
import json
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect('object_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                location TEXT,
                latitude REAL,
                longitude REAL,
                image_path TEXT
            )
        ''')

# الصفحة الرئيسية (التعريفية فقط)
@app.route('/')
def home():
    return render_template('object_home.html')

# صفحة السوق (عرض العقارات)
@app.route('/browse')
def browse():
    init_db()
    conn = get_db_connection()
    db_properties = conn.execute('SELECT * FROM properties').fetchall()
    conn.close()
    return render_template('browse.html', properties=db_properties)

@app.route('/add', methods=('GET', 'POST'))
def add_property():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        location = request.form['location']
        lat = request.form['lat']
        lng = request.form['lng']
        file = request.files['image']
        
        image_filename = None
        if file:
            image_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        conn = get_db_connection()
        conn.execute('INSERT INTO properties (title, price, location, latitude, longitude, image_path) VALUES (?, ?, ?, ?, ?, ?)',
                     (title, price, location, lat, lng, image_filename))
        conn.commit()
        conn.close()
        return redirect(url_for('browse')) # التوجيه لصفحة التصفح بعد الإضافة
    return render_template('add_property.html')

@app.route('/login')
def login(): return render_template('login.html')

@app.route('/signup')
def signup(): return render_template('signup.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)