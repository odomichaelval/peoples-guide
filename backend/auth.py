import hashlib
import secrets
import sqlite3
import time
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from pwdlib import PasswordHash

router = APIRouter(prefix="/auth", tags=["Accounts"])

DATABASE = Path(__file__).resolve().parents[1] / "data/private/accounts.db"
DATABASE.parent.mkdir(parents=True, exist_ok=True)

PASSWORDS = PasswordHash.recommended()
DUMMY_HASH = PASSWORDS.hash(secrets.token_urlsafe(32))
COOKIE = "peoples_guide_session"
SESSION_SECONDS = 8 * 60 * 60

# Local development through VS Code port forwarding.
ALLOWED_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}


def database():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


with database() as connection:
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at INTEGER NOT NULL
        );
    """)

DATABASE.chmod(0o600)


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


def check_origin(request: Request):
    if request.headers.get("origin") not in ALLOWED_ORIGINS:
        raise HTTPException(403, "This request origin is not allowed.")


def token_hash(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


def require_user(request: Request):
    token = request.cookies.get(COOKIE)

    if not token:
        raise HTTPException(401, "Please sign in.")

    with database() as connection:
        user = connection.execute(
            """
            SELECT users.id, users.email
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token_hash = ?
              AND sessions.expires_at > ?
            """,
            (token_hash(token), int(time.time())),
        ).fetchone()

    if user is None:
        raise HTTPException(401, "Your session has expired. Please sign in.")

    return dict(user)


@router.post("/register", dependencies=[Depends(check_origin)])
def register(credentials: Credentials):
    email = credentials.email.strip().lower()

    if (
        email.count("@") != 1
        or any(character.isspace() for character in email)
        or not all(email.split("@"))
    ):
        raise HTTPException(422, "Enter a valid email address.")

    if len(credentials.password) < 12:
        raise HTTPException(422, "Use a password of at least 12 characters.")

    password_hash = PASSWORDS.hash(credentials.password)

    try:
        with database() as connection:
            connection.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash),
            )
    except sqlite3.IntegrityError:
        raise HTTPException(
            409,
            "Unable to create this account. Try signing in instead.",
        )

    return {"message": "Account created. You can now sign in."}


@router.post("/login", dependencies=[Depends(check_origin)])
def login(
    credentials: Credentials,
    request: Request,
    response: Response,
):
    email = credentials.email.strip().lower()

    with database() as connection:
        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    saved_hash = user["password_hash"] if user else DUMMY_HASH
    valid = PASSWORDS.verify(credentials.password, saved_hash)

    if not user or not valid:
        raise HTTPException(401, "Email or password is incorrect.")

    token = secrets.token_urlsafe(32)
    old_token = request.cookies.get(COOKIE)

    with database() as connection:
        connection.execute(
            "DELETE FROM sessions WHERE expires_at <= ?",
            (int(time.time()),),
        )

        if old_token:
            connection.execute(
                "DELETE FROM sessions WHERE token_hash = ?",
                (token_hash(old_token),),
            )

        connection.execute(
            """
            INSERT INTO sessions (token_hash, user_id, expires_at)
            VALUES (?, ?, ?)
            """,
            (
                token_hash(token),
                user["id"],
                int(time.time()) + SESSION_SECONDS,
            ),
        )

    response.set_cookie(
        COOKIE,
        token,
        max_age=SESSION_SECONDS,
        httponly=True,
        samesite="strict",
        secure=False,  # Local HTTP development only; use True with HTTPS.
        path="/",
    )

    return {"email": user["email"]}


@router.get("/me")
def me(user=Depends(require_user)):
    return {"email": user["email"]}


@router.post("/logout", dependencies=[Depends(check_origin)])
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE)

    if token:
        with database() as connection:
            connection.execute(
                "DELETE FROM sessions WHERE token_hash = ?",
                (token_hash(token),),
            )

    response.delete_cookie(COOKIE, path="/", samesite="strict")
    return {"message": "Signed out."}