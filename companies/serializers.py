# companies/serializers.py (CORRIGÉ - FINAL)
from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer principal pour les entreprises.
    N'inclut PAS la liste des coaches et activités pour éviter l'importation circulaire.
    Utiliser les endpoints dédiés :
    - /api/companies/{id}/coaches/ pour récupérer les coaches
    - /api/companies/{id}/activities/ pour récupérer les activités
    """
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'logo', 'address', 'city', 'zip_code',
            'phone_number', 'website', 'sport_zen', 'is_verified', 'created_at'
        ]


class SimpleCompanySerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour afficher une entreprise dans un contexte imbriqué
    (par exemple, la company d'une activité).
    """
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'logo', 'phone_number',
            'website', 'sport_zen', 'address', 'city'
        ]
        read_only_fields = fields
