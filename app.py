from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'gif'}

def allow_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['MYSQL_DB'] = "student_db"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "root"
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)

@app.route("/")
def indexPage():
    return render_template("index.html")

@app.route("/add")
def regPage():
    cursor = mysql.connection.cursor()
    cursor.execute("select * from subject")
    subjects = cursor.fetchall()
    cursor.execute("select * from batch_time")
    batchTime = cursor.fetchall()
    cursor.close()
    return render_template("student_registration.html", sub=subjects, times=batchTime)

@app.route("/reg", methods=['POST'])
def add_student():
    rollNo = request.form['rollNo']
    name = request.form['name']
    subject = request.form['subject']
    email = request.form['email']
    gender = request.form['gender']
    batch_time = ','.join(request.form.getlist('batch_time'))
    photo = request.files['photo']

    if photo and allow_file(photo.filename):
        filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        return "Invalid photo format. Only allowed: {'png','jpg','jpeg','svg','gif'}", 400

    cursor = mysql.connection.cursor()
    query = "INSERT INTO student (rollNo, name, subject, email, gender, batch_time, photo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (rollNo, name, subject, email, gender, batch_time, filename))
    mysql.connection.commit()
    cursor.close()
    return redirect("/")

@app.route("/view")
def showStudentDetails():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM student")
    students = cursor.fetchall()
    cursor.close()
    return render_template("display.html", students=students)

@app.route("/view/<int:rollNo>")
def profile(rollNo):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM student where rollNo=%s", (rollNo,))
    student = cursor.fetchone()
    cursor.close()
    return render_template("profile.html", student=student)

@app.route("/edit/<int:rollNo>")
def editForm(rollNo):
    cursor = mysql.connection.cursor()
    cursor.execute("select * from subject")
    subjects = cursor.fetchall()
    cursor.execute("select * from batch_time")
    batchTime = cursor.fetchall()
    cursor.execute("SELECT * FROM student WHERE rollNo = %s", (rollNo,))
    student = cursor.fetchone()
    cursor.close()
    return render_template("edit.html", sub=subjects, times=batchTime, student=student)

@app.route("/save", methods=['POST'])
def updateData():
    rollNo = request.form.get('rollNo')
    name = request.form.get('name')
    subject = request.form.get('subject')
    email = request.form.get('email')
    gender = request.form.get('gender')
    batch_time = ','.join(request.form.getlist('batch_time'))
    photo = request.files.get('photo')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT photo FROM student WHERE rollNo=%s", (rollNo,))
    existing_filename = cursor.fetchone()[0]

    if photo and allow_file(photo.filename):
        filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = existing_filename

    query = """
        UPDATE student
        SET name=%s, subject=%s, email=%s, gender=%s, batch_time=%s, photo=%s
        WHERE rollNo=%s
    """
    cursor.execute(query, (name, subject, email, gender, batch_time, filename, rollNo))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for("showStudentDetails"))





if __name__ == '__main__':
    app.run(debug=True)


