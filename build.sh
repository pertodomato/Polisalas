#!/usr/bin/env bash
# exit on error
set -o errexit

set -x  # Habilita logs detalhados

echo "Instalando dependências do backend..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Convertendo banco Base64 para binário..."
if [ -f /etc/secrets/db_base64.txt ]; then
  echo "Banco de dados codificado encontrado. Decodificando..."
  base64 --decode /etc/secrets/db_base64.txt > /opt/render/project/src/db.sqlite3
else
  echo "Arquivo /etc/secrets/db_base64.txt não encontrado."
fi

echo "Aplicando migrações..."
python manage.py migrate

echo "Coletando arquivos estáticos do Django..."
python manage.py collectstatic --noinput

echo "Instalando dependências do frontend..."
cd reservas/frontend
rm -rf node_modules
npm install

echo "Compilando arquivos do React com Webpack..."
npx webpack --mode production || {
  echo "Erro ao compilar com Webpack."
  exit 1
}

cd ../..

set +x  # Desabilita logs detalhados
echo "Build concluído com sucesso!"
