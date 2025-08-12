import requests
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import pytz

# Função para extrair e salvar o valor da API
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

# Função para carregar dados do banco SQLite
def carregar_dados():
    conn = sqlite3.connect('socios.db')
    query = "SELECT data, socios FROM contador"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Processar os dados para pegar maior hora por dia e separar hora
def processar_dados(df):
    df['data'] = pd.to_datetime(df['data'])
    df['dia'] = df['data'].dt.date
    idx = df.groupby('dia')['data'].idxmax()
    df_final = df.loc[idx].sort_values('dia').copy()
    
    # Adicionar coluna hora formatada
    df_final['hora'] = df_final['data'].dt.strftime('%H:%M:%S')
    # Formatar a coluna dia para dd/mm/yyyy
    df_final['dia'] = df_final['dia'].apply(lambda d: d.strftime('%d/%m/%Y'))
    
    return df_final[['dia', 'hora', 'socios']]

# Interface Streamlit
def main():
    st.set_page_config(
        page_title="Sócios Botafogo - betoschneider.com",
        page_icon="⭐",
    )
    st.title("Gráfico de Sócios do Botafogo - Camisa 7")

    extrair_e_salvar()  # Executa antes de exibir os dados

    df = carregar_dados()

    if df.empty:
        st.write("Nenhum dado encontrado no banco.")
        return

    df_final = processar_dados(df)

    st.line_chart(data=df_final.set_index('dia')['socios'])

    st.write("Dados usados no gráfico:")
    # Mostrar tabela sem o índice no Streamlit:
    st.dataframe(df_final.style.hide(axis="index"))

if __name__ == '__main__':
    main()