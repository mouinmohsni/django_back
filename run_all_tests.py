# run_all_tests.py
import time

import requests
import os
from datetime import datetime, timedelta

# Importe les fonctions de nos fichiers de test
from api_tests.config import BASE_URL, clear_log_file, get_token
from api_tests.test_visitor import run_visitor_tests


from api_tests.test_business_user import run_business_user_tests # A décommenter plus tard
from api_tests.test_coach_user import run_coach_user_tests       # A décommenter plus tard
from api_tests.test_personal_user import run_personal_user_tests # A décommenter plus tard


def setup_test_environment():
    """
    Nettoie l'environnement et peuple la BDD avec des données de test.
    Retourne un dictionnaire 'context' avec tous les tokens et IDs.
    """
    print("\n" + "=" * 60)
    print("🚀 DÉMARRAGE DU SETUP DE L'ENVIRONNEMENT DE TEST")
    print("=" * 60)

    # --- 1. Nettoyage de la base de données ---
    print("\n[SETUP] Nettoyage de la base de données (flush)...")
    #os.system("python manage.py flush --no-input")
    print("✅ Base de données nettoyée.")
    # --- 2. Connexion en tant que Super-Utilisateur (Admin) ---
    print("\n[SETUP] Connexion en tant qu'administrateur pré-existant...")
    admin_email = "admin@test.com"
    admin_pass = "a_strong_password_123"
    admin_user = "adminuser"
    admin_token = get_token(admin_email, admin_pass)
    if not admin_token:
        raise Exception(
            "CRITICAL: Impossible d'obtenir le token admin. "
            f"Assurez-vous d'avoir créé le super-utilisateur manuellement avec l'email '{admin_email}' "
            f"et le mot de passe '{admin_pass}' via 'manage.py createsuperuser'."
        )
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Admin connecté avec succès.")

    # --- 3. Création des données de test ---
    context = {'headers_admin': headers_admin}
    print("\n[SETUP] Création des utilisateurs, entreprises et activités...")

    # a) Utilisateurs Business et leurs Entreprises
    for i in range(1, 3):
        email = f"business{i}@test.com"
        user_res = requests.post(f"{BASE_URL}/register-business/", headers=headers_admin,
                                 json={"email": email, "password": admin_pass, "username": f"business_user_{i}"})
        token = get_token(email, admin_pass)
        user_id = user_res.json()['id']

        company_res = requests.post(f"{BASE_URL}/companies/", headers={"Authorization": f"Bearer {token}"},
                                    json={"name": f"Entreprise Business {i}"})
        company_id = company_res.json()['id']
        context[f'business_{i}'] = {'token': token, 'user_id': user_id, 'company_id': company_id}
        print(f"  -> Créé Business User {i} (ID: {user_id}) et Entreprise {i} (ID: {company_id})")

    # b) Utilisateurs Coach (assignés à l'entreprise 1)
    headers_business1 = {"Authorization": f"Bearer {context['business_1']['token']}"}
    for i in range(1, 3):
        email = f"coach{i}@test.com"
        coach_res = requests.post(f"{BASE_URL}/users/add-coach/", headers=headers_business1,
                                  json={"email": email, "password": admin_pass, "username": f"coach_user_{i}"})
        token = get_token(email, admin_pass)
        user_id = coach_res.json()['id']
        context[f'coach_{i}'] = {'token': token, 'user_id': user_id}
        print(f"  -> Créé Coach User {i} (ID: {user_id})")

    # c) Utilisateurs Personal
    for i in range(1, 3):
        email = f"personal{i}@test.com"
        user_res = requests.post(f"{BASE_URL}/register/",
                                 json={"email": email, "password": admin_pass, "username": f"personal_user_{i}"})
        token = get_token(email, admin_pass)
        user_id = user_res.json()['id']
        context[f'personal_{i}'] = {'token': token, 'user_id': user_id}
        print(f"  -> Créé Personal User {i} (ID: {user_id})")

        # d) Création d'une activité par l'entreprise 1 avec le coach 1
        print("\n[SETUP] Création de l'activité de test...")
        activity_payload = {
            "name": "Cours de Yoga Test",
            "duration": "01:30:00",
            "price": "25.00",
            "instructor_id": context['coach_1']['user_id'],
            # --- CHAMP AJOUTÉ ICI ---
            "start_time": (datetime.now() + timedelta(days=7)).isoformat()
        }
        activity_res = requests.post(f"{BASE_URL}/activities/", headers=headers_business1, json=activity_payload)

        # --- GESTION D'ERREUR AJOUTÉE ICI ---
        if activity_res.status_code != 201:
            print("--- DÉTAILS DE LA RÉPONSE D'ERREUR (Activité) ---")
            print(activity_res.json())
            print("-------------------------------------------------")
            raise Exception(f"Échec de la création de l'activité. Statut: {activity_res.status_code}")

        context['activity_1_id'] = activity_res.json()['id']
        print(f"  -> Créé Activité 1 (ID: {context['activity_1_id']})")

        # e) Création d'une réservation par l'utilisateur personal_1 pour l'activité 1
        print("\n[SETUP] Création de la réservation de test...")
        booking_payload = {"activity": context['activity_1_id']}
        booking_res = requests.post(f"{BASE_URL}/bookings/", headers=headers_personal1, json=booking_payload)

        # --- GESTION D'ERREUR AJOUTÉE ICI ---
        if booking_res.status_code != 201:
            print("--- DÉTAILS DE LA RÉPONSE D'ERREUR (Réservation) ---")
            print(booking_res.json())
            print("---------------------------------------------------")
            raise Exception(f"Échec de la création de la réservation. Statut: {booking_res.status_code}")

        context['booking_1_id'] = booking_res.json()['id']
        print(f"  -> Créé Réservation 1 (ID: {context['booking_1_id']})")

        print("=" * 60)
        print("✅ CONTEXTE DE TEST PRÊT.")
        print("=" * 60)
        return context


if __name__ == "__main__":
    # 1. Préparer l'environnement
    try:
        test_context = setup_test_environment()
    except Exception as e:
        print(f"\n❌ ERREUR FATALE pendant le setup : {e}")
        exit(1)

    # 2. Lancer la suite de tests
    print("\n" + "=" * 60)
    print("🏁 DÉMARRAGE DE LA SUITE DE TESTS COMPLÈTE")
    print("=" * 60)

    clear_log_file()

    # Test 1 : Visiteur
    run_visitor_tests(context=test_context)

    # Les tests suivants seront ajoutés ici au fur et à mesure
    # print("\n--- Lancement des tests pour l'utilisateur BUSINESS ---")
    run_business_user_tests(context=test_context)

    # print("\n--- Lancement des tests pour l'utilisateur COACH ---")
    run_coach_user_tests(context=test_context)

    # print("\n--- Lancement des tests pour l'utilisateur PERSONAL ---")
    run_personal_user_tests(context=test_context)

    print("\n\n🎉 Suite de tests terminée. Consultez le fichier api_test_log.txt pour les détails.")
