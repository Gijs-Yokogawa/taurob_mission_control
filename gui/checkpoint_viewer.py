# gui/checkpoint_viewer.py

import tkinter as tk
from tkinter import ttk, messagebox
from api.client import (
    get_checkpoints,
    delete_checkpoint,
    sync_from_robot,
    create_checkpoint,
    update_checkpoint,
)
from storage.manager import (
    update_local_checkpoints_from_api,
    get_all_checkpoints_from_db,
    get_checkpoint_json_by_id,
    save_checkpoint,
    checkpoint_exists,
    get_modified_checkpoints,
    mark_checkpoint_modified,
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
        self.tree = ttk.Treeview(
            main_frame,
            columns=("checkpoint_id", "name", "type", "created_at"),
            show="headings",
        )

        self.heading_labels = {
            "checkpoint_id": "ID",
            "name": "Naam",
            "type": "Type",
            "created_at": "Created At",
        }

        for col, label in self.heading_labels.items():
            self.tree.heading(col, text=label, command=lambda c=col: self.sort_tree(c))

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
        tk.Button(button_frame, text="Sync from API", command=self.sync_from_api).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete & Sync Selected", command=self.delete_and_sync_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Sync to API", command=self.sync_to_api).pack(side=tk.LEFT, padx=5)

        # Variabelen voor sorteren
        self.sort_column = "id"
        self.sort_ascending = True

        # Initialiseer met data
        self.populate_tree()

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
            # Reset vorige kolom label indien nodig
            if self.sort_column in getattr(self, "heading_labels", {}):
                prev_label = self.heading_labels[self.sort_column]
                self.tree.heading(self.sort_column, text=prev_label)
            self.sort_column = col
            self.sort_ascending = True

        arrow = "▲" if self.sort_ascending else "▼"
        if col in getattr(self, "heading_labels", {}):
            label = self.heading_labels[col]
            self.tree.heading(col, text=f"{label} {arrow}")

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

    def sync_from_api(self):
        try:
            api_data = get_checkpoints()
            for cp in api_data:
                cp_id = cp.get("ActionID")
                name = cp.get("ActionName")

                if checkpoint_exists(cp_id):
                    overwrite = messagebox.askyesno(
                        "Overschrijven?",
                        f"Checkpoint '{name}' bestaat al. Overschrijven?",
                        parent=self,
                    )
                    if not overwrite:
                        continue

                save_checkpoint(cp)

            self.populate_tree()
            messagebox.showinfo("Sync voltooid", "Checkpoints gesynchroniseerd.", parent=self)
        except Exception as e:
            messagebox.showerror("Fout", f"Fout bij synchronisatie:\n{e}", parent=self)

    def sync_to_api(self):
        """Upload lokale wijzigingen naar de API."""
        try:
            modified = get_modified_checkpoints()
            for cp in modified:
                cp_id = cp.get("id") or cp.get("ActionID")
                if cp_id:
                    response = update_checkpoint(cp_id, cp)
                else:
                    response = create_checkpoint(cp)
                save_checkpoint(response)
                mark_checkpoint_modified(response.get("id") or response.get("ActionID"), False)

            self.populate_tree()
            messagebox.showinfo(
                "Sync voltooid",
                "Lokale wijzigingen gesynchroniseerd.",
                parent=self,
            )
        except Exception as e:
            messagebox.showerror("Fout", f"Fout bij synchroniseren:\n{e}", parent=self)
