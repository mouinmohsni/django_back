# companies/serializers.py
from rest_framework import serializers
from .models import Company
# On a besoin du UserSerializer pour représenter les coachs
from users.serializers import UserSerializer

class CompanySerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour créer, lister et mettre à jour les entreprises.
    """

    # On définit un champ qui n'existe pas directement dans le modèle Company.
    # 'source="customuser_set"' indique à DRF d'aller chercher les utilisateurs liés.
    # 'many=True' car il peut y avoir plusieurs coachs.
    # 'read_only=True' car cette liste est en lecture seule, on ne la modifie pas ici.
    coaches = UserSerializer(source='customuser_set', many=True, read_only=True)

    class Meta:
        # On expose tous les champs du modèle.
        model = Company
        # On ajoute 'coaches' à la liste des champs à afficher.
        fields = [
            'id', 'name', 'description', 'logo', 'address', 'city', 'zip_code',
            'phone_number', 'website', 'sport_zen', 'is_verified', 'coaches'
        ]

# --- NOUVEAU SÉRIALISEUR LÉGER ---
class SimpleCompanySerializer(serializers.ModelSerializer):
    """
    Un sérialiseur simplifié pour les entreprises, utilisé pour les affichages imbriqués.
    Il N'INCLUT PAS la liste des coachs pour éviter la redondance.
    """
    class Meta:
        model = Company
        # On choisit les champs essentiels à afficher quand l'entreprise
        # est vue dans le contexte d'une activité.
        fields = ['id', 'name',"description", 'logo', 'phone_number','website','sport_zen','address','city']

