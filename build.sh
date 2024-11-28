#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Convertendo banco Base64 para binário..."
base64 --decode /etc/secrets/db_base64.txt > /opt/render/project/src/db.sqlite3

echo "Aplicando migrações..."
python manage.py migrate

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Superuser creation is not needed since the database already includes it
