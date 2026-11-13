"""Create a login or reset a password.

    python scripts/create_user.py alice 'StrongPass123' "Alice Smith"
"""
import sys

import _path  # noqa: F401
from backend import auth, db

if len(sys.argv) < 3:
    sys.exit("usage: python scripts/create_user.py <username> <password> [full name]")
db.init_db()
user, pw, name = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "")
if db.get_user(user):
    db.set_password(user, auth.hash_password(pw))
    print(f"Password updated for '{user}'")
else:
    db.create_user(user, auth.hash_password(pw), name)
    print(f"Created user '{user}'")
