import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Suppress InsecureRequestWarning for unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_BASE_URL = "https://10.1.0.1:8443"

def login(username: str, password: str) -> str:
    response = requests.get(API_BASE_URL, auth=HTTPBasicAuth(username, password), verify=False)
    response.raise_for_status()
    return username  # token simulated by username

def create_checkpoint(data: dict, username: str) -> int:
    response = requests.post(
        API_BASE_URL,
        json=data,
        auth=HTTPBasicAuth(username, ''),
        verify=False
    )
    response.raise_for_status()
    return response.json().get("id")
