# ============================================================
# PROFILE ROUTES - DR. URCW AI
# ============================================================

import os
import shutil
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, StudentProfile, AdminProfile
from backend.auth_utils import hash_password, verify_password

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "frontend", "static", "uploads")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# ============================================================
# PROFILE PAGE
# ============================================================

@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    session_user = request.session["user"]
    user_id = session_user["id"]
    role = session_user["role"]

    user = db.query(User).filter(User.id == user_id).first()
    
    if role == "student":
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    else:
        profile = db.query(AdminProfile).filter(AdminProfile.user_id == user_id).first()

    return request.app.templates.TemplateResponse(
        f"{role}/profile.html",
        {
            "request": request,
            "user": user,
            "profile": profile
        }
    )


# ============================================================
# UPDATE PROFILE
# ============================================================

@router.post("/profile/update")
def update_profile(
    request: Request,
    name: str = Form(...),
    department: str = Form(""),
    phone: str = Form(""),
    student_id: str = Form(""),
    current_password: str = Form(""),
    new_password: str = Form(""),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    session_user = request.session["user"]
    user_id = session_user["id"]
    role = session_user["role"]

    user = db.query(User).filter(User.id == user_id).first()
    
    if role == "student":
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    else:
        profile = db.query(AdminProfile).filter(AdminProfile.user_id == user_id).first()

    # ---------- UPDATE BASIC FIELDS ----------
    user.name = name.strip()
    profile.department = department.strip()
    profile.phone = phone.strip()

    if role == "student":
        profile.student_id = student_id.strip()

    # ---------- PASSWORD UPDATE ----------
    if current_password and new_password:
        if verify_password(current_password, user.password_hash):
            user.password_hash = hash_password(new_password.strip())

    # ---------- PROFILE IMAGE UPLOAD ----------
    if profile_image and profile_image.filename:
        file_ext = profile_image.filename.split(".")[-1]
        filename = f"user_{user_id}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)

        profile.profile_image = f"/static/uploads/{filename}"

    db.commit()

    # Update session with new name
    request.session["user"]["name"] = user.name

    return RedirectResponse("/profile", status_code=303)


# ============================================================
# DELETE ACCOUNT
# ============================================================

@router.post("/profile/delete")
def delete_account(
    request: Request,
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    session_user = request.session["user"]
    user_id = session_user["id"]

    user = db.query(User).filter(User.id == user_id).first()

    if not verify_password(confirm_password, user.password_hash):
        return RedirectResponse("/profile", status_code=303)

    # Delete user (CASCADE handles related tables)
    db.delete(user)
    db.commit()

    request.session.clear()

    return RedirectResponse("/", status_code=303)