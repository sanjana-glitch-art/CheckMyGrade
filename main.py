import os
from getpass import getpass
from models import Student, Course, Professor
from storage import CsvTable
from services import StudentService, CourseService, ProfessorService, AuthService
from security import (
    validate_email, validate_name, validate_course_id, validate_grade,
    validate_password_strength
)

DATA_DIR = "data"
STUDENTS_HEADERS = ["Email_address", "First_name", "Last_name", "Course.id", "grades", "Marks"]
COURSES_HEADERS = ["Course_id", "Course_name", "Description"]
PROFESSORS_HEADERS = ["Professor_id", "Name", "Rank", "Course.id"]
LOGIN_HEADERS = ["User_id", "PasswordHash", "Role"]  # secure

def bootstrap_tables():
    os.makedirs(DATA_DIR, exist_ok=True)
    students = CsvTable(os.path.join(DATA_DIR, "students.csv"), STUDENTS_HEADERS)
    course   = CsvTable(os.path.join(DATA_DIR, "course.csv"),   COURSES_HEADERS)
    profs    = CsvTable(os.path.join(DATA_DIR, "professors.csv"), PROFESSORS_HEADERS)
    login    = CsvTable(os.path.join(DATA_DIR, "login.csv"),    LOGIN_HEADERS)
    return students, course, profs, login

def pause(msg="Press Enter to continue..."):
    try:
        input(msg)
    except EOFError:
        pass

def confirm(prompt: str) -> bool:
    while True:
        ans = input(f"{prompt} [y/n]: ").strip().lower()
        if ans in ("y", "yes"): return True
        if ans in ("n", "no"): return False
        print("Please answer y or n.")

def prompt_email(label="Email/User ID: "):
    while True:
        s = input(label).strip()
        if validate_email(s):
            return s
        print("Invalid email format.")

def prompt_name(label: str):
    while True:
        s = input(label).strip()
        if validate_name(s):
            return s
        print("Use letters/spaces/hyphens/apostrophes (max 50 chars).")

def prompt_course_id(label="Course id: "):
    while True:
        s = input(label).strip()
        if validate_course_id(s):
            return s
        print("Invalid course id (try CS101 or 2–16 chars of letters/digits/_/-).")

def prompt_grade(label="Grade letter (A/B/C...): ", default="A"):
    while True:
        s = (input(label).strip() or default).upper()
        if validate_grade(s):
            return s
        print("Use A–F with optional +/- (e.g., A, B+, C-).")

def prompt_marks(label="Marks (0-100): "):
    while True:
        s = input(label).strip()
        try:
            v = int(s)
            if 0 <= v <= 100:
                return v
            print("Marks must be 0–100.")
        except ValueError:
            print("Enter an integer 0–100.")

def prompt_role(label="Role (professor/student): ", default="student"):
    while True:
        s = (input(label).strip() or default).lower()
        if s in ("professor", "student"):
            return s
        print("Role must be 'professor' or 'student'.")

def prompt_password_for_registration():
    print("Password must be 8+ chars and include upper, lower, digit, special.")
    while True:
        pw1 = getpass("Password: ")
        pw2 = getpass("Confirm password: ")
        if pw1 != pw2:
            print("Passwords do not match.")
            continue
        if not validate_password_strength(pw1):
            print("Password does not meet complexity.")
            continue
        return pw1

def prompt_password_for_login():
    return getpass("Password: ")

#Menu
def auth_menu(auth_svc: AuthService) -> bool:
    while True:
        print("=== CheckMyGrade (Secure) ===")
        print("1) Register")
        print("2) Login")
        print("3) Demo mode (no login)")
        print("0) Exit")
        choice = input("> ").strip()
        if choice == "1":
            uid = prompt_email("Email/User ID: ")
            role = prompt_role()
            pw = prompt_password_for_registration()
            try:
                if auth_svc.register(uid, pw, role):
                    print("Registered successfully. Please log in.")
            except ValueError as e:
                print(e)
            pause()
        elif choice == "2":
            for _ in range(3):
                uid = prompt_email("Email/User ID: ")
                pw = prompt_password_for_login()
                if auth_svc.login(uid, pw):
                    print("Login success.")
                    pause()
                    return True
                print("Login failed.")
            print("Too many failed attempts.")
            if not confirm("Try again?"):
                return False
        elif choice == "3":
            print("Entering demo mode (writes still persist to CSV).")
            pause()
            return True
        elif choice == "0":
            if confirm("Exit now?"):
                return False
        else:
            print("Unknown choice.")
            pause()

def main_menu(student_svc: StudentService, course_svc: CourseService, prof_svc: ProfessorService):
    while True:
        print("\nMenu:")
        print(" 1) Add student")
        print(" 2) Search student by email")
        print(" 3) Sort students by marks (desc)")
        print(" 4) Course stats")
        print(" 5) Add course")
        print(" 6) Add professor")
        print(" 7) Course report")
        print(" 8) List students")
        print(" 9) List courses")
        print("10) List professors")
        print(" 0) Exit")
        c = input("> ").strip()

        if c == "0":
            if confirm("Are you sure you want to exit?"):
                print("Bye.")
                return

        elif c == "1":
            email = prompt_email("Email: ")
            fn = prompt_name("First name: ")
            ln = prompt_name("Last name: ")
            cid = prompt_course_id()
            if not course_svc.get_by_id(cid):
                print(f"Course '{cid}' does not exist.")
                if confirm("Create it now?"):
                    name = input("Course name: ").strip() or "Untitled"
                    desc = input("Description (optional): ").strip()
                    course_svc.add_course(Course(cid, name, desc))
                else:
                    pause()
                    continue
            grade = prompt_grade()
            marks = prompt_marks()
            try:
                student_svc.add_student(Student(email, fn, ln, cid, grade, marks))
                print("Student added.")
            except ValueError as e:
                print(e)
            pause()

        elif c == "2":
            email = prompt_email("Email to search: ")
            result, ms = student_svc.search(email_address=email)
            print(f"Search took {ms:.2f} ms. Found {len(result)}:")
            for s in result:
                print(f" {s.email_address} {s.first_name} {s.last_name} {s.course_id} {s.grade_letter} {s.marks}")
            pause()

        elif c == "3":
            result, ms = student_svc.sort("marks", reverse=True)
            print(f"Sort took {ms:.2f} ms. Top 5:")
            for s in result[:5]:
                print(f" {s.email_address:28} {s.first_name:12} {s.last_name:12} {s.marks:3d}")
            pause()

        elif c == "4":
            cid = prompt_course_id()
            stats = student_svc.course_stats(cid)
            if not stats:
                print("No data for course.")
            else:
                print(f"Avg: {stats['average']:.2f}  Median: {stats['median']:.2f}  Count: {stats['count']}")
            pause()

        elif c == "5":
            cid = prompt_course_id()
            name = input("Course name: ").strip() or "Untitled"
            desc = input("Description (optional): ").strip()
            try:
                course_svc.add_course(Course(cid, name, desc))
                print("Course added.")
            except ValueError as e:
                print(e)
            pause()

        elif c == "6":
            pid = prompt_email("Professor id (email): ")
            name = prompt_name("Name: ")
            rank = input("Rank: ").strip() or "Lecturer"
            cid = prompt_course_id()
            if not course_svc.get_by_id(cid):
                print(f"Course '{cid}' does not exist; add it first.")
                pause()
                continue
            try:
                prof_svc.add_professor(Professor(pid, name, rank, cid))
                print("Professor added.")
            except ValueError as e:
                print(e)
            pause()

        elif c == "7":
            cid = prompt_course_id()
            rows = student_svc.course_report(cid)
            print(f"{len(rows)} students in {cid}:")
            for s in rows:
                print(f" {s.email_address:28} {s.first_name:12} {s.last_name:12} {s.marks:3d}")
            pause()

        elif c == "8":
            ss = student_svc.list_students()
            print(f"{len(ss)} students total:")
            for s in sorted(ss, key=lambda x: (x.last_name.lower(), x.first_name.lower())):
                print(f" {s.email_address:28} {s.first_name:12} {s.last_name:12} {s.course_id:10} {s.grade_letter:2} {s.marks:3d}")
            pause()

        elif c == "9":
            cs = course_svc.list_courses()
            print(f"{len(cs)} courses total:")
            for c0 in sorted(cs, key=lambda x: x.course_id.lower()):
                print(f" {c0.course_id:10} {c0.course_name} — {c0.description}")
            pause()

        elif c == "10":
            ps = prof_svc.list_professors()
            print(f"{len(ps)} professors total:")
            for p in sorted(ps, key=lambda x: x.name.lower()):
                print(f" {p.professor_id:28} {p.name:18} {p.rank:12} {p.course_id}")
            pause()

        else:
            print("Unknown choice.")
            pause()

def main():
    students_tbl, course_tbl, prof_tbl, login_tbl = bootstrap_tables()
    student_svc = StudentService(students_tbl)
    course_svc  = CourseService(course_tbl)
    prof_svc    = ProfessorService(prof_tbl)
    auth_svc    = AuthService(login_tbl)

    if not auth_menu(auth_svc):
        print("Goodbye.")
        return

    main_menu(student_svc, course_svc, prof_svc)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Bye.")
