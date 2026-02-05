import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'object_super_secret_key_2026' # للأمان والجلسات

# إعدادات رفع الصور
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# قاموس الترجمة
TRANSLATIONS = {
    'ar': {'title': 'OBJECT', 'dir': 'rtl', 'align': 'right', 'home': 'الرئيسية', 'browse': 'سوق العقارات', 'request': 'اطلب عقارك', 'dashboard': 'لوحة التحكم', 'login': 'دخول', 'logout': 'خروج'},
    'en': {'title': 'OBJECT', 'dir': 'ltr', 'align': 'left', 'home': 'Home', 'browse': 'Marketplace', 'request': 'Request Property', 'dashboard': 'Dashboard', 'login': 'Login', 'logout': 'Logout'}
}

@app.context_processor
def inject_conf():
    lang = session.get('lang', 'ar')
    return dict(t=TRANSLATIONS[lang], lang=lang)

def get_db():
    conn = sqlite3.connect('object_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        # جدول المستخدمين
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )''')
        # جدول العقارات المطور (كل المواصفات)
        conn.execute('''CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            location TEXT,
            district TEXT,
            type TEXT,
            area REAL,
            rooms INTEGER,
            bathrooms INTEGER,
            age INTEGER,
            furnished TEXT,
            description TEXT,
            latitude REAL,
            longitude REAL,
            image_path TEXT,
            views INTEGER DEFAULT 0,
            owner_id INTEGER
        )''')
        # جدول طلبات العقارات
        conn.execute('''CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            phone TEXT,
            budget_min REAL,
            budget_max REAL,
            district TEXT,
            type TEXT,
            notes TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

# --- الروابط (Routes) ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/browse')
def browse():
    init_db()
    conn = get_db()
    
    # منطق البحث المتقدم
    query = "SELECT * FROM properties WHERE 1=1"
    params = []
    
    if request.args.get('district'):
        query += " AND district LIKE ?"
        params.append(f"%{request.args.get('district')}%")
    if request.args.get('type'):
        query += " AND type = ?"
        params.append(request.args.get('type'))
    if request.args.get('price_max'):
        query += " AND price <= ?"
        params.append(request.args.get('price_max'))
        
    properties = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('browse.html', properties=properties)

@app.route('/property/<int:id>')
def property_details(id):
    conn = get_db()
    # زيادة المشاهدات
    conn.execute('UPDATE properties SET views = views + 1 WHERE id = ?', (id,))
    conn.commit()
    prop = conn.execute('SELECT * FROM properties WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('details.html', p=prop)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # التحقق من الدخول (محاكاة)
    # if 'user_id' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        file = request.files['image']
        filename = secure_filename(file.filename) if file else None
        if filename: file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        conn = get_db()
        conn.execute('''INSERT INTO properties (title, price, location, district, type, area, rooms, bathrooms, age, furnished, description, latitude, longitude, image_path, owner_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (request.form['title'], request.form['price'], request.form['location'], request.form['district'],
                      request.form['type'], request.form['area'], request.form['rooms'], request.form['bathrooms'],
                      request.form['age'], request.form.get('furnished', 'no'), request.form['description'],
                      request.form['lat'], request.form['lng'], filename, 1)) # 1 هو رقم المالك الافتراضي
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
        
    conn = get_db()
    my_props = conn.execute('SELECT * FROM properties').fetchall()
    requests = conn.execute('SELECT * FROM requests ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('dashboard.html', properties=my_props, requests=requests)

@app.route('/request_property', methods=['GET', 'POST'])
def request_property():
    if request.method == 'POST':
        conn = get_db()
        conn.execute('INSERT INTO requests (user_name, phone, budget_min, budget_max, district, type, notes) VALUES (?,?,?,?,?,?,?)',
                     (request.form['name'], request.form['phone'], request.form['min'], request.form['max'], request.form['district'], request.form['type'], request.form['notes']))
        conn.commit()
        conn.close()
        return redirect(url_for('home')) # أو صفحة نجاح
    return render_template('request.html')

@app.route('/set_lang/<lang>')
def set_lang(lang):
    session['lang'] = lang
    return redirect(request.referrer or url_for('home'))

@app.route('/login')
def login(): return render_template('login.html')

@app.route('/signup')
def signup(): return render_template('signup.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)