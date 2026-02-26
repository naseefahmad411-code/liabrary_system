import sqlite3
import os
import sys
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk


# =================== مسار مجلد التطبيق (جنب exe) ===================
def app_dir():
    if getattr(sys, 'frozen', False):
        # exe: جنب ملف التنفيذ
        return os.path.dirname(sys.executable)
    # py: جنب الملف الحالي
    return os.path.dirname(os.path.abspath(__file__))


DB = os.path.join(app_dir(), "library.db")


# =================== مسار الموارد للصور (يعمل في exe و py) ===================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # داخل onefile exe
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))  # تشغيل عادي
    return os.path.join(base_path, relative_path)


# =================== إنشاء الجداول تلقائيًا إذا ناقصة ===================
def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # students
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        department TEXT
    )
    """)

    # books (مع category)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        category TEXT,
        status TEXT DEFAULT 'available'
    )
    """)

    # loans
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

    # users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    con.commit()
    con.close()


class BooksClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry('995x550+50+120')
        self.root.title('Books Management')
        self.root.config(bg='#ffffff')
        self.root.resizable(False, False)

        # ✅ تأكد من وجود DB والجداول
        try:
            init_db()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل تهيئة قاعدة البيانات:\n{e}")
            return

        # =================== صورة في الجانب الأيسر ===================
        img_path = resource_path(os.path.join("images", "tow.png"))

        try:
            self.logo = Image.open(img_path)
            self.logo = self.logo.resize((325, 200))
            self.logo = ImageTk.PhotoImage(self.logo)

            lbl_image = Label(self.root, image=self.logo, bg='#ffffff')
            lbl_image.place(x=5, y=5, width=325, height=200)
        except Exception as ex:
            messagebox.showwarning("Image Warning", f"لم يتم العثور على الصورة أو حدث خطأ:\n{str(ex)}")

        # =================== متغيرات البحث ===================
        self.var_search_by = StringVar()
        self.var_search_txt = StringVar()

        # =================== متغيرات الإدخال ===================
        self.var_id = StringVar()
        self.var_title = StringVar()
        self.var_author = StringVar()
        self.var_category = StringVar()
        self.var_status = StringVar()

        # =================== Frame البحث ===================
        search_frame = LabelFrame(self.root, text='بحث', font=("goudy old style", 12, "bold"),
                                  bd=2, relief=RIDGE, bg='#ffffff')
        search_frame.place(x=370, y=20, width=600, height=70)

        cmb_search = ttk.Combobox(search_frame, textvariable=self.var_search_by,
                                  values=('Select', 'title', 'author', 'category'),
                                  state='readonly', justify=CENTER, font=('tajwal', 15))
        cmb_search.place(x=10, y=10, width=180)
        cmb_search.current(0)

        Entry(search_frame, textvariable=self.var_search_txt, font=('tajwal', 15),
              bg='lightyellow', justify=CENTER).place(x=200, y=10, width=210)

        Button(search_frame, command=self.search, text='بحث', font=('goudy old style', 15),
               bg='#005c78', fg='#ffffff', cursor='hand2').place(x=415, y=9, width=150, height=30)

        # =================== عنوان ===================
        Label(self.root, text='إدارة الكتب', font=('goudy old style', 15),
              bg='#005c78', fg="#ffffff").place(x=340, y=100, width=645)

        # =================== حقول الإدخال ===================
        Label(self.root, text='العنوان', font=('tajwal', 15), bg='white').place(x=940, y=145)
        Label(self.root, text='المؤلف', font=('tajwal', 15), bg='white').place(x=710, y=145)
        Label(self.root, text='التصنيف', font=('tajwal', 15), bg='white').place(x=500, y=145)

        Entry(self.root, textvariable=self.var_title, font=('tajwal', 15),
              bg='lightyellow', justify=CENTER).place(x=780, y=150, width=150)
        Entry(self.root, textvariable=self.var_author, font=('tajwal', 15),
              bg='lightyellow', justify=CENTER).place(x=550, y=150, width=150)
        Entry(self.root, textvariable=self.var_category, font=('tajwal', 15),
              bg='lightyellow', justify=CENTER).place(x=342, y=150, width=150)

        Label(self.root, text='الحالة', font=('tajwal', 15), bg='white').place(x=940, y=200)
        cmb_status = ttk.Combobox(self.root, textvariable=self.var_status,
                                  values=('available', 'borrowed'),
                                  state='readonly', justify=CENTER, font=('tajwal', 15))
        cmb_status.place(x=780, y=200, width=150)
        cmb_status.current(0)

        # =================== الأزرار ===================
        Button(self.root, command=self.add, text='➕إضافة', font=('tajwal', 15),
               bg='#005c78', fg='#ffffff', cursor='hand2').place(x=175, y=215, width=155, height=28)

        Button(self.root, command=self.update, text='✒️تحديث', font=('tajwal', 15),
               bg='#005c78', fg='#ffffff', cursor='hand2').place(x=5, y=215, width=155, height=28)

        Button(self.root, command=self.delete, text='❌حذف', font=('tajwal', 15),
               bg='#005c78', fg='#ffffff', cursor='hand2').place(x=175, y=250, width=155, height=28)

        Button(self.root, command=self.clear, text='🔃تفريغ', font=('tajwal', 15),
               bg='#005c78', fg='#ffffff', cursor='hand2').place(x=5, y=250, width=155, height=28)

        # =================== TreeView ===================
        tree_frame = Frame(self.root, bd=3, relief=RIDGE)
        tree_frame.place(x=0, y=290, width=995, height=260)

        scrolly = Scrollbar(tree_frame, orient=VERTICAL)
        scrollx = Scrollbar(tree_frame, orient=HORIZONTAL)

        self.table = ttk.Treeview(tree_frame,
                                  columns=('status', 'category', 'author', 'title', 'id'),
                                  yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.table.xview)
        scrolly.config(command=self.table.yview)

        self.table.heading("status", text='الحالة')
        self.table.heading("category", text='التصنيف')
        self.table.heading("author", text='المؤلف')
        self.table.heading("title", text='العنوان')
        self.table.heading("id", text='ID')

        self.table['show'] = 'headings'
        self.table.column('id', width=60, anchor=CENTER)
        self.table.column('title', width=220, anchor=E)
        self.table.column('author', width=200, anchor=E)
        self.table.column('category', width=150, anchor=E)
        self.table.column('status', width=120, anchor=CENTER)

        self.table.pack(fill=BOTH, expand=1)
        self.table.bind('<ButtonRelease-1>', self.get_data)

        self.show()

    def connect(self):
        return sqlite3.connect(DB)

    def show(self):
        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("SELECT book_id, title, author, category, status FROM books ORDER BY book_id")
            rows = cur.fetchall()
            self.table.delete(*self.table.get_children())
            for r in rows:
                self.table.insert('', END, values=(r[4], r[3], r[2], r[1], r[0]))
            con.close()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"مشكلة أثناء عرض الكتب:\n{e}")

    def clear(self):
        self.var_id.set("")
        self.var_title.set("")
        self.var_author.set("")
        self.var_category.set("")
        self.var_status.set("available")
        self.var_search_by.set("Select")
        self.var_search_txt.set("")
        self.show()

    def get_data(self, ev):
        f = self.table.focus()
        row = self.table.item(f).get('values', [])
        if not row:
            return
        self.var_status.set(row[0])
        self.var_category.set(row[1])
        self.var_author.set(row[2])
        self.var_title.set(row[3])
        self.var_id.set(row[4])

    def add(self):
        title = self.var_title.get().strip()
        author = self.var_author.get().strip()
        category = self.var_category.get().strip()
        status = self.var_status.get().strip()

        if title == "" or author == "":
            messagebox.showerror("Error❗", "أدخل عنوان الكتاب واسم المؤلف")
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("""
                INSERT INTO books (title, author, category, status)
                VALUES (?, ?, ?, ?)
            """, (title, author, category, status))
            con.commit()
            con.close()
            messagebox.showinfo("Success✅", "تمت الإضافة")
            self.clear()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل الإضافة بسبب:\n{e}")

    def update(self):
        bid = self.var_id.get().strip()
        if bid == "":
            messagebox.showerror("Error❗", "اختر كتاباً للتعديل أولاً")
            return

        title = self.var_title.get().strip()
        author = self.var_author.get().strip()
        category = self.var_category.get().strip()
        status = self.var_status.get().strip()

        if title == "" or author == "":
            messagebox.showerror("Error❗", "أدخل عنوان الكتاب واسم المؤلف")
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("""
                UPDATE books SET title=?, author=?, category=?, status=?
                WHERE book_id=?
            """, (title, author, category, status, bid))
            con.commit()
            con.close()
            messagebox.showinfo("Success✅", "تم التحديث")
            self.clear()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل التحديث بسبب:\n{e}")

    def delete(self):
        bid = self.var_id.get().strip()
        if bid == "":
            messagebox.showerror("Error❗", "اختر كتاباً للحذف أولاً")
            return
        op = messagebox.askyesno("Confirm❗", "هل تريد الحذف؟")
        if not op:
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("DELETE FROM books WHERE book_id=?", (bid,))
            con.commit()
            con.close()
            messagebox.showinfo("Success✅", "تم الحذف")
            self.clear()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل الحذف بسبب:\n{e}")

    def search(self):
        by = self.var_search_by.get()
        txt = self.var_search_txt.get().strip()
        if by == "Select":
            messagebox.showerror("Error❗", "اختر نوع البحث")
            return
        if txt == "":
            messagebox.showerror("Error❗", "أدخل كلمة للبحث")
            return

        allowed = {"title", "author", "category"}
        if by not in allowed:
            messagebox.showerror("Error❗", "نوع البحث غير صالح")
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute(
                f"SELECT book_id, title, author, category, status FROM books WHERE {by} LIKE ?",
                ('%' + txt + '%',)
            )
            rows = cur.fetchall()
            con.close()

            self.table.delete(*self.table.get_children())
            for r in rows:
                self.table.insert('', END, values=(r[4], r[3], r[2], r[1], r[0]))
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل البحث بسبب:\n{e}")


if __name__ == "__main__":
    root = Tk()
    BooksClass(root)
    root.mainloop()
