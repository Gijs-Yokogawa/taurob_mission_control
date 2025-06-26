# gui/login.py

import tkinter as tk
from tkinter import messagebox
from api.client import set_credentials, is_authenticated

class LoginWindow:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success = on_success_callback

        self.frame = tk.Frame(root)
        self.frame.pack(padx=30, pady=30)

        tk.Label(self.frame, text="Inloggen", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        tk.Label(self.frame, text="Gebruikersnaam:").grid(row=1, column=0, sticky="e")
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.grid(row=1, column=1)

        tk.Label(self.frame, text="Wachtwoord:").grid(row=2, column=0, sticky="e")
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.grid(row=2, column=1)

        tk.Button(self.frame, text="Login", command=self.attempt_login).grid(row=3, column=0, columnspan=2, pady=10)

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        print(f"[Login] Ingevoerde gebruikersnaam: '{username}'")
        print(f"[Login] Ingevoerd wachtwoord: '{'*' * len(password)}'")  # Masked voor terminal

        set_credentials(username, password)

        if is_authenticated():
            print("[Login] Login succesvol via API")
            self.frame.destroy()
            self.on_success(self.root)
        else:
            print("[Login] Login mislukt via API")
            messagebox.showerror("Login mislukt", "Ongeldige gebruikersnaam of wachtwoord.", parent=self.root)
