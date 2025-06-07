# ui_components.py
import streamlit as st
import datetime
import pandas as pd
from utils import meses_portugues, FreqUnica
from dateutil.relativedelta import relativedelta # Importar para cálculo de tempo de empresa

def render_sidebar_filters(df):
    """
    Renderiza os filtros na barra lateral do Streamlit e retorna os valores selecionados.
    Os filtros de data (Data Inicial/Final) FORAM REMOVIDOS desta função,
    pois são agora tratados diretamente em main_dashboard.py.

    Args:
        df (pd.DataFrame): O DataFrame completo para extrair valores únicos para os filtros.

    Returns:
        dict: Um dicionário contendo os valores dos filtros selecionados (excluindo os filtros de data).
    """
    filters = {} # Dicionário para armazenar os valores selecionados dos filtros

    # Filtro por Status
    status_unicos = list(df['status'].unique())
    filters['status'] = st.sidebar.multiselect(
        "Status do Funcionário:",
        options=status_unicos,
        default=[],
        placeholder="Escolha uma opção"
    )

    # Filtro por Empresa
    empresas_unicas = list(df['empresa'].unique())
    filters['empresa'] = st.sidebar.multiselect(
        "Empresa:",
        options=empresas_unicas,
        default=[],
        placeholder="Escolha uma opção"
    )

    # Filtro por Setor
    setores_unicos = list(df['setor'].unique())
    filters['setor'] = st.sidebar.multiselect(
        "Setor:",
        options=setores_unicos,
        default=[],
        placeholder="Escolha uma opção"
    )

    sub_setores_unicos = list(df['sub_setor'].unique())
    filters['sub_setor'] = st.sidebar.multiselect(
        "Sub Setor:",
        options=sub_setores_unicos,
        default=[],
        placeholder="Escolha uma opção"
    )

    funcoes_unicas = list(df['funcao'].unique())
    filters['funcao'] = st.sidebar.multiselect(
        "Função:",
        options=funcoes_unicas,
        default=[],
        placeholder="Escolha uma opção"
    )

    # Filtro por Custo (Direto/Indireto)
    custo_opcoes = list(df['custo'].unique())
    filters['custo'] = st.sidebar.multiselect(
        "Tipo de Custo:",
        options=custo_opcoes,
        default=[],
        placeholder="Escolha uma opção"
    )

    # Filtro por Nível Escolaridade
    escolaridade_unicas = list(df['nivel_escolaridade'].unique())
    filters['nivel_escolaridade'] = st.sidebar.multiselect(
        "Nível de Escolaridade:",
        options=escolaridade_unicas,
        default=[],
        placeholder="Escolha uma opção"
    )

    # Filtro por Raça
    racas_unicas = list(df['raca'].unique())
    filters['raca'] = st.sidebar.multiselect(
        "Raça:",
        options=racas_unicas,
        default=[],
        placeholder="Escolha uma opção"
    )

    # Filtro por Sexo
    sexo_unicos = list(df['sexo'].unique())
    filters['sexo'] = st.sidebar.multiselect(
        "Sexo:",
        options=sexo_unicos,
        default=[],
        placeholder="Escolha uma opção"
    )

    min_idade = int(df['idade'].min()) if not df['idade'].empty and pd.notna(df['idade'].min()) else 0
    max_idade = int(df['idade'].max()) if not df['idade'].empty and pd.notna(df['idade'].max()) else 100
    valor_faixa_idade = st.sidebar.slider(
        "Faixa de Idade:",
        min_value=min_idade,
        max_value=max_idade,
        value=(min_idade, max_idade)
    )
    filters['idade_min_selecionada'] = valor_faixa_idade[0]
    filters['idade_max_selecionada'] = valor_faixa_idade[1]

    filhos_opcoes = ['SIM', 'NÃO']
    filters['filho(s)'] = st.sidebar.multiselect(
        "Possui Filho(s)?",
        options=filhos_opcoes,
        default=[],
        placeholder="Escolha uma opção"
    )

    min_quantos = int(df['quantos'].min()) if not df['quantos'].empty and pd.notna(df['quantos'].min()) else 0
    max_quantos = int(df['quantos'].max()) if not df['quantos'].empty and pd.notna(df['quantos'].max()) else 10
    quantos_filhos_selecionados = st.sidebar.slider(
        "Quantidade de Filho(s):",
        min_value=min_quantos,
        max_value=max_quantos,
        value=(min_quantos, max_quantos)
    )
    filters['quantos_min_selecionados'] = quantos_filhos_selecionados[0]
    filters['quantos_max_selecionados'] = quantos_filhos_selecionados[1]

    return filters

def render_kpis(df_filtrado, data_inicial_periodo, data_final_periodo):
    """
    Renderiza a secção de Indicadores Chave de Desempenho (KPIs).

    Args:
        df_filtrado (pd.DataFrame): O DataFrame filtrado.
        data_inicial_periodo (datetime.date): Data inicial do período de análise dos filtros.
        data_final_periodo (datetime.date): Data final do período de análise dos filtros.
    """
    # O layout de colunas é ajustado para 4 colunas de tamanho igual
    kpi1, kpi2, kpi3, kpi4 = st.columns([1, 1, 1, 1])

    total_funcionarios_filtrados = df_filtrado[df_filtrado['status'].isin(['ATIVO', 'EXPERIENCIA'])].shape[0]

    # Contratações no período selecionado
    contratacoes_no_periodo = df_filtrado[
        (df_filtrado['admissao'].dt.date >= data_inicial_periodo) &
        (df_filtrado['admissao'].dt.date <= data_final_periodo)
    ].shape[0]

    # Converter as datas do período para Pandas Timestamp para comparação robusta
    start_ts = pd.Timestamp(data_inicial_periodo)
    end_ts = pd.Timestamp(data_final_periodo)

    # Desligamentos no período, filtrando por 'demissao' e status 'DESLIGADO'
    # Garante que 'demissao' não é NaT (ou seja, só conta se houver data de demissão)
    # e que a data de demissão está dentro do período selecionado.
    desligamentos_no_periodo = df_filtrado[
        (df_filtrado['status'] == 'DESLIGADO') &
        (df_filtrado['demissao'].notna()) & # Garante que há uma data de demissão
        (df_filtrado['demissao'] >= start_ts) & # Comparação direta com Timestamp
        (df_filtrado['demissao'] <= end_ts)     # Comparação direta com Timestamp
    ].shape[0]

    # --- Cálculo do Tempo Médio de Empresa ---
    tempo_de_empresa_em_anos = []
    today = datetime.date.today()
    for index, row in df_filtrado[df_filtrado['status'].isin(['ATIVO', 'EXPERIENCIA'])].iterrows():
        if pd.notna(row['admissao']):
            diff = relativedelta(today, row['admissao'].date())
            tempo_de_empresa_em_anos.append(diff.years + diff.months/12 + diff.days/365.25)
    
    tempo_medio_empresa = 0.0
    if tempo_de_empresa_em_anos:
        tempo_medio_empresa = sum(tempo_de_empresa_em_anos) / len(tempo_de_empresa_em_anos)


    # --- Exibição dos KPIs ---
    with st.container(border=True):
        with kpi1:
            with st.container(border=True):
                st.image("img/ativos.png", width=75)
                st.metric("Funcionários Ativos", total_funcionarios_filtrados)

        with kpi2:
            with st.container(border=True):
                st.image("img/contratados.png", width=75)
                st.metric("Contratações no Período", contratacoes_no_periodo)

        with kpi3:
            with st.container(border=True):
                st.image("img/desligados.png", width=75)
                st.metric("Desligamentos no Período", desligamentos_no_periodo)

        with kpi4: # Antigo kpi5, agora kpi4
            with st.container(border=True):
                # Substituído por emoji para evitar erro de imagem
                st.markdown("### ⏳") # Emoji de relógio de areia para "Tempo Médio Empresa"
                st.metric("Tempo Médio Empresa", f"{tempo_medio_empresa:.1f} anos")


def render_aniversaries_and_vacations_section(df_filtrado, meses_portugues_dict):
    """
    Renderiza a secção de aniversários e férias.

    Args:
        df_filtrado (pd.DataFrame): O DataFrame filtrado.
        meses_portugues_dict (dict): Dicionário que mapeia números de meses para nomes em português.
    """
    st.markdown("###  **Aniversários** 🎉")
    with st.container(border=True):
        ani2, ani3 = st.columns([0.5, 1.2])

        with ani3:
            mes_atual = datetime.datetime.now().month
            aniversariantes_do_mes = df_filtrado[
                (df_filtrado['data_de_nasc.'].dt.month == mes_atual) &
                (df_filtrado['status'] == 'ATIVO')
            ].copy()

            nome_mes_portugues = meses_portugues_dict.get(mes_atual, "Mês Desconhecido")
            with st.expander(f"Lista dos aniversariantes do mês de {nome_mes_portugues} ({len(aniversariantes_do_mes)})"):
                if not aniversariantes_do_mes.empty:
                    aniversariantes_do_mes['dia_nascimento'] = aniversariantes_do_mes['data_de_nasc.'].dt.day
                    aniversariantes_do_mes = aniversariantes_do_mes.sort_values(by='dia_nascimento')
                    aniversariantes_do_mes['Data Nasc.'] = aniversariantes_do_mes['data_de_nasc.'].dt.strftime('%d/%m')
                    st.dataframe(
                        aniversariantes_do_mes[['nome', 'Data Nasc.', 'setor', 'funcao']],
                        use_container_width=True,
                        hide_index=True
                    )
        with ani2:
            st.metric("Aniversariantes no Mês", len(aniversariantes_do_mes))

    st.markdown("###  **Férias**")
    with st.container(border=True):
        f1, f2 = st.columns([0.2, 1])

        with f2:
            mes_atual = datetime.datetime.now().month
            ferias_do_mes = df_filtrado[
                (df_filtrado['previsao_ferias_2025'] == mes_atual) &
                (df_filtrado['status'] == 'ATIVO')
            ].copy()

            nome_mes_portugues = meses_portugues_dict.get(mes_atual, "Mês Desconhecido")
            with st.expander(f"Lista dos Funcionários com Férias no Mês de {nome_mes_portugues} ({len(ferias_do_mes)})"):
                if not ferias_do_mes.empty:
                    st.dataframe(
                        ferias_do_mes[['nome', 'funcao', 'setor']],
                        use_container_width=True,
                        hide_index=True
                    )
        with f1:
            st.metric("Férias no Mês", len(ferias_do_mes))
