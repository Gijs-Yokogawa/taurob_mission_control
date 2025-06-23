# gui/checkpoint_viewer.py — DB-driven viewer met correcte kolommapping voor 6-koloms tuple

import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
from requests.auth import HTTPBasicAuth
from storage.manager import load_all_checkpoints, save_checkpoint
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

API_URL_TEMPLATE = "https://10.1.0.1:8443/basic/mission_editor/data_model/editor/action/all?robot_name={}"


def launch_checkpoint_viewer(parent, username, password):
    viewer = tk.Toplevel(parent)
    viewer.title("Bekijk Checkpoints")

    # Layout
    frm = ttk.Frame(viewer, padding=10)
    frm.grid(sticky="nsew")
    viewer.rowconfigure(1, weight=1)
    viewer.columnconfigure(0, weight=1)

    # Robotnaam invoer
    ttk.Label(frm, text="Robot Naam:").grid(row=0, column=0, sticky='w')
    robot_entry = ttk.Entry(frm)
    robot_entry.grid(row=0, column=1, sticky='we')

    # Cache records list
    records = []

    def load_from_db():
        nonlocal records
        # now returns tuples: (id, checkpoint_id, type, name, json_str, created_at)
        records = load_all_checkpoints()
        tree.delete(*tree.get_children())
        details_box.delete('1.0', tk.END)
        for rec in records:
            internal_id, cp_id, ctype, name, json_str, created = rec
            tree.insert('', 'end', values=(internal_id, cp_id, ctype, name, created))

    def sync_from_api():
        robot_name = robot_entry.get().strip()
        if not robot_name:
            messagebox.showerror("Fout", "Robotnaam is leeg")
            return
        try:
            url = API_URL_TEMPLATE.format(robot_name)
            resp = requests.get(url, auth=HTTPBasicAuth(username, password), verify=False)
            resp.raise_for_status()
            actions = resp.json()
            for action in actions:
                save_checkpoint(action, action.get("ActionID", -1))
            messagebox.showinfo("Success", f"{len(actions)} checkpoints geïmporteerd.")
            load_from_db()
            parent.event_generate('<<CheckpointAdded>>', when='tail')
        except Exception as e:
            messagebox.showerror("Fout bij API", str(e))

    # Sync knop (na definities)
    sync_btn = ttk.Button(frm, text="Sync van Robot API", command=sync_from_api)
    sync_btn.grid(row=0, column=2, padx=5)

    # Treeview voor checkpoint-overzicht
    columns = ("internal_id", "checkpoint_id", "type", "name", "created_at")
    tree = ttk.Treeview(
        frm,
        columns=columns,
        show='headings',
        displaycolumns=("checkpoint_id", "type", "name", "created_at")
    )
    headings = {
        "checkpoint_id": "CheckpointID",
        "type": "Type",
        "name": "Naam",
        "created_at": "Aangemaakt"
    }
    def convert(val):
        try:
            return (0, int(val))
        except (ValueError, TypeError):
            return (1, str(val).lower())

    def sort_treeview(treeview, col, reverse):
        data = [(convert(treeview.set(item, col)), item) for item in treeview.get_children('')]
        data.sort(reverse=reverse)
        for idx, (_, item) in enumerate(data):
            treeview.move(item, '', idx)
        treeview.heading(col, command=lambda: sort_treeview(treeview, col, not reverse))

    for col in columns:
        tree.heading(col, text=headings.get(col, col), command=lambda c=col: sort_treeview(tree, c, False))
        tree.column(col, anchor='w')
    tree.grid(row=1, column=0, columnspan=3, sticky="nsew")

    # Scrollbar
    scrollbar = ttk.Scrollbar(frm, orient="vertical", command=tree.yview)
    scrollbar.grid(row=1, column=3, sticky="ns")
    tree.configure(yscroll=scrollbar.set)

    # Details text box
    details_box = tk.Text(frm, height=15, width=80)
    details_box.grid(row=2, column=0, columnspan=4, pady=10)

    def on_select(event):
        sel = tree.selection()
        if not sel:
            return
        item = sel[0]
        internal = int(tree.set(item, 'internal_id'))
        details_box.delete('1.0', tk.END)
        for rec in records:
            if rec[0] == internal:
                json_str = rec[4]
                try:
                    data = json.loads(json_str)
                    details_box.insert(tk.END, json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    details_box.insert(tk.END, json_str)
                break

    # Bind events
    tree.bind('<<TreeviewSelect>>', on_select)
    parent.bind('<<CheckpointAdded>>', lambda e: load_from_db())

    # Eerste load
    load_from_db()

    return viewer
