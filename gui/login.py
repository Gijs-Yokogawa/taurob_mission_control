# gui/login.py

import tkinter as tk
from tkinter import ttk, messagebox
from api.client import login

def login_and_then(callback):
    def try_login():
        user = user_entry.get()
        pw = pw_entry.get()
        try:
            token = login(user, pw)
            login_root.destroy()
            callback(token, user, pw)
        except Exception as e:
            messagebox.showerror("Login Failed", str(e))

    login_root = tk.Tk()
    login_root.title("Login to Fleet System")
    frm = ttk.Frame(login_root, padding=10)
    frm.grid()

    ttk.Label(frm, text="Username:").grid(column=0, row=0, sticky='w')
    user_entry = ttk.Entry(frm)
    user_entry.grid(column=1, row=0)

    ttk.Label(frm, text="Password:").grid(column=0, row=1, sticky='w')
    pw_entry = ttk.Entry(frm, show='*')
    pw_entry.grid(column=1, row=1)

    ttk.Button(frm, text="Login", command=try_login).grid(column=0, row=2, columnspan=2, pady=10)

    login_root.mainloop()
