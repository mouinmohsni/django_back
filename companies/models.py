# companies/models.py

from django.db import models

class Company(models.Model):
    """
    Représente le profil d'une entreprise, d'une association ou d'un coach.
    """

    # --- Informations de base ---
    name = models.CharField(
        max_length=200,
        verbose_name="Nom de l'entreprise"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    logo = models.ImageField(
        upload_to='company_logos/',
        blank=True,
        null=True,
        verbose_name="Logo"
    )

    # --- Adresse ---
    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Adresse"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ville"
    )
    zip_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Code Postal"
    )

    # --- Contact ---
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Numéro de téléphone"
    )
    website = models.URLField(
        blank=True,
        verbose_name="Site Web"
    )

    # --- Labels et Badges (comme demandé dans le cahier des charges) ---
    sport_zen = models.BooleanField(
        default=False,
        verbose_name="Label SportZen",
        help_text="Cocher si l'entreprise propose des activités accessibles, non-compétitives et bienveillantes."
    )

    # --- Métadonnées ---
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Vérifiée",
        help_text="Cocher si le profil de l'entreprise a été vérifié par un administrateur."
    )
    numero_siret = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        verbose_name="Numéro SIRET"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
        ordering = ['name']

    def __str__(self):
        return self.name
