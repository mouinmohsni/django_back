# api_tests/test_personal_user.py
import requests
from .config import BASE_URL, log_test


def run_personal_user_tests(context):
    """
    Exécute tous les tests pour un utilisateur 'personal' authentifié.
    """
    print("\n" + "=" * 50)
    print("===== 🏃‍♂️ DÉBUT DES TESTS POUR L'UTILISATEUR 'PERSONAL' =====")
    print("=" * 50)

    # Contexte pour le client 1
    user_context = context['personal_1']
    headers = {"Authorization": f"Bearer {user_context['token']}"}
    my_user_id = user_context['user_id']

    # Données pour les tests
    coach_id = context['coach_1']['user_id']
    other_personal_user_id = context['personal_2']['user_id']
    activity_id = context['activity_1_id']
    my_booking_id = context['booking_1_id']

    # --- Section: /users ---
    print("\n--- Tests sur /users ---")
    log_test("Personal - PEUT voir son propre profil via /me/", requests.get(f"{BASE_URL}/users/me/", headers=headers),
             200)

    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    log_test("Personal - PEUT lister les utilisateurs (devrait voir les coachs et lui-même)", response, 200)
    if response.status_code == 200:
        user_ids_seen = [user['id'] for user in response.json()]
        if coach_id in user_ids_seen and my_user_id in user_ids_seen:
            print(f"    ✅ SUCCÈS : Le coach (ID: {coach_id}) et soi-même sont visibles.")
        if other_personal_user_id in user_ids_seen:
            print(f"    ❌ ÉCHEC : Un autre client (ID: {other_personal_user_id}) est visible.")
        else:
            print(f"    ✅ SUCCÈS : Un autre client (ID: {other_personal_user_id}) est bien caché.")

    # --- Section: /bookings ---
    print("\n--- Tests sur /bookings ---")
    log_test("Personal - PEUT lister SES propres réservations", requests.get(f"{BASE_URL}/bookings/", headers=headers),
             200)
    log_test("Personal - PEUT annuler sa propre réservation",
             requests.delete(f"{BASE_URL}/bookings/{my_booking_id}/", headers=headers), 204)
    # On essaie de réserver à nouveau après annulation
    log_test("Personal - PEUT réserver une activité (après avoir annulé)",
             requests.post(f"{BASE_URL}/bookings/", headers=headers, json={"activity": activity_id}), 201)

    # --- Section: Actions Interdites ---
    print("\n--- Tests sur les actions interdites ---")
    log_test("Personal - Ne peut PAS créer d'entreprise",
             requests.post(f"{BASE_URL}/companies/", headers=headers, json={"name": "My Personal Company"}), 403)
    log_test("Personal - Ne peut PAS créer d'activité",
             requests.post(f"{BASE_URL}/activities/", headers=headers, json={"name": "My Personal Activity"}), 403)
    log_test("Personal - Ne peut PAS modifier le profil d'un autre (coach)",
             requests.patch(f"{BASE_URL}/users/{coach_id}/", headers=headers, json={"username": "hack"}), 403)

    print("\n===== 🏃‍♂️ FIN DES TESTS POUR L'UTILISATEUR 'PERSONAL' =====")
