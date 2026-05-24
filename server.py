import functools
import hashlib
import os
import sqlite3

from flask import Flask, flash, g, redirect, render_template, request, session, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "students.db")
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["DATABASE"] = DB_FILE


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL,
            age INTEGER NOT NULL
        )
        """
    )
    db.commit()

    user = db.execute("SELECT id, password FROM users WHERE username = ?", (DEFAULT_USERNAME,)).fetchone()
    if user is None:
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (DEFAULT_USERNAME, hash_password(DEFAULT_PASSWORD)),
        )
        db.commit()
        print(f"Created default user: {DEFAULT_USERNAME} / {DEFAULT_PASSWORD}")
    else:
        count = db.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
        if count == 1 and user["password"] != hash_password(DEFAULT_PASSWORD):
            db.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (hash_password(DEFAULT_PASSWORD), DEFAULT_USERNAME),
            )
            db.commit()
            print(f"Reset default admin password to: {DEFAULT_USERNAME} / {DEFAULT_PASSWORD}")

    # Ensure additional columns for student profile (GPA, skills, projects)
    cols = [r[1] for r in db.execute("PRAGMA table_info(students)").fetchall()]
    if 'gpa' not in cols:
        db.execute("ALTER TABLE students ADD COLUMN gpa REAL DEFAULT 0")
    if 'skills' not in cols:
        db.execute("ALTER TABLE students ADD COLUMN skills TEXT DEFAULT ''")
    if 'projects' not in cols:
        db.execute("ALTER TABLE students ADD COLUMN projects TEXT DEFAULT ''")
    db.commit()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        hashed_password = hash_password(password)

        db = get_db()
        user = db.execute(
            "SELECT id, password FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if user:
            if user["password"] == hashed_password:
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = username
                flash("You logged in successfully.", "success")
                return redirect(url_for("index"))
            else:
                flash("Password is incorrect.", "error")
        else:
            flash("Invalid username.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    db = get_db()
    search_query = request.args.get("q", "").strip()
    course_filter = request.args.get("course", "").strip()

    sql = "SELECT * FROM students"
    params = []
    where_clauses = []

    if search_query:
        where_clauses.append("(name LIKE ? OR email LIKE ? OR course LIKE ?)")
        like_query = f"%{search_query}%"
        params.extend([like_query, like_query, like_query])
    if course_filter:
        where_clauses.append("course = ?")
        params.append(course_filter)

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    sql += " ORDER BY id"
    students = db.execute(sql, params).fetchall()

    total_students = db.execute("SELECT COUNT(*) AS count FROM students").fetchone()["count"]
    avg_age = db.execute("SELECT AVG(age) AS avg_age FROM students").fetchone()["avg_age"]
    avg_age = round(avg_age, 1) if avg_age is not None else 0
    avg_gpa = db.execute("SELECT AVG(gpa) AS avg_gpa FROM students").fetchone()["avg_gpa"]
    avg_gpa = round(avg_gpa, 2) if avg_gpa is not None else 0.0
    course_summary = db.execute(
        "SELECT course, COUNT(*) AS count FROM students GROUP BY course ORDER BY count DESC"
    ).fetchall()

    return render_template(
        "index.html",
        students=students,
        search_query=search_query,
        course_filter=course_filter,
        total_students=total_students,
        avg_age=avg_age,
        avg_gpa=avg_gpa,
        course_summary=course_summary,
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        course = request.form.get("course", "").strip()
        age = request.form.get("age", "").strip()
        gpa = request.form.get("gpa", "").strip()
        skills = request.form.get("skills", "").strip()
        projects = request.form.get("projects", "").strip()

        if not name or not email or not course or not age:
            flash("All fields are required.", "error")
        elif not age.isdigit():
            flash("Age must be a number.", "error")
        else:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO students (name, email, course, age, gpa, skills, projects) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, email, course, int(age), float(gpa) if gpa else None, skills, projects),
                )
                db.commit()
                flash("Student added successfully.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                flash("A student with that email already exists.", "error")

    return render_template("student_form.html", title="Add Student", student=None)


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    db = get_db()
    student = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        course = request.form.get("course", "").strip()
        age = request.form.get("age", "").strip()
        gpa = request.form.get("gpa", "").strip()
        skills = request.form.get("skills", "").strip()
        projects = request.form.get("projects", "").strip()

        if not name or not email or not course or not age:
            flash("All fields are required.", "error")
        elif not age.isdigit():
            flash("Age must be a number.", "error")
        else:
            try:
                db.execute(
                    "UPDATE students SET name = ?, email = ?, course = ?, age = ?, gpa = ?, skills = ?, projects = ? WHERE id = ?",
                    (name, email, course, int(age), float(gpa) if gpa else None, skills, projects, student_id),
                )
                db.commit()
                flash("Student updated successfully.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                flash("A student with that email already exists.", "error")

    return render_template("student_form.html", title="Edit Student", student=student)


@app.route("/delete/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):
    db = get_db()
    db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    flash("Student deleted successfully.", "success")
    return redirect(url_for("index"))


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not current_password or not new_password or not confirm_password:
            flash("All password fields are required.", "error")
        elif new_password != confirm_password:
            flash("New password and confirmation do not match.", "error")
        else:
            db = get_db()
            user = db.execute(
                "SELECT password FROM users WHERE id = ?",
                (session["user_id"],),
            ).fetchone()
            if user is None or user["password"] != hash_password(current_password):
                flash("Current password is incorrect.", "error")
            else:
                db.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (hash_password(new_password), session["user_id"]),
                )
                db.commit()
                flash("Password changed successfully.", "success")
                return redirect(url_for("index"))

    return render_template("change_password.html")


@app.route('/assistant', methods=['GET', 'POST'])
@login_required
def assistant():
    answer = None
    question = None
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if question:
            q = question.lower()
            if 'add student' in q or 'new student' in q:
                answer = 'To add a student, open Add Student, fill in the details, then save. Be sure the email is unique.'
            elif 'edit' in q or 'update' in q:
                answer = 'Go to the student list, click Edit for the student you want, change the fields, and save.'
            elif 'delete' in q or 'remove' in q:
                answer = 'Use the Delete button next to a student record to remove it from the system.'
            elif 'login' in q or 'password' in q:
                answer = 'Use admin / admin123 to log in. If you change the password, remember the new one for future access.'
            elif 'background' in q or 'theme' in q:
                answer = 'The app uses a background image and a clean light panel style. You can change it in templates/layout.html.'
            elif 'gpa' in q or 'skills' in q or 'projects' in q:
                answer = 'Student records support GPA, skills, and project fields so you can store useful profile details for each student.'
            else:
                answer = 'This assistant helps with student management tasks: add, edit, delete, and profile details. Try asking how to use a feature.'
        else:
            answer = 'Please enter a question so I can assist you.'
    return render_template('assistant.html', question=question, answer=answer)


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
