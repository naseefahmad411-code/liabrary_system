import os
import sys
from tkinter import *
from PIL import Image, ImageTk
import time

def resource_path(relative_path):
    """
    يرجّع المسار الصحيح للملفات سواء تشغيل عادي أو بعد التحويل إلى EXE (PyInstaller)
    """
    try:
        base_path = sys._MEIPASS  # داخل exe
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))  # تشغيل عادي
    return os.path.join(base_path, relative_path)

from books import BooksClass
from students import StudentsClass
from loans import LoansClass
from users import UsersClass


class LibraryDashboard:
    def __init__(self, root):
        self.root = root
        self.root.geometry('1200x650+50+20')
        self.root.resizable(False, False)
        self.root.title('Library System')
        self.root.config(bg='#ffffff')

        self.lbl_date = Label(
            self.root,
            text='نظام إدارة المكتبة\t\t\t\t  Date:DD-MM-YYYY\t\t\t\t Time:HH:MM:SS',
            font=('times new roman', 15, 'bold'),
            bg='#005c78',
            fg='#ffffff'
        )
        self.lbl_date.place(x=0, y=0, width=1200, height=70)
        self.timed()

        btn_frame = Frame(self.root, bd=2, relief=RIDGE, bg='#ffffff')
        btn_frame.place(x=998, y=70, width=200, height=975)

        # ✅ الصورة 1 (menu) — لازم resource_path
        menu_path = resource_path(os.path.join("images", "four.png"))
        self.menu_image = Image.open(menu_path)
        self.menu_image = self.menu_image.resize((200, 270))
        self.menu_image = ImageTk.PhotoImage(self.menu_image)
        Label(btn_frame, image=self.menu_image).pack(side=TOP, fill=X)

        Label(btn_frame, text='Menu', font=('times new roman', 20),
              bg='#ffffff', fg='#005c78', relief=RIDGE).pack(fill=X)

        Button(btn_frame, text='إدارة الكتب', font=('times new roman', 19),
               bg='#005c78', fg='#ffffff', bd=3, cursor='hand2',
               command=self.open_books).pack(side=TOP, fill=X)

        Button(btn_frame, text='إدارة الطلاب', font=('times new roman', 19),
               bg='#005c78', fg='#ffffff', bd=3, cursor='hand2',
               command=self.open_students).pack(side=TOP, fill=X)

        Button(btn_frame, text='الإعارة والإرجاع', font=('times new roman', 19),
               bg='#005c78', fg='#ffffff', bd=3, cursor='hand2',
               command=self.open_loans).pack(side=TOP, fill=X)

        Button(btn_frame, text='إدارة المستخدمين', font=('times new roman', 19),
               bg='#005c78', fg='#ffffff', bd=3, cursor='hand2',
               command=self.open_users).pack(side=TOP, fill=X)

        Button(btn_frame, text='Exit', font=('times new roman', 19),
               bg='#005c78', fg='#ffffff', bd=3, cursor='hand2',
               command=self.root.destroy).pack(side=TOP, fill=X)

        frame_img = Frame(self.root, bd=2, relief=RIDGE, bg='gray')
        frame_img.place(x=1, y=72, width=995, height=577)

        # ✅ الصورة 2 (banner) — لازم resource_path
        banner_path = resource_path(os.path.join("images", "logo.png"))
        self.banner = Image.open(banner_path)
        self.banner = self.banner.resize((995, 577))
        self.banner = ImageTk.PhotoImage(self.banner)
        Label(frame_img, image=self.banner).place(x=0, y=0, width=995, height=577)

    def timed(self):
        tim = time.strftime("%I:%M:%S")
        date = time.strftime("%d-%m-%Y")
        self.lbl_date.config(text=f'نظام إدارة المكتبة\t\t\t\t Date:{date}\t\t\t\t Time:{tim}')
        self.lbl_date.after(1000, self.timed)

    def open_books(self):
        w = Toplevel(self.root)
        BooksClass(w)
        w.transient(self.root)
        w.focus_force()

    def open_students(self):
        w = Toplevel(self.root)
        StudentsClass(w)
        w.transient(self.root)
        w.focus_force()

    def open_loans(self):
        w = Toplevel(self.root)
        LoansClass(w)
        w.transient(self.root)
        w.focus_force()

    def open_users(self):
        w = Toplevel(self.root)
        UsersClass(w)
        w.transient(self.root)
        w.focus_force()


if __name__ == '__main__':
    root = Tk()
    LibraryDashboard(root)
    root.mainloop()
