# ============================================================
# AUTH ROUTES - DR. URCW AI
# ============================================================

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.database import get_db
from backend.models import User, StudentProfile, AdminProfile
from backend.auth_utils import hash_password, verify_password
import os

router = APIRouter()

# ============================================================
# LOGIN PAGE
# ============================================================

@router.get("/", response_class=HTMLResponse)
def login_page(request: Request, success: str = None):
    return request.app.templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "success": success
        }
    )


# ============================================================
# LOGIN SUBMIT
# ============================================================

@router.post("/login")
def login(
    request: Request,
    role: str = Form(...),
    identifier: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    # Fetch user by username or email and role
    user = db.query(User).filter(
        or_(User.username == identifier, User.email == identifier),
        User.role == role
    ).first()

    if not user or not verify_password(password, user.password_hash):
        return request.app.templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid credentials"
            }
        )

    # Store session securely
    request.session["user"] = {
        "id": user.id,
        "name": user.name,
        "role": user.role
    }

    # Role-based redirection
    if user.role == "admin":
        return RedirectResponse("/admin", status_code=303)
    else:
        return RedirectResponse("/dashboard", status_code=303)


# ============================================================
# REGISTER PAGE
# ============================================================

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return request.app.templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


# ============================================================
# REGISTER SUBMIT
# ============================================================

@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):

    # Check existing user
    existing_user = db.query(User).filter(
        or_(User.username == username, User.email == email)
    ).first()

    if password != confirm_password:
        return request.app.templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Passwords do not match"
            }
        )

    if existing_user:
        return request.app.templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Username or Email already exists"
            }
        )

    try:
        # Create new user
        new_user = User(
            name=name.strip(),
            username=username.strip(),
            email=email.strip(),
            password_hash=hash_password(password),
            role=role
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Create appropriate profile based on role
        if role == "student":
            profile = StudentProfile(user_id=new_user.id)
        else:
            profile = AdminProfile(user_id=new_user.id)

        db.add(profile)
        db.commit()

        return RedirectResponse("/?success=Registration successful! Please login.", status_code=303)
    
    except Exception as e:
        db.rollback()
        print(f"Registration error: {str(e)}")
        return request.app.templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Registration failed. Please try again."
            }
        )


# ============================================================
# LOGOUT
# ============================================================

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


# ============================================================
# API: GET PROFILE IMAGE
# ============================================================

@router.get("/api/profile-image")
def get_profile_image(request: Request, db: Session = Depends(get_db)):
    if "user" not in request.session:
        return {"image": None}
    
    user_id = request.session["user"]["id"]
    role = request.session["user"]["role"]
    
    if role == "student":
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    else:
        profile = db.query(AdminProfile).filter(AdminProfile.user_id == user_id).first()
    
    return {"image": profile.profile_image if profile and profile.profile_image else None}