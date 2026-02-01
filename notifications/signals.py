from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from .models import Notification


# --- 1. CLIENT & COACH : RÉSERVATIONS ---
@receiver(post_save,
          sender='bookings.Booking')  # Utilisation du nom du modèle en string pour éviter les erreurs d'import
def notify_booking_events(sender, instance, created, **kwargs):
    if created:
        # Import local du modèle User
        User = apps.get_model('users', 'CustomUser')

        # Pour le Client (Personal) : Confirmation
        Notification.objects.create(
            user=instance.user,
            type='booking',
            title='Réservation confirmée',
            message=f"Votre place est réservée pour : {instance.activity.name}."
        )

        # Pour le Coach : Nouvelle inscription
        if instance.activity.instructor:
            Notification.objects.create(
                user=instance.activity.instructor,
                type='booking',
                title='Nouvelle inscription',
                message=f"{instance.user.first_name} s'est inscrit à votre cours : {instance.activity.name}."
            )

        # Pour le Business : Nouvelle réservation
        business_owner = User.objects.filter(company=instance.activity.company, type='business').first()
        if business_owner:
            Notification.objects.create(
                user=business_owner,
                type='booking',
                title='Nouvelle réservation',
                message=f"Nouvelle réservation reçue pour {instance.activity.name}."
            )


# --- 2. COACH : ASSIGNATION À UNE ACTIVITÉ ---
@receiver(post_save, sender='activities.Activity')
def notify_coach_assignment(sender, instance, created, **kwargs):
    # Si un instructeur est assigné (nouveau ou changement)
    if instance.instructor:
        Notification.objects.create(
            user=instance.instructor,
            type='assignment',
            title='Nouvelle assignation',
            message=f"Vous avez été assigné à l'activité : {instance.name}."
        )


# --- 3. CLIENT & COACH : ANNULATION D'ACTIVITÉ ---
@receiver(post_delete, sender='activities.Activity')
def notify_activity_cancelled(sender, instance, **kwargs):
    if instance.instructor:
        Notification.objects.create(
            user=instance.instructor,
            type='cancellation',
            title='Activité annulée',
            message=f"L'activité '{instance.name}' à laquelle vous étiez assigné a été annulée."
        )


# --- 4. ADMIN : NOUVELLE INSCRIPTION ---
@receiver(post_save, sender='users.CustomUser')
def notify_admin_new_user(sender, instance, created, **kwargs):
    if created:
        User = apps.get_model('users', 'CustomUser')
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                type='info',
                title='Nouvel utilisateur',
                message=f"Un nouveau {instance.type} s'est inscrit : {instance.username}."
            )


# --- 5. FONCTIONS UTILITAIRES ---

def notify_resignation_request(coach, business_owner):
    Notification.objects.create(
        user=business_owner,
        type='resignation',
        title='Demande de démission',
        message=f"Le coach {coach.first_name} {coach.last_name} souhaite démissionner de votre salle.",
        related_object_type='user',
        related_object_id=coach.id
    )
