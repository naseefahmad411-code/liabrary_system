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
        return os.path.dirname(sys.executable)   # جنب exe
    return os.path.dirname(os.path.abspath(__file__))  # جنب .py


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


class StudentsClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry('995x550+50+120')
        self.root.title('Students Management')
        self.root.config(bg='#ffffff')
        self.root.resizable(False, False)

        # ✅ تهيئة DB والجداول
        try:
            init_db()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل تهيئة قاعدة البيانات:\n{e}")
            return

        # =================== صورة في الجانب الأيسر ===================
        img_path = resource_path(os.path.join("images", "one.png"))

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
        self.var_name = StringVar()
        self.var_contact = StringVar()
        self.var_dept = StringVar()

        # =================== Frame البحث ===================
        search_frame = LabelFrame(
            self.root, text='بحث', font=("goudy old style", 12, "bold"),
            bd=2, relief=RIDGE, bg='#ffffff'
        )
        search_frame.place(x=370, y=20, width=600, height=70)

        cmb_search = ttk.Combobox(
            search_frame,
            textvariable=self.var_search_by,
            values=('Select', 'name', 'contact', 'department'),
            state='readonly',
            justify=CENTER,
            font=('tajwal', 15)
        )
        cmb_search.place(x=10, y=10, width=180)
        cmb_search.current(0)

        Entry(
            search_frame,
            textvariable=self.var_search_txt,
            font=('tajwal', 15),
            bg='lightyellow',
            justify=RIGHT
        ).place(x=200, y=10, width=210)

        Button(
            search_frame,
            command=self.search,
            text='بحث',
            font=('goudy old style', 15),
            bg='#005c78',
            fg='#ffffff',
            cursor='hand2'
        ).place(x=415, y=9, width=150, height=30)

        # =================== عنوان الواجهة ===================
        Label(
            self.root,
            text='إدارة الطلاب',
            font=('goudy old style', 15),
            bg='#005c78',
            fg="#ffffff"
        ).place(x=340, y=100, width=645)

        # =================== الحقول ===================
        Label(self.root, text='الاسم', font=('tajwal', 15), bg='white').place(x=940, y=145)
        Label(self.root, text='الهاتف', font=('tajwal', 15), bg='white').place(x=710, y=145)
        Label(self.root, text='القسم', font=('tajwal', 15), bg='white').place(x=500, y=145)

        Entry(self.root, textvariable=self.var_name, font=('tajwal', 15),
              bg='lightyellow', justify=RIGHT).place(x=780, y=150, width=150)

        Entry(self.root, textvariable=self.var_contact, font=('tajwal', 15),
              bg='lightyellow', justify=RIGHT).place(x=550, y=150, width=150)

        Entry(self.root, textvariable=self.var_dept, font=('tajwal', 15),
              bg='lightyellow', justify=RIGHT).place(x=342, y=150, width=150)

        # =================== الأزرار ===================
        Button(self.root, command=self.add, text='➕إضافة', font=('tajwal', 15),
               bg='#005c78', fg='#ffffff', cursor='hand2').place(x=175, y=215, width=155, height=28)

        Button(self.root, command=self.update, text='✒️تحديث', font=('tajwal', 15),
               bg='#005c78', fg='#ffffff', cursor='hand2').place(x=5, y=215, width=155, height=28)

        Button(self.root, command=self.delete, text='❌حذف', font=('tajwal', 15),
               bg='#005c78', fg='#ffffff', cursor='hand2').place(x=175, y=250, width=155, height=28)

        Button(self.root, command=self.clear, text='🔃تفريغ', font=('tajwal', 15),
               bg='#005c78', fg='#ffffff', cursor='hand2').place(x=5, y=250, width=155, height=28)

        # =================== جدول العرض TreeView ===================
        tree_frame = Frame(self.root, bd=3, relief=RIDGE)
        tree_frame.place(x=0, y=290, width=995, height=260)

        scrolly = Scrollbar(tree_frame, orient=VERTICAL)
        scrollx = Scrollbar(tree_frame, orient=HORIZONTAL)

        self.table = ttk.Treeview(
            tree_frame,
            columns=('dept', 'contact', 'name', 'id'),
            yscrollcommand=scrolly.set,
            xscrollcommand=scrollx.set
        )

        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.table.xview)
        scrolly.config(command=self.table.yview)

        self.table.heading("dept", text='القسم')
        self.table.heading("contact", text='الهاتف')
        self.table.heading("name", text='الاسم')
        self.table.heading("id", text='ID')

        self.table['show'] = 'headings'
        self.table.column('id', width=60, anchor=CENTER)
        self.table.column('name', width=250, anchor=E)
        self.table.column('contact', width=200, anchor=CENTER)
        self.table.column('dept', width=200, anchor=E)

        self.table.pack(fill=BOTH, expand=1)
        self.table.bind('<ButtonRelease-1>', self.get_data)

        self.show()

    def connect(self):
        return sqlite3.connect(DB)

    def show(self):
        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("SELECT student_id, name, contact, department FROM students ORDER BY student_id")
            rows = cur.fetchall()
            self.table.delete(*self.table.get_children())
            for r in rows:
                self.table.insert('', END, values=(r[3], r[2], r[1], r[0]))
            con.close()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"مشكلة أثناء عرض البيانات:\n{e}")

    def clear(self):
        self.var_id.set("")
        self.var_name.set("")
        self.var_contact.set("")
        self.var_dept.set("")
        self.var_search_by.set("Select")
        self.var_search_txt.set("")
        self.show()

    def get_data(self, ev):
        f = self.table.focus()
        row = self.table.item(f).get('values', [])
        if not row:
            return
        self.var_dept.set(row[0])
        self.var_contact.set(row[1])
        self.var_name.set(row[2])
        self.var_id.set(row[3])

    def add(self):
        name = self.var_name.get().strip()
        contact = self.var_contact.get().strip()
        dept = self.var_dept.get().strip()

        if name == "":
            messagebox.showerror("Error❗", "أدخل اسم الطالب")
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute(
                "INSERT INTO students (name, contact, department) VALUES (?, ?, ?)",
                (name, contact, dept)
            )
            con.commit()
            con.close()
            messagebox.showinfo("Success✅", "تمت الإضافة")
            self.clear()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل حفظ الطالب بسبب:\n{e}")

    def update(self):
        sid = self.var_id.get().strip()
        name = self.var_name.get().strip()
        contact = self.var_contact.get().strip()
        dept = self.var_dept.get().strip()

        if sid == "":
            messagebox.showerror("Error❗", "اختر طالباً للتعديل أولاً")
            return
        if name == "":
            messagebox.showerror("Error❗", "أدخل اسم الطالب")
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("""
                UPDATE students SET name=?, contact=?, department=?
                WHERE student_id=?
            """, (name, contact, dept, sid))
            con.commit()
            con.close()
            messagebox.showinfo("Success✅", "تم التحديث")
            self.clear()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل التحديث بسبب:\n{e}")

    def delete(self):
        sid = self.var_id.get().strip()
        if sid == "":
            messagebox.showerror("Error❗", "اختر طالباً للحذف أولاً")
            return
        op = messagebox.askyesno("Confirm❗", "هل تريد الحذف؟")
        if not op:
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("DELETE FROM students WHERE student_id=?", (sid,))
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

        allowed = {"name", "contact", "department"}
        if by not in allowed:
            messagebox.showerror("Error❗", "نوع البحث غير صالح")
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute(
                f"SELECT student_id, name, contact, department FROM students WHERE {by} LIKE ?",
                ('%' + txt + '%',)
            )
            rows = cur.fetchall()
            con.close()

            self.table.delete(*self.table.get_children())
            for r in rows:
                self.table.insert('', END, values=(r[3], r[2], r[1], r[0]))
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل البحث بسبب:\n{e}")


if __name__ == "__main__":
    root = Tk()
    StudentsClass(root)
    root.mainloop()
