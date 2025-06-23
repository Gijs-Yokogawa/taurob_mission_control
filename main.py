# main.py

import tkinter as tk
from tkinter import ttk

from gui.login import login_and_then
from gui.template_gui import launch_template_generator
from gui.checkpoint_viewer import launch_checkpoint_viewer

def setup_main_menu(root, token, user, pw):
    # Maak hoofdvenster zichtbaar en zet titel
    root.deiconify()
    root.title(f"Mission Control — {user}")

    # Ruim oude widgets op
    for w in root.winfo_children():
        w.destroy()

    # Bouw je oorspronkelijke menu
    ttk.Label(root, text="Mission Control", font=("TkDefaultFont", 16))\
        .pack(pady=10)

    ttk.Button(
        root,
        text="Open Checkpoints",
        command=lambda: launch_checkpoint_viewer(root, user, pw)
    ).pack(fill='x', padx=20, pady=5)

    ttk.Button(
        root,
        text="Genereer Leeg Template",
        command=lambda: launch_template_generator(root, user, pw)
    ).pack(fill='x', padx=20, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # verberg venster tot na login

    # login_and_then geeft token, user en pw terug
    login_and_then(lambda token, user, pw: setup_main_menu(root, token, user, pw))

    root.mainloop()
