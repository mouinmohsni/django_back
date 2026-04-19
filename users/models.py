# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

from users.utils import random_avatar_name


def get_default_preferences():
    return {
        "level": "",  # ex: "beginner", "intermediate"
        "location": "",  # ex: "Paris", "Lyon"
        "objectives": []  # ex: ["perte de poids", "endurance cardio"]
    }


class CustomUser(AbstractUser):
    # --- Étape 1: Définir les NOUVEAUX types comme des variables de classe ---
    USER_TYPE_PERSONAL = 'personal'
    USER_TYPE_BUSINESS = 'business'
    USER_TYPE_COACH = 'coach'  # Le nouveau rôle que vous avez suggéré !

    # --- Étape 2: Mettre à jour les choix ---
    USER_TYPE_CHOICES = (
        (USER_TYPE_PERSONAL, 'Client'),
        (USER_TYPE_BUSINESS, 'Propriétaire'),
        (USER_TYPE_COACH, 'Coach'),
    )

    # --- Champs du modèle ---
    email = models.EmailField(unique=True)

    # ✅ AJOUT : Prénom et nom de famille
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Nom de famille")

    # Le champ 'type' utilise maintenant nos nouveaux rôles.
    # On peut mettre 'personal' par défaut pour les inscriptions publiques.
    type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default=USER_TYPE_PERSONAL,
        verbose_name="Rôle de l'utilisateur"
    )

    # La relation que nous avons définie précédemment est toujours parfaite.
    # Un 'business' ou un 'coach' sera lié à une entreprise.
    # Un 'personal' aura ce champ à NULL.
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name="Entreprise affiliée"
    )

    # ... (avatar, preferences, etc. restent les mêmes)
    avatar = models.ImageField(upload_to=random_avatar_name, null=True, blank=True)
    preferences = models.JSONField(default=get_default_preferences, blank=True)
    numero_siret = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        verbose_name="Numéro SIRET"
    )

    # --- Configuration du modèle (inchangée) ---
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.email} ({self.get_type_display()})"  # get_type_display() est une méthode magique de Django
