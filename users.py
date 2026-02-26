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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        department TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        category TEXT,
        status TEXT DEFAULT 'available'
    )
    """)

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'Admin'
    )
    """)

    con.commit()
    con.close()


class UsersClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry('995x620+50+120')  # ✅ ارتفاع أكبر حتى ما يتداخل شيء
        self.root.title('إدارة المستخدمين')
        self.root.config(bg='#ffffff')
        self.root.resizable(False, False)

        # ✅ تهيئة DB والجداول
        try:
            init_db()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل تهيئة قاعدة البيانات:\n{e}")
            return

        # =================== صورة يسار ===================
        img_path = resource_path(os.path.join("images", "tthree.png"))
        try:
            self.logo = Image.open(img_path).resize((325, 200))
            self.logo = ImageTk.PhotoImage(self.logo)
            Label(self.root, image=self.logo, bg='#ffffff').place(x=5, y=5, width=325, height=200)
        except Exception as ex:
            messagebox.showwarning("Image Warning", f"مشكلة بالصورة:\n{ex}")

        # =================== متغيرات ===================
        self.var_search_by = StringVar()
        self.var_search_txt = StringVar()

        self.var_id = StringVar()
        self.var_username = StringVar()
        self.var_password = StringVar()
        self.var_role = StringVar()

        # =================== Frame البحث ===================
        search_frame = LabelFrame(
            self.root, text='بحث', font=("goudy old style", 12, "bold"),
            bd=2, relief=RIDGE, bg='#ffffff'
        )
        search_frame.place(x=370, y=15, width=610, height=75)

        cmb_search = ttk.Combobox(
            search_frame, textvariable=self.var_search_by,
            values=('Select', 'username', 'role'),
            state='readonly', justify=CENTER, font=('tajwal', 14)
        )
        cmb_search.place(x=10, y=12, width=180)
        cmb_search.current(0)

        Entry(
            search_frame, textvariable=self.var_search_txt,
            font=('tajwal', 14), bg='lightyellow', justify=RIGHT
        ).place(x=200, y=12, width=230)

        Button(
            search_frame, command=self.search, text='بحث',
            font=('goudy old style', 14), bg='#005c78', fg='#ffffff', cursor='hand2'
        ).place(x=440, y=11, width=155, height=33)

        # =================== عنوان ===================
        Label(
            self.root, text='إدارة المستخدمين', font=('goudy old style', 16, 'bold'),
            bg='#005c78', fg="#ffffff"
        ).place(x=340, y=100, width=645, height=35)

        # =================== Frame الإدخال (Label فوق - Input تحت) ===================
        form = Frame(self.root, bg='white')
        form.place(x=340, y=145, width=645, height=150)

        for c in range(3):
            form.grid_columnconfigure(c, weight=1, uniform="col")

        def top_label(text, r, c):
            Label(form, text=text, font=('tajwal', 14), bg='white', anchor='center') \
                .grid(row=r, column=c, padx=10, pady=(8, 2), sticky="ew")

        # صف Labels
        top_label("اسم المستخدم", 0, 2)
        top_label("كلمة المرور", 0, 1)
        top_label("الصلاحية", 0, 0)

        # صف Inputs (✅ نصغّر العرض بواسطة padx)
        Entry(form, textvariable=self.var_username, font=('tajwal', 14),
              bg='lightyellow', justify=RIGHT) \
            .grid(row=1, column=2, padx=45, pady=(0, 12), sticky="ew")

        Entry(form, textvariable=self.var_password, font=('tajwal', 14),
              bg='lightyellow', justify=RIGHT, show="*") \
            .grid(row=1, column=1, padx=45, pady=(0, 12), sticky="ew")

        cmb_role = ttk.Combobox(
            form, textvariable=self.var_role,
            values=('Admin', 'Librarian'),
            state='readonly', justify=CENTER, font=('tajwal', 14)
        )
        cmb_role.grid(row=1, column=0, padx=45, pady=(0, 12), sticky="ew")
        self.var_role.set("Admin")

        # =================== Frame الأزرار (Grid) ===================
        btn_frame = Frame(self.root, bg="white")
        btn_frame.place(x=5, y=210, width=325, height=110)

        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        Button(btn_frame, command=self.add, text='➕ إضافة', font=('tajwal', 14),
               bg='#005c78', fg='#ffffff', cursor='hand2') \
            .grid(row=0, column=0, padx=6, pady=7, sticky="ew")

        Button(btn_frame, command=self.update, text='✒️ تحديث', font=('tajwal', 14),
               bg='#005c78', fg='#ffffff', cursor='hand2') \
            .grid(row=0, column=1, padx=6, pady=7, sticky="ew")

        Button(btn_frame, command=self.delete, text='❌ حذف', font=('tajwal', 14),
               bg='#005c78', fg='#ffffff', cursor='hand2') \
            .grid(row=1, column=0, padx=6, pady=7, sticky="ew")

        Button(btn_frame, command=self.clear, text='🔃 تفريغ', font=('tajwal', 14),
               bg='#005c78', fg='#ffffff', cursor='hand2') \
            .grid(row=1, column=1, padx=6, pady=7, sticky="ew")

        # =================== جدول ===================
        tree_frame = Frame(self.root, bd=3, relief=RIDGE)
        tree_frame.place(x=0, y=335, width=995, height=285)  # ✅ نزّلناه لتحت أكثر

        scrolly = Scrollbar(tree_frame, orient=VERTICAL)
        scrollx = Scrollbar(tree_frame, orient=HORIZONTAL)

        self.table = ttk.Treeview(
            tree_frame,
            columns=('role', 'username', 'id'),
            yscrollcommand=scrolly.set, xscrollcommand=scrollx.set
        )

        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.table.xview)
        scrolly.config(command=self.table.yview)

        self.table.heading("role", text='الصلاحية')
        self.table.heading("username", text='اسم المستخدم')
        self.table.heading("id", text='ID')

        self.table['show'] = 'headings'
        self.table.column('id', width=90, anchor=CENTER)
        self.table.column('username', width=320, anchor=CENTER)
        self.table.column('role', width=200, anchor=CENTER)

        self.table.pack(fill=BOTH, expand=1)
        self.table.bind('<ButtonRelease-1>', self.get_data)

        self.show()

    def connect(self):
        return sqlite3.connect(DB)

    def show(self):
        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("SELECT user_id, username, role FROM users ORDER BY user_id")
            rows = cur.fetchall()
            self.table.delete(*self.table.get_children())
            for r in rows:
                self.table.insert('', END, values=(r[2], r[1], r[0]))
            con.close()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"مشكلة أثناء عرض المستخدمين:\n{e}")

    def clear(self):
        self.var_id.set("")
        self.var_username.set("")
        self.var_password.set("")
        self.var_role.set("Admin")
        self.var_search_by.set("Select")
        self.var_search_txt.set("")
        self.show()

    def get_data(self, ev):
        f = self.table.focus()
        row = self.table.item(f).get('values', [])
        if not row:
            return
        self.var_role.set(row[0])
        self.var_username.set(row[1])
        self.var_id.set(row[2])
        self.var_password.set("")  # ما نعرض كلمة المرور

    def add(self):
        username = self.var_username.get().strip()
        password = self.var_password.get().strip()
        role = self.var_role.get().strip()

        if username == "" or password == "":
            messagebox.showerror("Error❗", "أدخل اسم المستخدم وكلمة المرور")
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                        (username, password, role))
            con.commit()
            con.close()
            messagebox.showinfo("Success✅", "تمت الإضافة")
            self.clear()
        except Exception as ex:
            messagebox.showerror("Error❗", f"{str(ex)}")

    def update(self):
        uid = self.var_id.get().strip()
        username = self.var_username.get().strip()
        role = self.var_role.get().strip()

        if uid == "":
            messagebox.showerror("Error❗", "اختر مستخدم للتعديل أولاً")
            return
        if username == "":
            messagebox.showerror("Error❗", "أدخل اسم المستخدم")
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("UPDATE users SET username=?, role=? WHERE user_id=?",
                        (username, role, uid))
            con.commit()
            con.close()
            messagebox.showinfo("Success✅", "تم التحديث")
            self.clear()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل التحديث بسبب:\n{e}")

    def delete(self):
        uid = self.var_id.get().strip()
        if uid == "":
            messagebox.showerror("Error❗", "اختر مستخدم للحذف أولاً")
            return
        op = messagebox.askyesno("Confirm❗", "هل تريد الحذف؟")
        if not op:
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("DELETE FROM users WHERE user_id=?", (uid,))
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
            messagebox.showerror("Error❗", "أدخل قيمة للبحث")
            return

        allowed = {"username", "role"}
        if by not in allowed:
            messagebox.showerror("Error❗", "نوع البحث غير صالح")
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute(f"SELECT user_id, username, role FROM users WHERE {by} LIKE ?",
                        ('%' + txt + '%',))
            rows = cur.fetchall()
            con.close()

            self.table.delete(*self.table.get_children())
            for r in rows:
                self.table.insert('', END, values=(r[2], r[1], r[0]))
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل البحث بسبب:\n{e}")


if __name__ == "__main__":
    root = Tk()
    UsersClass(root)
    root.mainloop()
