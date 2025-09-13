import sys
import os
import logging
# ensure project root is on sys.path so imports like `from app...` work when run as a script
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication, QMessageBox
from app.models import init_db, SessionLocal, User
from app.auth import register_user, authenticate_user, log_activity
from app.ui import MainChoiceDialog, LoginDialog, Dashboard

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ensure environment dirs exist
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "storage"), exist_ok=True)

def ensure_default_admin():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            # create default admin/admin for first-run convenience
            ok, msg, email_sent = register_user("admin", "admin1234", "admin@example.com", is_admin=True)
            if ok:
                print("Created default admin: admin / admin1234 (change this password)")
            else:
                print(f"Failed to create default admin: {msg}")
    finally:
        db.close()

def run_app():
    try:
        init_db()
        ensure_default_admin()
        app = QApplication(sys.argv)

        # load optional stylesheet for a more polished look
        style_path = os.path.join(BASE_DIR, "app", "style.qss")
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    app.setStyleSheet(f.read())
            except Exception as e:
                logger.error(f"Failed to load stylesheet: {e}")

        choice = MainChoiceDialog()

        def attempt_login(login_dialog, is_admin_flag):
            try:
                username = login_dialog.user_edit.text().strip()
                pw = login_dialog.pw_edit.text().strip()
                user = authenticate_user(username, pw)
                if user:
                    if user.is_admin != is_admin_flag:
                        if is_admin_flag:
                            QMessageBox.warning(login_dialog, "Access Denied", "This is the admin login page. Please use user login.")
                        else:
                            QMessageBox.warning(login_dialog, "Access Denied", "This is the user login page. Please use admin login.")
                        return
                    logger.info(f"{'Admin' if is_admin_flag else 'User'} {username} logged in successfully")
                    log_activity(user.id, "login", f"{'Admin' if is_admin_flag else 'User'} logged in")
                    login_dialog.user = user
                    login_dialog.accept()
                else:
                    logger.warning(f"Failed login attempt for {'admin' if is_admin_flag else 'user'} {username}")
                    log_activity(None, "failed_login", f"Failed login attempt for {'admin' if is_admin_flag else 'user'} {username}")
                    QMessageBox.warning(login_dialog, "Auth failed", "invalid credentials")
            except Exception as e:
                logger.error(f"Error during login: {e}")
                QMessageBox.critical(login_dialog, "Error", "An error occurred during login")

        def attempt_register(login_dialog, is_admin_flag):
            try:
                username = login_dialog.user_edit.text().strip()
                email = login_dialog.email_edit.text().strip()
                pw = login_dialog.pw_edit.text().strip()
                if not username or not pw:
                    QMessageBox.warning(login_dialog, "Invalid", "enter username and password")
                    return
                ok, msg, email_sent = register_user(username, pw, email, is_admin=is_admin_flag)
                if not ok:
                    QMessageBox.warning(login_dialog, "Error", msg)
                else:
                    logger.info(f"New {'admin' if is_admin_flag else 'user'} {username} registered")
                    log_activity(None, "register", f"New {'admin' if is_admin_flag else 'user'} {username} registered")
                    if email_sent is True:
                        msg_text = f"{'Admin' if is_admin_flag else 'User'} created; verification email sent. You can now sign in"
                    elif email_sent is False:
                        msg_text = f"{'Admin' if is_admin_flag else 'User'} created; verification email could not be sent. You can now sign in"
                    else:
                        msg_text = f"{'Admin' if is_admin_flag else 'User'} created. You can now sign in"
                    QMessageBox.information(login_dialog, "OK", msg_text)
            except Exception as e:
                logger.error(f"Error during registration: {e}")
                QMessageBox.critical(login_dialog, "Error", "An error occurred during registration")

        def on_user_login():
            login = LoginDialog(is_admin=False)

            login.login_btn.clicked.connect(lambda: attempt_login(login, is_admin_flag=False))
            login.register_btn.clicked.connect(lambda: attempt_register(login, is_admin_flag=False))

            login.back_btn.clicked.connect(lambda: (login.reject(), choice.show()))

            result = login.exec()
            if hasattr(login, 'user'):
                win = Dashboard(login.user)
                win.show()
                app.exec()

        def on_admin_login():
            login = LoginDialog(is_admin=True)

            login.login_btn.clicked.connect(lambda: attempt_login(login, is_admin_flag=True))
            login.register_btn.clicked.connect(lambda: attempt_register(login, is_admin_flag=True))

            login.back_btn.clicked.connect(lambda: (login.reject(), choice.show()))

            result = login.exec()
            if hasattr(login, 'user'):
                win = Dashboard(login.user)
                win.show()
                app.exec()

        choice.user_btn.clicked.connect(on_user_login)
        choice.admin_btn.clicked.connect(on_admin_login)

        # show choice dialog modally
        result = choice.exec()

    except Exception as e:
        logger.critical(f"Application error: {e}")
        QMessageBox.critical(None, "Critical Error", f"Application failed to start: {str(e)}")

if __name__ == "__main__":
    run_app()
