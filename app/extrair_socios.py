import requests
import sqlite3
from datetime import datetime
import pytz

def extrair_e_salvar():
    url = "https://api.camisa7.botafogo.com.br/public/counter"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        numero = data.get("res")
        print(f"Valor extraído: {numero}")

        conn = sqlite3.connect("socios.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contador (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                socios INTEGER
            )
        """)
        fuso_brasil = pytz.timezone("America/Sao_Paulo")
        agora = datetime.now(fuso_brasil).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO contador (data, socios) VALUES (?, ?)", (agora, numero))
        conn.commit()
        conn.close()
        print("Valor salvo com sucesso!")
    else:
        print(f"Erro na requisição. Código: {response.status_code}")

if __name__ == '__main__':
    extrair_e_salvar()