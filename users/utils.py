# users/utils.py
import os
import uuid
from django.utils.deconstruct import deconstructible

@deconstructible
class RandomFileName(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        # Récupère l'extension du fichier (ex: .jpg, .png)
        ext = os.path.splitext(filename)[1]
        # Génère un nom de fichier unique et aléatoire
        random_name = f"{uuid.uuid4().hex}{ext}"
        # Retourne le chemin complet (ex: avatars/xxxxxxxx.jpg)
        return os.path.join(self.path, random_name)

# On crée une instance de cette classe pour le dossier 'avatars'
random_avatar_name = RandomFileName('avatars/')
