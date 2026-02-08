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

# قاموس الترجمة - 7 Languages
TRANSLATIONS = {
    'ar': {
        'title': 'OBJECT', 'dir': 'rtl', 'align': 'right', 'font': 'Tajawal',
        'home': 'الرئيسية', 'browse': 'سوق العقارات', 'request': 'اطلب عقارك', 
        'dashboard': 'لوحة التحكم', 'login': 'دخول', 'logout': 'خروج', 'signup': 'تسجيل',
        'profile': 'ملفي الشخصي', 'contact_us': 'اتصل بنا', 'about_us': 'من نحن',
        'hero_title': 'مستقبل العقار', 'hero_subtitle': 'في الرياض',
        'hero_desc': 'اكتشف منزلك الجديد باستخدام أذكى تقنيات البحث العقاري.',
        'browse_now': 'تصفح السوق الآن', 'request_property': 'اطلب عقارك',
        'why_object': 'لماذا OBJECT؟', 'why_desc': 'نقدم تجربة عقارية لا مثيل لها',

        'maps': 'خرائط تفاعلية', 'maps_desc': 'شاهد موقع العقار بدقة على الخريطة',
        'calculator': 'حاسبة التمويل', 'calculator_desc': 'احسب القسط الشهري بناءً على راتبك',
        'properties': 'عقار متاح', 'districts': 'حي في الرياض', 'clients': 'عميل سعيد',
        'search': 'بحث', 'district': 'الحي', 'location': 'الموقع', 'property_type': 'نوع العقار', 'max_price': 'الحد الأقصى للسعر',
        'all_types': 'جميع الأنواع', 'villa': 'فيلا', 'apartment': 'شقة', 'land': 'أرض',
        'rooms': 'غرف', 'area': 'م²', 'views': 'مشاهدات', 'sar': 'ريال',
        'contact_owner': 'تواصل مع المالك', 'whatsapp': 'واتساب', 'book_visit': 'احجز زيارة',
        'finance_calc': 'حاسبة التمويل', 'salary': 'الراتب الشهري', 'downpayment': 'الدفعة الأولى',
        'calculate': 'احسب القسط', 'property_details': 'تفاصيل العقار',
        'add_property': 'إضافة عقار جديد', 'client_requests': 'طلبات الباحثين عن عقار',
        'publish': 'نشر العقار', 'name': 'الاسم', 'phone': 'رقم الجوال', 'notes': 'ملاحظات',
        'send_request': 'إرسال الطلب', 'not_found': 'ما لقيت اللي في بالك؟',
        'lang_name': 'العربية', 'bathrooms': 'حمام', 'age': 'عمر العقار',
        'email': 'البريد الإلكتروني', 'password': 'كلمة المرور', 'min_price': 'الحد الأدنى للسعر',
        'latitude': 'خط العرض', 'longitude': 'خط الطول',
        'footer_desc': 'مستقبل العقار في الرياض',
        
        # Add Property Page
        'add_property_title': 'إضافة عقار جديد',
        'property_name': 'اسم العقار',
        'property_name_placeholder': 'مثلاً: فيلا مودرن حطين',
        'price': 'السعر',
        'enter_amount': 'أدخل المبلغ',
        'location_placeholder': 'مثلاً: الملقا، الرياض',
        'property_image': 'صورة العقار',
        'publish_now': 'نشر العقار الآن',
        'cancel_return': 'إلغاء والعودة للسوق',
        'select_location_map': 'حدد الموقع على الخريطة',

        # Profile & Auth
        'my_properties': 'عقاراتي',
        'no_properties': 'لم تقم بإضافة عقارات بعد',
        'edit': 'تعديل', 'delete': 'حذف', 'save_changes': 'حفظ التغييرات',
        'welcome': 'مرحباً', 'join_date': 'تاريخ الانضمام',
        'login_title': 'تسجيل الدخول', 'signup_title': 'إنشاء حساب جديد',
        'have_account': 'لديك حساب؟', 'no_account': 'ليس لديك حساب؟',

        # Contact & About
        'contact_title': 'تواصل معنا',
        'message': 'الرسالة', 'send_message': 'إرسال الرسالة',
        'about_title': 'من نحن',
        'about_content': 'نحن منصة عقارية رائدة تهدف إلى تسهيل عملية بيع وشراء العقارات في الرياض باستخدام أحدث التقنيات.',
        'our_vision': 'رؤيتنا', 'vision_content': 'أن نكون الخيار الأول للبحث عن العقارات في المملكة.',
        'our_mission': 'رسالتنا', 'mission_content': 'تقديم تجربة مستخدم استثنائية وموثوقة.',
    },
    'en': {
        'title': 'OBJECT', 'dir': 'ltr', 'align': 'left', 'font': 'Inter',
        'home': 'Home', 'browse': 'Marketplace', 'request': 'Request', 
        'dashboard': 'Dashboard', 'login': 'Login', 'logout': 'Logout', 'signup': 'Sign Up',
        'profile': 'My Profile', 'contact_us': 'Contact Us', 'about_us': 'About Us',
        'hero_title': 'Future of Real Estate', 'hero_subtitle': 'in Riyadh',
        'hero_desc': 'Discover your new home using the smartest real estate search technology.',
        'browse_now': 'Browse Now', 'request_property': 'Request Property',
        'why_object': 'Why OBJECT?', 'why_desc': 'We offer an unparalleled real estate experience',

        'maps': 'Interactive Maps', 'maps_desc': 'View property location precisely on the map',
        'calculator': 'Finance Calculator', 'calculator_desc': 'Calculate monthly payment based on your salary',
        'properties': 'Available Properties', 'districts': 'Districts in Riyadh', 'clients': 'Happy Clients',
        'search': 'Search', 'district': 'District', 'location': 'Location', 'property_type': 'Property Type', 'max_price': 'Max Price',
        'all_types': 'All Types', 'villa': 'Villa', 'apartment': 'Apartment', 'land': 'Land',
        'rooms': 'Rooms', 'area': 'm²', 'views': 'Views', 'sar': 'SAR',
        'contact_owner': 'Contact Owner', 'whatsapp': 'WhatsApp', 'book_visit': 'Book Visit',
        'finance_calc': 'Finance Calculator', 'salary': 'Monthly Salary', 'downpayment': 'Down Payment',
        'calculate': 'Calculate', 'property_details': 'Property Details',
        'add_property': 'Add New Property', 'client_requests': 'Client Requests',
        'publish': 'Publish Property', 'name': 'Name', 'phone': 'Phone', 'notes': 'Notes',
        'send_request': 'Send Request', 'not_found': "Didn't find what you're looking for?",
        'lang_name': 'English', 'bathrooms': 'Bathrooms', 'age': 'Property Age',
        'email': 'Email', 'password': 'Password', 'min_price': 'Min Price',
        'latitude': 'Latitude', 'longitude': 'Longitude',
        'footer_desc': 'The Future of Real Estate in Riyadh',

        # Add Property Page
        'add_property_title': 'Add New Property',
        'property_name': 'Property Name',
        'property_name_placeholder': 'e.g. Modern Villa Hiteen',
        'price': 'Price',
        'enter_amount': 'Enter Amount',
        'location_placeholder': 'e.g. Al Malqa, Riyadh',
        'property_image': 'Property Image',
        'publish_now': 'Publish Property Now',
        'cancel_return': 'Cancel and Return',
        'select_location_map': 'Select Location on Map',

        # Profile & Auth
        'my_properties': 'My Properties',
        'no_properties': 'No properties listed yet',
        'edit': 'Edit', 'delete': 'Delete', 'save_changes': 'Save Changes',
        'welcome': 'Welcome', 'join_date': 'Join Date',
        'login_title': 'Login', 'signup_title': 'Sign Up',
        'have_account': 'Have an account?', 'no_account': "Don't have an account?",

        # Contact & About
        'contact_title': 'Contact Us',
        'message': 'Message', 'send_message': 'Send Message',
        'about_title': 'Who Are We',
        'about_content': 'We are a leading real estate platform aiming to facilitate the process of buying and selling real estate in Riyadh using the latest technologies.',
        'our_vision': 'Our Vision', 'vision_content': 'To be the first choice for real estate search in the Kingdom.',
        'our_mission': 'Our Mission', 'mission_content': 'providing an exceptional and reliable user experience.',
    }
}

# List of all languages for the selector
LANGUAGES = [
    {'code': 'ar', 'name': 'العربية', 'flag': '🇸🇦'},
    {'code': 'en', 'name': 'English', 'flag': '🇺🇸'}
]

@app.context_processor
def inject_conf():
    lang = session.get('lang', 'ar')
    if lang not in TRANSLATIONS:
        lang = 'ar'
    return dict(t=TRANSLATIONS[lang], lang=lang, languages=LANGUAGES)

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

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/set_lang/<lang>')
def set_lang(lang):
    session['lang'] = lang
    return redirect(request.referrer or url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE name = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db()
            conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                         (name, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists')
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    # In a real app, we would fetch properties belonging to this user
    # For now, we'll just fetch all properties to demonstrate the list, 
    # or if we had owner_id in properties table we would use that:
    # my_props = conn.execute('SELECT * FROM properties WHERE owner_id = ?', (session['user_id'],)).fetchall()
    
    # Using existing owner_id column from init_db schema
    my_props = conn.execute('SELECT * FROM properties WHERE owner_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('profile.html', properties=my_props)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)   # test update