import base64

# Caminho do arquivo a ser convertido
input_file = "db.sqlite3"
output_file = "db_base64.txt"

try:
    # Lê o arquivo binário
    with open(input_file, "rb") as file:
        file_content = file.read()

    # Converte para Base64
    base64_content = base64.b64encode(file_content).decode("utf-8")

    # Salva no arquivo de saída
    with open(output_file, "w") as output:
        output.write(base64_content)

    print(f"Arquivo '{input_file}' convertido para Base64 com sucesso em '{output_file}'.")
except FileNotFoundError:
    print(f"O arquivo '{input_file}' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
