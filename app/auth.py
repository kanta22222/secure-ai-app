from app.models import SessionLocal, User, ActivityLog
import bcrypt
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime

def register_user(username: str, password: str, email: str = None, is_admin: bool = False):
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == username).first():
            return False, "user_exists"
        if email and db.query(User).filter(User.email == email).first():
            return False, "email_exists"
        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user = User(username=username, hashed_password=pw_hash.decode("utf-8"), is_admin=is_admin, email=email, is_active=True, created_at=datetime.utcnow())
        db.add(user)
        db.commit()
        if email:
            send_verification_email(email, username)
        return True, "created"
    finally:
        db.close()

def authenticate_user(username: str, password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
            user.last_login = datetime.utcnow()
            db.commit()
            return user
        return None
    finally:
        db.close()

def list_users():
    db = SessionLocal()
    try:
        return db.query(User).order_by(User.username).all()
    finally:
        db.close()

def log_activity(user_id: int, action: str, details: str = ""):
    db = SessionLocal()
    try:
        log = ActivityLog(user_id=user_id, action=action, timestamp=datetime.utcnow(), details=details)
        db.add(log)
        db.commit()
    finally:
        db.close()

def send_verification_email(email: str, username: str):
    # Simple email sending function
    # Note: Requires SMTP server configuration
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER', 'your_email@gmail.com')
    smtp_pass = os.getenv('SMTP_PASS', 'your_password')

    msg = MIMEText(f"Hello {username},\n\nPlease verify your email by clicking the link: [verification link]\n\nThank you!")
    msg['Subject'] = 'Email Verification'
    msg['From'] = smtp_user
    msg['To'] = email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
