# DentaLink QSS Theme Stylesheets & Configuration Manager
import json
import os
import sys

DARK_STYLESHEET = """
QMainWindow {
    background-color: #101010;
}
QDialog {
    background-color: #161616;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #E2E8F0;
    font-size: 13px;
}
QFrame#Sidebar {
    background-color: #161616;
    border-right: 1px solid #2D2D30;
}
QLabel#SidebarTitle {
    color: #38BDF8;
    font-size: 18px;
    font-weight: bold;
    padding: 8px 12px;
    border: 1px solid #2D2D30;
    border-radius: 6px;
    background-color: #1a2032;
    margin-bottom: 10px;
}
QLabel#SidebarTitle:hover {
    color: #60A5FA;
    background-color: #26314f;
    border: 1px solid #38BDF8;
}
QPushButton#SidebarBtn {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 8px;
    padding: 12px 15px;
    text-align: left;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#SidebarBtn:hover {
    background-color: #1a2032;
    color: #E2E8F0;
}
QPushButton#SidebarBtn:checked {
    background-color: #0371bb;
    color: white;
}
QStackedWidget {
    background-color: #101010;
}
QTableWidget {
    background-color: #161616;
    border: 1px solid #2D2D30;
    gridline-color: #2D2D30;
    border-radius: 10px;
    color: #E2E8F0;
}
QTableWidget::item:selected {
    background-color: #1a2032;
    color: #0371bb;
}
QHeaderView::section {
    background-color: #1a2032;
    color: #94A3B8;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #2D2D30;
    font-weight: bold;
}
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background-color: #1a2032;
    border: 1px solid #2D2D30;
    border-radius: 6px;
    padding: 6px 10px;
    color: white;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1.5px solid #0371bb;
}
QPushButton {
    background-color: #1a2032;
    border: 1px solid #2D2D30;
    border-radius: 8px;
    padding: 8px 16px;
    color: white;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #26314f;
}
QPushButton#PrimaryBtn {
    background-color: #0371bb;
    border: none;
    color: white;
}
QPushButton#PrimaryBtn:hover {
    background-color: #025c99;
}
QPushButton#SuccessBtn {
    background-color: #10B981;
    border: none;
    color: white;
}
QPushButton#SuccessBtn:hover {
    background-color: #059669;
}
QTabWidget::pane {
    border: 1px solid #2D2D30;
    background-color: #161616;
    border-radius: 10px;
}
QTabBar::tab {
    background-color: #1a2032;
    color: #94A3B8;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}
QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: #161616;
    color: white;
}
QGroupBox {
    border: 1px solid #2D2D30;
    border-radius: 10px;
    margin-top: 15px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #0371bb;
}
QFrame#PatientBanner {
    background-color: #161616;
    border: 1px solid #2D2D30;
    border-radius: 10px;
}
QLabel#PatientBannerTitle {
    color: #0371bb;
}
QScrollArea, QScrollArea > QWidget > QWidget {
    background-color: transparent;
    border: none;
}
QPushButton#XrayListItem {
    background-color: #1a2032;
    color: #E2E8F0;
    border: 1px solid #2D2D30;
    border-radius: 8px;
    padding: 8px;
    text-align: left;
    font-size: 11px;
}
QPushButton#XrayListItem:hover {
    background-color: #26314f;
}
QLabel#XrayDisplayLabel {
    background-color: #161616;
    border: 2px dashed #2D2D30;
    border-radius: 10px;
    color: #64748B;
    font-size: 13px;
}
QLabel#SettingsLogoPreview {
    border: 1px dashed #2D2D30;
    border-radius: 8px;
    background-color: #161616;
}
QScrollBar:vertical {
    background-color: #101010;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #2D2D30;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background-color: #0371bb;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
QScrollBar:horizontal {
    background-color: #101010;
    height: 10px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background-color: #2D2D30;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #0371bb;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}
"""

LIGHT_STYLESHEET = """
QMainWindow {
    background-color: #EEEEEE;
}
QDialog {
    background-color: #FFFFFF;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #0F172A;
    font-size: 13px;
}
QFrame#Sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #CBD5E1;
}
QFrame#Sidebar QWidget {
    color: #475569;
}
QFrame#Sidebar QLabel#SidebarTitle {
    color: #0371bb;
    font-size: 18px;
    font-weight: bold;
    padding: 8px 12px;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    background-color: #F1F5F9;
    margin-bottom: 10px;
}
QFrame#Sidebar QLabel#SidebarTitle:hover {
    color: #025c99;
    background-color: #E2E8F0;
    border: 1px solid #0371bb;
}
QFrame#Sidebar QPushButton#SidebarBtn {
    background-color: transparent;
    color: #475569;
    border: none;
    border-radius: 8px;
    padding: 12px 15px;
    text-align: left;
    font-size: 13px;
    font-weight: bold;
}
QFrame#Sidebar QPushButton#SidebarBtn:hover {
    background-color: #EEEEEE;
    color: #0F172A;
}
QFrame#Sidebar QPushButton#SidebarBtn:checked {
    background-color: #0371bb;
    color: white;
}
QStackedWidget {
    background-color: #EEEEEE;
}
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    gridline-color: #D1D5DB;
    border-radius: 10px;
    color: #0F172A;
}
QTableWidget::item:selected {
    background-color: #E5E7EB;
    color: #0371bb;
}
QHeaderView::section {
    background-color: #F3F4F6;
    color: #475569;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #D1D5DB;
    font-weight: bold;
}
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 10px;
    color: #0F172A;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1.5px solid #0371bb;
}
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 16px;
    color: #0F172A;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #F3F4F6;
}
QPushButton#PrimaryBtn {
    background-color: #0371bb;
    border: none;
    color: white;
}
QPushButton#PrimaryBtn:hover {
    background-color: #025c99;
}
QPushButton#SuccessBtn {
    background-color: #10B981;
    border: none;
    color: white;
}
QPushButton#SuccessBtn:hover {
    background-color: #059669;
}
QTabWidget::pane {
    border: 1px solid #D1D5DB;
    background-color: #FFFFFF;
    border-radius: 10px;
}
QTabBar::tab {
    background-color: #E5E7EB;
    color: #475569;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}
QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: #FFFFFF;
    color: #0F172A;
}
QGroupBox {
    border: 1px solid #D1D5DB;
    border-radius: 10px;
    margin-top: 15px;
    font-weight: bold;
    color: #0F172A;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #0371bb;
}
QFrame#PatientBanner {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 10px;
}
QLabel#PatientBannerTitle {
    color: #0371bb;
}
QScrollArea, QScrollArea > QWidget > QWidget {
    background-color: transparent;
    border: none;
}
QPushButton#XrayListItem {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px;
    text-align: left;
    font-size: 11px;
}
QPushButton#XrayListItem:hover {
    background-color: #F3F4F6;
}
QLabel#XrayDisplayLabel {
    background-color: #FFFFFF;
    border: 2px dashed #CBD5E1;
    border-radius: 10px;
    color: #475569;
    font-size: 13px;
}
QLabel#SettingsLogoPreview {
    border: 1px dashed #CBD5E1;
    border-radius: 8px;
    background-color: #FFFFFF;
}
QScrollBar:vertical {
    background-color: #EEEEEE;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #CBD5E1;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background-color: #0371bb;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
QScrollBar:horizontal {
    background-color: #EEEEEE;
    height: 10px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background-color: #CBD5E1;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #0371bb;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}
"""


def detect_system_theme():
    """Detects whether the host Windows system theme is Dark or Light.
    
    On Windows 10/11, queries the Personalization Registry (AppsUseLightTheme / SystemUsesLightTheme).
    On Windows 7 and 8/8.1 (which lack a native Dark/Light toggle), gracefully falls back to 'dark'.
    
    Returns 'dark' or 'light'.
    """
    if sys.platform == "win32":
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "light" if val == 1 else "dark"
        except Exception:
            try:
                import winreg
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    val, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
                    return "light" if val == 1 else "dark"
            except Exception:
                pass

    return "dark"


def get_system_color_scheme():
    """Retrieves system theme mode and accent color scheme for Windows systems (7, 8, 8.1, 10, 11).
    
    - Windows 10/11: Retrieves Light/Dark theme mode, Explorer Accent Color, DWM Colorization, and High Contrast.
    - Windows 7/8/8.1: Retrieves DWM Aero Colorization accent color and High Contrast mode.
    
    Returns a dictionary:
    {
        'theme': 'dark' | 'light',
        'accent_color': '#RRGGBB',
        'is_high_contrast': bool,
        'supported_system': bool,
        'os_version': str
    }
    """
    theme = detect_system_theme()
    accent_color = "#0371bb"  # Default DentaLink primary accent color
    is_high_contrast = False
    supported_system = (sys.platform == "win32")
    os_version = "Non-Windows"

    if sys.platform == "win32":
        try:
            win_ver = sys.getwindowsversion()
            if win_ver.major >= 10:
                os_version = f"Windows {win_ver.major}+ (Build {win_ver.build})"
            elif win_ver.major == 6 and win_ver.minor == 1:
                os_version = "Windows 7"
            elif win_ver.major == 6 and win_ver.minor == 2:
                os_version = "Windows 8"
            elif win_ver.major == 6 and win_ver.minor == 3:
                os_version = "Windows 8.1"
            else:
                os_version = f"Windows {win_ver.major}.{win_ver.minor}"
        except Exception:
            os_version = "Windows"

        try:
            import winreg
            # 1. High contrast status (supported on Windows 7, 8, 8.1, 10, 11)
            try:
                hkcu_hc = r"Control Panel\Accessibility\HighContrast"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, hkcu_hc) as key:
                    flags, _ = winreg.QueryValueEx(key, "Flags")
                    if str(flags) == "1":
                        is_high_contrast = True
            except Exception:
                pass

            # 2. Explorer Accent color (Windows 10/11 AccentColorMenu - ABGR format)
            try:
                acc_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, acc_key) as key:
                    val, _ = winreg.QueryValueEx(key, "AccentColorMenu")
                    r = val & 0xFF
                    g = (val >> 8) & 0xFF
                    b = (val >> 16) & 0xFF
                    accent_color = f"#{r:02x}{g:02x}{b:02x}"
            except Exception:
                # 3. DWM ColorizationColor (Supported on Windows 7 Aero, Windows 8, and Windows 10/11 - ARGB format)
                try:
                    dwm_key = r"Software\Microsoft\Windows\DWM"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, dwm_key) as key:
                        val, _ = winreg.QueryValueEx(key, "ColorizationColor")
                        r = (val >> 16) & 0xFF
                        g = (val >> 8) & 0xFF
                        b = val & 0xFF
                        accent_color = f"#{r:02x}{g:02x}{b:02x}"
                except Exception:
                    pass
        except Exception:
            pass

    return {
        "theme": theme,
        "accent_color": accent_color,
        "is_high_contrast": is_high_contrast,
        "supported_system": supported_system,
        "os_version": os_version
    }




def resolve_theme_name(theme_name=None):
    """Resolves setting theme_name ('system', 'light', 'dark', 'classic') to actual theme 'dark' or 'light'."""
    if not theme_name or theme_name == "system":
        return detect_system_theme()
    if theme_name == "light":
        return "light"
    return "dark"


def load_theme_setting():
    """Loads active theme from configuration file. Defaults to 'system'."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return data.get("theme", "system")
        except Exception:
            pass
    return "system"


def save_theme_setting(theme_name):
    """Saves active theme to configuration file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings_config.json")
    try:
        with open(config_path, "w") as f:
            json.dump({"theme": theme_name}, f)
    except Exception:
        pass


def get_theme_stylesheet(theme_name="system"):
    """Returns corresponding QSS stylesheet for given theme name setting ('system', 'light', or 'dark')."""
    resolved = resolve_theme_name(theme_name)
    stylesheet = LIGHT_STYLESHEET if resolved == "light" else DARK_STYLESHEET
    if theme_name == "system":
        sys_scheme = get_system_color_scheme()
        acc = sys_scheme.get("accent_color")
        if acc and acc.startswith("#") and len(acc) == 7 and acc.lower() != "#0371bb":
            stylesheet = stylesheet.replace("#0371bb", acc)
    return stylesheet

