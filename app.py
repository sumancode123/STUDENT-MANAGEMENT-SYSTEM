import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "students.db")


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
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


def prompt_nonempty(prompt_text):
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Please enter a value.")


def list_students():
    with get_connection() as conn:
        students = conn.execute("SELECT id, name, email, course, age FROM students ORDER BY id").fetchall()

    if not students:
        print("\nNo students found.\n")
        return

    print("\nStudents:")
    for student in students:
        print(
            f"{student['id']}: {student['name']}, {student['email']}, {student['course']}, age {student['age']}"
        )


def add_student():
    name = prompt_nonempty("Name: ")
    email = prompt_nonempty("Email: ")
    course = prompt_nonempty("Course: ")

    while True:
        age_text = prompt_nonempty("Age: ")
        if age_text.isdigit():
            age = int(age_text)
            break
        print("Age must be a number.")

    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO students (name, email, course, age) VALUES (?, ?, ?, ?)",
                (name, email, course, age),
            )
            conn.commit()
            print("Student added.\n")
        except sqlite3.IntegrityError:
            print("A student with that email already exists.\n")


def edit_student():
    student_id_text = prompt_nonempty("Enter student ID to edit: ")
    if not student_id_text.isdigit():
        print("ID must be a number.\n")
        return

    student_id = int(student_id_text)
    with get_connection() as conn:
        student = conn.execute(
            "SELECT id, name, email, course, age FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()

    if student is None:
        print("Student not found.\n")
        return

    print("Leave blank to keep the current value.")
    name = input(f"Name [{student['name']}]: ").strip() or student["name"]
    email = input(f"Email [{student['email']}]: ").strip() or student["email"]
    course = input(f"Course [{student['course']}]: ").strip() or student["course"]
    age_text = input(f"Age [{student['age']}]: ").strip()

    age = student["age"]
    if age_text:
        if age_text.isdigit():
            age = int(age_text)
        else:
            print("Age not updated because it is not a valid number.")

    with get_connection() as conn:
        try:
            conn.execute(
                "UPDATE students SET name = ?, email = ?, course = ?, age = ? WHERE id = ?",
                (name, email, course, age, student_id),
            )
            conn.commit()
            print("Student updated.\n")
        except sqlite3.IntegrityError:
            print("A student with that email already exists.\n")


def delete_student():
    student_id_text = prompt_nonempty("Enter student ID to delete: ")
    if not student_id_text.isdigit():
        print("ID must be a number.\n")
        return

    student_id = int(student_id_text)
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()

    if cursor.rowcount == 0:
        print("Student not found.\n")
    else:
        print("Student deleted.\n")


def print_menu():
    print("Student Management System")
    print("1. List students")
    print("2. Add student")
    print("3. Edit student")
    print("4. Delete student")
    print("5. Exit")


def main():
    init_db()
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            list_students()
        elif choice == "2":
            add_student()
        elif choice == "3":
            edit_student()
        elif choice == "4":
            delete_student()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Please try again.\n")


if __name__ == "__main__":
    main()

    print()


def add_student():
    name = prompt_nonempty("Name: ")
    email = prompt_nonempty("Email: ")
    course = prompt_nonempty("Course: ")

    while True:
        age_text = prompt_nonempty("Age: ")
        if age_text.isdigit():
            age = int(age_text)
            break
        print("Age must be a number.")

    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO students (name, email, course, age) VALUES (?, ?, ?, ?)",
                (name, email, course, age),
            )
            conn.commit()
            print("Student added.\n")
        except sqlite3.IntegrityError:
            print("A student with that email already exists.\n")


def edit_student():
    student_id_text = prompt_nonempty("Enter student ID to edit: ")
    if not student_id_text.isdigit():
        print("ID must be a number.\n")
        return

    student_id = int(student_id_text)
    with get_connection() as conn:
        student = conn.execute(
            "SELECT id, name, email, course, age FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()

    if student is None:
        print("Student not found.\n")
        return

    print("Leave blank to keep the current value.")
    name = input(f"Name [{student['name']}]: ").strip() or student["name"]
    email = input(f"Email [{student['email']}]: ").strip() or student["email"]
    course = input(f"Course [{student['course']}]: ").strip() or student["course"]
    age_text = input(f"Age [{student['age']}]: ").strip()

    age = student["age"]
    if age_text:
        if age_text.isdigit():
            age = int(age_text)
        else:
            print("Age not updated because it is not a valid number.")

    with get_connection() as conn:
        try:
            conn.execute(
                "UPDATE students SET name = ?, email = ?, course = ?, age = ? WHERE id = ?",
                (name, email, course, age, student_id),
            )
            conn.commit()
            print("Student updated.\n")
        except sqlite3.IntegrityError:
            print("A student with that email already exists.\n")


def delete_student():
    student_id_text = prompt_nonempty("Enter student ID to delete: ")
    if not student_id_text.isdigit():
        print("ID must be a number.\n")
        return

    student_id = int(student_id_text)
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()

    if cursor.rowcount == 0:
        print("Student not found.\n")
    else:
        print("Student deleted.\n")


def print_menu():
    print("Student Management System")
    print("1. List students")
    print("2. Add student")
    print("3. Edit student")
    print("4. Delete student")
    print("5. Exit")


def main():
    init_db()
    if not authenticate_user():
        return

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            list_students()
        elif choice == "2":
            add_student()
        elif choice == "3":
            edit_student()
        elif choice == "4":
            delete_student()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Please try again.\n")


if __name__ == "__main__":
    main()
