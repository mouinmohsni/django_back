from django.db import models

from django.db import models
from django.conf import settings

# On importe les modèles auxquels on veut se lier
from activities.models import Activity

class Booking(models.Model):
    """
    Modèle de Réservation (Booking).
    Lie un Utilisateur (client) à une Activité.
    C'est le "contrat" de participation.
    """
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'En attente'
        CONFIRMED = 'confirmed', 'Confirmée'
        CANCELLED = 'cancelled', 'Annulée'

    # --- Liaisons ---
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE, # Si l'activité est annulée, les réservations le sont aussi.
        related_name='bookings',
        verbose_name="Activité réservée"
    )
    attendee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Si l'utilisateur supprime son compte, ses réservations aussi.
        related_name='bookings_as_attendee',  # ✅ CORRIGÉ : évite le conflit avec activity.bookings
        verbose_name="Participant"
    )

    # --- Informations sur la réservation ---
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.CONFIRMED, # On peut décider que par défaut, une réservation est confirmée.
        verbose_name="Statut"
    )

    booking_time = models.DateTimeField(
        auto_now_add=True, # La date et l'heure de la réservation sont enregistrées automatiquement.
        verbose_name="Date de réservation"
    )
    # On pourrait ajouter plus de champs ici plus tard (prix payé, etc.)

    class Meta:
        # Cette contrainte garantit qu'un utilisateur ne peut pas s'inscrire deux fois à la même activité.
        unique_together = ('activity', 'attendee')
        ordering = ['-booking_time']
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

    def __str__(self):
        return f"{self.attendee} -> {self.activity.name} ({self.get_status_display()})"