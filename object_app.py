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
        'hero_title': 'مستقبل العقار', 'hero_subtitle': 'في الرياض',
        'hero_desc': 'اكتشف منزلك الجديد باستخدام أذكى تقنيات البحث العقاري.',
        'browse_now': 'تصفح السوق الآن', 'request_property': 'اطلب عقارك',
        'why_object': 'لماذا OBJECT؟', 'why_desc': 'نقدم تجربة عقارية لا مثيل لها',

        'maps': 'خرائط تفاعلية', 'maps_desc': 'شاهد موقع العقار بدقة على الخريطة',
        'calculator': 'حاسبة التمويل', 'calculator_desc': 'احسب القسط الشهري بناءً على راتبك',
        'properties': 'عقار متاح', 'districts': 'حي في الرياض', 'clients': 'عميل سعيد',
        'search': 'بحث', 'district': 'الحي', 'property_type': 'نوع العقار', 'max_price': 'الحد الأقصى للسعر',
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
        'footer_desc': 'مستقبل العقار في الرياض'
    },
    'en': {
        'title': 'OBJECT', 'dir': 'ltr', 'align': 'left', 'font': 'Inter',
        'home': 'Home', 'browse': 'Marketplace', 'request': 'Request', 
        'dashboard': 'Dashboard', 'login': 'Login', 'logout': 'Logout', 'signup': 'Sign Up',
        'hero_title': 'Future of Real Estate', 'hero_subtitle': 'in Riyadh',
        'hero_desc': 'Discover your new home using the smartest real estate search technology.',
        'browse_now': 'Browse Now', 'request_property': 'Request Property',
        'why_object': 'Why OBJECT?', 'why_desc': 'We offer an unparalleled real estate experience',

        'maps': 'Interactive Maps', 'maps_desc': 'View property location precisely on the map',
        'calculator': 'Finance Calculator', 'calculator_desc': 'Calculate monthly payment based on your salary',
        'properties': 'Available Properties', 'districts': 'Districts in Riyadh', 'clients': 'Happy Clients',
        'search': 'Search', 'district': 'District', 'property_type': 'Property Type', 'max_price': 'Max Price',
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
        'footer_desc': 'The Future of Real Estate in Riyadh'
    },
    'fr': {
        'title': 'OBJECT', 'dir': 'ltr', 'align': 'left', 'font': 'Inter',
        'home': 'Accueil', 'browse': 'Marché', 'request': 'Demander', 
        'dashboard': 'Tableau de bord', 'login': 'Connexion', 'logout': 'Déconnexion', 'signup': 'Inscription',
        'hero_title': "L'avenir de l'immobilier", 'hero_subtitle': 'à Riyad',
        'hero_desc': 'Découvrez votre nouvelle maison avec la technologie de recherche immobilière la plus intelligente.',
        'browse_now': 'Parcourir', 'request_property': 'Demander un bien',
        'why_object': 'Pourquoi OBJECT?', 'why_desc': 'Nous offrons une expérience immobilière inégalée',

        'maps': 'Cartes interactives', 'maps_desc': 'Voir la localisation précise sur la carte',
        'calculator': 'Calculateur', 'calculator_desc': 'Calculez le paiement mensuel',
        'properties': 'Propriétés disponibles', 'districts': 'Quartiers à Riyad', 'clients': 'Clients satisfaits',
        'search': 'Rechercher', 'district': 'Quartier', 'property_type': 'Type de bien', 'max_price': 'Prix max',
        'all_types': 'Tous les types', 'villa': 'Villa', 'apartment': 'Appartement', 'land': 'Terrain',
        'rooms': 'Chambres', 'area': 'm²', 'views': 'Vues', 'sar': 'SAR',
        'contact_owner': 'Contacter le propriétaire', 'whatsapp': 'WhatsApp', 'book_visit': 'Réserver une visite',
        'finance_calc': 'Calculateur de financement', 'salary': 'Salaire mensuel', 'downpayment': 'Apport',
        'calculate': 'Calculer', 'property_details': 'Détails du bien',
        'add_property': 'Ajouter un bien', 'client_requests': 'Demandes clients',
        'publish': 'Publier', 'name': 'Nom', 'phone': 'Téléphone', 'notes': 'Notes',
        'send_request': 'Envoyer', 'not_found': "Vous n'avez pas trouvé ce que vous cherchez?",
        'lang_name': 'Français', 'bathrooms': 'Salles de bain', 'age': 'Âge du bien',
        'email': 'Email', 'password': 'Mot de passe', 'min_price': 'Prix min',
        'latitude': 'Latitude', 'longitude': 'Longitude',
        'footer_desc': "L'avenir de l'immobilier à Riyad"
    },
    'es': {
        'title': 'OBJECT', 'dir': 'ltr', 'align': 'left', 'font': 'Inter',
        'home': 'Inicio', 'browse': 'Mercado', 'request': 'Solicitar', 
        'dashboard': 'Panel', 'login': 'Iniciar sesión', 'logout': 'Cerrar sesión', 'signup': 'Registrarse',
        'hero_title': 'El futuro inmobiliario', 'hero_subtitle': 'en Riad',
        'hero_desc': 'Descubre tu nuevo hogar con la tecnología de búsqueda inmobiliaria más inteligente.',
        'browse_now': 'Explorar ahora', 'request_property': 'Solicitar propiedad',
        'why_object': '¿Por qué OBJECT?', 'why_desc': 'Ofrecemos una experiencia inmobiliaria sin igual',

        'maps': 'Mapas interactivos', 'maps_desc': 'Ver ubicación exacta en el mapa',
        'calculator': 'Calculadora', 'calculator_desc': 'Calcula tu cuota mensual',
        'properties': 'Propiedades disponibles', 'districts': 'Zonas en Riad', 'clients': 'Clientes felices',
        'search': 'Buscar', 'district': 'Zona', 'property_type': 'Tipo', 'max_price': 'Precio máx',
        'all_types': 'Todos los tipos', 'villa': 'Villa', 'apartment': 'Apartamento', 'land': 'Terreno',
        'rooms': 'Habitaciones', 'area': 'm²', 'views': 'Vistas', 'sar': 'SAR',
        'contact_owner': 'Contactar propietario', 'whatsapp': 'WhatsApp', 'book_visit': 'Reservar visita',
        'finance_calc': 'Calculadora financiera', 'salary': 'Salario mensual', 'downpayment': 'Entrada',
        'calculate': 'Calcular', 'property_details': 'Detalles de propiedad',
        'add_property': 'Añadir propiedad', 'client_requests': 'Solicitudes de clientes',
        'publish': 'Publicar', 'name': 'Nombre', 'phone': 'Teléfono', 'notes': 'Notas',
        'send_request': 'Enviar', 'not_found': '¿No encontraste lo que buscas?',
        'lang_name': 'Español', 'bathrooms': 'Baños', 'age': 'Antigüedad',
        'email': 'Correo electrónico', 'password': 'Contraseña', 'min_price': 'Precio mín',
        'latitude': 'Latitud', 'longitude': 'Longitud',
        'footer_desc': 'El futuro inmobiliario en Riad'
    },
    'zh': {
        'title': 'OBJECT', 'dir': 'ltr', 'align': 'left', 'font': 'Noto Sans SC',
        'home': '首页', 'browse': '市场', 'request': '请求', 
        'dashboard': '控制台', 'login': '登录', 'logout': '退出', 'signup': '注册',
        'hero_title': '房地产的未来', 'hero_subtitle': '在利雅得',
        'hero_desc': '使用最智能的房地产搜索技术发现您的新家。',
        'browse_now': '立即浏览', 'request_property': '请求房产',
        'why_object': '为什么选择 OBJECT?', 'why_desc': '我们提供无与伦比的房地产体验',

        'maps': '互动地图', 'maps_desc': '在地图上精确查看房产位置',
        'calculator': '贷款计算器', 'calculator_desc': '根据您的工资计算月供',
        'properties': '可用房产', 'districts': '利雅得区域', 'clients': '满意客户',
        'search': '搜索', 'district': '区域', 'property_type': '房产类型', 'max_price': '最高价格',
        'all_types': '所有类型', 'villa': '别墅', 'apartment': '公寓', 'land': '土地',
        'rooms': '房间', 'area': '平方米', 'views': '浏览量', 'sar': '里亚尔',
        'contact_owner': '联系房主', 'whatsapp': 'WhatsApp', 'book_visit': '预约看房',
        'finance_calc': '贷款计算器', 'salary': '月薪', 'downpayment': '首付',
        'calculate': '计算', 'property_details': '房产详情',
        'add_property': '添加房产', 'client_requests': '客户请求',
        'publish': '发布', 'name': '姓名', 'phone': '电话', 'notes': '备注',
        'send_request': '发送请求', 'not_found': '没有找到您想要的？',
        'lang_name': '中文', 'bathrooms': '浴室', 'age': '房龄',
        'email': '电子邮件', 'password': '密码', 'min_price': '最低价格',
        'latitude': '纬度', 'longitude': '经度',
        'footer_desc': '利雅得房地产的未来'
    },
    'hi': {
        'title': 'OBJECT', 'dir': 'ltr', 'align': 'left', 'font': 'Noto Sans Devanagari',
        'home': 'होम', 'browse': 'बाज़ार', 'request': 'अनुरोध', 
        'dashboard': 'डैशबोर्ड', 'login': 'लॉगिन', 'logout': 'लॉगआउट', 'signup': 'साइन अप',
        'hero_title': 'रियल एस्टेट का भविष्य', 'hero_subtitle': 'रियाद में',
        'hero_desc': 'सबसे स्मार्ट रियल एस्टेट सर्च तकनीक से अपना नया घर खोजें।',
        'browse_now': 'अभी ब्राउज़ करें', 'request_property': 'संपत्ति का अनुरोध करें',
        'why_object': 'OBJECT क्यों?', 'why_desc': 'हम एक अद्वितीय रियल एस्टेट अनुभव प्रदान करते हैं',

        'maps': 'इंटरैक्टिव मैप्स', 'maps_desc': 'मानचित्र पर सटीक स्थान देखें',
        'calculator': 'EMI कैलकुलेटर', 'calculator_desc': 'अपनी सैलरी के आधार पर EMI की गणना करें',
        'properties': 'उपलब्ध संपत्तियाँ', 'districts': 'रियाद में क्षेत्र', 'clients': 'खुश ग्राहक',
        'search': 'खोज', 'district': 'क्षेत्र', 'property_type': 'संपत्ति का प्रकार', 'max_price': 'अधिकतम मूल्य',
        'all_types': 'सभी प्रकार', 'villa': 'विला', 'apartment': 'अपार्टमेंट', 'land': 'भूमि',
        'rooms': 'कमरे', 'area': 'वर्ग मीटर', 'views': 'व्यूज़', 'sar': 'रियाल',
        'contact_owner': 'मालिक से संपर्क करें', 'whatsapp': 'WhatsApp', 'book_visit': 'विज़िट बुक करें',
        'finance_calc': 'EMI कैलकुलेटर', 'salary': 'मासिक वेतन', 'downpayment': 'डाउन पेमेंट',
        'calculate': 'गणना करें', 'property_details': 'संपत्ति विवरण',
        'add_property': 'संपत्ति जोड़ें', 'client_requests': 'ग्राहक अनुरोध',
        'publish': 'प्रकाशित करें', 'name': 'नाम', 'phone': 'फ़ोन', 'notes': 'नोट्स',
        'send_request': 'भेजें', 'not_found': 'जो चाहिए वो नहीं मिला?',
        'lang_name': 'हिन्दी', 'bathrooms': 'बाथरूम', 'age': 'संपत्ति की आयु',
        'email': 'ईमेल', 'password': 'पासवर्ड', 'min_price': 'न्यूनतम मूल्य',
        'latitude': 'अक्षांश', 'longitude': 'देशांतर',
        'footer_desc': 'रियाद में रियल एस्टेट का भविष्य'
    },
    'tr': {
        'title': 'OBJECT', 'dir': 'ltr', 'align': 'left', 'font': 'Inter',
        'home': 'Ana Sayfa', 'browse': 'Pazar', 'request': 'Talep', 
        'dashboard': 'Panel', 'login': 'Giriş', 'logout': 'Çıkış', 'signup': 'Kayıt Ol',
        'hero_title': 'Gayrimenkulün Geleceği', 'hero_subtitle': "Riyad'da",
        'hero_desc': 'En akıllı gayrimenkul arama teknolojisiyle yeni evinizi keşfedin.',
        'browse_now': 'Şimdi Gözat', 'request_property': 'Mülk Talep Et',
        'why_object': 'Neden OBJECT?', 'why_desc': 'Eşsiz bir gayrimenkul deneyimi sunuyoruz',

        'maps': 'Etkileşimli Haritalar', 'maps_desc': 'Haritada tam konumu görün',
        'calculator': 'Kredi Hesaplayıcı', 'calculator_desc': 'Maaşınıza göre aylık taksiti hesaplayın',
        'properties': 'Mevcut Mülkler', 'districts': "Riyad'daki Bölgeler", 'clients': 'Mutlu Müşteriler',
        'search': 'Ara', 'district': 'Bölge', 'property_type': 'Mülk Tipi', 'max_price': 'Maks Fiyat',
        'all_types': 'Tüm Tipler', 'villa': 'Villa', 'apartment': 'Daire', 'land': 'Arsa',
        'rooms': 'Oda', 'area': 'm²', 'views': 'Görüntüleme', 'sar': 'SAR',
        'contact_owner': 'Sahibiyle İletişim', 'whatsapp': 'WhatsApp', 'book_visit': 'Ziyaret Rezerve Et',
        'finance_calc': 'Kredi Hesaplayıcı', 'salary': 'Aylık Maaş', 'downpayment': 'Peşinat',
        'calculate': 'Hesapla', 'property_details': 'Mülk Detayları',
        'add_property': 'Mülk Ekle', 'client_requests': 'Müşteri Talepleri',
        'publish': 'Yayınla', 'name': 'Ad', 'phone': 'Telefon', 'notes': 'Notlar',
        'send_request': 'Gönder', 'not_found': 'Aradığınızı bulamadınız mı?',
        'lang_name': 'Türkçe', 'bathrooms': 'Banyo', 'age': 'Bina Yaşı',
        'email': 'E-posta', 'password': 'Şifre', 'min_price': 'Min Fiyat',
        'latitude': 'Enlem', 'longitude': 'Boylam',
        'footer_desc': "Riyad'da Gayrimenkulün Geleceği"
    }
}

# List of all languages for the selector
LANGUAGES = [
    {'code': 'ar', 'name': 'العربية', 'flag': '🇸🇦'},
    {'code': 'en', 'name': 'English', 'flag': '🇺🇸'},
    {'code': 'fr', 'name': 'Français', 'flag': '🇫🇷'},
    {'code': 'es', 'name': 'Español', 'flag': '🇪🇸'},
    {'code': 'zh', 'name': '中文', 'flag': '🇨🇳'},
    {'code': 'hi', 'name': 'हिन्दी', 'flag': '🇮🇳'},
    {'code': 'tr', 'name': 'Türkçe', 'flag': '🇹🇷'}
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