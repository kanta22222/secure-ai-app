import sys
import os
import logging
# ensure project root is on sys.path so imports like `from app...` work when run as a script
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication, QMessageBox
from app.models import init_db, SessionLocal, User
from app.auth import register_user, authenticate_user
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
            register_user("admin", "admin1234", "admin@example.com", is_admin=True)
            print("Created default admin: admin / admin1234 (change this password)")
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

        def on_user_login():
            login = LoginDialog(is_admin=False)

            def attempt_login():
                try:
                    username = login.user_edit.text().strip()
                    pw = login.pw_edit.text().strip()
                    user = authenticate_user(username, pw)
                    if user:
                        if user.is_admin:
                            QMessageBox.warning(login, "Access Denied", "This is the user login page. Please use admin login.")
                            return
                        logger.info(f"User {username} logged in successfully")
                        login.user = user
                        login.accept()
                    else:
                        logger.warning(f"Failed login attempt for user {username}")
                        QMessageBox.warning(login, "Auth failed", "invalid credentials")
                except Exception as e:
                    logger.error(f"Error during login: {e}")
                    QMessageBox.critical(login, "Error", "An error occurred during login")

            def attempt_register():
                try:
                    username = login.user_edit.text().strip()
                    email = login.email_edit.text().strip()
                    pw = login.pw_edit.text().strip()
                    if not username or not pw:
                        QMessageBox.warning(login, "Invalid", "enter username and password")
                        return
                    ok, msg = register_user(username, pw, email, is_admin=False)
                    if not ok:
                        QMessageBox.warning(login, "Error", msg)
                    else:
                        logger.info(f"New user {username} registered")
                        QMessageBox.information(login, "OK", "User created; verification email sent. You can now sign in")
                except Exception as e:
                    logger.error(f"Error during registration: {e}")
                    QMessageBox.critical(login, "Error", "An error occurred during registration")

            login.login_btn.clicked.connect(attempt_login)
            login.register_btn.clicked.connect(attempt_register)

            login.back_btn.clicked.connect(lambda: (login.reject(), choice.show()))

            result = login.exec()
            if hasattr(login, 'user'):
                win = Dashboard(login.user)
                win.show()
                app.exec()

        def on_admin_login():
            login = LoginDialog(is_admin=True)

            def attempt_login():
                try:
                    username = login.user_edit.text().strip()
                    pw = login.pw_edit.text().strip()
                    user = authenticate_user(username, pw)
                    if user:
                        if not user.is_admin:
                            QMessageBox.warning(login, "Access Denied", "This is the admin login page. Please use user login.")
                            return
                        logger.info(f"Admin {username} logged in successfully")
                        login.user = user
                        login.accept()
                    else:
                        logger.warning(f"Failed login attempt for admin {username}")
                        QMessageBox.warning(login, "Auth failed", "invalid credentials")
                except Exception as e:
                    logger.error(f"Error during login: {e}")
                    QMessageBox.critical(login, "Error", "An error occurred during login")

            def attempt_register():
                try:
                    username = login.user_edit.text().strip()
                    email = login.email_edit.text().strip()
                    pw = login.pw_edit.text().strip()
                    if not username or not pw:
                        QMessageBox.warning(login, "Invalid", "enter username and password")
                        return
                    ok, msg = register_user(username, pw, email, is_admin=True)
                    if not ok:
                        QMessageBox.warning(login, "Error", msg)
                    else:
                        logger.info(f"New admin {username} registered")
                        QMessageBox.information(login, "OK", "Admin created; verification email sent. You can now sign in")
                except Exception as e:
                    logger.error(f"Error during registration: {e}")
                    QMessageBox.critical(login, "Error", "An error occurred during registration")

            login.login_btn.clicked.connect(attempt_login)
            login.register_btn.clicked.connect(attempt_register)

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
