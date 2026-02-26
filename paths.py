import os
import sys

APP_NAME = "LibrarySystem"

def app_data_dir():
    # Windows: %APPDATA%
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path

def resource_path(relative_path: str) -> str:
    # للصور داخل exe
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def db_path() -> str:
    # قاعدة البيانات في AppData
    return os.path.join(app_data_dir(), "library.db")
