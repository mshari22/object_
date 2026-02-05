import os
import sqlite3
import json
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey' # ضروري لعمل التنبيهات

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

@app.route('/')
def home():
    return render_template('object_home.html')

@app.route('/browse')
def browse():
    init_db()
    conn = get_db_connection()
    db_properties = conn.execute('SELECT * FROM properties').fetchall()
    conn.close()
    return render_template('browse.html', properties=db_properties)

# تحديث صفحة الدخول لتعمل فعلياً
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # هنا نأخذ البيانات من الفورم
        username = request.form.get('username')
        password = request.form.get('password')
        
        # مؤقتاً: أي دخول سينقلك لصفحة العقارات
        # يمكنك لاحقاً التحقق من قاعدة البيانات
        if username and password:
            return redirect(url_for('browse'))
            
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)