import os
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from backend import auth, db
from backend.app.schemas import LoginIn, RegisterIn, TokenOut

router = APIRouter(prefix="/api/auth", tags=["auth"])
ALLOW_SIGNUP = os.getenv("ALLOW_SIGNUP", "true").lower() == "true"


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn):
    user = auth.authenticate(body.username, body.password)
    if not user:
        raise HTTPException(401, "Incorrect username or password")
    return TokenOut(access_token=auth.create_token(user["username"]),
                    username=user["username"], full_name=user["full_name"])


@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn):
    if not ALLOW_SIGNUP:
        raise HTTPException(403, "Sign-up is disabled")
    try:
        db.create_user(body.username, auth.hash_password(body.password), body.full_name)
    except sqlite3.IntegrityError:
        raise HTTPException(409, "That username is taken")
    return TokenOut(access_token=auth.create_token(body.username.lower()),
                    username=body.username.lower(), full_name=body.full_name)


@router.get("/me")
def me(user=Depends(auth.current_user)):
    return {"username": user["username"], "full_name": user["full_name"]}
