from dataclasses import dataclass

@dataclass
class Student:
    email_address: str
    first_name: str
    last_name: str
    course_id: str
    grade_letter: str
    marks: int

@dataclass
class Course:
    course_id: str
    course_name: str
    description: str = ""

@dataclass
class Professor:
    professor_id: str
    name: str
    rank: str
    course_id: str

@dataclass
class LoginUser:
    user_id: str
    password_hash: str
    role: str  
