# DentaLink QSS Theme Stylesheets & Configuration Manager
import json
import os

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


def load_theme_setting():
    """Loads active theme from configuration file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return data.get("theme", "classic")
        except Exception:
            pass
    return "classic"


def save_theme_setting(theme_name):
    """Saves active theme to configuration file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings_config.json")
    try:
        with open(config_path, "w") as f:
            json.dump({"theme": theme_name}, f)
    except Exception:
        pass


def get_theme_stylesheet(theme_name):
    """Returns corresponding QSS stylesheet for given theme name."""
    if theme_name == "light":
        return LIGHT_STYLESHEET
    else:
        return DARK_STYLESHEET
