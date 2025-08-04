import requests
import sqlite3
from datetime import datetime

# 1. Requisição para a API
url = "https://api.camisa7.botafogo.com.br/public/counter"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    numero = data.get("res")
    print(f"Valor extraído: {numero}")

    # 2. Conectar ou criar o banco de dados
    conn = sqlite3.connect("socios.db")
    cursor = conn.cursor()

    # 3. Criar tabela se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contador (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            socios INTEGER
        )
    """)

    # 4. Inserir o valor com data/hora atual
    agora = datetime.now().isoformat()
    cursor.execute("INSERT INTO contador (data, socios) VALUES (?, ?)", (agora, numero))
    conn.commit()
    conn.close()

    print("Valor salvo com sucesso!")
else:
    print(f"Erro na requisição. Código: {response.status_code}")
