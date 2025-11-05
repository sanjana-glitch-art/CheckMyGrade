import os
import base64
import hashlib
import hmac
import re
from typing import Optional

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
ROLE_RE = re.compile(r"^(student|professor)$", re.IGNORECASE)
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z'\- ]{0,49}$")
COURSE_ID_RE = re.compile(r"^[A-Za-z]{2,4}\d{3}$|^[A-Za-z0-9_\-]{2,16}$")
GRADE_RE = re.compile(r"^[A-F][\+\-]?$", re.IGNORECASE)
# At least 8 chars, include upper, lower, digit, special
PASSWORD_POLICY_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,128}$")

def validate_email(s): 
    return bool(EMAIL_RE.match(s or ""))
def validate_role(s):
    return bool(ROLE_RE.match((s or "").lower()))
def validate_name(s):
    return bool(NAME_RE.match(s or ""))
def validate_course_id(s): 
    return bool(COURSE_ID_RE.match(s or ""))
def validate_grade(s):
    return bool(GRADE_RE.match(s or ""))
def validate_password_strength(s):
    return bool(PASSWORD_POLICY_RE.match(s or ""))

#password hashing
# _PBKDF2_ALGO = "sha256"
_PBKDF2_ITER = 200_000
_SALT_BYTES = 16

def _b64(x: bytes) -> str:
    return base64.urlsafe_b64encode(x).decode("ascii").rstrip("=")

def _unb64(s: str) -> bytes:
    pad = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + pad)

def hash_password(password: str) -> str:
    if not isinstance(password, str):
        raise TypeError("password must be str")
    salt = os.urandom(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(_PBKDF2_ALGO, password.encode("utf-8"), salt, _PBKDF2_ITER)
    return f"pbkdf2_{_PBKDF2_ALGO}${_PBKDF2_ITER}${_b64(salt)}${_b64(dk)}"

def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iters, salt_b64, dk_b64 = stored.split("$", 3)
        if not scheme.startswith("pbkdf2_"):
            return False
        iters = int(iters)
        algo = scheme.split("_", 1)[1]
        salt = _unb64(salt_b64)
        expected = _unb64(dk_b64)
        dk = hashlib.pbkdf2_hmac(algo, password.encode("utf-8"), salt, iters)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False