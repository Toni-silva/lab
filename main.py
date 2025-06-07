# main_dashboard.py
import streamlit as st
import pandas as pd
import datetime
import altair as alt

# Importar componentes modularizados
from data_loader import load_and_preprocess_data
from ui_components import render_sidebar_filters, render_kpis, render_aniversaries_and_vacations_section
from charts import create_employees_by_company_chart, create_employees_by_function_chart, \
    create_employees_by_children_chart, create_gender_distribution_chart, \
    create_education_level_distribution_chart, create_monthly_admissions_chart, \
    create_cost_type_distribution_chart
from utils import FreqUnica, meses_portugues

# ================================== Configuração da Página ================================
st.set_page_config(
    page_title="Dashboard de RH Interativo",
    page_icon="img/cacto.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)
alt.theme.enable("default") # Ativar o tema padrão do Altair

# ================================== Carregamento e Pré-processamento de Dados ================================
@st.cache_data
def get_processed_data():
    """
    Carrega e pré-processa os dados do ficheiro Excel.
    Esta função é cacheada para evitar recarregar os dados desnecessariamente.
    """
    return load_and_preprocess_data('INDICADORES - NATURAYO -ATUALIZADA 01.xlsx')

df_rh = get_processed_data()

# ================================== Navegação Principal (Cabeçalho) ================================
o1, o2, o3, o4 = st.columns([1.2, 0.3, 0.4, 0.4])

with o1:
    st.header("Dashboard RH Naturayo")

if 'page' not in st.session_state:
    st.session_state.page = "Visão Geral"

with o2:
    if st.button("Visão Geral"):
        st.session_state.page = "Visão Geral"
with o3:
    if st.button("Métricas e Gráficos"):
        st.session_state.page = "Métricas e Gráficos"
with o4:
    if st.button("Tabelas de Resumo"):
        st.session_state.page = "Tabelas de Resumo"

st.sidebar.image("img/im1.jpg", use_container_width=True)
st.sidebar.title("Painel de Controle RH")

# ================================== Filtros de Data (Movidos para cá) ================================
# Cálculo das datas mínima e máxima para o filtro de admissão
if not df_rh.empty and 'admissao' in df_rh.columns and pd.api.types.is_datetime64_any_dtype(df_rh['admissao']):
    min_data_admissao_df = df_rh['admissao'].min().date()
    max_data_admissao_df = df_rh['admissao'].max().date()
else:
    min_data_admissao_df = datetime.date.today()
    max_data_admissao_df = datetime.date.today()
    st.sidebar.warning("Nenhum dado válido para filtrar datas de admissão.")

data_inicial_admissao = st.sidebar.date_input(
    "Data Inicial:",
    value=min_data_admissao_df,
    min_value=min_data_admissao_df,
    max_value=max_data_admissao_df,
    format="DD/MM/YYYY",
    key="data_inicial_key" # Adicionado key única
)
data_final_admissao = st.sidebar.date_input(
    "Data Final:",
    value=max_data_admissao_df,
    min_value=min_data_admissao_df,
    max_value=max_data_admissao_df,
    format="DD/MM/YYYY",
    key="data_final_key" # Adicionado key única
)
if data_inicial_admissao > data_final_admissao:
    st.error("Erro: A Data Inicial não pode ser maior que a Data Final.")
    st.stop()

# ================================== Navegação por Rádio (Movido para cá) ================================
# Movido para logo abaixo dos filtros de data
pagina = st.sidebar.radio("Navegar para:", ["Visão Geral", "Métricas e Gráficos", "Tabelas de Resumo"],
                          index=["Visão Geral", "Métricas e Gráficos", "Tabelas de Resumo"].index(st.session_state.page))

# ================================== Outros Filtros da Barra Lateral ================================
st.sidebar.header("Outras Opções de Filtro")
selected_filters = render_sidebar_filters(df_rh)

# Adicionar as datas selecionadas ao dicionário de filtros
selected_filters['data_inicial_admissao'] = data_inicial_admissao
selected_filters['data_final_admissao'] = data_final_admissao

# =================================================================================
# --- ⌛Aplicando os Filtros ao DataFrame ---
# ================================================================================
df_filtrado = df_rh.copy()

for key, value in selected_filters.items():
    if value:
        if key == 'idade_min_selecionada':
            df_filtrado = df_filtrado[df_filtrado['idade'] >= value]
        elif key == 'idade_max_selecionada':
            df_filtrado = df_filtrado[df_filtrado['idade'] <= value]
        elif key == 'quantos_min_selecionados':
            df_filtrado = df_filtrado[df_filtrado['quantos'] >= value]
        elif key == 'quantos_max_selecionados':
            df_filtrado = df_filtrado[df_filtrado['quantos'] <= value]
        elif key == 'data_inicial_admissao':
            df_filtrado = df_filtrado[df_filtrado['admissao'].dt.date >= value]
        elif key == 'data_final_admissao':
            df_filtrado = df_filtrado[df_filtrado['admissao'].dt.date <= value]
        else:
            df_filtrado = df_filtrado[df_filtrado[key].isin(value)]

# ================================== Renderização das Páginas ================================

if pagina == "Visão Geral":
    render_kpis(df_filtrado)

    chart_rh_col1, chart_rh_col2 = st.columns([1.1, 0.9])

    with chart_rh_col1:
        render_aniversaries_and_vacations_section(df_filtrado, meses_portugues)

    with chart_rh_col2:
        with st.container(border=True):
            if not df_filtrado.empty:
                id_empresa = FreqUnica(df_filtrado, 'empresa', 'nome')
                fig_idade = create_employees_by_company_chart(id_empresa)
                st.plotly_chart(fig_idade, use_container_width=True)
            else:
                st.info("Sem dados para o gráfico de Relação de Funcionários por Empresa.")

elif pagina == "Métricas e Gráficos":
    if df_filtrado.empty:
        st.info("Nenhum dado para gerar análises detalhadas com os filtros atuais.")
    else:
        blc1, blc2, blc3 = st.columns(3)

        with blc1:
            tab_rh_col1, tab_rh_col2, tab_rh_col3, tab_rh_col4, tab_rh_col5, tab_rh_col6 = st.tabs([
                "Funcionários por Status", "Qtd. por Nível Escolaridade", "Qtd. por Raça",
                "Qtd. por Sexo (Gênero)", "Qtd. por Empresa", "Qtd. por Tipo de Custo"
            ])

            with tab_rh_col1:
                status_counts = df_filtrado['status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                status_counts['Percentual'] = (status_counts['Count'] / status_counts['Count'].sum() * 100).map('{:.2f}%'.format)
                st.dataframe(status_counts, use_container_width=True, hide_index=True)
                st.markdown(f"**Total de funcionários:** **`{status_counts['Count'].sum()}`**")

            with tab_rh_col2:
                ordem_escolaridade = ['Fundamental', 'Médio', 'Superior Incompleto', 'Superior Completo', 'Pós-graduação']
                escolaridade_counts = df_filtrado['nivel_escolaridade'].value_counts().reset_index()
                escolaridade_counts.columns = ['Nível Escolaridade', 'Count']
                escolaridade_counts['Percentual'] = (escolaridade_counts['Count'] / escolaridade_counts['Count'].sum() * 100).map('{:.2f}%'.format)
                escolaridade_counts['Nível Escolaridade'] = pd.Categorical(escolaridade_counts['Nível Escolaridade'], categories=ordem_escolaridade, ordered=True)
                escolaridade_counts = escolaridade_counts.sort_values('Nível Escolaridade')
                st.dataframe(escolaridade_counts, use_container_width=True, hide_index=True)
                st.markdown(f"**Total de funcionários:** **`{escolaridade_counts['Count'].sum()}`**")

            with tab_rh_col3:
                raca_counts = df_filtrado['raca'].value_counts().reset_index()
                raca_counts.columns = ['Raça', 'Count']
                raca_counts['Percentual'] = (raca_counts['Count'] / raca_counts['Count'].sum() * 100).map('{:.2f}%'.format)
                st.dataframe(raca_counts, use_container_width=True, hide_index=True)
                st.markdown(f"**Total de funcionários:** **`{raca_counts['Count'].sum()}`**")

            with tab_rh_col4:
                sexo_counts = df_filtrado['sexo'].value_counts().reset_index()
                sexo_counts.columns = ['Sexo', 'Count']
                sexo_counts['Percentual'] = (sexo_counts['Count'] / sexo_counts['Count'].sum() * 100).map('{:.2f}%'.format)
                st.dataframe(sexo_counts, use_container_width=True, hide_index=True)
                st.markdown(f"**Total de funcionários:** **`{sexo_counts['Count'].sum()}`**")

            with tab_rh_col5:
                empresa_counts = df_filtrado['empresa'].value_counts().reset_index()
                empresa_counts.columns = ['Empresa', 'Count']
                empresa_counts['Percentual'] = (empresa_counts['Count'] / empresa_counts['Count'].sum() * 100).map('{:.2f}%'.format)
                st.dataframe(empresa_counts, use_container_width=True, hide_index=True)
                st.markdown(f"**Total de funcionários:** **`{empresa_counts['Count'].sum()}`**")

            with tab_rh_col6:
                custo_counts = df_filtrado['custo'].value_counts().reset_index()
                custo_counts.columns = ['Tipo de Custo', 'Count']
                custo_counts['Percentual'] = (custo_counts['Count'] / custo_counts['Count'].sum() * 100).map('{:.2f}%'.format)
                st.dataframe(custo_counts, use_container_width=True, hide_index=True)
                st.markdown(f"**Total de funcionários:** **`{custo_counts['Count'].sum()}`**")

        with blc2:
            fig_funcao = create_employees_by_function_chart(df_filtrado)
            st.plotly_chart(fig_funcao, use_container_width=True)

        with blc3:
            fig_filhos = create_employees_by_children_chart(df_filtrado)
            st.plotly_chart(fig_filhos, use_container_width=True)

        blc4, blc5, blc6, blc7 = st.columns(4)
        with blc4:
            fig_sexo = create_gender_distribution_chart(df_filtrado)
            st.plotly_chart(fig_sexo, use_container_width=True)

        with blc5:
            ordem_escolaridade = ['Fundamental', 'Médio', 'Superior Incompleto', 'Superior Completo', 'Pós-graduação']
            fig_escolaridade = create_education_level_distribution_chart(df_filtrado, ordem_escolaridade)
            st.plotly_chart(fig_escolaridade, use_container_width=True)

        with blc6:
            fig_admissoes_mes = create_monthly_admissions_chart(df_filtrado)
            st.plotly_chart(fig_admissoes_mes, use_container_width=True)

        with blc7:
            fig_custo_tipo = create_cost_type_distribution_chart(df_filtrado)
            st.plotly_chart(fig_custo_tipo, use_container_width=True)

elif pagina == "Tabelas de Resumo":
    st.header("Dados de Funcionários (Bruto e Filtrado)")

    if df_filtrado.empty:
        st.warning("Nenhum funcionário corresponde aos filtros selecionados. Por favor, ajuste os critérios.")
    else:
        st.dataframe(df_filtrado[[
            'ald', 'nome', 'status', 'empresa', 'setor', 'funcao', 'custo',
            'admissao', 'tempo_de_empresa', 'data_de_nasc.', 'idade', 'formula_hoje',
            'nivel_escolaridade', 'filho(s)', 'quantos', 'faixa_idade', 'previsao_ferias_2025', 'limite'
        ]], use_container_width=True)
        st.markdown(f"**Total de funcionários encontrados:** **`{len(df_filtrado)}`**")

    st.write("---")

    a1, a2 = st.columns([0.4, 1])

    with a1:
        with st.container(border=True):
            b1, b2 = st.columns([0.3, 1])
            with b1:
                st.image("img/cacto.jpg")

            with b2:
                with st.expander("Expandir"):
                    st.write("Lista de Funcionários de Férias")
