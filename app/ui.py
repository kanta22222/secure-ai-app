from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog,
    QListWidget, QCheckBox, QMessageBox, QDialog, QFormLayout, QProgressBar, QProgressBar
)
from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtGui import QIcon
from app.auth import authenticate_user, register_user, list_users, log_activity
from app.models import SessionLocal, FileRecord
from app.file_manager import save_encrypted_file, load_decrypted_file
from app.ai_processor import summarize_text, extract_keywords, analyze_sentiment
from app.file_sharing import share_file
import os

ASSETS_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "src", "assets")

class MainChoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Secure AI App - Choose Login Type")
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)
        layout = QVBoxLayout()

        title = QLabel("Choose Login Type")
        title.setObjectName("title_label")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        btn_layout = QVBoxLayout()
        self.user_btn = QPushButton("User Login")
        self.user_btn.setObjectName("user_login_btn")
        self.admin_btn = QPushButton("Admin Login")
        self.admin_btn.setObjectName("admin_login_btn")
        btn_layout.addWidget(self.user_btn)
        btn_layout.addWidget(self.admin_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

class LoginDialog(QDialog):
    def __init__(self, parent=None, is_admin=False):
        super().__init__(parent)
        self.is_admin = is_admin
        title_text = "Secure AI App - Admin Sign In" if is_admin else "Secure AI App - User Sign In"
        self.setWindowTitle(title_text)
        self.setMinimumWidth(450)
        self.setMinimumHeight(300)
        layout = QVBoxLayout()

        # Logo or title
        title = QLabel(title_text)
        title.setObjectName("title_label")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("Enter username")
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Enter email")
        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.Password)
        self.pw_edit.setPlaceholderText("Enter password")
        self.show_pw_check = QCheckBox("Show Password")
        # Create a horizontal layout for password field and checkbox
        pw_layout = QHBoxLayout()
        pw_layout.addWidget(self.pw_edit)
        pw_layout.addWidget(self.show_pw_check)
        form.addRow("Username:", self.user_edit)
        form.addRow("Email:", self.email_edit)
        form.addRow("Password:", pw_layout)
        layout.addLayout(form)

        self.show_pw_check.stateChanged.connect(self.toggle_password_visibility)

        # Remember me and forgot password
        options_layout = QHBoxLayout()
        self.remember_check = QCheckBox("Remember Me")
        self.forgot_btn = QPushButton("Forgot Password?")
        self.forgot_btn.setStyleSheet("border: none; color: blue; text-decoration: underline;")
        options_layout.addWidget(self.remember_check)

        options_layout.addStretch()
        options_layout.addWidget(self.forgot_btn)
        layout.addLayout(options_layout)

        btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("Back")
        self.back_btn.setObjectName("back_btn")
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("login_btn")
        self.register_btn = QPushButton("Register")
        self.register_btn.setObjectName("register_btn")
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.register_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Connect forgot password
        self.forgot_btn.clicked.connect(self.forgot_password)


    def toggle_password_visibility(self, state):
        if state == Qt.Checked:
            self.pw_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.pw_edit.setEchoMode(QLineEdit.Password)

    def forgot_password(self):
        # Simple placeholder for forgot password functionality
        QMessageBox.information(self, "Forgot Password", "Please contact the administrator to reset your password.")

class AdminDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin — Users")
        self.resize(600, 400)
        layout = QVBoxLayout()
        self.users_list = QListWidget()
        layout.addWidget(self.users_list)
        create_layout = QHBoxLayout()
        self.new_user = QLineEdit()
        self.new_email = QLineEdit()
        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.Password)
        self.admin_check = QCheckBox("is admin")
        self.create_btn = QPushButton("Create")
        create_layout.addWidget(self.new_user)
        create_layout.addWidget(self.new_email)
        create_layout.addWidget(self.new_pw)
        create_layout.addWidget(self.admin_check)
        create_layout.addWidget(self.create_btn)
        layout.addLayout(create_layout)
        self.setLayout(layout)
        self.create_btn.clicked.connect(self.create_user)
        self.refresh()

    def refresh(self):
        self.users_list.clear()
        for u in list_users():
            self.users_list.addItem(f"{u.username} {'(admin)' if u.is_admin else ''}")

    def create_user(self):
        username = self.new_user.text().strip()
        email = self.new_email.text().strip()
        pw = self.new_pw.text().strip()
        is_admin = self.admin_check.isChecked()
        if not username or not pw:
            QMessageBox.warning(self, "Invalid", "username and password required")
            return
        ok, msg = register_user(username, pw, email, is_admin)
        if not ok:
            QMessageBox.warning(self, "Error", msg)
            return
        self.new_user.clear(); self.new_email.clear(); self.new_pw.clear(); self.admin_check.setChecked(False)
        self.refresh()
        QMessageBox.information(self, "OK", "User created")

class Dashboard(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Dashboard — {user.username}")
        self.resize(900, 600)

        layout = QHBoxLayout()
        left = QVBoxLayout()
        right = QVBoxLayout()

        if user.is_admin:
            # Admin Dashboard
            self.setup_admin_dashboard(left, right)
        else:
            # User Dashboard
            self.setup_user_dashboard(left, right)

        layout.addLayout(left, 3)
        layout.addLayout(right, 5)
        self.setLayout(layout)

    def setup_user_dashboard(self, left, right):
        # Upload / process
        self.upload_btn = QPushButton("Upload file")
        self.upload_btn.setObjectName("upload_btn")
        upload_high = os.path.join(ASSETS_DIR, "upload_high.svg")
        upload_icon = os.path.join(ASSETS_DIR, "upload.svg")
        if os.path.exists(upload_high):
            self.upload_btn.setIcon(QIcon(upload_high))
        elif os.path.exists(upload_icon):
            self.upload_btn.setIcon(QIcon(upload_icon))
        self.process_btn = QPushButton("Process selected")
        self.process_btn.setObjectName("process_btn")
        process_high = os.path.join(ASSETS_DIR, "process_high.svg")
        process_icon = os.path.join(ASSETS_DIR, "process.svg")
        if os.path.exists(process_high):
            self.process_btn.setIcon(QIcon(process_high))
        elif os.path.exists(process_icon):
            self.process_btn.setIcon(QIcon(process_icon))

        # set application/window icon if available
        app_icon = os.path.join(ASSETS_DIR, "app_icon.svg")
        if os.path.exists(app_icon):
            self.setWindowIcon(QIcon(app_icon))

        self.files_list = QListWidget()
        left.addWidget(QLabel("Your files"))
        left.addWidget(self.files_list)
        left.addWidget(self.upload_btn)
        left.addWidget(self.process_btn)

        # Delete button
        self.delete_btn = QPushButton("Delete selected")
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        left.addWidget(self.delete_btn)
        self.delete_btn.clicked.connect(self.delete_selected_file)

        # Share button
        self.share_btn = QPushButton("Share selected")
        self.share_btn.setStyleSheet("background-color: #2196F3; color: white;")
        left.addWidget(self.share_btn)
        self.share_btn.clicked.connect(self.share_selected_file)

        # AI output
        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        right.addWidget(QLabel("AI Output"))
        right.addWidget(self.output_view)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right.addWidget(self.progress_bar)

        # add a subtle pulse animation to the upload button
        self.anim = QPropertyAnimation(self.upload_btn, b"geometry")
        self.anim.setDuration(900)
        rect = self.upload_btn.geometry()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(rect.adjusted(-2, -1, 2, 1))
        self.anim.setLoopCount(-1)
        try:
            self.anim.start()
        except Exception:
            pass

        self.upload_btn.clicked.connect(self.upload_file)
        self.process_btn.clicked.connect(self.process_selected)
        self.refresh_files()

    def setup_admin_dashboard(self, left, right):
        # User Management Section
        left.addWidget(QLabel("User Management"))
        self.users_list = QListWidget()
        left.addWidget(self.users_list)

        create_layout = QHBoxLayout()
        self.new_user = QLineEdit()
        self.new_user.setPlaceholderText("Username")
        self.new_email = QLineEdit()
        self.new_email.setPlaceholderText("Email")
        self.new_pw = QLineEdit()
        self.new_pw.setPlaceholderText("Password")
        self.new_pw.setEchoMode(QLineEdit.Password)
        self.admin_check = QCheckBox("Admin")
        self.create_btn = QPushButton("Create User")
        create_layout.addWidget(self.new_user)
        create_layout.addWidget(self.new_email)
        create_layout.addWidget(self.new_pw)
        create_layout.addWidget(self.admin_check)
        create_layout.addWidget(self.create_btn)
        left.addLayout(create_layout)
        self.create_btn.clicked.connect(self.create_user)

        # Activity Logs Section
        right.addWidget(QLabel("Activity Logs"))
        from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel
        self.activity_widget = QWidget()
        self.activity_layout = QGridLayout()
        self.activity_widget.setLayout(self.activity_layout)
        right.addWidget(self.activity_widget)

        # Threat Alerts Section
        right.addWidget(QLabel("Threat Alerts"))
        self.threat_list = QListWidget()
        right.addWidget(self.threat_list)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        right.addWidget(refresh_btn)
        refresh_btn.clicked.connect(self.refresh_admin_data)

        self.refresh_admin_data()

    def refresh_files(self):
        self.files_list.clear()
        db = SessionLocal()
        try:
            rows = db.query(FileRecord).filter(FileRecord.owner == self.user.username).all()
            for r in rows:
                self.files_list.addItem(f"{r.id}: {r.filename} ({r.storage_name})")
        finally:
            db.close()

    def upload_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose file to upload")
        if not path:
            return
        with open(path, "rb") as f:
            data = f.read()
        storage = save_encrypted_file(self.user.username, os.path.basename(path), data)
        db = SessionLocal()
        try:
            rec = FileRecord(filename=os.path.basename(path), owner=self.user.username, storage_name=storage)
            db.add(rec); db.commit()
            log_activity(self.user.id, "file_upload", f"Uploaded file: {rec.filename}")
        finally:
            db.close()
        self.refresh_files()
        QMessageBox.information(self, "Saved", "File uploaded and encrypted.")

    def process_selected(self):
        sel = self.files_list.currentItem()
        if not sel:
            QMessageBox.warning(self, "Select one", "please select a file")
            return
        # parse id from display
        txt = sel.text()
        fid = int(txt.split(":")[0])
        db = SessionLocal()
        try:
            rec = db.query(FileRecord).filter(FileRecord.id == fid).first()
            if not rec:
                QMessageBox.warning(self, "Missing", "Record not found")
                return
            raw = load_decrypted_file(rec.storage_name)
            try:
                text = raw.decode("utf-8", errors="ignore")
            except Exception:
                text = ""
            summary = summarize_text(text, max_sentences=4)
            keywords = extract_keywords(text, num_keywords=8)
            sentiment = analyze_sentiment(text)
            output = f"Summary:\n{summary or '(no text extracted)'}\n\nKeywords:\n{', '.join(keywords)}\n\nSentiment: {sentiment}"
            self.output_view.setPlainText(output)
            log_activity(self.user.id, "file_process", f"Processed file: {rec.filename}")
        finally:
            db.close()

    def open_admin(self):
        dlg = AdminDialog(self)
        dlg.exec()

    def delete_selected_file(self):
        sel = self.files_list.currentItem()
        if not sel:
            QMessageBox.warning(self, "Select one", "please select a file to delete")
            return
        txt = sel.text()
        fid = int(txt.split(":")[0])
        db = SessionLocal()
        try:
            rec = db.query(FileRecord).filter(FileRecord.id == fid).first()
            if not rec:
                QMessageBox.warning(self, "Missing", "Record not found")
                return
            # Delete file from storage
            import os
            storage_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "storage", rec.storage_name)
            if os.path.exists(storage_path):
                os.remove(storage_path)
            # Delete record from DB
            db.delete(rec)
            db.commit()
            log_activity(self.user.id, "file_delete", f"Deleted file: {rec.filename}")
            self.refresh_files()
            QMessageBox.information(self, "Deleted", f"File '{rec.filename}' deleted.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete file: {str(e)}")
        finally:
            db.close()

    def share_selected_file(self):
        sel = self.files_list.currentItem()
        if not sel:
            QMessageBox.warning(self, "Select one", "please select a file to share")
            return
        txt = sel.text()
        fid = int(txt.split(":")[0])
        try:
            msg, error = share_file(fid, self.user.username)
            if error:
                QMessageBox.warning(self, "Error", error)
            else:
                log_activity(self.user.id, "file_share", f"Shared file with ID: {fid}")
                QMessageBox.information(self, "Sharing", msg)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to share file: {str(e)}")

    def refresh_admin_data(self):
        # Refresh users list
        self.users_list.clear()
        for u in list_users():
            self.users_list.addItem(f"{u.username} {'(admin)' if u.is_admin else ''}")

        # Refresh activity logs
        # Clear previous widgets in grid layout
        while self.activity_layout.count():
            item = self.activity_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        db = SessionLocal()
        try:
            from server.models import ActivityLog
            logs = db.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).limit(20).all()

            # Map action types to icons (use placeholder icons or paths)
            icon_map = {
                "file_upload": "upload.svg",
                "file_process": "process.svg",
                "file_delete": "delete.svg",
                "file_share": "share.svg",
                # Add more mappings as needed
            }

            row = 0
            col = 0
            max_cols = 3  # Number of columns in grid

            for log in logs:
                action = log.action
                icon_file = icon_map.get(action, "default.svg")
                icon_path = os.path.join(ASSETS_DIR, icon_file)
                icon_label = QLabel()
                if os.path.exists(icon_path):
                    icon_label.setPixmap(QIcon(icon_path).pixmap(48, 48))
                else:
                    icon_label.setText("Icon")

                text_label = QLabel(f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\nUser: {log.user_id}\nAction: {action}")
                text_label.setWordWrap(True)

                vbox = QVBoxLayout()
                vbox.addWidget(icon_label, alignment=Qt.AlignCenter)
                vbox.addWidget(text_label, alignment=Qt.AlignCenter)

                container = QWidget()
                container.setLayout(vbox)
                container.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")

                self.activity_layout.addWidget(container, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

        except Exception as e:
            error_label = QLabel(f"Error loading logs: {str(e)}")
            self.activity_layout.addWidget(error_label, 0, 0)
        finally:
            db.close()

        # Refresh threat alerts
        self.threat_list.clear()
        db = SessionLocal()
        try:
            from server.models import ThreatDetection
            threats = db.query(ThreatDetection).filter(ThreatDetection.status == 'active').order_by(ThreatDetection.detected_at.desc()).limit(10).all()
            for threat in threats:
                self.threat_list.addItem(f"{threat.detected_at}: File {threat.file_id} - {threat.threat_type} ({threat.confidence}%)")
        except Exception as e:
            self.threat_list.addItem(f"Error loading threats: {str(e)}")
        finally:
            db.close()

    def create_user(self):
        username = self.new_user.text().strip()
        email = self.new_email.text().strip()
        pw = self.new_pw.text().strip()
        is_admin = self.admin_check.isChecked()
        if not username or not pw:
            QMessageBox.warning(self, "Invalid", "username and password required")
            return
        ok, msg = register_user(username, pw, email, is_admin)
        if not ok:
            QMessageBox.warning(self, "Error", msg)
            return
        self.new_user.clear(); self.new_email.clear(); self.new_pw.clear(); self.admin_check.setChecked(False)
        self.refresh_admin_data()
        QMessageBox.information(self, "OK", "User created")
