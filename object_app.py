import os
import sqlite3
import json
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'object_secret_key_2026'  # ضروري لحفظ اللغة

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# قاموس الترجمة (عربي / إنجليزي)
TRANSLATIONS = {
    'ar': {
        'home': 'الرئيسية',
        'browse': 'سوق العقارات',
        'account': 'حسابي',
        'about': 'معلومات عنا',
        'contact': 'تواصل معنا',
        'add': 'أضف عقار',
        'login': 'تسجيل الدخول',
        'logout': 'تسجيل الخروج',
        'lang_switch': 'English',
        'hero_title': 'مستقبل العقار بين يديك',
        'hero_desc': 'منصة OBJECT تقدم لك تجربة فريدة لاكتشاف أرقى العقارات في الرياض.',
        'explore_btn': 'اكتشف السوق الآن',
        'features_title': 'لماذا تختار OBJECT؟',
        'feat1': 'مواقع دقيقة',
        'feat2': 'سرعة وتفاعلية',
        'feat3': 'موثوقية وأمان',
        'footer_copy': '© 2026 OBJECT العقارية',
        'dir': 'rtl',
        'align': 'right'
    },
    'en': {
        'home': 'Home',
        'browse': 'Properties Market',
        'account': 'My Account',
        'about': 'About Us',
        'contact': 'Contact Us',
        'add': 'Add Property',
        'login': 'Login',
        'logout': 'Logout',
        'lang_switch': 'العربية',
        'hero_title': 'Real Estate Future is Here',
        'hero_desc': 'OBJECT platform offers a unique experience to discover the finest properties in Riyadh.',
        'explore_btn': 'Explore Market',
        'features_title': 'Why Choose OBJECT?',
        'feat1': 'Precise Locations',
        'feat2': 'Fast & Interactive',
        'feat3': 'Trust & Security',
        'footer_copy': '© 2026 OBJECT Real Estate',
        'dir': 'ltr',
        'align': 'left'
    }
}

# دالة لتمرير الترجمة لكل الصفحات تلقائياً
@app.context_processor
def inject_conf():
    lang = session.get('lang', 'ar')
    return dict(t=TRANSLATIONS[lang], lang=lang)

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

# --- الروابط الأساسية ---

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

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['ar', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('browse'))
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/add', methods=['GET', 'POST'])
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
            from werkzeug.utils import secure_filename
            image_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        conn = get_db_connection()
        conn.execute('INSERT INTO properties (title, price, location, latitude, longitude, image_path) VALUES (?, ?, ?, ?, ?, ?)',
                     (title, price, location, lat, lng, image_filename))
        conn.commit()
        conn.close()
        return redirect(url_for('browse'))
    return render_template('add_property.html')

# روابط إضافية للقائمة الجانبية (لمنع خطأ 404)
@app.route('/about')
def about(): return render_template('object_home.html') # مؤقتاً نفس الرئيسية

@app.route('/contact')
def contact(): return render_template('object_home.html') # مؤقتاً نفس الرئيسية

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)