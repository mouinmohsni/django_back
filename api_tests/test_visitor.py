# api_tests/test_visitor.py
import requests
from datetime import datetime
from .config import BASE_URL, log_test, clear_log_file

# --- VARIABLES DE TEST ---
# On utilise un ID élevé pour les tests de détail/modification/suppression
# afin de ne pas dépendre d'une donnée existante.
# L'API devrait renvoyer 401 (Unauthorized) avant même de vérifier si l'ID existe (404).
DUMMY_ID = 1


def run_visitor_tests():
    """
    Exécute tous les tests pour un utilisateur non authentifié (visiteur)
    en se basant sur la liste complète des endpoints.
    """

    print("\n" + "=" * 50)
    print("===== 👤 DÉBUT DES TESTS COMPLETS POUR LE VISITEUR =====")
    print("=" * 50)

    headers = {}  # Le visiteur n'a pas de token d'authentification

    # --- Section: /activities ---
    print("\n--- Tests sur /activities ---")
    log_test("Visiteur - PEUT lister les activités", requests.get(f"{BASE_URL}/activities/", headers=headers), 200)
    log_test("Visiteur - PEUT voir le détail d'une activité",
             requests.get(f"{BASE_URL}/activities/1/", headers=headers), 200)  # Note: ID 1 doit exister
    log_test("Visiteur - Ne peut PAS créer une activité",
             requests.post(f"{BASE_URL}/activities/", headers=headers, json={}), 401)
    log_test("Visiteur - Ne peut PAS modifier (PUT) une activité",
             requests.put(f"{BASE_URL}/activities/{DUMMY_ID}/", headers=headers, json={}), 401)
    log_test("Visiteur - Ne peut PAS modifier (PATCH) une activité",
             requests.patch(f"{BASE_URL}/activities/{DUMMY_ID}/", headers=headers, json={}), 401)
    log_test("Visiteur - Ne peut PAS supprimer une activité",
             requests.delete(f"{BASE_URL}/activities/{DUMMY_ID}/", headers=headers), 401)

    # --- Section: /bookings ---
    print("\n--- Tests sur /bookings ---")
    log_test("Visiteur - Ne peut PAS lister les réservations", requests.get(f"{BASE_URL}/bookings/", headers=headers),
             401)
    log_test("Visiteur - Ne peut PAS créer une réservation",
             requests.post(f"{BASE_URL}/bookings/", headers=headers, json={}), 401)
    log_test("Visiteur - Ne peut PAS supprimer une réservation",
             requests.delete(f"{BASE_URL}/bookings/{DUMMY_ID}/", headers=headers), 401)

    # --- Section: /companies ---
    print("\n--- Tests sur /companies ---")
    log_test("Visiteur - PEUT lister les entreprises", requests.get(f"{BASE_URL}/companies/", headers=headers), 200)
    log_test("Visiteur - PEUT voir le détail d'une entreprise",
             requests.get(f"{BASE_URL}/companies/1/", headers=headers), 200)  # Note: ID 1 doit exister
    log_test("Visiteur - Ne peut PAS créer une entreprise",
             requests.post(f"{BASE_URL}/companies/", headers=headers, json={}), 401)
    log_test("Visiteur - Ne peut PAS modifier (PUT) une entreprise",
             requests.put(f"{BASE_URL}/companies/{DUMMY_ID}/", headers=headers, json={}), 401)
    log_test("Visiteur - Ne peut PAS modifier (PATCH) une entreprise",
             requests.patch(f"{BASE_URL}/companies/{DUMMY_ID}/", headers=headers, json={}), 401)
    log_test("Visiteur - Ne peut PAS supprimer une entreprise",
             requests.delete(f"{BASE_URL}/companies/{DUMMY_ID}/", headers=headers), 401)

    # --- Section: Authentification & Inscription ---
    print("\n--- Tests sur /register et /token ---")
    new_email = f"visitor_test_{datetime.now().strftime('%H%M%S')}@test.com"
    log_test(
        "Visiteur - PEUT s'inscrire comme 'personal'",
        requests.post(f"{BASE_URL}/register/", headers=headers, json={
            "email": new_email,
            # --- CORRECTION ICI ---
            "password": "a_strong_password_123",
            "username": "test"
        }),
        201
    )
    log_test("Visiteur - Ne peut PAS s'inscrire comme 'business'",
             requests.post(f"{BASE_URL}/register-business/", headers=headers, json={}), 401)
    # Le test pour /token/ et /token/refresh/ est moins pertinent ici car ils sont faits pour fonctionner.

    # --- Section: /users ---
    print("\n--- Tests sur /users ---")
    log_test("Visiteur - PEUT lister les utilisateurs (coachs)", requests.get(f"{BASE_URL}/users/", headers=headers),
             200)
    log_test("Visiteur - PEUT voir le détail d'un utilisateur (coach)",
             requests.get(f"{BASE_URL}/users/1/", headers=headers), 200)  # Note: ID 1 doit être un coach
    log_test("Visiteur - Ne peut PAS voir son profil via /me/", requests.get(f"{BASE_URL}/users/me/", headers=headers),
             401)
    log_test("Visiteur - Ne peut PAS créer un utilisateur",
             requests.post(f"{BASE_URL}/users/", headers=headers, json={}), 401)
    log_test("Visiteur - Ne peut PAS modifier (PUT) un utilisateur",
             requests.put(f"{BASE_URL}/users/{DUMMY_ID}/", headers=headers, json={}), 401)
    log_test("Visiteur - Ne peut PAS modifier (PATCH) un utilisateur",
             requests.patch(f"{BASE_URL}/users/{DUMMY_ID}/", headers=headers, json={}), 401)
    log_test("Visiteur - Ne peut PAS supprimer un utilisateur",
             requests.delete(f"{BASE_URL}/users/{DUMMY_ID}/", headers=headers), 401)
    log_test("Visiteur - Ne peut PAS ajouter un coach",
             requests.post(f"{BASE_URL}/users/add-coach/", headers=headers, json={}), 401)
    log_test("Visiteur - Ne peut PAS retirer un coach",
             requests.post(f"{BASE_URL}/users/{DUMMY_ID}/remove-coach/", headers=headers, json={}), 401)

    print("\n===== 👤 FIN DES TESTS COMPLETS POUR LE VISITEUR =====")


if __name__ == "__main__":
    # Pour que les tests soient valides, assurez-vous d'avoir au moins :
    # - une activité avec l'ID 1
    # - une entreprise avec l'ID 1
    # - un utilisateur (coach) avec l'ID 1
    clear_log_file()
    run_visitor_tests()
    print("\n--- Tous les tests du visiteur sont terminés. Consultez api_test_log.txt ---")
