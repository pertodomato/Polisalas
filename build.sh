#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Instalando dependências do backend..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Convertendo banco Base64 para binário..."
if [ -f /etc/secrets/db_base64.txt ]; then
  echo "Banco de dados codificado encontrado. Decodificando..."
  base64 --decode /etc/secrets/db_base64.txt > /opt/render/project/src/db.sqlite3
else
  echo "Arquivo /etc/secrets/db_base64.txt não encontrado. Certifique-se de que o banco de dados está configurado corretamente."
fi

echo "Aplicando migrações..."
python manage.py migrate

echo "Coletando arquivos estáticos do Django..."
python manage.py collectstatic --noinput

echo "Instalando dependências do frontend..."
cd reservas/frontend

# Instala as dependências e força a instalação do webpack-cli
npm install

echo "Compilando arquivos do React com Webpack..."
yes | npm run build || {
  echo "Erro ao compilar com Webpack. Verifique as dependências do frontend."
  exit 1
}

cd ../..

echo "Build concluído com sucesso!"
