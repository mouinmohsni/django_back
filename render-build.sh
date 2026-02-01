#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Installer les dépendances listées dans requirements.txt
pip install -r requirements.txt

# 2. Collecter les fichiers statiques (pour l'interface d'admin Django)
python manage.py collectstatic --no-input

# 3. Appliquer les migrations à la base de données de production (PostgreSQL)
python manage.py migrate
