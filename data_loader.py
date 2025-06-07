# data_loader.py
import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from unidecode import unidecode # Para remover acentos
import streamlit as st # Importado para exibir st.warning

# Importar funções e variáveis do módulo utils
from utils import LimTexA, LimTex, RemAC, generate_tempo_de_empresa_text, meses_portugues, meses_para_numeros

def load_and_preprocess_data(excel_file):
    """
    Carrega os dados do ficheiro Excel especificado e realiza as etapas iniciais de pré-processamento.

    Args:
        excel_file (file-like object): O ficheiro Excel carregado (e.g., st.UploadedFile).

    Returns:
        pd.DataFrame: O DataFrame pré-processado.
    """
    excel = pd.ExcelFile(excel_file)

    # Carregar as folhas específicas para DataFrames
    df_todos = pd.read_excel(excel, sheet_name='TODOS')
    df_ferias = pd.read_excel(excel, sheet_name='Férias')
    
    # NOVO: Carregar a aba 'DESLIGADOS'
    try:
        df_desligados = pd.read_excel(excel, sheet_name='DESLIGADOS')
        # Aplicar a limpeza de texto nos nomes das colunas de df_desligados
        LimTex(df_desligados)
        RemAC(df_desligados)
    except ValueError:
        st.warning("Aviso: A aba 'DESLIGADOS' não foi encontrada no ficheiro Excel. Os dados de demissão não serão carregados.")
        df_desligados = pd.DataFrame() # Cria um DataFrame vazio se a aba não for encontrada

    # Aplicar a limpeza de texto nos nomes das colunas de df_todos e df_ferias
    LimTex(df_todos)
    RemAC(df_todos)

    LimTex(df_ferias)
    RemAC(df_ferias)

    df_ferias_periodo = df_ferias[['nome', 'previsao_ferias_2025', 'limite']].copy()
    df_ferias_periodo['previsao_ferias_2025'] = df_ferias_periodo['previsao_ferias_2025'].astype(str).str.strip().str.lower().map(meses_para_numeros)

    df_todos = pd.merge(df_todos, df_ferias_periodo, on='nome', how='left')

    # NOVO: Lógica para mesclar a coluna 'demissao' de df_desligados para df_todos
    if not df_desligados.empty:
        # Tenta encontrar a coluna 'demissao' em df_desligados (após limpeza de nomes)
        demissao_col_name_in_desligados = None
        for col in df_desligados.columns:
            if unidecode(col.strip().lower()) == 'demissao': # Considera 'Demissão', 'demissao', etc.
                demissao_col_name_in_desligados = col
                break

        if demissao_col_name_in_desligados:
            # Identificar coluna chave para a junção (preferir 'matricula', senão 'nome')
            merge_key = None
            if 'matricula' in df_todos.columns and 'matricula' in df_desligados.columns:
                merge_key = 'matricula'
            elif 'nome' in df_todos.columns and 'nome' in df_desligados.columns:
                merge_key = 'nome'
            
            if merge_key:
                # Criar um DataFrame temporário com a chave e a coluna de demissão
                df_temp_demissao = df_desligados[[merge_key, demissao_col_name_in_desligados]].copy()
                df_temp_demissao.rename(columns={demissao_col_name_in_desligados: 'demissao_data_merged'}, inplace=True)
                
                # Converter a coluna de demissão do df temporário para datetime antes de mesclar
                df_temp_demissao['demissao_data_merged'] = pd.to_datetime(df_temp_demissao['demissao_data_merged'], errors='coerce')
                
                # Realizar a junção para trazer a coluna de demissão para df_todos
                # Usamos um 'left' merge para manter todos os funcionários do df_todos
                df_todos = pd.merge(df_todos, df_temp_demissao, on=merge_key, how='left')
                
                # Se 'demissao' já existe em df_todos, a nova coluna virá como 'demissao_data_merged'.
                # Vamos consolidar: se 'demissao' original é NaT, preencher com a mesclada.
                if 'demissao' in df_todos.columns:
                    df_todos['demissao'] = df_todos['demissao'].fillna(df_todos['demissao_data_merged'])
                    df_todos.drop(columns=['demissao_data_merged'], errors='ignore', inplace=True)
                else:
                    df_todos['demissao'] = df_todos['demissao_data_merged']
                    df_todos.drop(columns=['demissao_data_merged'], errors='ignore', inplace=True)

            else:
                st.warning("Aviso: Não foi possível encontrar uma coluna comum ('matricula' ou 'nome') para mesclar os dados da aba 'DESLIGADOS'. A coluna 'demissao' pode não ser precisa.")
                df_todos['demissao'] = pd.NaT # Garante que a coluna 'demissao' existe, mesmo que vazia
        else:
            st.warning("Aviso: A coluna 'demissao' (ou variação similar) não foi encontrada na aba 'DESLIGADOS - 2025'. Os cálculos de desligamento podem não ser precisos.")
            df_todos['demissao'] = pd.NaT # Garante que a coluna 'demissao' existe, mesmo que vazia
    else:
        # Se a aba 'DESLIGADOS - 2025' não foi carregada com sucesso, cria a coluna demissao como NaT
        df_todos['demissao'] = pd.NaT


    # Processamento restante do df_todos
    colunas_texto = df_todos.select_dtypes(include='object').columns
    df_todos[colunas_texto] = df_todos[colunas_texto].fillna('NÃO INFORMADO')

    df_todos['quantos'] = df_todos['quantos'].fillna(0).astype('int64')
    df_todos['filho(s)'] = df_todos['filho(s)'].str.upper()
    df_todos['idade'] = df_todos['idade'].astype(str).str.extract('(\d+)')[0].astype('Int64')
    df_todos['admissao'] = pd.to_datetime(df_todos['admissao'], errors='coerce')
    df_todos['limite'] = pd.to_datetime(df_todos['limite'], errors='coerce')

    df_todos = df_todos.drop(['cpf', 'rg'], axis=1, errors='ignore')

    today_date = datetime.date.today()
    df_todos['tempo_de_empresa'] = df_todos['admissao'].apply(lambda x: generate_tempo_de_empresa_text(x, today_date))

    df_todos['setor'].replace({'MAMUTENÇÃO': 'MANUTENÇÃO'}, inplace=True)

    return df_todos
