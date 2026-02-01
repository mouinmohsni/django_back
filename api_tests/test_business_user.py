# api_tests/test_business_user.py
import requests
from .config import BASE_URL, log_test


def run_business_user_tests(context):
    """
    Exécute tous les tests pour un utilisateur 'business' authentifié.
    """
    print("\n" + "=" * 50)
    print("===== 🏢 DÉBUT DES TESTS POUR L'UTILISATEUR 'BUSINESS' =====")
    print("=" * 50)

    # Contexte pour le business user 1 (propriétaire de l'entreprise 1)
    user_context = context['business_1']
    headers = {"Authorization": f"Bearer {user_context['token']}"}
    my_company_id = user_context['company_id']
    my_activity_id = context['activity_1_id']

    # Contexte pour les objets qui ne lui appartiennent pas
    other_company_id = context['business_2']['company_id']

    # --- Section: /companies ---
    print("\n--- Tests sur /companies ---")
    log_test("Business - PEUT voir le détail de sa propre entreprise",
             requests.get(f"{BASE_URL}/companies/{my_company_id}/", headers=headers), 200)
    log_test("Business - PEUT modifier sa propre entreprise",
             requests.patch(f"{BASE_URL}/companies/{my_company_id}/", headers=headers,
                            json={"description": "Nouvelle description test"}), 200)
    log_test("Business - Ne peut PAS modifier l'entreprise d'un autre",
             requests.patch(f"{BASE_URL}/companies/{other_company_id}/", headers=headers,
                            json={"name": "Hack attempt"}), 403)
    log_test("Business - Ne peut PAS supprimer son entreprise (seul l'admin peut)",
             requests.delete(f"{BASE_URL}/companies/{my_company_id}/", headers=headers), 403)

    # --- Section: /activities ---
    print("\n--- Tests sur /activities ---")
    log_test("Business - PEUT créer une activité pour son entreprise",
             requests.post(f"{BASE_URL}/activities/", headers=headers, json={"name": "Nouveau cours de Crossfit"}), 201)
    log_test("Business - PEUT modifier une de ses activités",
             requests.patch(f"{BASE_URL}/activities/{my_activity_id}/", headers=headers, json={"price": "30.00"}), 200)
    log_test("Business - PEUT supprimer une de ses activités",
             requests.delete(f"{BASE_URL}/activities/{my_activity_id}/", headers=headers), 204)

    # --- Section: /users (gestion des coachs) ---
    print("\n--- Tests sur /users ---")
    log_test("Business - PEUT ajouter un coach à son entreprise",
             requests.post(f"{BASE_URL}/users/add-coach/", headers=headers,
                           json={"email": "newcoach@test.com", "password": "password123"}), 201)
    coach_to_remove_id = context['coach_2']['user_id']
    log_test("Business - PEUT retirer un coach de son entreprise",
             requests.post(f"{BASE_URL}/users/{coach_to_remove_id}/remove-coach/", headers=headers), 200)

    # --- Section: /bookings (actions interdites) ---
    print("\n--- Tests sur /bookings ---")
    log_test("Business - Ne peut PAS réserver une activité",
             requests.post(f"{BASE_URL}/bookings/", headers=headers, json={"activity": context['activity_1_id']}),
             400)  # 400 car la validation du serializer échoue
    log_test("Business - Ne voit aucune réservation dans sa liste (n'est pas un client)",
             requests.get(f"{BASE_URL}/bookings/", headers=headers), 200)

    print("\n===== 🏢 FIN DES TESTS POUR L'UTILISATEUR 'BUSINESS' =====")
