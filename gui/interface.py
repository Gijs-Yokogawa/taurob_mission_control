# gui/interface.py

import tkinter as tk
from gui.template_gui import TemplateGenerator
from gui.checkpoint_viewer import CheckpointViewer

def show_main_menu(root=None):
    # Sluit het loginvenster netjes als het meegegeven is
    if root:
        root.destroy()

    main_root = tk.Tk()
    main_root.title("Taurob Mission Control")

    frame = tk.Frame(main_root, padx=20, pady=20)
    frame.pack()

    tk.Label(frame, text="Taurob Mission Control", font=("Arial", 20, "bold")).pack(pady=(0, 20))

    tk.Button(
        frame,
        text="Template Generator",
        width=25,
        command=lambda: TemplateGenerator(main_root)
    ).pack(pady=5)

    tk.Button(
        frame,
        text="Checkpoint Viewer",
        width=25,
        command=lambda: CheckpointViewer(main_root)
    ).pack(pady=5)

    main_root.mainloop()
