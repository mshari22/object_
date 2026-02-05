from flask import Flask, render_template, request, redirect, url_for, flash, session
import pyodbc

app = Flask(__name__)
app.secret_key = "object_luxury_secret_2026"

# إعدادات قاعدة البيانات
server_name = r'LAPTOP-P1QFRI6B' 
database_name = 'OBJECT_DB'

def get_db_connection():
    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}}; SERVER={server_name}; DATABASE={database_name}; Trusted_Connection=yes;'
        )
        return conn
    except Exception as e:
        print(f"Database Error: {e}")
        return None

@app.route('/')
def home():
    user_name = session.get('user_name')
    conn = get_db_connection()
    properties_list = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT PropertyID, Title, Price, Location, Beds, Baths, Area, ImageURL, OwnerID FROM Properties ORDER BY PropertyID DESC")
        columns = [column[0] for column in cursor.description]
        properties_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
    return render_template('object_home.html', user_name=user_name, properties=properties_list, current_user_id=session.get('user_id'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name, email, password = request.form['fullName'], request.form['email'], request.form['password']
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Users (FullName, Email, Password) VALUES (?, ?, ?)", (name, email, password))
                conn.commit()
                flash("Account created! Please login.", "success")
                return redirect(url_for('login'))
            except:
                flash("Email already exists.", "danger")
            finally:
                conn.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT UserID, FullName FROM Users WHERE Email = ? AND Password = ?", (email, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                session['user_id'], session['user_name'] = user.UserID, user.FullName
                return redirect(url_for('home'))
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        data = (request.form['title'], request.form['price'], request.form['location'], 
                request.form['beds'], request.form['baths'], request.form['area'], 
                request.form['image_url'], session['user_id'])
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Properties (Title, Price, Location, Beds, Baths, Area, ImageURL, OwnerID) VALUES (?,?,?,?,?,?,?,?)", data)
            conn.commit()
            conn.close()
            return redirect(url_for('home'))
    return render_template('add_property.html')

@app.route('/delete_property/<int:id>')
def delete_property(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # التأكد أن الشخص الذي يحذف هو صاحب العقار
        cursor.execute("DELETE FROM Properties WHERE PropertyID = ? AND OwnerID = ?", (id, session['user_id']))
        conn.commit()
        conn.close()
        flash("Property deleted!", "info")
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)