import sqlite3
import os

# ✅ قاعدة البيانات ثابتة على سطح المكتب
DB = os.path.join(os.path.expanduser("~"), "Desktop", "library.db")

con = sqlite3.connect(DB)
cur = con.cursor()

# ===================== students =====================
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT,
    department TEXT
)
""")

# ===================== books (مع category) =====================
cur.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT,
    status TEXT DEFAULT 'available'
)
""")

# ===================== loans =====================
cur.execute("""
CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrow_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    return_date TEXT,
    state TEXT DEFAULT 'borrowed',
    FOREIGN KEY(student_id) REFERENCES students(student_id),
    FOREIGN KEY(book_id) REFERENCES books(book_id)
)
""")

# ===================== users =====================
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

con.commit()
con.close()

print("✅ DB created at:", DB)
print("✅ Tables ensured: students, books, loans, users")
