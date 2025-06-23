# gui/template_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path
from models.template_generator import generate_empty_checkpoint_template
from storage.manager import save_checkpoint

# Zorg dat de template-folder bestaat
TEMPLATE_OUTPUT_PATH = Path("checkpoints/templates")
TEMPLATE_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# API-endpoint voor aanmaken van checkpoints
API_POST_URL = (
    "https://10.1.0.1:8443/basic/mission_editor/data_model/editor/action"
)


def launch_template_generator(parent, username, password):
    """
    Opent een venster om een nieuw checkpoint-template te genereren,
    stuurt het naar de API, en slaat het lokale en in de DB op.
    """
    win = tk.Toplevel(parent)
    win.title("Genereer Leeg Checkpoint Template")
    win.grab_set()  # modal

    frm = ttk.Frame(win, padding=10)
    frm.grid(sticky="nsew")
    frm.columnconfigure(1, weight=1)

    # Naam van checkpoint
    ttk.Label(frm, text="Naam van Checkpoint:").grid(column=0, row=0, sticky='w')
    name_entry = ttk.Entry(frm)
    name_entry.grid(column=1, row=0, sticky='ew')

    # Type checkpoint
    ttk.Label(frm, text="Type Checkpoint:").grid(column=0, row=1, sticky='w')
    type_menu = ttk.Combobox(
        frm,
        values=['drive', 'dock', 'measure'],
        state='readonly'
    )
    type_menu.grid(column=1, row=1, sticky='ew')
    type_menu.set('drive')  # standaardkeuze

    def on_generate():
        name = name_entry.get().strip()
        ctype = type_menu.get().strip().lower()

        # Genereer lokale template
        try:
            template = generate_empty_checkpoint_template(name, ctype)
        except ValueError as e:
            messagebox.showerror("Fout", str(e), parent=win)
            return

        # Bereid payload voor (zonder ActionID)
        payload = {
            key: template[key]
            for key in template
            if key != 'ActionID'
        }

        # API-call om ActionID te verkrijgen
        try:
            response = requests.post(
                API_POST_URL,
                auth=HTTPBasicAuth(username, password),
                headers={
                    'accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                json=payload,
                verify=False
            )
            response.raise_for_status()
            result = response.json()
            action_id = result.get('ActionID')
            if action_id is None:
                raise KeyError("Geen ActionID in API-response.")
        except Exception as e:
            messagebox.showerror("API-fout", str(e), parent=win)
            return

        # Voeg ontvangen ActionID toe aan de template
        template['ActionID'] = action_id

        # Schrijf volledige JSON-template naar bestand
        filename = f"{name.replace(' ', '_')}_{ctype}_{action_id}.json"
        out_path = TEMPLATE_OUTPUT_PATH / filename
        with open(out_path, 'w') as f:
            json.dump(template, f, indent=2)

        # Opslaan in lokale DB
        save_checkpoint(template, checkpoint_id=action_id)

        # Bericht voor open viewers om te updaten
        parent.event_generate('<<CheckpointAdded>>', when='tail')

        messagebox.showinfo(
            "Succes",
            f"Template opgeslagen als: {out_path.name}\nID: {action_id}",
            parent=win
        )
        win.destroy()

    # Genereer-knop
    btn = ttk.Button(frm, text="Genereer Template", command=on_generate)
    btn.grid(column=0, row=2, columnspan=2, pady=10, sticky='ew')

    win.wait_window()
