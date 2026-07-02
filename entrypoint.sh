#!/bin/sh
set -e

echo "Application des migrations"
python manage.py migrate

echo "Seed de la base de données"
python manage.py remplir_db

echo "Démarrage du serveur sur 0.0.0.0:8000"
exec python manage.py runserver 0.0.0.0:8000
