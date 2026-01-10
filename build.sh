#!/bin/bash
set -o errexit

# Installer les dépendances
pip install -r requirements.txt

# Migrations Django
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
