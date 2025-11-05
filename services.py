from __future__ import annotations
from typing import List, Dict, Optional, Tuple
import time
import statistics
from models import Student, Course, Professor, LoginUser
from storage import CsvTable
from security import hash_password, verify_password

#  Student Service
class StudentService:
    def __init__(self, table: CsvTable):
        self.table = table
        self._students: List[Student] = [self._row_to_student(r) for r in self.table.read_all()]
        self._index: Dict[str, Student] = {s.email_address.lower(): s for s in self._students}

    @staticmethod
    def _safe_int(v: str) -> int:
        try:
            return int(v)
        except Exception:
            return 0

    def _row_to_student(self, r: Dict[str, str]) -> Student:
        return Student(
            email_address=r["Email_address"].strip(),
            first_name=r["First_name"].strip(),
            last_name=r["Last_name"].strip(),
            course_id=r["Course.id"].strip(),
            grade_letter=r["grades"].strip(),
            marks=self._safe_int(r.get("Marks", "0")),
        )

    def _student_to_row(self, s: Student) -> Dict[str, str]:
        return {
            "Email_address": s.email_address,
            "First_name": s.first_name,
            "Last_name": s.last_name,
            "Course.id": s.course_id,
            "grades": s.grade_letter,
            "Marks": str(s.marks),
        }

    def _flush(self) -> None:
        rows = [self._student_to_row(s) for s in self._students]
        self.table.overwrite(rows)

    # CRUD
    def add_student(self, s: Student) -> bool:
        key = s.email_address.lower()
        if not s.email_address:
            raise ValueError("email_address cannot be empty")
        if key in self._index:
            raise ValueError(f"Duplicate student email: {s.email_address}")
        self._students.append(s)
        self._index[key] = s
        self.table.append(self._student_to_row(s))
        return True

    def delete_student(self, email_address: str) -> bool:
        key = (email_address or "").lower()
        s = self._index.pop(key, None)
        if not s:
            return False
        self._students = [x for x in self._students if x.email_address.lower() != key]
        self._flush()
        return True

    def update_student(self, email_address: str, **updates) -> bool:
        key = (email_address or "").lower()
        s = self._index.get(key)
        if not s:
            return False
        for k, v in updates.items():
            if hasattr(s, k):
                setattr(s, k, v)
        self._flush()
        return True

    def sort(self, key: str, reverse: bool = False) -> Tuple[List[Student], float]:
        t0 = time.perf_counter()
        if key == "email_address":
            result = sorted(self._students, key=lambda s: s.email_address.lower(), reverse=reverse)
        elif key == "marks":
            result = sorted(self._students, key=lambda s: s.marks, reverse=reverse)
        elif key == "name":
            result = sorted(self._students, key=lambda s: (s.first_name.lower(), s.last_name.lower()), reverse=reverse)
        else:
            raise ValueError(f"Unsupported sort key: {key}")
        ms = (time.perf_counter() - t0) * 1000.0
        return result, ms

    def search(self, **criteria) -> Tuple[List[Student], float]:
        t0 = time.perf_counter()
        result = self._students
        for k, v in criteria.items():
            key = str(k)
            val = str(v)
            result = [
                s for s in result
                if hasattr(s, key) and str(getattr(s, key)).lower() == val.lower()
            ]
        ms = (time.perf_counter() - t0) * 1000.0
        return result, ms

    def course_stats(self, course_id: str) -> Optional[Dict[str, float]]:
        marks = [s.marks for s in self._students if s.course_id.lower() == (course_id or "").lower()]
        if not marks:
            return None
        marks.sort()
        return {
            "average": sum(marks) / len(marks),
            "median": float(statistics.median(marks)),
            "count": len(marks),
        }

    def course_report(self, course_id: str) -> List[Student]:
        out = [s for s in self._students if s.course_id.lower() == (course_id or "").lower()]
        out.sort(key=lambda s: (-s.marks, s.last_name.lower(), s.first_name.lower()))
        return out

    def list_students(self) -> List[Student]:
        return list(self._students)

#Course Service
class CourseService:
    def __init__(self, table: CsvTable):
        self.table = table
        self._courses: Dict[str, Course] = {}
        for r in self.table.read_all():
            cid = r["Course_id"].strip()
            self._courses[cid.lower()] = Course(
                course_id=cid,
                course_name=r["Course_name"].strip(),
                description=r.get("Description", "").strip()
            )

    def _flush(self) -> None:
        rows = [{
            "Course_id": c.course_id,
            "Course_name": c.course_name,
            "Description": c.description
        } for c in self._courses.values()]
        self.table.overwrite(rows)

    def add_course(self, c: Course) -> bool:
        if not c.course_id:
            raise ValueError("course_id cannot be empty")
        key = c.course_id.lower()
        if key in self._courses:
            raise ValueError(f"Duplicate course_id: {c.course_id}")
        self._courses[key] = c
        self.table.append({
            "Course_id": c.course_id,
            "Course_name": c.course_name,
            "Description": c.description
        })
        return True

    def delete_course(self, course_id: str) -> bool:
        key = (course_id or "").lower()
        if key not in self._courses:
            return False
        del self._courses[key]
        self._flush()
        return True

    def update_course(self, course_id: str, **updates) -> bool:
        key = (course_id or "").lower()
        c = self._courses.get(key)
        if not c:
            return False
        for k, v in updates.items():
            if hasattr(c, k):
                setattr(c, k, v)
        self._flush()
        return True

    def get_by_id(self, course_id: str) -> Optional[Course]:
        return self._courses.get((course_id or "").lower())

    def list_courses(self) -> List[Course]:
        return list(self._courses.values())

#Professor Service
class ProfessorService:
    def __init__(self, table: CsvTable):
        self.table = table
        self._professors: Dict[str, Professor] = {}
        for r in self.table.read_all():
            pid = r["Professor_id"].strip()
            self._professors[pid.lower()] = Professor(
                professor_id=pid,
                name=r["Name"].strip(),
                rank=r["Rank"].strip(),
                course_id=r["Course.id"].strip()
            )

    def _flush(self) -> None:
        rows = [{
            "Professor_id": p.professor_id,
            "Name": p.name,
            "Rank": p.rank,
            "Course.id": p.course_id
        } for p in self._professors.values()]
        self.table.overwrite(rows)

    def add_professor(self, p: Professor) -> bool:
        if not p.professor_id:
            raise ValueError("professor_id cannot be empty")
        key = p.professor_id.lower()
        if key in self._professors:
            raise ValueError(f"Duplicate professor_id: {p.professor_id}")
        self._professors[key] = p
        self.table.append({
            "Professor_id": p.professor_id,
            "Name": p.name,
            "Rank": p.rank,
            "Course.id": p.course_id
        })
        return True

    def delete_professor(self, professor_id: str) -> bool:
        key = (professor_id or "").lower()
        if key not in self._professors:
            return False
        del self._professors[key]
        self._flush()
        return True

    def update_professor(self, professor_id: str, **updates) -> bool:
        key = (professor_id or "").lower()
        p = self._professors.get(key)
        if not p:
            return False
        for k, v in updates.items():
            if hasattr(p, k):
                setattr(p, k, v)
        self._flush()
        return True

    def list_professors(self) -> List[Professor]:
        return list(self._professors.values())

# Authentication Service 
class AuthService:
    def __init__(self, table: CsvTable):
        self.table = table
        self._users: Dict[str, LoginUser] = {}
        self._load_or_migrate()

    def _load_or_migrate(self) -> None:
        rows = self.table.read_all()
        if not rows:
            self._users = {}
            return

        sample = rows[0]
        if "PasswordHash" in sample:
            # Secure format
            for r in rows:
                uid = r["User_id"].strip()
                self._users[uid.lower()] = LoginUser(
                    user_id=uid,
                    password_hash=r["PasswordHash"].strip(),
                    role=(r.get("Role", "student") or "student").lower()
                )
        else:
            migrated: Dict[str, Dict[str, str]] = {}
            for r in rows:
                uid = r["User_id"].strip()
                plain = r.get("Password", "")
                role = (r.get("Role", "student") or "student").lower()
                pwd_hash = hash_password(plain)
                migrated[uid.lower()] = {
                    "User_id": uid,
                    "PasswordHash": pwd_hash,
                    "Role": role,
                }
                self._users[uid.lower()] = LoginUser(uid, pwd_hash, role)
            self.table.headers = ["User_id", "PasswordHash", "Role"]
            self.table.overwrite(list(migrated.values()))

    def register(self, user_id: str, plain_password: str, role: str) -> bool:
        key = (user_id or "").lower()
        if not user_id:
            raise ValueError("user_id cannot be empty")
        if key in self._users:
            raise ValueError(f"Duplicate user_id: {user_id}")
        pwd_hash = hash_password(plain_password)
        user = LoginUser(user_id=user_id, password_hash=pwd_hash, role=(role or "student").lower())
        self._users[key] = user
        self.table.append({
            "User_id": user.user_id,
            "PasswordHash": user.password_hash,
            "Role": user.role
        })
        return True

    def login(self, user_id: str, plain_password: str) -> bool:
        user = self._users.get((user_id or "").lower())
        if not user:
            return False
        return verify_password(plain_password, user.password_hash)
