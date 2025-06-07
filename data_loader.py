# data_loader.py
import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from unidecode import unidecode
# Importar funções e variáveis do módulo utils
from utils import LimTexA, LimTex, RemAC, generate_tempo_de_empresa_text, meses_portugues, meses_para_numeros

def load_and_preprocess_data(excel_file_path):
    """
    Carrega os dados do ficheiro Excel especificado e realiza as etapas iniciais de pré-processamento.

    Args:
        excel_file_path (str): O caminho para o ficheiro Excel.

    Returns:
        pd.DataFrame: O DataFrame pré-processado.
    """
    # Carregar todas as folhas para manusear a limpeza dos nomes das folhas,
    # embora apenas 'TODOS' e 'Férias' sejam usadas no pré-processamento.
    excel = pd.ExcelFile(excel_file_path)
    sheet_names_raw = excel.sheet_names
    # LimTexA(sheet_names_raw) # Esta função foi projetada para um DataFrame, não para uma lista de nomes.
                               # Não é usada diretamente para os nomes das folhas aqui, mas é uma função de utilidade.

    # Carregar as folhas específicas para DataFrames
    df_todos = pd.read_excel(excel_file_path, sheet_name='TODOS')
    df_ferias = pd.read_excel(excel_file_path, sheet_name='Férias')

    # Aplicar a limpeza de texto nos nomes das colunas de ambos os DataFrames
    LimTex(df_todos)
    RemAC(df_todos)

    LimTex(df_ferias)
    RemAC(df_ferias)

    # Pré-processamento específico para df_ferias
    # Criar uma cópia para evitar SettingWithCopyWarning
    df_ferias_periodo = df_ferias[['nome', 'previsao_ferias_2025', 'limite']].copy()
    # Mapear nomes de meses para números usando o dicionário meses_para_numeros do utils
    df_ferias_periodo['previsao_ferias_2025'] = df_ferias_periodo['previsao_ferias_2025'].astype(str).str.strip().str.lower().map(meses_para_numeros)

    # Fazer um merge (junção) entre os DataFrames 'df_todos' e 'df_ferias_periodo'
    # usando a coluna 'nome' como chave. 'how='left'' garante que todos os registos
    # de 'df_todos' são mantidos.
    df_todos = pd.merge(df_todos, df_ferias_periodo, on='nome', how='left')

    # Limpeza e Transformação de Dados para 'df_todos'
    # Identificar colunas de texto (tipo 'object')
    colunas_texto = df_todos.select_dtypes(include='object').columns
    # Preencher valores nulos nas colunas de texto com "NÃO INFORMADO"
    df_todos[colunas_texto] = df_todos[colunas_texto].fillna('NÃO INFORMADO')

    # Substituir valores nulos na coluna 'quantos' por 0 e converter para inteiro
    df_todos['quantos'] = df_todos['quantos'].fillna(0).astype('int64')
    # Converter textos na coluna 'filho(s)' para maiúsculas
    df_todos['filho(s)'] = df_todos['filho(s)'].str.upper()
    # Extrair apenas números da coluna 'idade' e converter para inteiro
    # Usa `.astype(str)` para garantir que a extração de regex funcione em todos os tipos
    df_todos['idade'] = df_todos['idade'].astype(str).str.extract('(\d+)')[0].astype('Int64')
    # Converter a coluna 'admissao' para o tipo datetime, convertendo erros para NaT (Not a Time)
    df_todos['admissao'] = pd.to_datetime(df_todos['admissao'], errors='coerce')
    # Converter a coluna 'limite' para o tipo datetime, convertendo erros para NaT
    df_todos['limite'] = pd.to_datetime(df_todos['limite'], errors='coerce')

    # Remover colunas com dados sensíveis ('cpf', 'rg')
    # 'errors='ignore'' evita um erro se as colunas já não existirem
    df_todos = df_todos.drop(['cpf', 'rg'], axis=1, errors='ignore')

    # Adicionar a coluna 'tempo_de_empresa' usando a função utilitária
    today_date = datetime.date.today()
    df_todos['tempo_de_empresa'] = df_todos['admissao'].apply(lambda x: generate_tempo_de_empresa_text(x, today_date))

    # Correção ortográfica na coluna 'setor'
    df_todos['setor'].replace({'MAMUTENÇÃO': 'MANUTENÇÃO'}, inplace=True)

    return df_todos

