# Student Management System

A simple command-line student management system written with basic Python and SQLite.

## Features

- List students
- Add new students
- Edit student details
- Delete students

## Setup

1. Install Python 3 if needed.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the server app:

   ```bash
   python server.py
   ```

4. Open your browser at `http://localhost:5000`.

## Login

The web app requires authentication before you can manage students.

- Default username: `admin`
- Default password: `admin123`

## New features

- Browser-based student management
- Login required for access
- Search and filter students by name, email, or course
- Dashboard stats: total students, average age, and course summary
- Student profile fields: `gpa`, `skills`, `projects`
- AI assistant page for help and guidance
- Background image layout for a nicer look

## Notes

- Student data is saved in `students.db` automatically.
- The app uses Flask and SQLite.
