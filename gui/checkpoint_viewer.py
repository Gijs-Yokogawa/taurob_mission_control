# gui/checkpoint_viewer.py

import tkinter as tk
from tkinter import ttk, messagebox
from api.client import get_checkpoints, delete_checkpoint, sync_from_robot
from storage.manager import (
    update_local_checkpoints_from_api,
    get_all_checkpoints_from_db,
    get_checkpoint_json_by_id,
)
import json

class CheckpointViewer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Checkpoints Bekijken")

        # Titel
        title = tk.Label(self, text="Checkpoints", font=("Arial", 16, "bold"))
        title.pack(pady=(10, 0))

        # Hoofdframe (Tree + editor)
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # TreeView met kolommen
        self.tree = ttk.Treeview(main_frame, columns=("checkpoint_id", "name", "type", "created_at"), show="headings")
        self.tree.heading("checkpoint_id", text="ID", command=lambda: self.sort_tree("checkpoint_id"))
        self.tree.heading("name", text="Naam", command=lambda: self.sort_tree("name"))
        self.tree.heading("type", text="Type", command=lambda: self.sort_tree("type"))
        self.tree.heading("created_at", text="Created At", command=lambda: self.sort_tree("created_at"))

        self.tree.column("checkpoint_id", width=120)
        self.tree.column("name", width=250)
        self.tree.column("type", width=100)
        self.tree.column("created_at", width=150)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # JSON-editor onderin
        self.json_text = tk.Text(self, height=10, font=("Courier", 10))
        self.json_text.pack(fill=tk.BOTH, padx=10, pady=(0, 10), expand=False)

        # Knoppenframe
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Erase DB & Sync", command=self.erase_and_sync).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete & Sync Selected", command=self.delete_and_sync_selected).pack(side=tk.LEFT, padx=5)

        # Variabelen voor sorteren
        self.sort_column = "id"
        self.sort_ascending = True

        # Initialiseer met data
        self.erase_and_sync()

    def erase_and_sync(self):
        try:
            api_data = get_checkpoints()
            update_local_checkpoints_from_api(api_data)
            self.populate_tree()
            messagebox.showinfo("Succes", "Database geleegd en gesynchroniseerd met API.", parent=self)
        except Exception as e:
            messagebox.showerror("Fout", f"Fout bij synchronisatie:\n{e}", parent=self)

    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        rows = get_all_checkpoints_from_db(order_by=self.sort_column, ascending=self.sort_ascending)
        for checkpoint_id, name, ctype, created_at in rows:
            self.tree.insert("", "end", values=(checkpoint_id, name, ctype, created_at))
        self.json_text.delete("1.0", tk.END)

    def sort_tree(self, col):
        if self.sort_column == col:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = col
            self.sort_ascending = True
        self.populate_tree()

    def delete_and_sync_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Geen selectie", "Selecteer een checkpoint om te verwijderen.", parent=self)
            return

        checkpoint_id = self.tree.item(selected_item[0], "values")[0]
        naam = self.tree.item(selected_item[0], "values")[1]

        confirm = messagebox.askyesno("Bevestig verwijdering", f"Weet je zeker dat je '{naam}' wil verwijderen?", parent=self)
        if not confirm:
            return

        try:
            success = delete_checkpoint(checkpoint_id)
            if success:
                self.erase_and_sync()
                messagebox.showinfo("Verwijderd", f"Checkpoint '{naam}' verwijderd en database gesynchroniseerd.", parent=self)
            else:
                messagebox.showwarning("Mislukt", "Verwijderen mislukt.", parent=self)
        except Exception as e:
            messagebox.showerror("Fout bij verwijderen", str(e), parent=self)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        checkpoint_id = self.tree.item(selected_item[0], "values")[0]
        json_data = get_checkpoint_json_by_id(checkpoint_id)

        self.json_text.delete("1.0", tk.END)
        if json_data:
            pretty_json = json.dumps(json_data, indent=2)
            self.json_text.insert(tk.END, pretty_json)
