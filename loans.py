
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


class LoansClass:
    def __init__(self, root):
        self.root = root

        # ✅ تهيئة DB والجداول
        try:
            init_db()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل تهيئة قاعدة البيانات:\n{e}")
            return

        # ✅ زودنا ارتفاع الشاشة حتى ما ينقص مكان الأزرار
        self.root.geometry('995x600+50+120')
        self.root.title('إدارة الإعارة والإرجاع')
        self.root.config(bg='#ffffff')
        self.root.resizable(False, False)

        # =================== صورة في الجانب الأيسر ===================
        img_path = resource_path(os.path.join("images", "th.png"))

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
        self.var_loan_id = StringVar()
        self.var_student_id = StringVar()
        self.var_book_id = StringVar()
        self.var_borrow_date = StringVar()
        self.var_due_date = StringVar()
        self.var_return_date = StringVar()
        self.var_state = StringVar()

        # =================== Frame البحث ===================
        search_frame = LabelFrame(
            self.root, text='بحث', font=("goudy old style", 12, "bold"),
            bd=2, relief=RIDGE, bg='#ffffff'
        )
        search_frame.place(x=370, y=10, width=600, height=70)

        cmb_search = ttk.Combobox(
            search_frame, textvariable=self.var_search_by,
            values=('اختر', 'student_id', 'book_id', 'state'),
            state='readonly', justify=CENTER, font=('tajwal', 13)
        )
        cmb_search.place(x=10, y=10, width=180)
        cmb_search.current(0)

        Entry(
            search_frame, textvariable=self.var_search_txt, font=('tajwal', 13),
            bg='lightyellow', justify=RIGHT
        ).place(x=200, y=10, width=210)

        Button(
            search_frame, command=self.search, text='بحث', font=('goudy old style', 14),
            bg='#005c78', fg='#ffffff', cursor='hand2'
        ).place(x=415, y=9, width=170, height=32)

        # =================== عنوان ===================
        Label(
            self.root, text='الإعارة والإرجاع', font=('goudy old style', 16, "bold"),
            bg='#005c78', fg="#ffffff"
        ).place(x=340, y=90, width=645, height=30)

        # =================== Frame إدخال البيانات ===================
        form_frame = Frame(self.root, bg="white")
        form_frame.place(x=340, y=125, width=645, height=165)

        lbl_font = ('tajwal', 13)
        for c in range(3):
            form_frame.grid_columnconfigure(c, weight=1, uniform="col")

        def label_at(col, row, text):
            Label(form_frame, text=text, font=lbl_font, bg="white", anchor="e") \
                .grid(row=row, column=col, padx=10, pady=(6, 2), sticky="ew")

        # ---- الصف العلوي ----
        label_at(2, 0, "رقم الطالب")
        label_at(1, 0, "رقم الكتاب")
        label_at(0, 0, "تاريخ الاستعارة")

        # Combobox للطلاب
        self.cmb_students = ttk.Combobox(
            form_frame, textvariable=self.var_student_id,
            state="readonly", justify=CENTER, font=('tajwal', 13)
        )
        self.cmb_students.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        # Combobox للكتب المتاحة
        self.cmb_books = ttk.Combobox(
            form_frame, textvariable=self.var_book_id,
            state="readonly", justify=CENTER, font=('tajwal', 13)
        )
        self.cmb_books.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        Entry(form_frame, textvariable=self.var_borrow_date, font=('tajwal', 13),
              bg="lightyellow", justify=RIGHT) \
            .grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # ---- الصف السفلي ----
        label_at(2, 2, "تاريخ الاستحقاق")
        label_at(1, 2, "تاريخ الإرجاع")
        label_at(0, 2, "الحالة")

        Entry(form_frame, textvariable=self.var_due_date, font=('tajwal', 13),
              bg="lightyellow", justify=RIGHT) \
            .grid(row=3, column=2, padx=10, pady=(0, 10), sticky="ew")

        Entry(form_frame, textvariable=self.var_return_date, font=('tajwal', 13),
              bg="lightyellow", justify=RIGHT) \
            .grid(row=3, column=1, padx=10, pady=(0, 10), sticky="ew")

        cmb_state = ttk.Combobox(
            form_frame, textvariable=self.var_state,
            values=("borrowed", "returned"),
            state="readonly", justify=CENTER, font=('tajwal', 13)
        )
        cmb_state.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        cmb_state.current(0)

        # =================== Frame الأزرار ===================
        btn_frame = Frame(self.root, bg="white")
        btn_frame.place(x=5, y=205, width=325, height=95)

        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        Button(btn_frame, command=self.return_book, text='✅ إرجاع', font=('tajwal', 14),
               bg='#005c78', fg='#ffffff', cursor='hand2') \
            .grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        Button(btn_frame, command=self.borrow, text='📌 استعارة', font=('tajwal', 14),
               bg='#005c78', fg='#ffffff', cursor='hand2') \
            .grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        Button(btn_frame, command=self.clear, text='🔃 تفريغ', font=('tajwal', 14),
               bg='#005c78', fg='#ffffff', cursor='hand2') \
            .grid(row=1, column=0, padx=6, pady=6, sticky="ew")

        Button(btn_frame, command=self.delete, text='❌ حذف', font=('tajwal', 14),
               bg='#005c78', fg='#ffffff', cursor='hand2') \
            .grid(row=1, column=1, padx=6, pady=6, sticky="ew")

        # =================== جدول ===================
        tree_frame = Frame(self.root, bd=3, relief=RIDGE)
        tree_frame.place(x=0, y=315, width=995, height=280)

        scrolly = Scrollbar(tree_frame, orient=VERTICAL)
        scrollx = Scrollbar(tree_frame, orient=HORIZONTAL)

        self.table = ttk.Treeview(
            tree_frame,
            columns=('state', 'return_date', 'due_date', 'borrow_date', 'book_id', 'student_id', 'loan_id'),
            yscrollcommand=scrolly.set, xscrollcommand=scrollx.set
        )

        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.table.xview)
        scrolly.config(command=self.table.yview)

        self.table.heading("state", text='الحالة')
        self.table.heading("return_date", text='تاريخ الإرجاع')
        self.table.heading("due_date", text='تاريخ الاستحقاق')
        self.table.heading("borrow_date", text='تاريخ الاستعارة')
        self.table.heading("book_id", text='رقم الكتاب')
        self.table.heading("student_id", text='رقم الطالب')
        self.table.heading("loan_id", text='رقم الإعارة')

        self.table['show'] = 'headings'
        for c in self.table['columns']:
            self.table.column(c, width=130, anchor=CENTER)

        self.table.pack(fill=BOTH, expand=1)
        self.table.bind('<ButtonRelease-1>', self.get_data)

        # تحميل الطلاب والكتب + عرض الجدول
        self.load_students()
        self.load_books_available()
        self.show()

    # =================== DB ===================
    def connect(self):
        return sqlite3.connect(DB)

    # =================== تحميل الطلاب ===================
    def load_students(self):
        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("SELECT student_id FROM students ORDER BY student_id")
            rows = cur.fetchall()
            con.close()

            vals = [str(r[0]) for r in rows]
            self.cmb_students['values'] = vals

            if vals and self.var_student_id.get() not in vals:
                self.var_student_id.set(vals[0])
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل تحميل الطلاب:\n{e}")

    # =================== تحميل الكتب المتاحة ===================
    def load_books_available(self):
        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("""
                SELECT book_id FROM books
                WHERE LOWER(status)='available'
                ORDER BY book_id
            """)
            rows = cur.fetchall()
            con.close()

            vals = [str(r[0]) for r in rows]
            self.cmb_books['values'] = vals

            if vals and self.var_book_id.get() not in vals:
                self.var_book_id.set(vals[0])
            if not vals:
                self.var_book_id.set("")
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل تحميل الكتب:\n{e}")

    # =================== عرض ===================
    def show(self):
        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute("""
                SELECT loan_id, student_id, book_id, borrow_date, due_date, return_date, state
                FROM loans ORDER BY loan_id
            """)
            rows = cur.fetchall()
            self.table.delete(*self.table.get_children())
            for r in rows:
                self.table.insert('', END, values=(r[6], r[5], r[4], r[3], r[2], r[1], r[0]))
            con.close()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"مشكلة أثناء عرض الإعارات:\n{e}")

    # =================== تفريغ ===================
    def clear(self):
        self.var_loan_id.set("")
        self.var_borrow_date.set("")
        self.var_due_date.set("")
        self.var_return_date.set("")
        self.var_state.set("borrowed")
        self.var_search_by.set("اختر")
        self.var_search_txt.set("")
        self.load_students()
        self.load_books_available()
        self.show()

    # =================== جلب بيانات ===================
    def get_data(self, ev):
        f = self.table.focus()
        row = self.table.item(f).get('values', [])
        if not row:
            return
        self.var_state.set(row[0])
        self.var_return_date.set(row[1] if row[1] else "")
        self.var_due_date.set(row[2])
        self.var_borrow_date.set(row[3])
        self.var_book_id.set(row[4])
        self.var_student_id.set(row[5])
        self.var_loan_id.set(row[6])

    # =================== استعارة ===================
    def borrow(self):
        sid = self.var_student_id.get().strip()
        bid = self.var_book_id.get().strip()
        bdate = self.var_borrow_date.get().strip()
        ddate = self.var_due_date.get().strip()

        if sid == "" or bid == "" or bdate == "" or ddate == "":
            messagebox.showerror("خطأ ❗", "اختر الطالب والكتاب وأدخل تاريخ الاستعارة والاستحقاق")
            return

        try:
            con = self.connect()
            cur = con.cursor()

            cur.execute("SELECT student_id FROM students WHERE student_id=?", (sid,))
            if not cur.fetchone():
                con.close()
                messagebox.showerror("خطأ ❗", "رقم الطالب غير موجود")
                return

            cur.execute("SELECT status FROM books WHERE book_id=?", (bid,))
            row = cur.fetchone()
            if not row:
                con.close()
                messagebox.showerror("خطأ ❗", "رقم الكتاب غير موجود")
                return

            if str(row[0]).lower() != 'available':
                con.close()
                messagebox.showerror("خطأ ❗", "الكتاب غير متوفر للإعارة")
                return

            cur.execute("""
                INSERT INTO loans (student_id, book_id, borrow_date, due_date, state)
                VALUES (?, ?, ?, ?, 'borrowed')
            """, (sid, bid, bdate, ddate))

            cur.execute("UPDATE books SET status='borrowed' WHERE book_id=?", (bid,))

            con.commit()
            con.close()
            messagebox.showinfo("تم ✅", "تمت الاستعارة بنجاح")
            self.clear()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل الاستعارة بسبب:\n{e}")

    # =================== إرجاع ===================
    def return_book(self):
        loan_id = self.var_loan_id.get().strip()
        rdate = self.var_return_date.get().strip()

        if loan_id == "":
            messagebox.showerror("خطأ ❗", "لازم تضغط على سجل من الجدول أولاً")
            return
        if rdate == "":
            messagebox.showerror("خطأ ❗", "أدخل تاريخ الإرجاع")
            return

        try:
            con = self.connect()
            cur = con.cursor()

            cur.execute("SELECT book_id, state FROM loans WHERE loan_id=?", (loan_id,))
            row = cur.fetchone()
            if not row:
                con.close()
                messagebox.showerror("خطأ ❗", "عملية الإعارة غير موجودة")
                return

            book_id, state = row
            if state != 'borrowed':
                con.close()
                messagebox.showerror("خطأ ❗", "هذه الإعارة ليست فعّالة (قد تكون مُرجعة)")
                return

            cur.execute("""
                UPDATE loans SET return_date=?, state='returned'
                WHERE loan_id=?
            """, (rdate, loan_id))
            cur.execute("UPDATE books SET status='available' WHERE book_id=?", (book_id,))

            con.commit()
            con.close()
            messagebox.showinfo("تم ✅", "تم الإرجاع بنجاح")
            self.clear()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل الإرجاع بسبب:\n{e}")

    # =================== حذف ===================
    def delete(self):
        loan_id = self.var_loan_id.get().strip()
        if loan_id == "":
            messagebox.showerror("خطأ ❗", "اختر عملية إعارة للحذف أولاً")
            return

        op = messagebox.askyesno("تأكيد ❗", "هل تريد حذف سجل الإعارة؟")
        if not op:
            return

        try:
            con = self.connect()
            cur = con.cursor()

            cur.execute("SELECT book_id, state FROM loans WHERE loan_id=?", (loan_id,))
            row = cur.fetchone()
            if row:
                book_id, state = row
                if state == 'borrowed':
                    cur.execute("UPDATE books SET status='available' WHERE book_id=?", (book_id,))

            cur.execute("DELETE FROM loans WHERE loan_id=?", (loan_id,))
            con.commit()
            con.close()

            messagebox.showinfo("تم ✅", "تم الحذف بنجاح")
            self.clear()
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل الحذف بسبب:\n{e}")

    # =================== بحث ===================
    def search(self):
        by = self.var_search_by.get()
        txt = self.var_search_txt.get().strip()

        if by == "اختر":
            messagebox.showerror("خطأ ❗", "اختر نوع البحث")
            return
        if txt == "":
            messagebox.showerror("خطأ ❗", "أدخل قيمة للبحث")
            return

        allowed = {"student_id", "book_id", "state"}
        if by not in allowed:
            messagebox.showerror("خطأ ❗", "نوع البحث غير صالح")
            return

        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute(f"""
                SELECT loan_id, student_id, book_id, borrow_date, due_date, return_date, state
                FROM loans WHERE {by} LIKE ?
                ORDER BY loan_id
            """, ('%' + txt + '%',))
            rows = cur.fetchall()
            con.close()

            self.table.delete(*self.table.get_children())
            for r in rows:
                self.table.insert('', END, values=(r[6], r[5], r[4], r[3], r[2], r[1], r[0]))
        except Exception as e:
            messagebox.showerror("DB Error❗", f"فشل البحث بسبب:\n{e}")


if __name__ == "__main__":
    root = Tk()
    LoansClass(root)
    root.mainloop()
