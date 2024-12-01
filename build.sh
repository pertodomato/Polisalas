#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Convertendo banco Base64 para binário..."
if [ -f /etc/secrets/db_base64.txt ]; then
  base64 --decode /etc/secrets/db_base64.txt > /opt/render/project/src/db.sqlite3
else
  echo "Arquivo /etc/secrets/db_base64.txt não encontrado. Certifique-se de que o banco de dados está configurado corretamente."
fi

echo "Aplicando migrações..."
python manage.py migrate

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Instalando dependências do frontend..."
cd reservas/frontend
npm install
npm run build
cd ../..

echo "Script concluído com sucesso!"
