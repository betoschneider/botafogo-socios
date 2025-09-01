import sqlite3
import pandas as pd
import streamlit as st

# Função para carregar dados do banco SQLite
def carregar_dados():
    conn = sqlite3.connect('socios.db')
    query = "SELECT data, socios FROM contador"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Processar os dados para pegar maior hora por dia e separar hora
def processar_dados(df):
    # Converter para datetime sem fuso (já gravado no horário de Brasília)
    df['data'] = pd.to_datetime(df['data'], format="%Y-%m-%d %H:%M:%S")

    # Criar coluna de dia
    df['dia'] = df['data'].dt.date

    # Pegar última leitura de cada dia
    idx = df.groupby('dia')['data'].idxmax()
    df_final = df.loc[idx].sort_values('dia').copy()
    
    # Coluna de hora formatada
    df_final['hora'] = df_final['data'].dt.strftime('%H:%M:%S')

    # Formatar dia para dd/mm/yyyy
    df_final['dia'] = df_final['dia'].apply(lambda d: d.strftime('%d/%m/%Y'))
    
    return df_final[['data', 'dia', 'hora', 'socios']]

# Interface Streamlit
def main():
    st.set_page_config(
        page_title="Sócios Botafogo - betoschneider.com",
        page_icon="⭐",
    )
    st.title("Gráfico de Sócios do Botafogo - Camisa 7")

    df = carregar_dados()

    if df.empty:
        st.write("Nenhum dado encontrado no banco.")
        return

    df_final = processar_dados(df)

    # Gráfico de sócios
    st.line_chart(data=df_final.set_index('data')['socios'])

    # Tabela sem índice
    st.write("Dados usados no gráfico:")
    # st.dataframe(df_final.style.hide(axis="index"))
    df_final = df_final.drop(columns='data').reset_index(drop=True)
    st.dataframe(df_final)

if __name__ == '__main__':
    main()
