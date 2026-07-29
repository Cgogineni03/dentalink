# DentaLink QSS Theme Stylesheets & Configuration Manager (Libadwaita / System Theme Edition)
import json
import os
import subprocess
import time
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette

# Map of system accent colors (e.g. GNOME 47 / Libadwaita / KDE Plasma standard accent names)
ACCENT_PRESETS = {
    "blue": {
        "dark_primary": "#3584E4", "dark_hover": "#1C71D8",
        "light_primary": "#1C71D8", "light_hover": "#1553A4"
    },
    "teal": {
        "dark_primary": "#2190A4", "dark_hover": "#186F7F",
        "light_primary": "#0A7B83", "light_hover": "#06595F"
    },
    "green": {
        "dark_primary": "#3A944A", "dark_hover": "#2C7339",
        "light_primary": "#26A269", "light_hover": "#1D7B4F"
    },
    "yellow": {
        "dark_primary": "#E5A50A", "dark_hover": "#B88407",
        "light_primary": "#D48200", "light_hover": "#A76600"
    },
    "orange": {
        "dark_primary": "#ED5B00", "dark_hover": "#BF4900",
        "light_primary": "#E66100", "light_hover": "#B34B00"
    },
    "red": {
        "dark_primary": "#E62E00", "dark_hover": "#B82500",
        "light_primary": "#C01C28", "light_hover": "#981620"
    },
    "pink": {
        "dark_primary": "#D56199", "dark_hover": "#A84A78",
        "light_primary": "#D13B82", "light_hover": "#A62B65"
    },
    "purple": {
        "dark_primary": "#9141AC", "dark_hover": "#73328A",
        "light_primary": "#78281F", "light_hover": "#5E1F18"
    },
    "slate": {
        "dark_primary": "#6E7A85", "dark_hover": "#545E67",
        "light_primary": "#5E6C79", "light_hover": "#48545F"
    }
}

DARK_STYLESHEET_TEMPLATE = """
QMainWindow {{
    background-color: #202020;
}}
QDialog {{
    background-color: #282828;
}}
QWidget {{
    font-family: 'Ubuntu', 'Cantarell', 'Inter', 'Liberation Sans', 'DejaVu Sans', sans-serif;
    color: #FFFFFF;
    font-size: 13px;
}}
QFrame#Sidebar {{
    background-color: #242424;
    border-right: 1px solid #383838;
}}
QLabel#SidebarTitle {{
    color: {ACCENT_PRIMARY};
    font-size: 18px;
    font-weight: bold;
    padding: 10px 14px;
    border: 1px solid #383838;
    border-radius: 8px;
    background-color: #2D2D2D;
    margin-bottom: 12px;
}}
QLabel#SidebarTitle:hover {{
    color: {ACCENT_PRIMARY};
    background-color: #353535;
    border: 1px solid {ACCENT_PRIMARY};
}}
QPushButton#SidebarBtn {{
    background-color: transparent;
    color: #C0C0C0;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#SidebarBtn:hover {{
    background-color: #303030;
    color: #FFFFFF;
}}
QPushButton#SidebarBtn:checked {{
    background-color: {ACCENT_PRIMARY};
    color: #FFFFFF;
    font-weight: bold;
}}
QPushButton#SidebarBtn:checked:hover {{
    background-color: {ACCENT_HOVER};
    color: #FFFFFF;
    font-weight: bold;
}}
QStackedWidget {{
    background-color: #202020;
}}
QTableWidget {{
    background-color: #2A2A2A;
    border: 1px solid #383838;
    gridline-color: #383838;
    border-radius: 10px;
    color: #FFFFFF;
    selection-background-color: {ACCENT_PRIMARY};
    selection-color: #FFFFFF;
}}
QTableWidget::item:selected {{
    background-color: {ACCENT_PRIMARY};
    color: #FFFFFF;
}}
QHeaderView::section {{
    background-color: #303030;
    color: #C0C0C0;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #383838;
    font-weight: bold;
}}
QLineEdit, QTextEdit, QComboBox, QDateEdit {{
    background-color: #303030;
    border: 1px solid #383838;
    border-radius: 8px;
    padding: 6px 12px;
    color: #FFFFFF;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
    border: 2px solid {ACCENT_PRIMARY};
}}
QPushButton {{
    background-color: #303030;
    border: 1px solid #383838;
    border-radius: 8px;
    padding: 8px 16px;
    color: #FFFFFF;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: #3A3A3A;
    border-color: #454545;
}}
QPushButton#PrimaryBtn {{
    background-color: {ACCENT_PRIMARY};
    border: none;
    color: #FFFFFF;
}}
QPushButton#PrimaryBtn:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton#SuccessBtn {{
    background-color: #2EC27E;
    border: none;
    color: #FFFFFF;
}}
QPushButton#SuccessBtn:hover {{
    background-color: #26A269;
}}
QTabWidget::pane {{
    border: 1px solid #383838;
    background-color: #282828;
    border-radius: 10px;
}}
QTabBar::tab {{
    background-color: #303030;
    color: #C0C0C0;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}}
QTabBar::tab:selected, QTabBar::tab:hover {{
    background-color: #282828;
    color: #FFFFFF;
    border-bottom: 2px solid {ACCENT_PRIMARY};
}}
QGroupBox {{
    border: 1px solid #383838;
    border-radius: 10px;
    margin-top: 15px;
    font-weight: bold;
    background-color: #262626;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {ACCENT_PRIMARY};
}}
QFrame#PatientBanner {{
    background-color: #282828;
    border: 1px solid #383838;
    border-radius: 10px;
}}
QLabel#PatientBannerTitle {{
    color: {ACCENT_PRIMARY};
}}
QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: transparent;
    border: none;
}}
QPushButton#XrayListItem {{
    background-color: #303030;
    color: #FFFFFF;
    border: 1px solid #383838;
    border-radius: 8px;
    padding: 8px;
    text-align: left;
    font-size: 11px;
}}
QPushButton#XrayListItem:hover {{
    background-color: #3A3A3A;
}}
QLabel#XrayDisplayLabel {{
    background-color: #242424;
    border: 2px dashed #383838;
    border-radius: 10px;
    color: #9A9996;
    font-size: 13px;
}}
QLabel#SettingsLogoPreview {{
    border: 1px dashed #383838;
    border-radius: 8px;
    background-color: #242424;
}}
QScrollBar:vertical {{
    background-color: #202020;
    width: 10px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background-color: #3E3E3E;
    min-height: 24px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {ACCENT_PRIMARY};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
}}
QScrollBar:horizontal {{
    background-color: #202020;
    height: 10px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background-color: #3E3E3E;
    min-width: 24px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {ACCENT_PRIMARY};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    border: none;
    background: none;
}}
"""

LIGHT_STYLESHEET_TEMPLATE = """
QMainWindow {{
    background-color: #F6F6F6;
}}
QDialog {{
    background-color: #FFFFFF;
}}
QWidget {{
    font-family: 'Ubuntu', 'Cantarell', 'Inter', 'Liberation Sans', 'DejaVu Sans', sans-serif;
    color: #2E3436;
    font-size: 13px;
}}
QFrame#Sidebar {{
    background-color: #F8F9FA;
    border-right: 1px solid #E2E8F0;
}}
QFrame#Sidebar QWidget {{
    color: #475569;
}}
QFrame#Sidebar QLabel#SidebarTitle {{
    color: {ACCENT_PRIMARY};
    font-size: 18px;
    font-weight: bold;
    padding: 10px 14px;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    background-color: #FFFFFF;
    margin-bottom: 12px;
}}
QFrame#Sidebar QLabel#SidebarTitle:hover {{
    color: {ACCENT_HOVER};
    background-color: #F1F5F9;
    border: 1px solid {ACCENT_PRIMARY};
}}
QFrame#Sidebar QPushButton#SidebarBtn {{
    background-color: transparent;
    color: #475569;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}}
QFrame#Sidebar QPushButton#SidebarBtn:hover {{
    background-color: #E2E8F0;
    color: #0F172A;
}}
QFrame#Sidebar QPushButton#SidebarBtn:checked {{
    background-color: {ACCENT_PRIMARY};
    color: #FFFFFF;
    font-weight: bold;
}}
QFrame#Sidebar QPushButton#SidebarBtn:checked:hover {{
    background-color: {ACCENT_HOVER};
    color: #FFFFFF;
    font-weight: bold;
}}
QStackedWidget {{
    background-color: #F6F6F6;
}}
QTableWidget {{
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    gridline-color: #E0E0E0;
    border-radius: 10px;
    color: #2E3436;
    selection-background-color: {ACCENT_PRIMARY};
    selection-color: #FFFFFF;
}}
QTableWidget::item:selected {{
    background-color: {ACCENT_PRIMARY};
    color: #FFFFFF;
}}
QHeaderView::section {{
    background-color: #F0F0F0;
    color: #5E5C64;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #E0E0E0;
    font-weight: bold;
}}
QLineEdit, QTextEdit, QComboBox, QDateEdit {{
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 6px 12px;
    color: #2E3436;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
    border: 2px solid {ACCENT_PRIMARY};
}}
QPushButton {{
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 8px 16px;
    color: #2E3436;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: #F0F0F0;
}}
QPushButton#PrimaryBtn {{
    background-color: {ACCENT_PRIMARY};
    border: none;
    color: #FFFFFF;
}}
QPushButton#PrimaryBtn:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton#SuccessBtn {{
    background-color: #26A269;
    border: none;
    color: #FFFFFF;
}}
QPushButton#SuccessBtn:hover {{
    background-color: #1D7B4F;
}}
QTabWidget::pane {{
    border: 1px solid #E0E0E0;
    background-color: #FFFFFF;
    border-radius: 10px;
}}
QTabBar::tab {{
    background-color: #F0F0F0;
    color: #5E5C64;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}}
QTabBar::tab:selected, QTabBar::tab:hover {{
    background-color: #FFFFFF;
    color: #2E3436;
    border-bottom: 2px solid {ACCENT_PRIMARY};
}}
QGroupBox {{
    border: 1px solid #E0E0E0;
    border-radius: 10px;
    margin-top: 15px;
    font-weight: bold;
    color: #2E3436;
    background-color: #FFFFFF;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {ACCENT_PRIMARY};
}}
QFrame#PatientBanner {{
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 10px;
}}
QLabel#PatientBannerTitle {{
    color: {ACCENT_PRIMARY};
}}
QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: transparent;
    border: none;
}}
QPushButton#XrayListItem {{
    background-color: #FFFFFF;
    color: #2E3436;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 8px;
    text-align: left;
    font-size: 11px;
}}
QPushButton#XrayListItem:hover {{
    background-color: #F0F0F0;
}}
QLabel#XrayDisplayLabel {{
    background-color: #FFFFFF;
    border: 2px dashed #E0E0E0;
    border-radius: 10px;
    color: #5E5C64;
    font-size: 13px;
}}
QLabel#SettingsLogoPreview {{
    border: 1px dashed #E0E0E0;
    border-radius: 8px;
    background-color: #FFFFFF;
}}
QScrollBar:vertical {{
    background-color: #F6F6F6;
    width: 10px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background-color: #D0D0D0;
    min-height: 24px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {ACCENT_PRIMARY};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
}}
QScrollBar:horizontal {{
    background-color: #F6F6F6;
    height: 10px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background-color: #D0D0D0;
    min-width: 24px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {ACCENT_PRIMARY};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    border: none;
    background: none;
}}
"""

DARK_STYLESHEET = DARK_STYLESHEET_TEMPLATE.format(ACCENT_PRIMARY="#3584E4", ACCENT_HOVER="#1C71D8")
LIGHT_STYLESHEET = LIGHT_STYLESHEET_TEMPLATE.format(ACCENT_PRIMARY="#1C71D8", ACCENT_HOVER="#1553A4")


def adjust_color_lightness(hex_color, factor):
    """Adjusts color lightness by a multiplier (e.g. 0.85 for 15% darker)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            r = max(0, min(255, int(r * factor)))
            g = max(0, min(255, int(g * factor)))
            b = max(0, min(255, int(b * factor)))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            pass
    return f"#{hex_color}"


def detect_system_theme():
    """
    Detects active system theme (light/dark) across all Linux Desktop Environments
    and UI Toolkits (GTK, Qt, KDE Plasma, XFCE, LXQt, Freedesktop Portal, etc.).
    """
    desktop_env = (os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION") or "").lower()

    # Priority 1: XDG Freedesktop Portal DBus API (Standard across KDE, GNOME, XFCE, LXQt, etc.)
    try:
        res = subprocess.run(
            ["dbus-send", "--session", "--print-reply",
             "--dest=org.freedesktop.portal.Desktop",
             "/org/freedesktop/portal/desktop",
             "org.freedesktop.portal.Settings.Read",
             "string:org.freedesktop.appearance",
             "string:color-scheme"],
            capture_output=True, text=True, timeout=1
        )
        out = res.stdout.strip()
        if "uint32 1" in out:
            return "dark"
        elif "uint32 2" in out or "uint32 0" in out:
            return "light"
    except Exception:
        pass

    # Priority 2: KDE Plasma / Qt Environments
    if any(k in desktop_env for k in ["kde", "plasma", "lxqt", "qt"]):
        # Check KDE kreadconfig6 / kreadconfig5
        for tool in ["kreadconfig6", "kreadconfig5"]:
            try:
                res = subprocess.run(
                    [tool, "--group", "Colors:Window", "--key", "BackgroundNormal"],
                    capture_output=True, text=True, timeout=1
                )
                rgb_str = res.stdout.strip()
                if rgb_str:
                    parts = [int(c) for c in rgb_str.split(",") if c.strip().isdigit()]
                    if len(parts) >= 3:
                        lum = 0.2126 * parts[0] + 0.7152 * parts[1] + 0.0722 * parts[2]
                        return "dark" if lum < 128 else "light"
            except Exception:
                pass

        # Check ~/.config/kdeglobals directly
        kdeglobals = os.path.expanduser("~/.config/kdeglobals")
        if os.path.exists(kdeglobals):
            try:
                with open(kdeglobals, "r") as f:
                    content = f.read()
                    if "[Colors:Window]" in content:
                        for line in content.splitlines():
                            if line.startswith("BackgroundNormal="):
                                vals = line.split("=")[1].split(",")
                                if len(vals) >= 3:
                                    r, g, b = int(vals[0]), int(vals[1]), int(vals[2])
                                    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
                                    return "dark" if lum < 128 else "light"
            except Exception:
                pass

    # Priority 3: GNOME / GTK-based environments (GNOME, Cinnamon, MATE, XFCE)
    try:
        res = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True, text=True, timeout=1
        )
        out = res.stdout.strip().strip("'\"").lower()
        if any(d in out for d in ["dark", "prefer-dark"]):
            return "dark"
        elif any(l in out for l in ["light", "prefer-light", "default"]):
            return "light"
    except Exception:
        pass

    try:
        res = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            capture_output=True, text=True, timeout=1
        )
        out = res.stdout.strip().strip("'\"").lower()
        if "dark" in out:
            return "dark"
        else:
            return "light"
    except Exception:
        pass

    # Priority 4: Qt Application System Palette Luminance (Toolkit level fallback)
    try:
        app = QApplication.instance()
        if app:
            win_color = app.palette().color(QPalette.ColorRole.Window)
            r, g, b = win_color.red(), win_color.green(), win_color.blue()
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
            return "dark" if luminance < 128 else "light"
    except Exception:
        pass

    return "light"


def detect_system_gtk_theme():
    """Alias for backwards compatibility."""
    return detect_system_theme()


def detect_system_accent_colors(effective_theme):
    """
    Detects active system accent color (primary & hover hex) across GTK, Qt, KDE, and system palettes.
    """
    # 1. KDE Plasma accent color from ~/.config/kdeglobals
    kdeglobals = os.path.expanduser("~/.config/kdeglobals")
    if os.path.exists(kdeglobals):
        try:
            with open(kdeglobals, "r") as f:
                content = f.read()
                if "AccentColor=" in content:
                    for line in content.splitlines():
                        if line.startswith("AccentColor="):
                            vals = line.split("=")[1].split(",")
                            if len(vals) >= 3:
                                r, g, b = int(vals[0]), int(vals[1]), int(vals[2])
                                primary_hex = f"#{r:02x}{g:02x}{b:02x}"
                                hover_hex = adjust_color_lightness(primary_hex, 0.85 if effective_theme == "dark" else 1.15)
                                return primary_hex, hover_hex
        except Exception:
            pass

    # 2. GNOME 47 / GTK accent-color setting
    try:
        res = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "accent-color"],
            capture_output=True, text=True, timeout=1
        )
        name = res.stdout.strip().strip("'\"").lower()
        if name in ACCENT_PRESETS:
            preset = ACCENT_PRESETS[name]
            if effective_theme == "dark":
                return preset["dark_primary"], preset["dark_hover"]
            else:
                return preset["light_primary"], preset["light_hover"]
    except Exception:
        pass

    # 3. Qt System Palette Highlight Color
    try:
        app = QApplication.instance()
        if app:
            hl = app.palette().color(QPalette.ColorRole.Highlight)
            if hl.isValid() and hl.name() not in ["#000000", "#ffffff"]:
                primary_hex = hl.name()
                hover_hex = adjust_color_lightness(primary_hex, 0.85 if effective_theme == "dark" else 1.15)
                return primary_hex, hover_hex
    except Exception:
        pass

    # Fallback default Libadwaita / Qt Blue accent
    if effective_theme == "dark":
        return "#3584E4", "#1C71D8"
    else:
        return "#1C71D8", "#1553A4"


def get_effective_theme_name(theme_name):
    """Returns effective theme string ('dark' or 'light') for a given theme setting name."""
    if not theme_name or theme_name == "system" or theme_name == "classic":
        return detect_system_theme()
    return theme_name


def get_user_config_path():
    """Returns absolute path to configuration file in user config directory (~/.config/dentalink/)."""
    config_home = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    app_config_dir = os.path.join(config_home, "dentalink")
    try:
        os.makedirs(app_config_dir, exist_ok=True)
    except Exception:
        pass
    return os.path.join(app_config_dir, "settings_config.json")


def load_theme_setting():
    """Loads active theme setting ('system', 'light', 'dark') from configuration file."""
    user_config = get_user_config_path()
    paths_to_check = [
        user_config,
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings_config.json"),
        "settings_config.json",
    ]
    for config_path in paths_to_check:
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    val = data.get("theme", "system")
                    if val in ["system", "light", "dark"]:
                        return val
                    elif val == "classic":
                        return "system"
            except Exception:
                pass
    return "system"


def save_theme_setting(theme_name):
    """Saves active theme setting to configuration file."""
    config_path = get_user_config_path()
    try:
        with open(config_path, "w") as f:
            json.dump({"theme": theme_name}, f)
    except Exception:
        pass

    # Also sync workspace local settings_config.json if present
    try:
        local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings_config.json")
        with open(local_path, "w") as f:
            json.dump({"theme": theme_name}, f)
    except Exception:
        pass


def get_theme_stylesheet(theme_name="system"):
    """Returns corresponding QSS stylesheet for given theme name with system accent color integration."""
    effective_theme = get_effective_theme_name(theme_name)
    primary_accent, hover_accent = detect_system_accent_colors(effective_theme)

    if effective_theme == "light":
        return LIGHT_STYLESHEET_TEMPLATE.format(ACCENT_PRIMARY=primary_accent, ACCENT_HOVER=hover_accent)
    else:
        return DARK_STYLESHEET_TEMPLATE.format(ACCENT_PRIMARY=primary_accent, ACCENT_HOVER=hover_accent)


class SystemThemeMonitor(QThread):
    """Background thread monitoring system GTK/Qt/desktop theme and accent changes."""
    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.proc = None
        self.last_theme_state = None

    def run(self):
        # Attempt to run gsettings monitor
        try:
            self.proc = subprocess.Popen(
                ["gsettings", "monitor", "org.gnome.desktop.interface"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        except Exception:
            self.proc = None

        self.last_theme_state = (detect_system_theme(), detect_system_accent_colors(detect_system_theme()))

        while self.running:
            if self.proc and self.proc.stdout:
                try:
                    line = self.proc.stdout.readline()
                    if not line:
                        break
                    new_theme = detect_system_theme()
                    new_accents = detect_system_accent_colors(new_theme)
                    current_state = (new_theme, new_accents)
                    if current_state != self.last_theme_state:
                        self.last_theme_state = current_state
                        self.theme_changed.emit(new_theme)
                    continue
                except Exception:
                    break

            # Fallback polling loop (every 3 seconds)
            time.sleep(3)
            new_theme = detect_system_theme()
            new_accents = detect_system_accent_colors(new_theme)
            current_state = (new_theme, new_accents)
            if current_state != self.last_theme_state:
                self.last_theme_state = current_state
                self.theme_changed.emit(new_theme)

    def stop(self):
        self.running = False
        if hasattr(self, 'proc') and self.proc:
            try:
                self.proc.terminate()
                self.proc.kill()
            except Exception:
                pass
        self.quit()
        self.wait(1000)
