# CheckMyGrade

A secure, console-based grade management system built on Python and CSV storage.

# Project Overview

This project enables students to develop a grade evaluation system using Python, with a focus on object-oriented design and efficient data handling. The app supports adding, modifying, and deleting student, course, and professor records, and generating reports and statistics.

# Features

- Add, delete, and modify student, course, and professor records
- Secure login with password encryption
- Search and sort student data with performance metrics
- Generate course-wise and professor-wise reports
- Calculate average and median scores
   
# Project Structure

| File             | Purpose |
|------------------|---------|
| `main.py`        | Handles menus, input, and flow control |
| `models.py`      | Defines core data classes (`Student`, `Course`, `Professor`, `LoginUser` ) |
| `services.py`    | Business logic for managing entities |
| `storage.py`     | CSV read/write operations via `CsvTable` |
| `security.py`    | Input validation and password hashing |
| `test_checkmygrade.py` | Unit tests for all major modules |
| `data/*.csv`     | Persistent storage for students, courses, professors, and login info |

# Security

Passwords are hashed using PBKDF2 with SHA-256 and stored securely in `login.csv`. Validation ensures strong password policies and safe authentication.

# Installation and Setup

git clone https://github.com/sanjana-glitch-art/checkmygrade.git
cd checkmygrade
python main.py

# Testing

Run `test_checkmygrade.py` to validate:
- Student/course/professor CRUD operations
- Sorting and searching performance
- CSV data integrity

