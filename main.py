# DentaLink Native Patient Management Desktop Application (main.py)
"""
Application Main Entry Point & Component Facade.
"""

import os
import sys
import traceback

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QDialog

import database
from gui.components.clickable_label import ClickableLabel
from gui.components.file_uploader import FileUploaderWidget
from gui.components.icon_helpers import create_sidebar_toggle_icon
from gui.dialogs.admin_auth_dialog import AdminAuthDialog
from gui.dialogs.first_launch_dialog import FirstLaunchSetupDialog
from gui.dialogs.forgot_password_dialog import ForgotPasswordDialog
from gui.dialogs.treatment_done_dialog import ViewTreatmentDoneDialog
from gui.dialogs.universal_key_dialog import UniversalKeyDisplayDialog
from gui.dialogs.version_history_dialog import FullVersionHistoryDialog
from gui.login_window import LoginWindow
from gui.main_window import DentaLinkMainWindow
from gui.styles import (
    DARK_STYLESHEET,
    LIGHT_STYLESHEET,
    get_theme_stylesheet,
    load_theme_setting,
    save_theme_setting,
)


def crash_exception_hook(exctype, value, tb):
    """Global unhandled exception hook logging crashes to crash.log."""
    with open("crash.log", "w") as f:
        traceback.print_exception(exctype, value, tb, file=f)
    sys.__excepthook__(exctype, value, tb)


sys.excepthook = crash_exception_hook


def main():
    """Main application runner."""
    try:
        if "--initialize-db" in sys.argv:
            database.initialize_database()
            print("Database initialized successfully via CLI flag.")
            return

        app = QApplication(sys.argv)
        if os.path.exists("app_icon.ico"):
            app.setWindowIcon(QIcon("app_icon.ico"))
        elif os.path.exists("_internal/app_icon.ico"):
            app.setWindowIcon(QIcon("_internal/app_icon.ico"))

        database.initialize_database()

        default_login = {}
        if not database.has_clinics() or not database.has_doctors():
            start_step = 2 if (database.has_clinics() and not database.has_doctors()) else 1
            setup_dialog = FirstLaunchSetupDialog(start_step=start_step)
            if setup_dialog.exec() == QDialog.DialogCode.Accepted:
                default_login['username'] = setup_dialog.saved_doctor_username or setup_dialog.saved_admin_username
                default_login['password'] = setup_dialog.saved_doctor_password or setup_dialog.saved_admin_password
            else:
                sys.exit(0)

        login = LoginWindow(default_login.get('username', ''), default_login.get('password', ''))
        if login.exec() == QDialog.DialogCode.Accepted:
            window = DentaLinkMainWindow(login.logged_in_session)
            window.show()
            sys.exit(app.exec())
        else:
            sys.exit(0)
    except Exception as e:
        with open("crash.log", "w") as f:
            traceback.print_exc(file=f)
        raise e


if __name__ == "__main__":
    main()
