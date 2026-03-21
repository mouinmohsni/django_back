from django.db import models
from django.conf import settings
from activities.models import Activity

class Booking(models.Model):
    """
    Modèle de Réservation (Booking).
    Lie un Utilisateur (attendee) à une Activité avec un nombre de places (nb_persone).
    """
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'En attente'
        CONFIRMED = 'confirmed', 'Confirmée'
        CANCELLED = 'cancelled', 'Annulée'

    # --- Liaisons ---
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="Activité réservée"
    )
    attendee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings_as_attendee',
        verbose_name="Participant"
    )

    # --- Nombre de personnes (Le champ clé) ---
    nb_persone = models.PositiveIntegerField(
        default=1,
        verbose_name="Nombre de participants"
    )

    # --- Informations sur la réservation ---
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.CONFIRMED,
        verbose_name="Statut"
    )

    booking_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de réservation"
    )

    class Meta:
        # Empêche un utilisateur d'avoir deux lignes pour la même activité
        unique_together = ('activity', 'attendee')
        ordering = ['-booking_time']
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

    def __str__(self):
        activity_title = getattr(self.activity, 'title', 'Activité')
        return f"{self.attendee} -> {activity_title} ({self.nb_persone} pers.)"
