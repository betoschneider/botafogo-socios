import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

# Função para carregar dados do banco SQLite
def carregar_dados():
    conn = sqlite3.connect('socios.db')  # Nome correto do banco
    query = "SELECT data, socios FROM contador"  # Nome correto da tabela e colunas
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Processar os dados para pegar maior hora por dia
def processar_dados(df):
    # Converter string para datetime
    df['data'] = pd.to_datetime(df['data'])

    # Extrair somente a data (sem hora) para agrupamento
    df['dia'] = df['data'].dt.date

    # Para cada dia, pegar o registro mais recente
    idx = df.groupby('dia')['data'].idxmax()
    df_final = df.loc[idx].sort_values('dia')

    return df_final[['dia', 'socios']]

# Interface Streamlit
def main():
    st.title("Gráfico de Sócios do Botafogo - Camisa 7")

    df = carregar_dados()

    if df.empty:
        st.write("Nenhum dado encontrado no banco.")
        return

    df_final = processar_dados(df)

    st.line_chart(data=df_final.set_index('dia')['socios'])

    st.write("Dados usados no gráfico:")
    st.dataframe(df_final)

if __name__ == '__main__':
    main()
