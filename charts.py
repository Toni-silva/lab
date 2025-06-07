# charts.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_employees_by_company_chart(df):
    """
    Cria um gráfico de barras que mostra a frequência de funcionários por empresa.

    Args:
        df (pd.DataFrame): DataFrame com as colunas 'empresa' e 'frequencia'.

    Returns:
        go.Figure: Objeto de figura do gráfico de barras Plotly.
    """
    if df.empty:
        # Retorna uma figura vazia com um título indicando falta de dados
        return go.Figure().update_layout(title_text="Sem dados para Relação de Funcionários por Empresa.")

    fig = px.bar(
        df,
        y='empresa',
        x='frequencia',
        color='empresa',
        color_discrete_sequence=px.colors.sequential.Aggrnyl, # Sequência de cores agradável
        labels={'empresa': 'Empresas', 'frequencia': 'Frequência'}
    )
    # Atualiza o layout do gráfico para definir altura e estilo
    fig.update_layout(
        height=450 # Define uma altura padrão
    )
    # Adiciona estilo aos traços do gráfico (por exemplo, bordas nas barras)
    fig.update_traces(
        marker=dict(
            line=dict(color='rgba(0,0,0,0.6)', width=0.5) # Borda preta semi-transparente
        )
    )
    # Configurações adicionais de layout para o fundo, título e grade do eixo Y
    fig.update_layout(
        plot_bgcolor="#d2cda4", # Cor de fundo da área de plotagem
        paper_bgcolor="#fdfae6", # Cor de fundo do papel (área ao redor do gráfico)
        title={'text': 'Relação de Funcionários por Empresa', 'x': 0.5}, # Título centralizado
        yaxis=dict(gridcolor='#fdfae6') # Cor da grade horizontal do eixo Y
    )
    return fig

def create_employees_by_function_chart(df):
    """
    Cria um gráfico de barras que mostra o número de funcionários por função.

    Args:
        df (pd.DataFrame): DataFrame filtrado contendo a coluna 'funcao'.

    Returns:
        go.Figure: Objeto de figura do gráfico de barras Plotly.
    """
    if df.empty:
        return go.Figure().update_layout(title_text="Sem dados para Funcionários por Função.")

    count_por_funcao = df['funcao'].value_counts().reset_index()
    count_por_funcao.columns = ['Função', 'Count'] # Renomeia as colunas
    fig = px.bar(
        count_por_funcao,
        x='Função',
        y='Count',
        title='Funcionários por Função',
        labels={'Count': 'Número de Funcionários'},
        color='Count', # Colore as barras com base na contagem
        color_continuous_scale=px.colors.sequential.Viridis # Escala de cores contínua
    )
    # Atualiza os títulos dos eixos e o ângulo das legendas do eixo X
    fig.update_layout(xaxis_title="Função", yaxis_title="Contagem", xaxis_tickangle=-45)
    return fig

def create_employees_by_children_chart(df):
    """
    Cria um gráfico de barras que mostra o número de funcionários pela quantidade de filhos.

    Args:
        df (pd.DataFrame): DataFrame filtrado contendo a coluna 'quantos'.

    Returns:
        go.Figure: Objeto de figura do gráfico de barras Plotly.
    """
    if df.empty:
        return go.Figure().update_layout(title_text="Sem dados para Distribuição de Filhos.")

    filhos_counts = df['quantos'].value_counts().sort_index().reset_index()
    filhos_counts.columns = ['Número de Filhos', 'Count']
    fig = px.bar(
        filhos_counts,
        x='Número de Filhos',
        y='Count',
        title='Número de Funcionários por Quantidade de Filhos',
        labels={'Count': 'Número de Funcionários'},
        color='Count',
        color_continuous_scale=px.colors.sequential.Inferno
    )
    fig.update_layout(xaxis_title="Número de Filhos", yaxis_title="Contagem")
    return fig

def create_gender_distribution_chart(df):
    """
    Cria um gráfico de pizza que mostra a distribuição de funcionários por género.

    Args:
        df (pd.DataFrame): DataFrame filtrado contendo a coluna 'sexo'.

    Returns:
        go.Figure: Objeto de figura do gráfico de pizza Plotly.
    """
    if df.empty:
        return go.Figure().update_layout(title_text="Sem dados para Gênero.")

    sexo_counts_chart = df['sexo'].value_counts().reset_index()
    sexo_counts_chart.columns = ['Sexo', 'Count']
    fig = px.pie(
        sexo_counts_chart,
        values='Count',
        names='Sexo',
        title='Distribuição de Funcionários por Gênero',
        hole=0.4 # Cria um gráfico de donut (com buraco no centro)
    )
    # Atualiza os traços do gráfico para exibir percentagem e label, e separar ligeiramente as fatias
    fig.update_traces(textinfo='percent+label', pull=[0.05] * len(sexo_counts_chart))
    return fig

def create_education_level_distribution_chart(df, order_categories=None):
    """
    Cria um gráfico de pizza que mostra a distribuição por nível de escolaridade.

    Args:
        df (pd.DataFrame): DataFrame filtrado contendo a coluna 'nivel_escolaridade'.
        order_categories (list, optional): Lista que define a ordem das categorias.
                                          Útil para ordenar categorias de escolaridade.

    Returns:
        go.Figure: Objeto de figura do gráfico de pizza Plotly.
    """
    if df.empty:
        return go.Figure().update_layout(title_text="Sem dados para Escolaridade.")

    if order_categories:
        # Reindexa para garantir a ordem e inclui categorias com zero (se não houver dados para elas)
        escolaridade_counts_chart = df['nivel_escolaridade'].value_counts().reindex(order_categories, fill_value=0).reset_index()
    else:
        escolaridade_counts_chart = df['nivel_escolaridade'].value_counts().reset_index()

    escolaridade_counts_chart.columns = ['Nível Escolaridade', 'Count']
    fig = px.pie(
        escolaridade_counts_chart,
        values='Count',
        names='Nível Escolaridade',
        title='Distribuição por Nível de Escolaridade',
        hole=0.4
    )
    fig.update_traces(textinfo='percent+label', pull=[0.05] * len(escolaridade_counts_chart))
    return fig

def create_monthly_admissions_chart(df):
    """
    Cria um gráfico de linha que mostra o número de novas admissões por mês.

    Args:
        df (pd.DataFrame): DataFrame filtrado contendo as colunas 'admissao' e 'ald'.

    Returns:
        go.Figure: Objeto de figura do gráfico de linha Plotly.
    """
    if df.empty:
        return go.Figure().update_layout(title_text="Sem dados para Admissões por Mês.")

    # Agrupa por mês de admissão e conta o número de 'ald' (funcionários)
    admissoes_por_mes = df.groupby(df['admissao'].dt.to_period('M'))['ald'].count().reset_index()
    admissoes_por_mes.columns = ['Mês', 'Novas Admissões']
    # Converte o período do mês para string para exibição no eixo X
    admissoes_por_mes['Mês'] = admissoes_por_mes['Mês'].astype(str)

    fig = px.line(
        admissoes_por_mes,
        x='Mês',
        y='Novas Admissões',
        title='Número de Novas Admissões por Mês',
        labels={'Novas Admissões': 'Contagem'},
        markers=True # Adiciona marcadores nos pontos de dados
    )
    return fig

def create_cost_type_distribution_chart(df):
    """
    Cria um gráfico de pizza que mostra a distribuição por tipo de custo.

    Args:
        df (pd.DataFrame): DataFrame filtrado contendo a coluna 'custo'.

    Returns:
        go.Figure: Objeto de figura do gráfico de pizza Plotly.
    """
    if df.empty:
        return go.Figure().update_layout(title_text="Sem dados para Tipo de Custo.")

    custo_tipo_counts = df['custo'].value_counts().reset_index()
    custo_tipo_counts.columns = ['Tipo de Custo', 'Count']
    fig = px.pie(
        custo_tipo_counts,
        values='Count',
        names='Tipo de Custo',
        title='Distribuição por Tipo de Custo',
        hole=0.4
    )
    fig.update_traces(textinfo='percent+label', pull=[0.05] * len(custo_tipo_counts))
    return fig

# --- Novos gráficos sugeridos na última interação (mantidos, mas turnover será removido) ---

# REMOVIDO: create_monthly_turnover_trend_chart
# def create_monthly_turnover_trend_chart(df):
#     """
#     Cria um gráfico de linha que mostra a tendência de desligamentos mensais.
#     Assumimos que 'status' == 'DESLIGADO' para desligamentos.
#     Para um cálculo mais preciso, seria ideal ter uma 'data_desligamento'.
#     """
#     if df.empty:
#         return go.Figure().update_layout(title_text="Sem dados para Tendência de Desligamentos Mensais.")

#     # Filtra apenas os desligados
#     df_desligados = df[df['status'] == 'DESLIGADO'].copy()
    
#     # Agrupa por mês de admissão (usado como proxy para o evento no período)
#     # Em um cenário real, usaríamos a 'data_desligamento' real.
#     desligamentos_por_mes = df_desligados.groupby(df_desligados['admissao'].dt.to_period('M')).size().reset_index(name='Contagem')
#     desligamentos_por_mes['admissao'] = desligamentos_por_mes['admissao'].dt.to_timestamp() # Converte para datetime para Plotly
    
#     fig = px.line(
#         desligamentos_por_mes,
#         x='admissao',
#         y='Contagem',
#         title='Tendência de Desligamentos Mensais',
#         labels={'admissao': 'Mês', 'Contagem': 'Número de Desligamentos'},
#         markers=True
#     )
#     fig.update_xaxes(dtick="M1", tickformat="%b\n%Y") # Formato de mês/ano
#     return fig

def create_hires_vs_terminations_chart(df):
    """
    Cria um gráfico de barras comparando contratações e desligamentos por mês.
    """
    if df.empty:
        return go.Figure().update_layout(title_text="Sem dados para Contratações vs. Desligamentos.")

    # Agrupa contratações por mês
    df_contratacoes = df.groupby(df['admissao'].dt.to_period('M')).size().reset_index(name='Contratações')
    df_contratacoes['admissao'] = df_contratacoes['admissao'].dt.to_timestamp()

    # Agrupa desligamentos por mês (baseado na data de admissão e status 'DESLIGADO' como proxy)
    df_desligamentos = df[df['status'] == 'DESLIGADO'].groupby(df['admissao'].dt.to_period('M')).size().reset_index(name='Desligamentos')
    df_desligamentos['admissao'] = df_desligamentos['admissao'].dt.to_timestamp()

    # Une os DataFrames
    df_merged = pd.merge(df_contratacoes, df_desligamentos, on='admissao', how='outer').fillna(0)
    df_merged = df_merged.sort_values('admissao')

    fig = go.Figure(data=[
        go.Bar(name='Contratações', x=df_merged['admissao'], y=df_merged['Contratações'], marker_color='#3b82f6'),
        go.Bar(name='Desligamentos', x=df_merged['admissao'], y=df_merged['Desligamentos'], marker_color='#ef4444')
    ])
    fig.update_layout(
        barmode='group',
        title='Contratações vs. Desligamentos Mensais',
        xaxis_title='Mês',
        yaxis_title='Contagem',
        xaxis=dict(dtick="M1", tickformat="%b\n%Y")
    )
    return fig
