# api_tests/test_coach_user.py
import requests
from .config import BASE_URL, log_test


def run_coach_user_tests(context):
    """
    Exécute tous les tests pour un utilisateur 'coach' authentifié.
    """
    print("\n" + "=" * 50)
    print("===== 🤸‍♀️ DÉBUT DES TESTS POUR L'UTILISATEUR 'COACH' =====")
    print("=" * 50)

    # Contexte pour le coach 1 (instructeur de l'activité 1)
    user_context = context['coach_1']
    headers = {"Authorization": f"Bearer {user_context['token']}"}
    my_user_id = user_context['user_id']

    # ID du client qui a réservé son cours
    participant_id = context['personal_1']['user_id']

    # --- Section: /users ---
    print("\n--- Tests sur /users ---")
    log_test("Coach - PEUT voir son propre profil via /me/", requests.get(f"{BASE_URL}/users/me/", headers=headers),
             200)
    log_test("Coach - PEUT modifier son propre profil",
             requests.patch(f"{BASE_URL}/users/{my_user_id}/", headers=headers, json={"username": "Coach_Updated"}),
             200)

    # Test de la logique de visibilité
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    log_test("Coach - PEUT lister les utilisateurs (devrait voir les participants et autres coachs)", response, 200)
    if response.status_code == 200:
        user_ids_seen = [user['id'] for user in response.json()]
        if participant_id in user_ids_seen:
            print(f"    ✅ SUCCÈS : Le participant (ID: {participant_id}) est bien visible.")
        else:
            print(f"    ❌ ÉCHEC : Le participant (ID: {participant_id}) n'est PAS visible.")

    # --- Section: Actions Interdites ---
    print("\n--- Tests sur les actions interdites ---")
    log_test("Coach - Ne peut PAS créer d'activité",
             requests.post(f"{BASE_URL}/activities/", headers=headers, json={"name": "Cours non autorisé"}), 403)
    log_test("Coach - Ne peut PAS modifier une entreprise",
             requests.patch(f"{BASE_URL}/companies/1/", headers=headers, json={"name": "Hack attempt"}), 403)
    log_test("Coach - Ne peut PAS ajouter un autre coach",
             requests.post(f"{BASE_URL}/users/add-coach/", headers=headers, json={"email": "another@coach.com"}), 403)
    log_test("Coach - Ne peut PAS réserver une activité",
             requests.post(f"{BASE_URL}/bookings/", headers=headers, json={"activity": context['activity_1_id']}), 400)

    print("\n===== 🤸‍♀️ FIN DES TESTS POUR L'UTILISATEUR 'COACH' =====")
