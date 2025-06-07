# utils.py
import pandas as pd
from unidecode import unidecode # Para remover acentos
from dateutil.relativedelta import relativedelta # Para cálculo de diferença de datas
import datetime # Módulo nativo para datas e horas

# --- Dicionário de meses em português ---
meses_portugues = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# Dicionário INVERSO para mapear nomes de meses (em minúsculas) para números
# Isso facilita a busca do número do mês a partir do nome
meses_para_numeros = {v.lower(): k for k, v in meses_portugues.items()}

def LimTexA(abas):
    """
    Limpa uma lista de strings (ideal para nomes de abas de ficheiro Excel),
    deixando tudo em maiúsculas, removendo hífens e espaços extras.

    Args:
        abas (list): Uma lista de strings a serem limpas.

    Returns:
        list: A lista de strings limpas.
    """
    return [nome.strip().lower().replace('-', '').upper() for nome in abas]

def LimTex(df):
    """
    Limpa os nomes das colunas de um DataFrame: remove espaços no início e fim,
    converte para minúsculas e substitui espaços por underscores.
    Modifica o DataFrame no local (inplace).

    Args:
        df (pd.DataFrame): O DataFrame cujas colunas serão limpas.
    """
    df.columns = (
        df.columns.str.strip() # Remove espaços iniciais/finais
        .str.lower()           # Converte para minúsculas
        .str.replace(' ', '_') # Substitui espaços por underscores
    )
    return

def RemAC(df):
    """
    Remove acentos e caracteres especiais dos nomes das colunas de um DataFrame.
    Modifica o DataFrame no local (inplace).

    Args:
        df (pd.DataFrame): O DataFrame cujas colunas terão os acentos removidos.
    """
    # Itera sobre os nomes das colunas e aplica a função unidecode a cada um
    df.columns = [unidecode(col) for col in df.columns]
    return

def generate_tempo_de_empresa_text(admissao_date, today_date):
    """
    Calcula o tempo de empresa (anos, meses, dias) desde a data de admissão
    até a data atual.

    Args:
        admissao_date (datetime.datetime ou pd.Timestamp): A data de admissão do funcionário.
        today_date (datetime.date): A data atual (hoje).

    Returns:
        str: Uma string formatada com o tempo de empresa, ou None se a data de admissão for inválida.
    """
    if pd.isna(admissao_date):
        return None # Retorna None se a data de admissão for nula/inválida

    # Garante que ambas as datas são objetos datetime para o cálculo com relativedelta
    admissao_date = pd.to_datetime(admissao_date)
    today_date = pd.to_datetime(today_date) # Converte date para datetime se necessário

    # Calcula a diferença de tempo usando relativedelta
    diff = relativedelta(today_date, admissao_date)
    years = diff.years
    months = diff.months
    days = diff.days

    return f"{years} anos, {months} meses e {days} dias"

def FreqUnica(df, coluna_grupo, coluna_valor, nome_resultado='frequencia'):
    """
    Calcula a frequência única de valores em 'coluna_valor' agrupados por 'coluna_grupo'.
    Por exemplo, para contar quantos funcionários únicos há em cada empresa.

    Args:
        df (pd.DataFrame): O DataFrame de entrada.
        coluna_grupo (str): A coluna pela qual agrupar.
        coluna_valor (str): A coluna da qual contar os valores únicos.
        nome_resultado (str, optional): O nome para a coluna de frequência resultante.
                                        O padrão é 'frequencia'.

    Returns:
        pd.DataFrame: Um DataFrame com as frequências agrupadas.
    """
    # Agrupa o DataFrame pela 'coluna_grupo' e conta o número de valores únicos em 'coluna_valor'
    resultado = df.groupby(coluna_grupo)[coluna_valor].nunique().reset_index(name=nome_resultado)
    # Garante que o resultado é um DataFrame
    resultado = pd.DataFrame(resultado)
    return resultado

