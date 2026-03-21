# activities/models.py

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
# On importe le modèle Company pour créer la liaison
from companies.models import Company
from django.db.models import Sum


class Activity(models.Model):
    """
    Représente une activité sportive proposée par une entreprise.
    La liste des participants est gérée par le modèle 'Booking' dans l'application 'bookings'.
    """

    # --- Énumérations pour des choix de données propres et cohérents ---
    class LevelChoices(models.TextChoices):
        ALL = 'all', 'Tous niveaux'
        BEGINNER = 'beginner', 'Débutant'
        INTERMEDIATE = 'intermediate', 'Intermédiaire'
        ADVANCED = 'advanced', 'Avancé'

    class VenueChoices(models.TextChoices):
        INDOOR = 'indoor', 'Intérieur'
        OUTDOOR = 'outdoor', 'Extérieur'

    # --- Informations de base sur l'activité ---
    name = models.CharField(max_length=200, verbose_name="Nom de l'activité")
    description = models.TextField(blank=True, verbose_name="Description")
    category = models.CharField(max_length=50, blank=True, verbose_name="Catégorie")
    image = models.ImageField(
        upload_to='activity_images/',
        blank=True,
        null=True,
        verbose_name="Image de l'activité"
    )

    location_address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Adresse spécifique de l'activité"
    )

    # --- Liaisons aux autres modèles (le plus important) ---
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE, # Si l'entreprise est supprimée, ses activités le sont aussi.
        related_name='activities',
        verbose_name="Entreprise organisatrice"
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Si le coach est supprimé, l'activité reste mais sans instructeur.
        null=True,
        blank=True,
        # On ne peut choisir qu'un utilisateur de type 'coach' dans l'admin.
        limit_choices_to={'type': 'coach'},
        related_name='instructed_activities',
        verbose_name="Instructeur"
    )

    # --- Date, Heure et Durée ---
    start_time = models.DateTimeField(verbose_name="Date et heure de début")
    duration = models.DurationField(verbose_name="Durée (ex: 1h30min)")

    # --- Détails pratiques ---
    max_participants = models.PositiveIntegerField(
        default=20,
        verbose_name="Nombre maximum de participants"
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name="Prix"
    )
    level = models.CharField(
        max_length=20,
        choices=LevelChoices.choices,
        default=LevelChoices.ALL,
        verbose_name="Niveau requis"
    )
    venue = models.CharField(
        max_length=10,
        choices=VenueChoices.choices,
        default=VenueChoices.INDOOR,
        verbose_name="Lieu (Intérieur/Extérieur)"
     )

    sport_zen = models.BooleanField(
        default=False,
        verbose_name="Label SportZen",
        help_text="Cocher si l'activité est accessible, non-compétitive et bienveillante."
    )


    # --- Métadonnées ---
    is_public = models.BooleanField(
        default=True,
        verbose_name="Publique",
        help_text="Décocher pour masquer l'activité du site public."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def participants_count(self):
        """
        Calcule la somme totale des places réservées (nb_persone)
        pour cette activité via la table Booking.
        """
        # On utilise 'bookings' car c'est le related_name dans votre modèle Booking
        result = self.bookings.aggregate(total=Sum('nb_persone'))['total']
        return result or 0

    @property
    def places_disponibles(self):
        """
        Retourne le nombre de places restantes.
        """
        return max(0, self.max_participants - self.participants_count)

    class Meta:
        ordering = ['start_time'] # Les activités sont triées par date de début par défaut.
        verbose_name = "Activité"
        verbose_name_plural = "Activités"

    def __str__(self):
        # Cette méthode définit comment l'objet est affiché dans l'admin de Django.
        return f"{self.name} chez {self.company.name} le {self.start_time.strftime('%d/%m/%Y')}"


class ActivityRating(models.Model):
    """
    Stocke la note donnée par un utilisateur à une activité.
    """
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='ratings', # Très important pour les calculs
        verbose_name="Activité"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,  # <-- AJOUTER : Le champ est optionnel dans les formulaires Django
        null=True,  # <-- AJOUTER : La base de données peut stocker une valeur NULL
        verbose_name="Note (sur 5)"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Commentaire"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un utilisateur ne peut noter une activité qu'une seule fois.
        unique_together = ('activity', 'user')
        verbose_name = "Note d'activité"
        verbose_name_plural = "Notes d'activités"

    def __str__(self):
        return f"Note de {self.user} pour {self.activity.name}: {self.score}/5"