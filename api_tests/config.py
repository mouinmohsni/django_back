# api_tests/config.py
import json
import requests  # <-- Assurez-vous que requests est importé
from datetime import datetime

# --- CONFIGURATION PARTAGÉE ---
BASE_URL = "http://127.0.0.1:8000/api"
LOG_FILE = "api_test_log.txt"


# --- FONCTIONS UTILITAIRES PARTAGÉES ---

def log_test(title, response, expected_status):
    """Affiche et enregistre le résultat d'un test."""
    status = response.status_code
    result = "✅ SUCCÈS" if status == expected_status else f"❌ ÉCHEC (attendu: {expected_status}, reçu: {status})"

    log_entry = f"""
--------------------------------------------------
[TEST]: # "{title}"
[RÉSULTAT]: # "{result}"
[URL]: # "{response.request.method} {response.url}"
[RÉPONSE]
{json.dumps(response.json(), indent=2, ensure_ascii=False) if response.content and 'application/json' in response.headers.get('Content-Type', '') else response.text}
--------------------------------------------------
"""
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)


def clear_log_file():
    """Efface le fichier de log au début d'une session de test."""
    with open(LOG_FILE, "w") as f:
        f.write(f"--- Début des tests API pour SportRadar le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")


# --- NOUVELLE FONCTION AJOUTÉE ICI ---
def get_token(email, password):
    """Obtient un token JWT pour un utilisateur."""
    try:
        response = requests.post(f"{BASE_URL}/token/", data={"email": email, "password": password})
        if response.status_code == 200:
            token = response.json().get("access")
            print(f"    ➡️  Token obtenu pour {email}")
            return token
        else:
            print(f"    ❌ Impossible d'obtenir le token pour {email}. Statut: {response.status_code}")
            log_test(f"Échec de l'obtention du token pour {email}", response, 200)
            return None
    except requests.exceptions.ConnectionError as e:
        print(
            f"FATAL: Impossible de se connecter au serveur à {BASE_URL}. Assurez-vous que le serveur Django est lancé.")
        return None
