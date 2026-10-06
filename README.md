# Student Management System

A simple Python + SQLite app for managing student records in a browser or from the terminal.

## Features

- List students
- Add student records
- Edit student records
- Delete student records
- Login system with default admin account
- Search and filter students
- Dashboard summary cards
- Student profile fields for GPA, skills, and projects
- AI assistant page

## Setup

1. Install Python 3 if needed.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the web application:

   ```bash
   python server.py
   ```

4. Open your browser at `http://localhost:5000`.

## CLI version

You can also run the command-line app:

```bash
python app.py
```

## Login

- Username: `admin`
- Password: `admin123`

## Notes

- Student data is saved in `students.db` automatically.
- The project uses Flask and SQLite.
