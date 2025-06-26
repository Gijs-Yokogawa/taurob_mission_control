# main.py

import tkinter as tk
from gui.interface import show_main_menu
from gui.login import LoginWindow

def on_login_success(root):
    # Vernietig loginvenster, toon hoofdmenu
    for widget in root.winfo_children():
        widget.destroy()
    show_main_menu(root)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Taurob Mission Control Login")
    LoginWindow(root, on_login_success)
    root.mainloop()
