# gui/interface.py — Updated: removed Start Checkpoint GUI

import tkinter as tk
from tkinter import ttk
from gui.template_gui import launch_template_generator
from gui.checkpoint_viewer import launch_checkpoint_viewer

def show_main_menu(session_token, username, password):
    root = tk.Tk()
    root.title("Taurob Mission Control")

    frm = ttk.Frame(root, padding=20)
    frm.grid()

    ttk.Label(frm, text="Welkom bij Taurob Mission Control").grid(column=0, row=0, columnspan=2, pady=10)

    ttk.Button(frm, text="Genereer Leeg Template", command=lambda: launch_template_generator()).grid(column=0, row=1, pady=5)
    ttk.Button(frm, text="Bekijk Checkpoints", command=lambda: launch_checkpoint_viewer(root, username, password)).grid(column=0, row=2, pady=5)

    root.mainloop()