import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'object_super_secret_key_2026')

# Database Configuration - Read from environment variable
database_url = os.environ.get('DATABASE_URL', 'sqlite:///object_database.db')
# Fix for Heroku/Render postgres:// vs postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Upload folder configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- SQLAlchemy Models ---

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    properties = db.relationship('Property', backref='owner', lazy=True)

class Property(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200))
    district = db.Column(db.String(100))
    type = db.Column(db.String(50))
    area = db.Column(db.Float)
    rooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    age = db.Column(db.Integer)
    furnished = db.Column(db.String(10))
    description = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    image_path = db.Column(db.String(256))
    views = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    budget_min = db.Column(db.Float)
    budget_max = db.Column(db.Float)
    district = db.Column(db.String(100))
    type = db.Column(db.String(50))
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# --- Pricing Model ---

# District base prices per square meter (SAR)
DISTRICT_PRICES = {
    'malqa': 5500, 'ملقا': 5500, 'al malqa': 5500,
    'hiteen': 6500, 'حطين': 6500, 'al hiteen': 6500,
    'narjis': 4200, 'نرجس': 4200, 'al narjis': 4200,
    'olaya': 4800, 'عليا': 4800, 'al olaya': 4800,
    'yasmin': 4000, 'ياسمين': 4000, 'al yasmin': 4000,
    'riyadh': 3500, 'رياض': 3500,
}

def estimate_property_price(district, area, rooms=0, bathrooms=0, age=0, furnished='no'):
    """
    Smart pricing model using heuristic algorithm.
    Returns: (estimated_price, low_range, high_range)
    """
    # Normalize district name
    district_key = district.lower().strip() if district else 'riyadh'
    base_price_per_sqm = DISTRICT_PRICES.get(district_key, 3500)
    
    # Base calculation
    base_value = area * base_price_per_sqm
    
    # Apply multipliers
    multiplier = 1.0
    multiplier += (rooms * 0.02)  # +2% per room
    multiplier += (bathrooms * 0.015)  # +1.5% per bathroom
    multiplier += (0.15 if furnished == 'yes' else 0)  # +15% if furnished
    multiplier -= (age * 0.005)  # -0.5% per year (depreciation)
    
    estimated_price = base_value * multiplier
    
    # Calculate range (±10%)
    low_range = estimated_price * 0.9
    high_range = estimated_price * 1.1
    
    return round(estimated_price), round(low_range), round(high_range)

# --- Translations ---
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
        'my_properties': 'عقاراتي',
        'no_properties': 'لم تقم بإضافة عقارات بعد',
        'edit': 'تعديل', 'delete': 'حذف', 'save_changes': 'حفظ التغييرات',
        'welcome': 'مرحباً', 'join_date': 'تاريخ الانضمام',
        'login_title': 'تسجيل الدخول', 'signup_title': 'إنشاء حساب جديد',
        'have_account': 'لديك حساب؟', 'no_account': 'ليس لديك حساب؟',
        'contact_title': 'تواصل معنا',
        'message': 'الرسالة', 'send_message': 'إرسال الرسالة',
        'about_title': 'من نحن',
        'about_content': 'نحن منصة عقارية رائدة تهدف إلى تسهيل عملية بيع وشراء العقارات في الرياض باستخدام أحدث التقنيات.',
        'our_vision': 'رؤيتنا', 'vision_content': 'أن نكون الخيار الأول للبحث عن العقارات في المملكة.',
        'our_mission': 'رسالتنا', 'mission_content': 'تقديم تجربة مستخدم استثنائية وموثوقة.',
        
        # Pricing Model
        'get_estimate': '✨ احسب السعر الذكي',
        'estimating': 'جاري الحساب...',
        'estimated_price': 'السعر المقدر',
        'price_range': 'النطاق السعري',
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
        'my_properties': 'My Properties',
        'no_properties': 'No properties listed yet',
        'edit': 'Edit', 'delete': 'Delete', 'save_changes': 'Save Changes',
        'welcome': 'Welcome', 'join_date': 'Join Date',
        'login_title': 'Login', 'signup_title': 'Sign Up',
        'have_account': 'Have an account?', 'no_account': "Don't have an account?",
        'contact_title': 'Contact Us',
        'message': 'Message', 'send_message': 'Send Message',
        'about_title': 'Who Are We',
        'about_content': 'We are a leading real estate platform aiming to facilitate the process of buying and selling real estate in Riyadh using the latest technologies.',
        'our_vision': 'Our Vision', 'vision_content': 'To be the first choice for real estate search in the Kingdom.',
        'our_mission': 'Our Mission', 'mission_content': 'providing an exceptional and reliable user experience.',
        
        # Pricing Model
        'get_estimate': '✨ Get Smart Estimate',
        'estimating': 'Estimating...',
        'estimated_price': 'Estimated Price',
        'price_range': 'Price Range',
    }
}

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

# --- Routes ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/browse')
def browse():
    query = Property.query
    
    if request.args.get('district'):
        query = query.filter(Property.district.ilike(f"%{request.args.get('district')}%"))
    if request.args.get('type'):
        query = query.filter(Property.type == request.args.get('type'))
    if request.args.get('price_max'):
        query = query.filter(Property.price <= float(request.args.get('price_max')))
    
    properties = query.all()
    return render_template('browse.html', properties=properties)

@app.route('/property/<int:id>')
def property_details(id):
    prop = Property.query.get_or_404(id)
    prop.views = (prop.views or 0) + 1
    db.session.commit()
    return render_template('details.html', p=prop)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        file = request.files.get('image')
        filename = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        new_property = Property(
            title=request.form['title'],
            price=float(request.form['price']),
            location=request.form.get('location'),
            district=request.form.get('district'),
            type=request.form.get('type'),
            area=float(request.form.get('area', 0) or 0),
            rooms=int(request.form.get('rooms', 0) or 0),
            bathrooms=int(request.form.get('bathrooms', 0) or 0),
            age=int(request.form.get('age', 0) or 0),
            furnished=request.form.get('furnished', 'no'),
            description=request.form.get('description'),
            latitude=float(request.form.get('lat', 0) or 0),
            longitude=float(request.form.get('lng', 0) or 0),
            image_path=filename,
            owner_id=session.get('user_id', 1)
        )
        db.session.add(new_property)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    properties = Property.query.all()
    requests_list = Request.query.order_by(Request.date.desc()).all()
    return render_template('dashboard.html', properties=properties, requests=requests_list)

@app.route('/request_property', methods=['GET', 'POST'])
def request_property():
    if request.method == 'POST':
        new_request = Request(
            user_name=request.form['name'],
            phone=request.form['phone'],
            budget_min=float(request.form.get('min', 0) or 0),
            budget_max=float(request.form.get('max', 0) or 0),
            district=request.form.get('district'),
            type=request.form.get('type'),
            notes=request.form.get('notes')
        )
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('request.html')

@app.route('/api/estimate_price', methods=['POST'])
def api_estimate_price():
    """API endpoint for property price estimation"""
    data = request.get_json()
    
    try:
        district = data.get('district', 'Riyadh')
        area = float(data.get('area', 0))
        rooms = int(data.get('rooms', 0))
        bathrooms = int(data.get('bathrooms', 0))
        age = int(data.get('age', 0))
        furnished = data.get('furnished', 'no')
        
        estimated, low, high = estimate_property_price(
            district, area, rooms, bathrooms, age, furnished
        )
        
        return {
            'success': True,
            'estimated_price': estimated,
            'price_range_low': low,
            'price_range_high': high
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}, 400

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
        
        user = User.query.filter_by(name=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
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
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists')
        else:
            new_user = User(name=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    properties = Property.query.filter_by(owner_id=session['user_id']).all()
    return render_template('profile.html', properties=properties)

# Create tables on startup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)