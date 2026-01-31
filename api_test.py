from users.models import CustomUser

# Trouve l'utilisateur
user = CustomUser.objects.get(email='personal2@test.com')

# Change son mot de passe (ça le hashera automatiquement)
user.set_password('a_strong_password_123')
user.save()

print(f"Mot de passe mis à jour pour {user.email}")

