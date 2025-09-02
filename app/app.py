import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, time

# exemplo de datetime
dt = datetime(2025, 9, 1, 10, 30, 15)

# ajusta para última hora do dia
dt_fim_dia = datetime.combine(dt.date(), time(23, 59, 59))

print(dt_fim_dia)
# saída: 2025-09-01 23:59:59


# Função para carregar maior data no banco SQLite
def carregar_data_atualizacao():
    conn = sqlite3.connect('socios.db')
    query = "SELECT MIN(data) as min_value, MAX(data) as max_value FROM contador"
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['min_value'] = pd.to_datetime(df['min_value'], format="%Y-%m-%d %H:%M:%S")
    df['max_value'] = pd.to_datetime(df['max_value'], format="%Y-%m-%d %H:%M:%S")
    return df['min_value'].iloc[0], df['max_value'].iloc[0]

# Função para carregar dados do banco SQLite
def carregar_dados(dt_inicio=None, dt_fim=None):
    conn = sqlite3.connect('socios.db')
    if dt_inicio and dt_fim:
        query = f"""
        SELECT data, socios FROM contador
        WHERE data BETWEEN '{dt_inicio.strftime('%Y-%m-%d %H:%M:%S')}' 
                  AND '{dt_fim.strftime('%Y-%m-%d %H:%M:%S')}'
        """
    else:
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
    datas = carregar_data_atualizacao()
    dt_atualizacao = datas[1]
    min_data = datas[0]
    dt_fim = datetime.combine(dt_atualizacao.date(), time(23, 59, 59))
    dias_padrao = 90
    dt_inicio = datetime.combine((dt_fim - pd.Timedelta(days=dias_padrao)).date(), time(0, 0, 0))
    valor_padrao = [dt_inicio, dt_atualizacao]

    st.set_page_config(
        page_title="Sócios Camisa 7 - Botafogo",
        page_icon="⭐",
    )
    st.title("Número de sócios Camisa 7 Botafogo")

    # Inicializa session_state na primeira execução
    if "periodo" not in st.session_state:
        st.session_state["periodo"] = valor_padrao

    # Botão para restaurar valor padrão
    if st.button("🔄 Restaurar período"):
        st.session_state["periodo"] = valor_padrao

    # componente de seleção de intervalo de datas
    data_selecionada = st.date_input(
        "Selecione o período:",
        # value=st.session_state["periodo"],
        format="DD/MM/YYYY",
        key="periodo"
    )

    # Garante que sempre seja uma tupla de duas datas
    if isinstance(data_selecionada, (list, tuple)) and len(data_selecionada) == 2:
        dt_inicio, dt_fim = data_selecionada
    else:
        dt_inicio = dt_fim = data_selecionada[0]
        

    df = carregar_dados(datetime.combine(dt_inicio, time(0, 0, 0)), 
                        datetime.combine(dt_fim, time(23, 59, 59))
    )

    if df.empty:
        st.write("Nenhum dado encontrado no banco.")
        return

    df_final = processar_dados(df)

    # Gráfico de sócios
    st.line_chart(data=df_final.set_index('data')['socios'])

    # Tabela sem índice
    st.write("Dados usados no gráfico:")
    # st.dataframe(df_final.style.hide(axis="index"))
    df_final = df_final.sort_values(by='data', ascending=False).reset_index(drop=True)
    st.dataframe(df_final.drop(columns=['data', 'hora']).rename(columns={'dia': 'Data', 'socios': 'Número de Sócios'}))
    
    st.write(f"Dados atualizados em: {dt_atualizacao.strftime('%d/%m/%Y %H:%M')}.")
    

if __name__ == '__main__':
    main()
