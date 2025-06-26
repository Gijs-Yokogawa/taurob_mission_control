# api/client.py

import requests
import urllib3
from requests.auth import HTTPBasicAuth
from storage.manager import save_checkpoint, delete_checkpoint_local

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://10.1.0.1:8443"
API_PREFIX = "/basic/mission_editor/data_model"
VERIFY_SSL = False

session = requests.Session()
credentials = {"username": None, "password": None}


def set_credentials(username, password):
    print("[API] → set_credentials() aangeroepen")
    credentials["username"] = username
    credentials["password"] = password
    print(f"[API] Credentials ingesteld: username='{username}', password='{'*' * len(password)}'")


def is_authenticated():
    print("[API] → is_authenticated() aangeroepen")
    if not credentials["username"] or not credentials["password"]:
        print("[API] Geen gebruikersnaam of wachtwoord ingesteld.")
        return False

    url = BASE_URL
    print(f"[API] Login-test via GET naar: {url}")

    try:
        response = session.get(url, auth=HTTPBasicAuth(credentials["username"], credentials["password"]), verify=VERIFY_SSL)
        print(f"[API] Statuscode: {response.status_code}")
        print(f"[API] Response body (max 300): {response.text[:300]}")
        return response.status_code == 200
    except Exception as e:
        print(f"[API] Fout bij login: {e}")
        return False


def get_checkpoints():
    print("[API] → get_checkpoints() aangeroepen")
    url = f"{BASE_URL}{API_PREFIX}/editor/action/all"
    print(f"[API] Ophalen ALLE checkpoints via: {url}")
    response = session.get(url, auth=HTTPBasicAuth(credentials["username"], credentials["password"]), verify=VERIFY_SSL)
    response.raise_for_status()
    #print(response.json())
    return response.json()


def delete_checkpoint(checkpoint_id):
    print("[API] → delete_checkpoint() aangeroepen")
    url = f"{BASE_URL}{API_PREFIX}/editor/action/{checkpoint_id}"
    print(f"[API] Verwijderen checkpoint ID {checkpoint_id}: {url}")
    response = session.delete(url, auth=HTTPBasicAuth(credentials["username"], credentials["password"]), verify=VERIFY_SSL)
    response.raise_for_status()

    # Als API succesvol verwijdert, ook lokaal verwijderen
    delete_checkpoint_local(checkpoint_id)
    return response.status_code == 200


def sync_from_robot():
    print("[API] → sync_from_robot() aangeroepen")
    url = f"{BASE_URL}{API_PREFIX}/editor/sync"
    print(f"[API] Start sync via: {url}")
    response = session.post(url, auth=HTTPBasicAuth(credentials["username"], credentials["password"]), verify=VERIFY_SSL)
    response.raise_for_status()
    return response.status_code == 200


def create_checkpoint(payload):
    print("[API] → create_checkpoint() aangeroepen")
    url = f"{BASE_URL}{API_PREFIX}/editor/action"
    print(f"[API] Nieuw checkpoint aanmaken via: {url}")
    print(f"[API] Payload: {payload}")
    response = session.post(url, json=payload, auth=HTTPBasicAuth(credentials["username"], credentials["password"]), verify=VERIFY_SSL)
    response.raise_for_status()
    return response.json()


def update_checkpoint(checkpoint_id, payload):
    """Update an existing checkpoint via the API."""
    print("[API] → update_checkpoint() aangeroepen")
    url = f"{BASE_URL}{API_PREFIX}/editor/action/{checkpoint_id}"
    print(f"[API] Bijwerken checkpoint ID {checkpoint_id} via: {url}")
    print(f"[API] Payload: {payload}")
    response = session.put(
        url,
        json=payload,
        auth=HTTPBasicAuth(credentials["username"], credentials["password"]),
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    return response.json()


def create_and_save_checkpoint(payload):
    print("[FLOW] → create_and_save_checkpoint() gestart")
    api_response = create_checkpoint(payload)
    save_checkpoint(api_response)
    print("[FLOW] Checkpoint succesvol aangemaakt en lokaal opgeslagen")
    return api_response
