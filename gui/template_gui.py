# gui/template_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from api.client import create_and_save_checkpoint

class TemplateGenerator(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Template Generator")

        tk.Label(self, text="Naam checkpoint:").pack(pady=(10, 0))
        self.name_entry = tk.Entry(self)
        self.name_entry.pack(padx=10, pady=(0, 10), fill=tk.X)

        tk.Label(self, text="Type checkpoint:").pack(pady=(10, 0))
        self.type_var = tk.StringVar(value="drive")

        type_frame = tk.Frame(self)
        type_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        types = [("Drive", "drive"), ("Dock", "dock"), ("Measure", "measure")]
        for text, val in types:
            rb = ttk.Radiobutton(type_frame, text=text, variable=self.type_var, value=val)
            rb.pack(side=tk.LEFT, padx=5)

        save_btn = tk.Button(self, text="Checkpoint Aanmaken", command=self.save_checkpoint)
        save_btn.pack(pady=(10, 15))

    def save_checkpoint(self):
        name = self.name_entry.get().strip()
        ctype = self.type_var.get()

        if not name:
            messagebox.showwarning("Validatie", "Voer een naam in voor het checkpoint.")
            return

        if ctype == "drive":
            payload = {
                "ActionName": name,
                "ActionType": ctype,
                "RobotPose": "",
                "Metadata": "",
                "ActionInfo": ""
                # Voeg hier eventueel extra velden toe als je API dat verwacht
                }

        else:
            payload = {
                "ActionName": name,
                "ActionType": ctype,
                "AssetName":"null",
                "RobotPose": "",
                "Metadata": "",
                "ActionInfo": ""
                # Voeg hier eventueel extra velden toe als je API dat verwacht
                }

        try:
            result = create_and_save_checkpoint(payload)
            messagebox.showinfo("Succes", f"Checkpoint '{result.get('name')}' succesvol aangemaakt.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Fout", f"Fout bij aanmaken checkpoint:\n{e}")
