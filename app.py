from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your-secret-key'

# اسم ملف قاعدة البيانات
database_file = "bookings.db"

# صفحة البداية
@app.route("/")
def home():
    return render_template("home.html")

# صفحة حجز موعد جديد
@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        # البيانات التي تم إدخالها في النموذج
        name = request.form["name"]
        doctor = request.form["doctor"]
        date = request.form["date"]
        time = request.form["time"]

        # إنشاء اتصال بقاعدة البيانات وإدخال البيانات في جدول "bookings"
        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        c.execute(''' CREATE TABLE If NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            doctor TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )''')
        c.execute("INSERT INTO bookings (name, doctor, date, time) VALUES (?, ?, ?, ?)", (name, doctor, date, time))
        conn.commit()
        conn.close()

        return redirect(url_for("view"))

    return render_template("book.html")

# صفحة عرض قائمة المواعيد المحجوزة
@app.route("/view")
def view():
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    c.execute("SELECT * from bookings")
    rows = c.fetchall()
    conn.close()

    return render_template("view.html", rows=rows)

# صفحة تسجيل الدخول للمشرف
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['admin'] = True
            return redirect(url_for('admin_index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

# صفحة الواجهة الإدارية
@app.route('/admin')
def admin_index():
    if 'admin' not in session or not session['admin']:
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    # إستعلام SQL لاسترداد جميع الحجوزات
    c.execute("SELECT * from bookings")
    rows = c.fetchall()
    conn.close()
    return render_template('admin.html', rows=rows)

# صفحة تعديل حجز موعد
@app.route("/admin/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if request.method == "POST":
        name = request.form["name"]
        doctor = request.form["doctor"]
        date = request.form["date"]
        time = request.form["time"]

        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        c.execute("UPDATE bookings SET name=?, doctor=?, date=?, time=? WHERE id=?", (name, doctor, date, time, id))
        conn.commit()
        conn.close()

        return redirect(url_for("admin_index"))

    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    c.execute("SELECT * FROM bookings WHERE id=?", (id,))
    row = c.fetchone()
    conn.close()

    return render_template("edit.html", row=row)

# صفحة حذف حجز موعد
@app.route("/admin/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_index"))

# صفحة إضافة حجز موعد جديد
@app.route("/admin/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        doctor = request.form["doctor"]
        date = request.form["date"]
        time = request.form["time"]

        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        c.execute("INSERT INTO bookings (name, doctor, date, time) VALUES (?, ?, ?, ?)", (name, doctor, date, time))
        conn.commit()
        conn.close()

        return redirect(url_for("admin_index"))

    return render_template("add.html")
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
