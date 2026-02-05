from flask import Flask, render_template, request, redirect, url_for
import sqlite3 # استبدلنا pyodbc بـ sqlite3 للعمل على السيرفر العام

app = Flask(__name__)

# إنشاء قاعدة البيانات تلقائياً إذا لم تكن موجودة
def init_db():
    conn = sqlite3.connect('object_database.db')
    cursor = conn.cursor()
    # إنشاء جدول العقارات كمثال
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('object_home.html')

# أضف بقية الـ routes الخاصة بك هنا بنفس الطريقة

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)