import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, no_update, State, html, dcc, dash_table
from app import app
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import numpy as np

#----------------------------------------------------------------------
# 1. MÓDULOS (LÓGICA DE NEGÓCIO)
#----------------------------------------------------------------------

#
# modules/config_manager.py
#

# Adicione no início do arquivo (após os imports)
CONFIG_ESTOQUE = {
    'caminho_arquivo_csv': "./pages/cta_express/estoque/data/DAMI29-05.csv",
    'df_global': None
}

CONFIG_FILE_PATH = "dashboard_config.json"
VALORES_PADRAO_NIVEIS = {
    "limite_estoque_baixo": 10,
    "limite_estoque_medio": 100
}
VALORES_PADRAO_EXCLUSAO = {
    "excluir_grupos": [],
    "excluir_categorias": [],
    "excluir_produtos_codigos": []
}

def _carregar_config_completa():
    """Função auxiliar para carregar todo o JSON de configuração."""
    if not os.path.exists(CONFIG_FILE_PATH):
      return {**VALORES_PADRAO_NIVEIS, **VALORES_PADRAO_EXCLUSAO}
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)
        return config
    except (json.JSONDecodeError, Exception) as e:
        print(f"Erro ao ler arquivo de configuração '{CONFIG_FILE_PATH}': {e}. Usando todos os padrões.")
        return {**VALORES_PADRAO_NIVEIS, **VALORES_PADRAO_EXCLUSAO}

def _salvar_config_completa(config_data):
    """Função auxiliar para salvar todo o JSON de configuração."""
    try:
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config_data, f, indent=4)
        print(f"Configurações salvas em '{CONFIG_FILE_PATH}'")
        return True
    except Exception as e:
        print(f"Erro inesperado ao salvar configuração completa: {e}")
        return False

def carregar_definicoes_niveis_estoque():
    config_completa = _carregar_config_completa()
    niveis = {}
    niveis["limite_estoque_baixo"] = int(config_completa.get("limite_estoque_baixo", VALORES_PADRAO_NIVEIS["limite_estoque_baixo"]))
    niveis["limite_estoque_medio"] = int(config_completa.get("limite_estoque_medio", VALORES_PADRAO_NIVEIS["limite_estoque_medio"]))

    if not (isinstance(niveis["limite_estoque_baixo"], int) and \
            isinstance(niveis["limite_estoque_medio"], int) and \
            niveis["limite_estoque_baixo"] >= 0 and \
            niveis["limite_estoque_medio"] >= 0 and \
            niveis["limite_estoque_medio"] > niveis["limite_estoque_baixo"]):
        print("Valores de níveis de estoque inválidos no config, usando padrões.")
        return VALORES_PADRAO_NIVEIS.copy()
    return niveis

def salvar_definicoes_niveis_estoque(limite_baixo, limite_medio):
    try:
        val_limite_baixo = int(limite_baixo)
        val_limite_medio = int(limite_medio)

        if val_limite_baixo < 0:
            return False, "Limite para Estoque Baixo não pode ser negativo."
        if val_limite_medio <= val_limite_baixo:
            return False, "Limite para Estoque Médio deve ser maior que o Limite para Estoque Baixo."

        config_completa = _carregar_config_completa()
        config_completa["limite_estoque_baixo"] = val_limite_baixo
        config_completa["limite_estoque_medio"] = val_limite_medio
        
        if _salvar_config_completa(config_completa):
            return True, "Definições de níveis de estoque salvas com sucesso!"
        else:
            return False, "Falha ao salvar o arquivo de configuração."
            
    except (ValueError, TypeError):
        return False, "Valores inválidos. Os limites devem ser números inteiros."
    except Exception as e:
        return False, f"Erro inesperado ao salvar níveis: {str(e)}"

def carregar_configuracoes_exclusao():
    """Carrega as configurações de exclusão do arquivo JSON."""
    config_completa = _carregar_config_completa()
    exclusoes = {}
    exclusoes["excluir_grupos"] = config_completa.get("excluir_grupos", VALORES_PADRAO_EXCLUSAO["excluir_grupos"])
    exclusoes["excluir_categorias"] = config_completa.get("excluir_categorias", VALORES_PADRAO_EXCLUSAO["excluir_categorias"])
    exclusoes["excluir_produtos_codigos"] = config_completa.get("excluir_produtos_codigos", VALORES_PADRAO_EXCLUSAO["excluir_produtos_codigos"])
    
    for key in exclusoes:
        if not isinstance(exclusoes[key], list):
            exclusoes[key] = VALORES_PADRAO_EXCLUSAO.get(key, [])
            
    return exclusoes

def salvar_configuracoes_exclusao(grupos_excluir, categorias_excluir, produtos_codigos_excluir):
    """Salva as configurações de exclusão no arquivo JSON."""
    try:
        lista_grupos = grupos_excluir if grupos_excluir is not None else []
        lista_categorias = categorias_excluir if categorias_excluir is not None else []
        lista_produtos_codigos = produtos_codigos_excluir if produtos_codigos_excluir is not None else []

        lista_grupos = [str(g) for g in lista_grupos]
        lista_categorias = [str(c) for c in lista_categorias]
        lista_produtos_codigos = [str(p) for p in lista_produtos_codigos]

        config_completa = _carregar_config_completa()
        config_completa["excluir_grupos"] = lista_grupos
        config_completa["excluir_categorias"] = lista_categorias
        config_completa["excluir_produtos_codigos"] = lista_produtos_codigos

        if _salvar_config_completa(config_completa):
            return True, "Configurações de exclusão salvas com sucesso!"
        else:
            return False, "Falha ao salvar o arquivo de configuração."

    except Exception as e:
        print(f"Erro inesperado ao salvar configurações de exclusão: {e}")
        return False, f"Erro inesperado ao salvar exclusões: {str(e)}"

#
# modules/data_loader.py
#
PREFIXO_CATEGORIA = "* Total Categoria :"
PREFIXO_GRUPO = "* Total GRUPO :"

def _limpar_valor_numerico(serie_valores): 
    """Converte uma série de strings para numérico, tratando separadores e erros."""
    if not pd.api.types.is_string_dtype(serie_valores):
        serie_valores = serie_valores.astype(str)
    
    serie_limpa = serie_valores.str.replace('.', '', regex=False) 
    serie_limpa = serie_limpa.str.replace(',', '.', regex=False)
    return pd.to_numeric(serie_limpa, errors='coerce')

def carregar_produtos_com_hierarquia(caminho_arquivo):
    """
    Carrega produtos e atribui Categoria e Grupo extraídos das linhas de totais.
    """
    try:
        # 1. Adicionando as colunas 6 (Custo Estoque) e 9 (Dias Estoque)
        df_full = pd.read_csv(
            caminho_arquivo,
            delimiter=';',
            encoding='latin-1',
            skiprows=4,
            usecols=[0, 1, 2, 4, 6, 7, 8],  # COLUNAS CORRIGIDAS - índice 8 para DiasEstoque
            header=None,
            low_memory=False,
            dtype=str
        )
        # 2. Renomeando as colunas para refletir os novos dados
        df_full.columns = ['Código', 'Un', 'Produto_Original', 'VendaMensal_Original', 'CustoEstoque_Original', 'Estoque_Original', 'DiasEstoque_Original']
        df_full['CategoriaExtraida'] = pd.NA
        df_full['GrupoExtraido'] = pd.NA

        for index, row in df_full.iterrows():
            produto_original_strip = row['Produto_Original'].strip() if pd.notna(row['Produto_Original']) else ''
            
            if produto_original_strip.startswith(PREFIXO_CATEGORIA):
                nome_categoria = produto_original_strip[len(PREFIXO_CATEGORIA):].strip()
                df_full.loc[index, 'CategoriaExtraida'] = nome_categoria
            
            if produto_original_strip.startswith(PREFIXO_GRUPO):
                nome_grupo = produto_original_strip[len(PREFIXO_GRUPO):].strip()
                df_full.loc[index, 'GrupoExtraido'] = nome_grupo
        
        df_full['Categoria'] = df_full['CategoriaExtraida'].bfill()
        df_full['Grupo'] = df_full['GrupoExtraido'].bfill()

        df_produtos = df_full.copy()

        df_produtos.dropna(subset=['Código'], inplace=True)
        df_produtos['Código'] = df_produtos['Código'].str.strip()
        df_produtos = df_produtos[df_produtos['Código'] != '']

        df_produtos['Produto_Original_strip'] = df_produtos['Produto_Original'].str.strip()
        df_produtos = df_produtos[~df_produtos['Produto_Original_strip'].str.startswith(PREFIXO_CATEGORIA, na=False)]
        df_produtos = df_produtos[~df_produtos['Produto_Original_strip'].str.startswith(PREFIXO_GRUPO, na=False)]
        
        # 3. Selecionando as novas colunas para o DataFrame final
        df_produtos = df_produtos[['Código', 'Un', 'Produto_Original', 
                                   'Estoque_Original', 'VendaMensal_Original', 'CustoEstoque_Original', 'DiasEstoque_Original',
                                   'Categoria', 'Grupo']].copy()
        df_produtos.rename(columns={
            'Produto_Original': 'Produto', 
            'Estoque_Original': 'Estoque',
            'VendaMensal_Original': 'VendaMensal',
            'CustoEstoque_Original': 'CustoEstoque', # <-- NOVO
            'DiasEstoque_Original': 'DiasEstoque'     # <-- NOVO
            }, inplace=True)

        # 4. Limpando e convertendo as novas colunas para número
        df_produtos['Estoque'] = _limpar_valor_numerico(df_produtos['Estoque'])
        df_produtos['VendaMensal'] = _limpar_valor_numerico(df_produtos['VendaMensal'])
        df_produtos['CustoEstoque'] = _limpar_valor_numerico(df_produtos['CustoEstoque']) # <-- NOVO
        df_produtos['DiasEstoque'] = _limpar_valor_numerico(df_produtos['DiasEstoque'])     # <-- NOVO


        if df_produtos.empty:
            print(f"Nenhum produto encontrado após atribuição de hierarquia e filtragem no arquivo: {caminho_arquivo}")
        else:
            print(f"Produtos com hierarquia carregados: {len(df_produtos)} do arquivo: {caminho_arquivo}")
        
        return df_produtos
    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro ao carregar (com hierarquia) os dados de estoque: {e}")
        return pd.DataFrame()


#
# modules/inventory_manager.py
#
def identificar_produtos_estoque_baixo(df_estoque, limite_estoque_baixo):
    """
    Identifica produtos com estoque baixo (Estoque <= limite_estoque_baixo).
    """
    if df_estoque is None or df_estoque.empty or 'Estoque' not in df_estoque.columns:
        return pd.DataFrame(columns=df_estoque.columns if df_estoque is not None else [])

    try:
        limite = float(limite_estoque_baixo)
    except (ValueError, TypeError):
        print(f"Limite de estoque baixo inválido: {limite_estoque_baixo}. Nenhum produto será classificado como baixo.")
        return pd.DataFrame(columns=df_estoque.columns)

    df_copia = df_estoque.copy()
    df_copia['EstoqueNum'] = pd.to_numeric(df_copia['Estoque'], errors='coerce')
    
    df_baixo = df_copia[
        (df_copia['EstoqueNum'].notna()) & 
        (df_copia['EstoqueNum'] <= limite)
    ].copy()
    
    return df_baixo.drop(columns=['EstoqueNum'], errors='ignore')

def gerar_sugestao_compras(df, limite_baixo=10, limite_medio=100, dias_estoque_alerta=30):
    """
    Gera sugestões de compra com lógica AJUSTADA para ter menos "Forte Recomendação".
    
    Nova Lógica:
    - Forte Recomendação: Situações REALMENTE críticas (estoque E dias ambos baixos)
    - Recomendado: Situações problemáticas (pelo menos um critério ruim)
    - Monitorar: Situações controladas mas que merecem atenção
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    df_analise = df.copy()
    
    # Converter colunas para numérico
    df_analise['Estoque'] = pd.to_numeric(df_analise['Estoque'], errors='coerce').fillna(0)
    df_analise['VendaMensal'] = pd.to_numeric(df_analise['VendaMensal'], errors='coerce').fillna(0)
    df_analise['DiasEstoque'] = pd.to_numeric(df_analise['DiasEstoque'], errors='coerce').fillna(0)
    
    # Filtrar apenas produtos com vendas (relevantes para compra)
    df_relevantes = df_analise[df_analise['VendaMensal'] > 0].copy()
    
    if df_relevantes.empty:
        return pd.DataFrame()
    
    # NOVA LÓGICA: Mais restritiva para Forte Recomendação
    def determinar_prioridade(row):
        estoque = row['Estoque']
        dias = row['DiasEstoque']
        
        # Critérios mais específicos
        estoque_critico = estoque <= limite_baixo  # <= 10
        estoque_medio = limite_baixo < estoque <= limite_medio  # 10 < estoque <= 100
        
        dias_muito_criticos = dias <= 15  # Muito crítico
        dias_criticos = 15 < dias <= dias_estoque_alerta  # 15 < dias <= 30
        dias_atenção = dias_estoque_alerta < dias <= 45  # 30 < dias <= 45
        
        # FORTE RECOMENDAÇÃO: Só casos REALMENTE críticos (E, não OU)
        if estoque_critico and dias_muito_criticos:
            return 'Forte Recomendação'
        
        # RECOMENDADO: Situações problemáticas (mais amplo)
        elif (estoque_critico or  # Estoque baixo
              dias_criticos or  # Dias críticos
              (estoque_medio and dias_atenção) or  # Estoque médio + dias atenção
              (estoque_critico and dias <= 30)):  # Estoque baixo + dias razoáveis
            return 'Recomendado'
        
        # MONITORAR: Situações controladas mas que merecem atenção
        else:
            return 'Monitorar'
    
    df_relevantes['Prioridade'] = df_relevantes.apply(determinar_prioridade, axis=1)
    
    # Calcular sugestão de compra (mesma lógica anterior)
    def calcular_sugestao_compra(row):
        venda_diaria = row['VendaMensal'] / 30
        estoque_atual = row['Estoque']
        
        # Definir dias de cobertura desejados baseado na prioridade
        if row['Prioridade'] == 'Forte Recomendação':
            dias_cobertura_desejados = 60  # 2 meses de cobertura
        elif row['Prioridade'] == 'Recomendado':
            dias_cobertura_desejados = 45  # 1.5 meses de cobertura
        else:
            dias_cobertura_desejados = 30  # 1 mês de cobertura
        
        # Calcular estoque ideal
        estoque_ideal = venda_diaria * dias_cobertura_desejados
        
        # Calcular quantidade necessária
        quantidade_necessaria = estoque_ideal - estoque_atual
        
        # Se não precisa comprar, retornar 0
        if quantidade_necessaria <= 0:
            return 0
        
        # Arredondar para múltiplos de 5
        quantidade_sugerida = max(5, int(quantidade_necessaria / 5) * 5)
        
        return quantidade_sugerida
    
    # Calcular quantidade numérica
    df_relevantes['QtdSugerida'] = df_relevantes.apply(calcular_sugestao_compra, axis=1)
    
    # Filtrar apenas produtos que realmente precisam de compra
    df_relevantes = df_relevantes[df_relevantes['QtdSugerida'] > 0].copy()
    
    if df_relevantes.empty:
        return pd.DataFrame()
    
    # Criar coluna formatada para exibição
    df_relevantes['SugestaoCompraFormatada'] = df_relevantes.apply(
        lambda row: f"{int(row['QtdSugerida'])} {row['Un']}" if pd.notna(row['Un']) and str(row['Un']).strip() != '' 
        else f"{int(row['QtdSugerida'])} un",
        axis=1
    )
    
    # Ordenar por prioridade e depois por quantidade sugerida
    ordem_prioridade = ['Forte Recomendação', 'Recomendado', 'Monitorar']
    df_relevantes['PrioridadeOrdem'] = df_relevantes['Prioridade'].map({p: i for i, p in enumerate(ordem_prioridade)})
    df_relevantes = df_relevantes.sort_values(
        by=['PrioridadeOrdem', 'QtdSugerida', 'DiasEstoque'],
        ascending=[True, False, True]
    )
    
    # Selecionar e renomear colunas para retorno
    colunas_retorno = [
        'Código', 'Produto', 'Un', 'Estoque', 'VendaMensal', 
        'DiasEstoque', 'Prioridade', 'SugestaoCompraFormatada'
    ]
    
    df_final = df_relevantes[colunas_retorno].copy()
    df_final.rename(columns={'SugestaoCompraFormatada': 'Sugestão Compra'}, inplace=True)
    
    return df_final

def criar_tabela_sugestao_compras(df_sugestao):
    """Cria tabela de sugestão de compras SEM EMOJIS e com lógica ajustada."""
    if df_sugestao.empty:
        return dbc.Alert("Nenhuma sugestão de compra encontrada. Todos os produtos estão com estoque adequado.", color="success")
    
    # Contar produtos por prioridade para estatísticas
    stats_prioridade = df_sugestao['Prioridade'].value_counts()
    forte_rec = stats_prioridade.get('Forte Recomendação', 0)
    recomendado = stats_prioridade.get('Recomendado', 0)
    monitorar = stats_prioridade.get('Monitorar', 0)
    
    colunas = [
        {"name": "Prioridade", "id": "Prioridade"},
        {"name": "Código", "id": "Código"},
        {"name": "Produto", "id": "Produto"},
        {"name": "Estoque Atual", "id": "Estoque", "type": "numeric"},
        {"name": "Venda Mensal", "id": "VendaMensal", "type": "numeric"},
        {"name": "Dias Estoque", "id": "DiasEstoque", "type": "numeric"},
        {"name": "Sugestão Compra", "id": "Sugestão Compra"}
    ]
    
    estilo = {
        'style_header': {
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold',
            'borderBottom': '2px solid #dee2e6'
        },
        'style_cell': {
            'textAlign': 'left',
            'padding': '8px',
            'borderRight': '1px solid #f0f0f0',
            'borderBottom': '1px solid #f0f0f0'
        },
        'style_data_conditional': [
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgba(0,0,0,0.025)'
            },
            {
                'if': {'filter_query': '{Prioridade} = "Forte Recomendação"'},
                'backgroundColor': 'rgba(220, 53, 69, 0.15)',
                'fontWeight': 'bold'
            },
            {
                'if': {'filter_query': '{Prioridade} = "Recomendado"'},
                'backgroundColor': 'rgba(255, 193, 7, 0.15)'
            },
            {
                'if': {'column_id': 'DiasEstoque', 'filter_query': '{DiasEstoque} <= 7'},
                'backgroundColor': 'rgba(220, 53, 69, 0.3)',
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': 'DiasEstoque', 'filter_query': '{DiasEstoque} > 7 && {DiasEstoque} <= 30'},
                'backgroundColor': 'rgba(255, 193, 7, 0.3)'
            }
        ]
    }
    
    return html.Div([
        html.H5("Sugestão de Compras", className="mb-3"),
        
        # MUDANÇA: Badges SEM EMOJIS
        dbc.Row([
            dbc.Col([
                dbc.Badge(f"Forte Recomendação: {forte_rec}", color="danger", className="me-2"),
                dbc.Badge(f"Recomendado: {recomendado}", color="warning", className="me-2"),
                dbc.Badge(f"Monitorar: {monitorar}", color="info", className="me-2"),
            ], className="mb-3")
        ]),
        
        html.P("Sugestões baseadas em venda mensal e dias de estoque restantes", className="text-muted mb-3"),
        
        dash_table.DataTable(
            id='tabela-sugestao-compras',
            columns=colunas,
            data=df_sugestao.to_dict('records'),
            page_size=20,
            filter_action='native',
            sort_action='native',
            sort_by=[{'column_id': 'Prioridade', 'direction': 'asc'}],
            style_table={'overflowX': 'auto', 'border': '1px solid #dee2e6'},
            **estilo
        )
    ], className="mb-4")
#----------------------------------------------------------------------
# 2. COMPONENTES (ELEMENTOS DA INTERFACE)
#----------------------------------------------------------------------

#
# components/graphs/graficos_estoque.py
#
ORANGE_PALETTE_DISCRETE = px.colors.sequential.YlOrBr
ORANGE_PALETTE_CONTINUOUS = px.colors.sequential.Oranges
MAIN_ORANGE_COLOR_RGB = '255, 127, 42'
MARGENS_GRAFICO_PADRAO = dict(l=40, r=20, t=70, b=50)
MARGENS_GRAFICO_HORIZONTAL = dict(l=120, r=20, t=70, b=40)
MARGENS_GRAFICO_COMPACTO = dict(l=20, r=20, t=40, b=20)

def criar_figura_vazia(titulo="Sem dados para exibir", height=None):
    fig = go.Figure()
    fig.update_layout(
        title_text=titulo,
        title_x=0.5,
        xaxis={"visible": False},
        yaxis={"visible": False},
        paper_bgcolor='white', 
        plot_bgcolor='white',
        margin=MARGENS_GRAFICO_COMPACTO,
        annotations=[{
            "text": titulo, "xref": "paper", "yref": "paper",
            "showarrow": False, "font": {"size": 16}
        }]
    )
    if height: fig.update_layout(height=height)
    return fig

def criar_grafico_estoque_por_grupo(df):
    if df.empty or 'Grupo' not in df.columns or 'Estoque' not in df.columns:
        return criar_figura_vazia("Volume de Estoque por Grupo (Sem Dados)")
    
    df_plot = df.copy()
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)
    
    df_agrupado = df_plot.groupby('Grupo', as_index=False)['Estoque'].sum()
    df_agrupado = df_agrupado[df_agrupado['Estoque'] > 0] 
    
    if df_agrupado.empty:
        return criar_figura_vazia("Volume de Estoque por Grupo (Sem Estoque > 0)")

    try:
        df_agrupado['OrdemNumerica'] = df_agrupado['Grupo'].str.extract(r'^(\d+)').astype(float)
        df_agrupado = df_agrupado.sort_values(by='OrdemNumerica', ascending=True)
    except Exception as e:
        print(f"Aviso: Não foi possível ordenar grupos numericamente, usando ordem alfabética. Erro: {e}")
        df_agrupado = df_agrupado.sort_values(by='Grupo', ascending=True)
    
    fig = px.line(df_agrupado, x='Grupo', y='Estoque', markers=True, title='Volume de Estoque por Grupo', labels={'Estoque': 'Quantidade Total em Estoque', 'Grupo': 'Grupo'})
    
    cor_da_linha = f'rgba({MAIN_ORANGE_COLOR_RGB}, 0.9)'
    cor_do_preenchimento = f'rgba({MAIN_ORANGE_COLOR_RGB}, 0.2)'

    fig.update_traces(line=dict(width=2.5, shape='spline', color=cor_da_linha), marker=dict(size=8, symbol='circle', line=dict(width=1.5, color=cor_da_linha)), fill='tozeroy', fillcolor=cor_do_preenchimento)
    
    fig.update_layout(title_x=0.5, xaxis_title="Grupos de Produto", yaxis_title="Quantidade Total em Estoque", paper_bgcolor='white', plot_bgcolor='white', margin=dict(l=70, r=30, t=70, b=110), xaxis_tickangle=-45, showlegend=False, yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.7)', zeroline=True, zerolinewidth=1.5, zerolinecolor='rgba(200, 200, 200, 0.9)'), xaxis=dict(showgrid=False))
    return fig

def criar_grafico_top_n_produtos_estoque(df, n=7, height=None):
    if df.empty or 'Produto' not in df.columns or 'Estoque' not in df.columns:
        return criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem Dados)", height=height)

    df_plot = df.copy()
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)
    df_com_estoque = df_plot[df_plot['Estoque'] > 0].copy()

    if df_com_estoque.empty:
        return criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem Estoque > 0)", height=height)

    estoque_total_geral = df_com_estoque['Estoque'].sum()
    top_n_df = df_com_estoque.nlargest(n, 'Estoque')
    
    if top_n_df.empty:
        return criar_figura_vazia(f"Top {n} Produtos por Estoque (Nenhum produto no Top N)", height=height)

    estoque_top_n_soma = top_n_df['Estoque'].sum()
    estoque_outros = estoque_total_geral - estoque_top_n_soma
    data_para_pie = [{'NomeExibicao': str(row['Produto']), 'Estoque': row['Estoque']} for _, row in top_n_df.iterrows()]
    if estoque_outros > 0.001:
        data_para_pie.append({'NomeExibicao': 'Outros Produtos', 'Estoque': estoque_outros})
    
    if not data_para_pie:
        return criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem dados para gráfico)", height=height)
        
    df_pie = pd.DataFrame(data_para_pie)
        
    fig = px.pie(df_pie, values='Estoque', names='NomeExibicao', title=f'Participação dos Top {n} Produtos no Estoque (+ Outros)', hole=.4, labels={'Estoque': 'Quantidade em Estoque', 'NomeExibicao': 'Produto/Segmento'}, color_discrete_sequence=px.colors.sequential.Oranges_r)
    
    fig.update_traces(textposition='inside', textinfo='percent+label', insidetextorientation='radial', pull=[0.05 if nome != 'Outros Produtos' else 0 for nome in df_pie['NomeExibicao']])
    fig.update_layout(legend_title_text='Produtos', legend=dict(orientation="v", yanchor="top", y=0.85, xanchor="left", x=1.01), title_x=0.5, paper_bgcolor='white', plot_bgcolor='white', margin=dict(l=20, r=150, t=60, b=20), height=height)
    return fig

def _classificar_nivel_estoque(estoque_val, limite_baixo, limite_medio):
    try:
        lim_b = float(limite_baixo)
        lim_m = float(limite_medio)
    except (ValueError, TypeError):
        return 'Desconhecido (Limites Inválidos)'
    if pd.isna(estoque_val):
        return 'Desconhecido'
    try:
        val = float(estoque_val)
    except (ValueError, TypeError):
        return 'Desconhecido'
    if val <= lim_b:
        return f'Baixo (≤{lim_b:g})'
    elif val <= lim_m:
        return f'Médio ({lim_b:g} < E ≤ {lim_m:g})'
    else: 
        return f'Alto (>{lim_m:g})'

def criar_grafico_niveis_estoque(df, limite_baixo=10, limite_medio=100, height=None):
    if df.empty or 'Estoque' not in df.columns:
        return criar_figura_vazia("Produtos por Nível de Estoque", height=height)

    df_plot = df.copy()
    df_plot['EstoqueNum'] = pd.to_numeric(df_plot['Estoque'], errors='coerce') 
    df_plot['NivelEstoque'] = df_plot['EstoqueNum'].apply(lambda x: _classificar_nivel_estoque(x, limite_baixo, limite_medio))
    
    contagem_niveis = df_plot['NivelEstoque'].value_counts().reset_index()
    contagem_niveis.columns = ['NivelEstoque', 'Contagem']
    
    cat_baixo_label = f'Baixo (≤{float(limite_baixo):g})'
    cat_medio_label = f'Médio ({float(limite_baixo):g} < E ≤ {float(limite_medio):g})'
    cat_alto_label = f'Alto (>{float(limite_medio):g})'
    
    ordem_niveis_plot = [cat_alto_label, cat_medio_label, cat_baixo_label, 'Desconhecido', 'Desconhecido (Limites Inválidos)']
    
    niveis_presentes_dados = df_plot['NivelEstoque'].unique()
    ordem_final_para_plot = [nivel for nivel in ordem_niveis_plot if nivel in niveis_presentes_dados]

    contagem_niveis['NivelEstoque'] = pd.Categorical(contagem_niveis['NivelEstoque'], categories=ordem_final_para_plot, ordered=True)
    contagem_niveis = contagem_niveis.sort_values('NivelEstoque').dropna(subset=['NivelEstoque'])
    
    if contagem_niveis.empty or contagem_niveis['Contagem'].sum() == 0:
        return criar_figura_vazia("Níveis de Estoque (Sem Produtos para Classificar)", height=height)

    mapa_cores = { cat_baixo_label: 'rgba(255, 87, 34, 0.8)', cat_medio_label: 'rgba(251, 140, 0, 0.8)', cat_alto_label: 'rgba(255, 193, 7, 0.8)', 'Desconhecido': 'rgba(245, 172, 123, 0.8)', 'Desconhecido (Limites Inválidos)': 'rgba(205, 133, 63, 0.8)' }

    fig = px.bar(contagem_niveis, x='NivelEstoque', y='Contagem', title='Produtos por Nível de Estoque', labels={'Contagem': 'Nº de Produtos', 'NivelEstoque': 'Nível de Estoque'}, color='NivelEstoque', color_discrete_map=mapa_cores)
    
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False, title_x=0.5, xaxis_title=None, yaxis_showgrid=True, yaxis_gridcolor='lightgray', paper_bgcolor='white', plot_bgcolor='white', margin=MARGENS_GRAFICO_PADRAO, height=height)
    return fig

def criar_grafico_categorias_com_estoque_baixo(df_estoque_baixo, top_n=10):
    if df_estoque_baixo is None or df_estoque_baixo.empty or 'Categoria' not in df_estoque_baixo.columns or 'Código' not in df_estoque_baixo.columns:
        return criar_figura_vazia(f"Categorias com Estoque Baixo (Sem Dados)")

    contagem_categorias = df_estoque_baixo.groupby('Categoria')['Código'].nunique().reset_index()
    contagem_categorias.rename(columns={'Código': 'NumeroDeProdutosBaixos'}, inplace=True)
    contagem_categorias_top_n = contagem_categorias.nlargest(top_n, 'NumeroDeProdutosBaixos')
    
    if contagem_categorias_top_n.empty:
        return criar_figura_vazia(f"Categorias com Estoque Baixo (Sem produtos baixos)")

    contagem_categorias_top_n = contagem_categorias_top_n.sort_values(by='NumeroDeProdutosBaixos', ascending=True)

    fig = px.bar(contagem_categorias_top_n, y='Categoria', x='NumeroDeProdutosBaixos', orientation='h', title=f'Top {top_n} Categorias por Nº de Produtos em Estoque Baixo', labels={'NumeroDeProdutosBaixos': 'Nº de Produtos Baixos', 'Categoria': 'Categoria'}, color_discrete_sequence=[f'rgba({MAIN_ORANGE_COLOR_RGB}, 0.8)'])
    
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis={'categoryorder':'total ascending', 'dtick': 1, 'ticksuffix': '  '}, xaxis_showgrid=True, xaxis_gridcolor='lightgray', title_x=0.5, paper_bgcolor='white', plot_bgcolor='white', margin=MARGENS_GRAFICO_HORIZONTAL)
    return fig

def criar_grafico_estoque_produtos_populares(df, n=7, abreviar_nomes=False):
    if df is None or df.empty or 'Produto' not in df.columns or 'VendaMensal' not in df.columns or 'Estoque' not in df.columns:
        return criar_figura_vazia(f"Venda vs. Estoque dos Top {n} Produtos (Sem Dados)")

    df_plot = df.copy()
    df_plot['VendaMensalNum'] = pd.to_numeric(df_plot['VendaMensal'], errors='coerce').fillna(0)
    df_plot['EstoqueNum'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)

    produtos_populares_df = df_plot[df_plot['VendaMensalNum'] > 0].nlargest(n, 'VendaMensalNum')
    
    if produtos_populares_df.empty:
        return criar_figura_vazia(f"Venda vs. Estoque dos Top {n} Produtos (Sem produtos com vendas)")

    produtos_populares_df = produtos_populares_df.sort_values(by='VendaMensalNum', ascending=False)
    
    x_axis_values = produtos_populares_df['Produto']

    cor_estoque = 'rgba(251, 140, 0, 0.8)'
    cor_vendas = 'rgba(220, 53, 69, 0.8)'

    trace_estoque = go.Bar(
        name='Estoque',
        x=x_axis_values,
        y=produtos_populares_df['EstoqueNum'],
        marker_color=cor_estoque
    )
    
    trace_vendas = go.Bar(
        name='Vendas no Mês',
        x=x_axis_values,
        y=produtos_populares_df['VendaMensalNum'],
        marker_color=cor_vendas
    )

    fig = go.Figure(data=[trace_estoque, trace_vendas])

    margem_inferior = 80 if abreviar_nomes else 180
    
    fig.update_layout(
        barmode='group',
        title_text=f'Estoque vs. Venda Mensal (Top {produtos_populares_df.shape[0]} Produtos Populares)',
        title_x=0.5,
        xaxis_title=None,
        yaxis_title="Quantidade",
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=50, r=20, t=80, b=margem_inferior),
        showlegend=False,
        # --- ALTERAÇÃO AQUI ---
        yaxis=dict(
            showgrid=True, 
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=1, # <-- Espessura alterada para 1
            zerolinecolor='lightgray' # <-- Cor alterada para coincidir com o grid
        )
    )

    if abreviar_nomes:
        tick_labels = [(p[:10] + '...') if len(p) > 10 else p for p in x_axis_values]
        fig.update_xaxes(
            tickvals=x_axis_values,
            ticktext=tick_labels,
            tickangle=-45
        )
    else:
        fig.update_xaxes(tickangle=-45)

    return fig

def criar_grafico_colunas_estoque_por_grupo(df_filtrado):
    titulo_grafico = "Estoque por Grupo (Treemap)"
    nova_altura_grafico = 450

    if df_filtrado.empty or 'Grupo' not in df_filtrado.columns or 'Estoque' not in df_filtrado.columns:
        fig = px.treemap(title=f"{titulo_grafico} - Sem dados")
        fig.update_layout(height=nova_altura_grafico, margin=dict(t=50, b=5, l=5, r=5), paper_bgcolor='white', font_color="black")
        return fig

    df_filtrado['Estoque'] = pd.to_numeric(df_filtrado['Estoque'], errors='coerce').fillna(0)
    df_para_treemap = df_filtrado[df_filtrado['Estoque'] > 0].copy()

    if df_para_treemap.empty:
        fig = px.treemap(title=f"{titulo_grafico} - Sem dados positivos")
        fig.update_layout(height=nova_altura_grafico, margin=dict(t=50, b=5, l=5, r=5), paper_bgcolor='white', font_color="black")
        return fig

    df_para_treemap['NomeGrupo'] = df_para_treemap['Grupo'].str.replace(r'^\d+\s*', '', regex=True)

    fig = px.treemap(df_para_treemap, path=[px.Constant("Todos os Grupos"), 'NomeGrupo'], values='Estoque', title=titulo_grafico, color='Estoque', color_continuous_scale=ORANGE_PALETTE_CONTINUOUS, custom_data=['NomeGrupo', 'Estoque'])
    fig.update_traces(textinfo='label + percent root', hovertemplate='<b>%{customdata[0]}</b><br>Estoque: %{customdata[1]:,.0f}<extra></extra>', textposition='middle center', textfont=dict(family="Arial Black, sans-serif", size=11, color="black"), marker_line_width=1, marker_line_color='rgba(255,255,255,0.5)')
    fig.update_layout(height=nova_altura_grafico, margin=dict(t=50, b=15, l=15, r=15), paper_bgcolor='white', plot_bgcolor='white', font_color="black", title_font_size=18, title_x=0.5)
    return fig

def criar_grafico_produtos_sem_venda(df, top_n: int = 20):
    """Mostra os produtos que não venderam nada no mês."""
    if df is None or df.empty or \
       {'VendaMensal', 'Estoque', 'Produto'}.difference(df.columns):
        return criar_figura_vazia("Produtos Sem Venda (Dados incompletos)")

    df_plot = df.copy()
    df_plot['VendaMensal'] = pd.to_numeric(df_plot['VendaMensal'], errors='coerce').fillna(0)
    df_plot['Estoque']     = pd.to_numeric(df_plot['Estoque'],     errors='coerce').fillna(0)

    df_sem_venda = df_plot[df_plot['VendaMensal'] == 0]
    if df_sem_venda.empty:
        return criar_figura_vazia("Nenhum produto sem venda no período")

    top_df = df_sem_venda.nlargest(top_n, 'Estoque')      # ordena pelos maiores estoques
    fig = px.bar(
        top_df,
        x='Estoque', y='Produto', orientation='h',
        title=f'Produtos Sem Venda (Top {top_df.shape[0]})',
        labels={'Estoque': 'Qtde em Estoque'},
        color_discrete_sequence=[f'rgba({MAIN_ORANGE_COLOR_RGB},0.8)']
    )
    fig.update_traces(text=top_df['Estoque'], textposition='outside')
    fig.update_layout(title_x=0.5, paper_bgcolor='white', plot_bgcolor='white',
                      margin=MARGENS_GRAFICO_HORIZONTAL)
    return fig

def criar_tabela_previsao_estoque(df, dias_maximos=100):
    """Cria uma tabela com produtos que têm previsão de estoque até X dias, ordenada crescente."""
    
    # 1. Checa se os dados necessários existem
    if df is None or df.empty or 'DiasEstoque' not in df.columns or 'Produto' not in df.columns or 'Estoque' not in df.columns:
        return dbc.Alert("Dados incompletos para calcular previsão de estoque.", color="warning")
    
    # 2. Limpa e filtra os dados
    df_plot = df.copy()
    df_plot['DiasEstoque'] = pd.to_numeric(df_plot['DiasEstoque'], errors='coerce')
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce')
    
    # Filtrar produtos com previsão válida (0 < dias <= 100) e estoque > 0
    df_filtrado = df_plot[
        (df_plot['DiasEstoque'] > 0) & 
        (df_plot['DiasEstoque'] <= dias_maximos) &
        (df_plot['Estoque'] > 0) &
        (df_plot['DiasEstoque'].notna())
    ]
    
    if df_filtrado.empty:
        return dbc.Alert(f"Nenhum produto com previsão de estoque entre 1 e {dias_maximos} dias.", color="info")
    
    # Ordenar por dias de estoque (crescente)
    df_filtrado = df_filtrado.sort_values('DiasEstoque', ascending=True)
    
    # Formatar colunas para exibição
    df_filtrado['DiasEstoque'] = df_filtrado['DiasEstoque'].round(1)
    df_filtrado['Estoque'] = df_filtrado['Estoque'].round(0)
    
    # Criar a tabela
    colunas = [
        {"name": "Produto", "id": "Produto"},
        {"name": "Dias de Estoque", "id": "DiasEstoque", "type": "numeric"},
        {"name": "Estoque Atual", "id": "Estoque", "type": "numeric"}
    ]
    
    estilo = {
        'style_header': {
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold',
            'borderBottom': '2px solid #dee2e6'
        },
        'style_cell': {
            'textAlign': 'left',
            'padding': '8px',
            'borderRight': '1px solid #f0f0f0',
            'borderBottom': '1px solid #f0f0f0'
        },
        'style_data_conditional': [
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgba(0,0,0,0.025)'
            },
            {
                'if': {'column_id': 'DiasEstoque', 'filter_query': '{DiasEstoque} <= 7'},
                'backgroundColor': 'rgba(220, 53, 69, 0.2)',
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': 'DiasEstoque', 'filter_query': '{DiasEstoque} > 7 && {DiasEstoque} <= 30'},
                'backgroundColor': 'rgba(255, 193, 7, 0.2)'
            }
        ]
    }
    
    tabela = dash_table.DataTable(
        id='tabela-previsao-estoque',
        columns=colunas,
        data=df_filtrado.to_dict('records'),
        page_size=20,
        filter_action='native',
        sort_action='native',
        style_table={'overflowX': 'auto', 'border': '1px solid #dee2e6'},
        **estilo
    )
    
    return html.Div([
        html.H5(f"Previsão de Estoque (até {dias_maximos} dias)", className="mb-3"),
        tabela
    ])


#
# components/tables/table1.py
#
def criar_tabela_produtos_criticos(df_produtos, id_tabela, titulo_alerta, page_size=5, altura_tabela='300px'):
    if df_produtos.empty:
        return dbc.Alert(f"{titulo_alerta}: Nenhum produto encontrado.", color="info", className="mt-2")

    colunas_para_dash = [{"name": "Produto", "id": "Produto"}, {"name": "Estoque Atual", "id": "Estoque"}]
    dados_para_tabela = df_produtos[['Produto', 'Estoque']].to_dict('records')
    page_size_real = max(1, len(dados_para_tabela)) 

    return html.Div([
        html.H6(titulo_alerta, className="mt-3 text-danger fw-bold"),
        dash_table.DataTable(id=id_tabela, columns=colunas_para_dash, data=dados_para_tabela, page_size=page_size_real, style_table={'height': altura_tabela, 'overflowY': 'auto', 'overflowX': 'auto', 'width': '100%', 'border': '1px solid #dee2e6', 'borderRadius': '0.25rem'}, style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold', 'borderBottom': '2px solid #dee2e6', 'padding': '8px', 'textAlign': 'left', 'position': 'sticky', 'top': 0, 'zIndex': 1}, style_cell={'textAlign': 'left', 'padding': '8px', 'borderRight': '1px solid #f0f0f0', 'borderBottom': '1px solid #f0f0f0', 'overflow': 'hidden', 'textOverflow': 'ellipsis', 'maxWidth': 0}, style_cell_conditional=[{'if': {'column_id': 'Produto'}, 'minWidth': '200px', 'width': '70%'}, {'if': {'column_id': 'Estoque'}, 'textAlign': 'right', 'minWidth': '80px', 'width': '30%'}], style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.025)'}, {'if': {'filter_query': '{Estoque} <= 0', 'column_id': 'Estoque'}, 'backgroundColor': 'rgba(220, 53, 69, 0.7)', 'color': 'white', 'fontWeight': 'bold'}])
    ])


def criar_grafico_produtos_sem_venda_por_grupo(df):
    """Cria um treemap dos produtos sem venda agrupados por grupo."""
    titulo_grafico = "Produtos Sem Venda por Grupo"
    nova_altura_grafico = 450

    if df.empty or 'Grupo' not in df.columns or 'VendaMensal' not in df.columns or 'Estoque' not in df.columns:
        fig = px.treemap(title=f"{titulo_grafico} - Sem dados")
        fig.update_layout(height=nova_altura_grafico, margin=dict(t=50, b=5, l=5, r=5), paper_bgcolor='white', font_color="black")
        return fig

    df_plot = df.copy()
    df_plot['VendaMensal'] = pd.to_numeric(df_plot['VendaMensal'], errors='coerce').fillna(0)
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)

    # Filtrar apenas produtos sem venda e com estoque
    df_sem_venda = df_plot[(df_plot['VendaMensal'] == 0) & (df_plot['Estoque'] > 0)].copy()

    if df_sem_venda.empty:
        fig = px.treemap(title=f"{titulo_grafico} - Nenhum produto sem venda")
        fig.update_layout(height=nova_altura_grafico, margin=dict(t=50, b=5, l=5, r=5), paper_bgcolor='white', font_color="black")
        return fig

    # Agrupar por grupo e contar produtos sem venda
    df_agrupado = df_sem_venda.groupby('Grupo').agg({
        'Código': 'count',  # Contagem de produtos sem venda
        'Estoque': 'sum'    # Soma do estoque parado
    }).reset_index()
    
    df_agrupado.columns = ['Grupo', 'QtdProdutosSemVenda', 'EstoqueParado']
    df_agrupado['NomeGrupo'] = df_agrupado['Grupo'].str.replace(r'^\d+\s*', '', regex=True)

    # Usar a quantidade de produtos sem venda como valor do treemap
    fig = px.treemap(
        df_agrupado, 
        path=[px.Constant("Todos os Grupos"), 'NomeGrupo'], 
        values='QtdProdutosSemVenda', 
        title=titulo_grafico,
        color='EstoqueParado',
        color_continuous_scale=px.colors.sequential.Reds,
        custom_data=['NomeGrupo', 'QtdProdutosSemVenda', 'EstoqueParado']
    )
    
    fig.update_traces(
        textinfo='label + value',
        hovertemplate='<b>%{customdata[0]}</b><br>Produtos sem venda: %{customdata[1]}<br>Estoque parado: %{customdata[2]:,.0f}<extra></extra>',
        textposition='middle center',
        textfont=dict(
            family="Arial Black, sans-serif", 
            size=11, 
            color="black"  # MUDANÇA: texto branco
        ),
        marker_line_width=1,
        marker_line_color='rgba(255,255,255,0.5)'
    )
    
    fig.update_layout(
        height=nova_altura_grafico,
        margin=dict(t=50, b=15, l=15, r=15),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color="black",
        title_font_size=18,
        title_x=0.5
    )
    
    return fig

def criar_conteudo_principal(df_completo, page_size_tabela=20):
    '''Cria o layout principal - VERSÃO COM ALTURA CORRIGIDA DA PREVISÃO.'''
    if df_completo is None or df_completo.empty:
        return dbc.Alert("Dados de estoque não carregados. Verifique o arquivo de dados.", color="danger")

    # Previsão de estoque compacta com altura ajustada para dar match
    previsao_estoque_compacta_card = dbc.Card(
        dbc.CardBody([
            html.H5("Previsão de Estoque", className="mb-3 text-center fw-bold"),
            html.Div(id='tabela-previsao-estoque-container')  # Container será preenchido pelo callback
        ], style={'height': '450px'}),  # MUDANÇA: altura fixa de 450px para dar match
        className="shadow-sm h-100"
    )

    altura_graficos_padrao = '410px'
    grafico_estoque_grupo_card = dbc.Card(dbc.CardBody(dcc.Graph(id='grafico-estoque-grupo', config={'displayModeBar': False}, style={'height': '530px'})), className="shadow-sm h-100")
    grafico_estoque_populares_card = html.Div(
        dbc.Card(dbc.CardBody(dcc.Graph(id='grafico-estoque-populares', config={'displayModeBar': False}, style={'height': altura_graficos_padrao}))),
        id='card-clicavel-populares',
        style={'cursor': 'pointer'},
        className="shadow-sm h-100"
    )
    grafico_colunas_resumo_treemap_card = dbc.Card(dbc.CardBody(dcc.Graph(id='grafico-colunas-resumo-estoque', config={'displayModeBar': False})), className="shadow-sm h-100")
    grafico_sec_top_n_card_clicavel = html.Div(dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-top-n-produtos', config={'displayModeBar': True}, style={'height': altura_graficos_padrao}))], className="shadow-sm h-100 clickable-card"), id="card-clicavel-grafico-donut", style={'cursor': 'pointer'})
    grafico_sec_niveis_card_clicavel = html.Div(dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-niveis-estoque', config={'displayModeBar': True}, style={'height': '530px'}))], className="shadow-sm h-100 clickable-card"), id="card-clicavel-grafico-niveis", style={'cursor': 'pointer'})
    tabela_estoque_baixo_card = dbc.Card([dbc.CardBody(html.Div(id='container-tabela-alerta-estoque-baixo-geral'))], className="shadow-sm h-100", style={'height': '450px'})
    grafico_cat_estoque_baixo_card = dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-categorias-estoque-baixo-visao-geral', config={'displayModeBar': False}))], className="shadow-sm h-100", style={'height': '400px'})
    
    # Card do gráfico de produtos sem venda
    grafico_sem_venda_card = html.Div(
        dbc.Card(
            dbc.CardBody(
                dcc.Graph(id='grafico-produtos-sem-venda-grupo', config={'displayModeBar': False})
            ),
            className="shadow-sm"
        ),
        id='card-clicavel-sem-venda',
        style={'cursor': 'pointer'}
    )
    
    tabela_sugestao_compras_card = dbc.Card(
        dbc.CardBody(html.Div(id='tabela-sugestao-compras-container')),
        className="shadow-sm"
    )

    download_component = dcc.Download(id="download-tabela-geral-excel")
    modal_grafico_donut = dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Participação dos Top 7 Produtos no Estoque")), dbc.ModalBody(dcc.Graph(id='grafico-donut-modal', style={'height': '65vh'})), dbc.ModalFooter(dbc.Button("Fechar", id="btn-fechar-modal-donut", className="ms-auto", n_clicks=0, color="warning"))], id="modal-grafico-donut-popup", size="xl", is_open=False, centered=True)
    modal_grafico_niveis = dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Clique na Coluna para ver Detalhes")), dbc.ModalBody([dcc.Graph(id='grafico-niveis-modal', style={'height': '50vh'}), html.Hr(), html.H5("Produtos no Nível Selecionado:", className="mt-3"), html.Div(id='tabela-detalhes-nivel-estoque-modal-container')]), dbc.ModalFooter(dbc.Button("Fechar", id="btn-fechar-modal-niveis", className="ms-auto", n_clicks=0, color="warning"))], id="modal-grafico-niveis-popup", size="xl", is_open=False, centered=True)
    modal_grafico_populares = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Estoque vs. Venda Mensal (Nomes Completos)")),
        dbc.ModalBody(dcc.Graph(id='grafico-populares-modal', style={'height': '70vh'})),
        dbc.ModalFooter(dbc.Button("Fechar", id="btn-fechar-modal-populares", className="ms-auto", n_clicks=0))
    ],
    id="modal-grafico-populares-popup",
    size="xl",
    is_open=False,
    )   

    # Modal para produtos sem venda
    modal_produtos_sem_venda = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Produtos Sem Venda no Grupo Selecionado")),
        dbc.ModalBody([
            html.H5(id="titulo-grupo-sem-venda", className="mb-3"),
            html.Div(id='tabela-produtos-sem-venda-grupo-modal-container')
        ]),
        dbc.ModalFooter(
            dbc.Button("Fechar", id="btn-fechar-modal-sem-venda", className="ms-auto", n_clicks=0, color="warning")
        )
    ], id="modal-produtos-sem-venda-popup", size="xl", is_open=False, centered=True)

    layout_principal = html.Div([
        dbc.Row([
            dbc.Col(grafico_estoque_grupo_card, width=12, lg=7),
            dbc.Col(grafico_sec_niveis_card_clicavel, width=12, lg=5),
        ], className="g-2 mb-2", align="stretch"),

        html.Hr(className="my-2"),
        dbc.Row([
            dbc.Col(grafico_estoque_populares_card, width=12, lg=6),
            dbc.Col(grafico_sec_top_n_card_clicavel, width=12, lg=6),
        ], className="g-2 mb-2", align="stretch"),

        html.Hr(className="my-2"),
        # MUDANÇA: Previsão de estoque com altura corrigida
        dbc.Row([
            dbc.Col(previsao_estoque_compacta_card, width=12, lg=3),
            dbc.Col(grafico_colunas_resumo_treemap_card, width=12, lg=9),
        ], className="g-2 mb-2", align="stretch"),

        html.Hr(className="my-2"),
        dbc.Row([
            dbc.Col(grafico_cat_estoque_baixo_card, width=12, lg=8),
            dbc.Col(tabela_estoque_baixo_card, width=12, lg=4)
        ], className="mb-2", align="stretch"),
        html.Hr(className="my-2"),
        
        # Gráfico de produtos sem venda
        dbc.Row([
            dbc.Col(grafico_sem_venda_card, width=12)
        ], className="mb-2"),
        
        dbc.Row([
            dbc.Col(tabela_sugestao_compras_card, width=12)
        ], className="mb-2"),
        download_component,
        modal_grafico_donut,
        modal_grafico_niveis,
        modal_grafico_populares,
        modal_produtos_sem_venda
    ], className="p-2")

    return layout_principal


#
# components/header.py
#
def criar_cabecalho(df_completo):
    """Cria um cabeçalho estilizado com cards de métricas do estoque FILTRADO."""
    
    def criar_card_metrica(titulo, id_valor, icone_bootstrap):
        """Função auxiliar para criar um card de métrica individual."""
        return dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.P(titulo, className="text-muted mb-2", style={'fontSize': '0.85rem'}),
                        dbc.Row(
                            [
                                dbc.Col(html.I(className=f"{icone_bootstrap} fs-2 text-muted"), width="auto"),
                                dbc.Col(html.H4(id=id_valor, className="fw-bold text-end"), width=True),
                            ],
                            align="center",
                        ),
                    ]
                ),
                className="shadow-sm border-0 h-100",
            ),
            width=6,
            lg=3,
            className="mb-3 mb-lg-0",
        )

    header_layout = html.Div(
        dbc.Container(
            [
                dbc.Row(
                    [
                        # Coluna do Título e Botões
                        dbc.Col(
                            [
                                html.H4("Controle de Estoque", className="fw-bold"),
                                html.P("Dados atualizados conforme filtros aplicados", className="text-muted mb-2"),
                                html.Div([
                                    dbc.Button(
                                        "Configurações", id="btn-abrir-modal-config", n_clicks=0,
                                        color="secondary", outline=True, size="sm", className="me-2"
                                    ),
                                    dbc.Button(
                                        "Filtros", id="btn-toggle-painel-esquerdo", n_clicks=0,
                                        color="warning", outline=True, size="sm"
                                    ),
                                ], className="mt-2")
                            ],
                            width=12,
                            lg=4,
                            className="d-flex flex-column justify-content-center",
                        ),
                        # Coluna dos Cards de Métrica FILTRADA
                        dbc.Col(
                            dbc.Row(
                                [
                                    criar_card_metrica("Total de SKUs", "header-total-skus", "bi bi-upc-scan"),
                                    criar_card_metrica("Estoque Total", "header-estoque-total", "bi bi-archive-fill"),
                                    criar_card_metrica("Categorias", "header-categorias", "bi bi-tags-fill"),
                                    criar_card_metrica("Grupos", "header-grupos", "bi bi-diagram-3-fill"),
                                ],
                            ),
                            width=12,
                            lg=8,
                        ),
                    ],
                    align="stretch",
                    className="py-3",
                )
            ],
            fluid=True,
        ),
        className="border-bottom bg-light mb-4",
    )

    return header_layout

#
# components/configuracoes.py
#
def criar_conteudo_aba_configuracoes(df_completo_para_opcoes):
    """Cria o layout para a aba de Configurações."""
    config_niveis_atuais = carregar_definicoes_niveis_estoque()
    valor_inicial_baixo = config_niveis_atuais.get("limite_estoque_baixo")
    valor_inicial_medio = config_niveis_atuais.get("limite_estoque_medio")

    config_exclusao_atuais = carregar_configuracoes_exclusao()
    grupos_excluidos_atuais = config_exclusao_atuais.get("excluir_grupos", [])
    categorias_excluidas_atuais = config_exclusao_atuais.get("excluir_categorias", [])
    produtos_excluidos_atuais_codigos = config_exclusao_atuais.get("excluir_produtos_codigos", [])

    opcoes_grupos_excluir, opcoes_categorias_excluir, opcoes_produtos_excluir = [], [], []
    if df_completo_para_opcoes is not None and not df_completo_para_opcoes.empty:
        opcoes_grupos_excluir = [{'label': str(grp), 'value': str(grp)} for grp in sorted(df_completo_para_opcoes['Grupo'].dropna().unique())]
        opcoes_categorias_excluir = [{'label': str(cat), 'value': str(cat)} for cat in sorted(df_completo_para_opcoes['Categoria'].dropna().unique())]
        produtos_unicos = df_completo_para_opcoes.drop_duplicates(subset=['Código'])
        opcoes_produtos_excluir = sorted([
            {'label': f"{row['Produto']} (Cód: {row['Código']})", 'value': str(row['Código'])} 
            for index, row in produtos_unicos.iterrows() if pd.notna(row['Código']) and str(row['Código']).strip() != ''
        ], key=lambda x: x['label'])

    card_definicoes_niveis = dbc.Card([
        dbc.CardHeader(html.H5("Definições de Níveis de Estoque", className="my-2")),
        dbc.CardBody([
            html.P("Defina os valores para as faixas de Estoque Baixo, Médio e Alto."),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Estoque Baixo é: Estoque ≤", html_for="input-limite-config-baixo", className="fw-bold"),
                    dcc.Input(id="input-limite-config-baixo", type="number", placeholder=f"Padrão: {VALORES_PADRAO_NIVEIS['limite_estoque_baixo']}", min=0, step=1, value=valor_inicial_baixo, className="form-control mb-2", style={'maxWidth': '150px'}),
                ], md=6),
                dbc.Col([
                    dbc.Label("Estoque Médio é: > Baixo e ≤", html_for="input-limite-config-medio", className="fw-bold"),
                    dcc.Input(id="input-limite-config-medio", type="number", placeholder=f"Padrão: {VALORES_PADRAO_NIVEIS['limite_estoque_medio']}", min=0, step=1, value=valor_inicial_medio, className="form-control mb-2", style={'maxWidth': '150px'}),
                ], md=6)
            ], className="mb-3"),
            html.P(html.Small(["Estoque Alto será: Estoque > Limite Médio"]), className="text-muted mt-1"),
            dbc.Button("Salvar Definições de Níveis", id="btn-salvar-config-niveis", color="primary", className="mt-2 mb-3"),
            html.Div(id="div-status-config-niveis", className="mt-2"),
            html.Div([
                html.H6("Definições de Níveis Atuais:", className="mt-3"),
                dbc.Row([dbc.Col(html.Strong("Limite Estoque Baixo (≤):"), width="auto", className="pe-0"), dbc.Col(html.Span(id="span-config-atual-limite-baixo", children=str(valor_inicial_baixo)))]),
                dbc.Row([dbc.Col(html.Strong("Limite Estoque Médio (> Baixo e ≤):"), width="auto", className="pe-0"), dbc.Col(html.Span(id="span-config-atual-limite-medio", children=str(valor_inicial_medio)))]),
            ], className="mt-3 p-3 border rounded bg-light")
        ])
    ], className="h-100 shadow-sm")

    card_excluir_itens = dbc.Card([
        dbc.CardHeader(html.H5("Excluir Itens da Visualização Principal", className="my-2")),
        dbc.CardBody([
            html.P("Selecione itens para não exibir na aba 'Visão Geral do Estoque'."),
            dbc.Label("Grupos a Excluir:", className="fw-bold"),
            dcc.Dropdown(id='dropdown-excluir-grupos', options=opcoes_grupos_excluir, value=grupos_excluidos_atuais, multi=True, placeholder="Selecione Grupos"),
            html.Br(),
            dbc.Label("Categorias a Excluir:", className="fw-bold"),
            dcc.Dropdown(id='dropdown-excluir-categorias', options=opcoes_categorias_excluir, value=categorias_excluidas_atuais, multi=True, placeholder="Selecione Categorias"),
            html.Br(),
            dbc.Label("Produtos (por Código) a Excluir:", className="fw-bold"),
            dcc.Dropdown(id='dropdown-excluir-produtos-codigos', options=opcoes_produtos_excluir, value=produtos_excluidos_atuais_codigos, multi=True, searchable=True, placeholder="Busque e selecione Produtos"),
            dbc.Button("Salvar Exclusões", id="btn-salvar-exclusoes", color="danger", className="mt-3 mb-3"),
            html.Div(id="div-status-salvar-exclusoes", className="mt-2"),
            html.Div([
                html.H6("Itens Atualmente Excluídos:", className="mt-3"),
                dbc.Row([dbc.Col(html.Strong("Grupos:"), width="auto", className="pe-0"), dbc.Col(html.Span(id="span-excluidos-grupos", children=", ".join(grupos_excluidos_atuais) if grupos_excluidos_atuais else "Nenhum"))]),
                dbc.Row([dbc.Col(html.Strong("Categorias:"), width="auto", className="pe-0"), dbc.Col(html.Span(id="span-excluidos-categorias", children=", ".join(categorias_excluidas_atuais) if categorias_excluidas_atuais else "Nenhuma"))]),
                dbc.Row([dbc.Col(html.Strong("Produtos (Códigos):"), width="auto", className="pe-0"), dbc.Col(html.Span(id="span-excluidos-produtos-codigos", children=", ".join(produtos_excluidos_atuais_codigos) if produtos_excluidos_atuais_codigos else "Nenhum"))]),
            ], className="mt-3 p-3 border rounded bg-light")
        ])
    ], className="h-100 shadow-sm")

    layout_configuracoes = html.Div([
        dbc.Row([ 
            dbc.Col(card_definicoes_niveis, width=12, lg=6, className="mb-4"), 
            dbc.Col(card_excluir_itens, width=12, lg=6, className="mb-4")    
        ], className="g-3") 
    ])

    return layout_configuracoes

#
# components/main_content.py
#


    '''Cria o layout principal com todos os gráficos e cartões - VERSÃO REORGANIZADA.'''
    if df_completo is None or df_completo.empty:
        return dbc.Alert("Dados de estoque não carregados. Verifique o arquivo de dados.", color="danger")

    # MUDANÇA: Remover os cards de resumo e substituir por previsão de estoque compacta
    previsao_estoque_compacta_card = dbc.Card(
        dbc.CardBody([
            html.H5("Previsão de Estoque", className="mb-3 text-center fw-bold"),
            html.Div(id='tabela-previsao-estoque-container', style={'height': '400px', 'overflow-y': 'auto'})
        ]), 
        className="shadow-sm h-100"
    )

    altura_graficos_padrao = '410px'
    grafico_estoque_grupo_card = dbc.Card(dbc.CardBody(dcc.Graph(id='grafico-estoque-grupo', config={'displayModeBar': False}, style={'height': '530px'})), className="shadow-sm h-100")
    grafico_estoque_populares_card = html.Div(
        dbc.Card(dbc.CardBody(dcc.Graph(id='grafico-estoque-populares', config={'displayModeBar': False}, style={'height': altura_graficos_padrao}))),
        id='card-clicavel-populares',
        style={'cursor': 'pointer'},
        className="shadow-sm h-100"
    )
    grafico_colunas_resumo_treemap_card = dbc.Card(dbc.CardBody(dcc.Graph(id='grafico-colunas-resumo-estoque', config={'displayModeBar': False})), className="shadow-sm h-100")
    grafico_sec_top_n_card_clicavel = html.Div(dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-top-n-produtos', config={'displayModeBar': True}, style={'height': altura_graficos_padrao}))], className="shadow-sm h-100 clickable-card"), id="card-clicavel-grafico-donut", style={'cursor': 'pointer'})
    grafico_sec_niveis_card_clicavel = html.Div(dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-niveis-estoque', config={'displayModeBar': True}, style={'height': '530px'}))], className="shadow-sm h-100 clickable-card"), id="card-clicavel-grafico-niveis", style={'cursor': 'pointer'})
    tabela_estoque_baixo_card = dbc.Card([dbc.CardBody(html.Div(id='container-tabela-alerta-estoque-baixo-geral'))], className="shadow-sm h-100", style={'height': '400px'})
    grafico_cat_estoque_baixo_card = dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-categorias-estoque-baixo-visao-geral', config={'displayModeBar': False}))], className="shadow-sm h-100", style={'height': '400px'})
    
    # Card do gráfico de produtos sem venda
    grafico_sem_venda_card = html.Div(
        dbc.Card(
            dbc.CardBody(
                dcc.Graph(id='grafico-produtos-sem-venda-grupo', config={'displayModeBar': False})
            ),
            className="shadow-sm"
        ),
        id='card-clicavel-sem-venda',
        style={'cursor': 'pointer'}
    )
    
    tabela_sugestao_compras_card = dbc.Card(
        dbc.CardBody(html.Div(id='tabela-sugestao-compras-container')),
        className="shadow-sm"
    )

    download_component = dcc.Download(id="download-tabela-geral-excel")
    modal_grafico_donut = dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Participação dos Top 7 Produtos no Estoque")), dbc.ModalBody(dcc.Graph(id='grafico-donut-modal', style={'height': '65vh'})), dbc.ModalFooter(dbc.Button("Fechar", id="btn-fechar-modal-donut", className="ms-auto", n_clicks=0, color="warning"))], id="modal-grafico-donut-popup", size="xl", is_open=False, centered=True)
    modal_grafico_niveis = dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Clique na Coluna para ver Detalhes")), dbc.ModalBody([dcc.Graph(id='grafico-niveis-modal', style={'height': '50vh'}), html.Hr(), html.H5("Produtos no Nível Selecionado:", className="mt-3"), html.Div(id='tabela-detalhes-nivel-estoque-modal-container')]), dbc.ModalFooter(dbc.Button("Fechar", id="btn-fechar-modal-niveis", className="ms-auto", n_clicks=0, color="warning"))], id="modal-grafico-niveis-popup", size="xl", is_open=False, centered=True)
    modal_grafico_populares = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Estoque vs. Venda Mensal (Nomes Completos)")),
        dbc.ModalBody(dcc.Graph(id='grafico-populares-modal', style={'height': '70vh'})),
        dbc.ModalFooter(dbc.Button("Fechar", id="btn-fechar-modal-populares", className="ms-auto", n_clicks=0))
    ],
    id="modal-grafico-populares-popup",
    size="xl",
    is_open=False,
    )   

    # Modal para produtos sem venda
    modal_produtos_sem_venda = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Produtos Sem Venda no Grupo Selecionado")),
        dbc.ModalBody([
            html.H5(id="titulo-grupo-sem-venda", className="mb-3"),
            html.Div(id='tabela-produtos-sem-venda-grupo-modal-container')
        ]),
        dbc.ModalFooter(
            dbc.Button("Fechar", id="btn-fechar-modal-sem-venda", className="ms-auto", n_clicks=0, color="warning")
        )
    ], id="modal-produtos-sem-venda-popup", size="xl", is_open=False, centered=True)

    layout_principal = html.Div([
        dbc.Row([
            dbc.Col(grafico_estoque_grupo_card, width=12, lg=7),
            dbc.Col(grafico_sec_niveis_card_clicavel, width=12, lg=5),
        ], className="g-2 mb-2", align="stretch"),

        html.Hr(className="my-2"),
        dbc.Row([
            dbc.Col(grafico_estoque_populares_card, width=12, lg=6),
            dbc.Col(grafico_sec_top_n_card_clicavel, width=12, lg=6),
        ], className="g-2 mb-2", align="stretch"),

        html.Hr(className="my-2"),
        # MUDANÇA: Previsão de estoque no lugar dos cards de resumo
        dbc.Row([
            dbc.Col(previsao_estoque_compacta_card, width=12, lg=3),
            dbc.Col(grafico_colunas_resumo_treemap_card, width=12, lg=9),
        ], className="g-2 mb-2", align="stretch"),

        html.Hr(className="my-2"),
        dbc.Row([
            dbc.Col(grafico_cat_estoque_baixo_card, width=12, lg=8),
            dbc.Col(tabela_estoque_baixo_card, width=12, lg=4)
        ], className="mb-2", align="stretch"),
        html.Hr(className="my-2"),
        
        # Gráfico de produtos sem venda
        dbc.Row([
            dbc.Col(grafico_sem_venda_card, width=12)
        ], className="mb-2"),
        
        dbc.Row([
            dbc.Col(tabela_sugestao_compras_card, width=12)
        ], className="mb-2"),
        download_component,
        modal_grafico_donut,
        modal_grafico_niveis,
        modal_grafico_populares,
        modal_produtos_sem_venda
    ], className="p-2")

    return layout_principal
#----------------------------------------------------------------------
# 3. LAYOUT PRINCIPAL (AGORA SEM ABAS)
#----------------------------------------------------------------------
def criar_layout_principal(df_completo, nome_arquivo, page_size_tabela=20):
    """Cria o layout principal do dashboard de estoque, agora sem abas."""
    
    # --- Definindo o Offcanvas de Filtros ---
    opcoes_categoria, opcoes_grupo = [], []
    if df_completo is not None and not df_completo.empty:
        opcoes_categoria = [{'label': str(cat), 'value': str(cat)} for cat in sorted(df_completo['Categoria'].dropna().unique())]
        opcoes_grupo = [{'label': str(grp), 'value': str(grp)} for grp in sorted(df_completo['Grupo'].dropna().unique())]

    painel_esquerdo_conteudo = html.Div([
        html.H5("Filtros", className="mb-3"),
        html.Div([dbc.Label("Grupo:", className="fw-bold"), dcc.Dropdown(id='dropdown-grupo-filtro', options=opcoes_grupo, value=None, multi=False, placeholder="Todos os Grupos")], className="mb-3"),
        html.Div([dbc.Label("Categoria:", className="fw-bold"), dcc.Dropdown(id='dropdown-categoria-filtro', options=opcoes_categoria, value=None, multi=False, placeholder="Todas as Categorias")], className="mb-3"),
        html.Div([dbc.Label("Nome do Produto:", className="fw-bold"), dcc.Input(id='input-nome-produto-filtro', type='text', placeholder='Buscar por nome...', debounce=True, className="form-control")], className="mb-3"),
        dbc.Button("Resetar Todos os Filtros", id="btn-resetar-filtros", color="warning", outline=True, className="w-100 mb-4"),
    ])

    offcanvas_filtros = dbc.Offcanvas(
        painel_esquerdo_conteudo,
        id="offcanvas-filtros-estoque-geral",
        title="Filtros e Resumo",
        is_open=False,
        placement="start",
        backdrop=False,
        scrollable=True,
        style={'width': '350px'},
    )
    
    # --- Definindo o Modal de Configurações ---
    modal_configuracoes = dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Configurações Gerais")),
            dbc.ModalBody(criar_conteudo_aba_configuracoes(df_completo)),
            dbc.ModalFooter(
                dbc.Button("Fechar", id="btn-fechar-modal-config", className="ms-auto", n_clicks=0, color="secondary")
            ),
        ],
        id="modal-configuracoes",
        size="xl",
        is_open=False,
        centered=True,
    )

    # --- Montando o Layout Final ---
    layout = dbc.Container([
        criar_cabecalho(df_completo),
        criar_conteudo_principal(df_completo, page_size_tabela),
        
        # Componentes "invisíveis" que são controlados por callbacks
        offcanvas_filtros,
        modal_configuracoes
        
    ], fluid=True, className="p-0")
    
    return layout

#----------------------------------------------------------------------
# 4. CALLBACKS (INTERATIVIDADE)
#----------------------------------------------------------------------
def registrar_callbacks_gerais(app, df_global_original):
    app.config.suppress_callback_exceptions = True
    
    @app.callback(
        [
            Output('grafico-colunas-resumo-estoque', 'figure'),
            Output('grafico-estoque-grupo', 'figure'),
            Output('container-tabela-alerta-estoque-baixo-geral', 'children'),
            Output('grafico-top-n-produtos', 'figure'),
            Output('grafico-niveis-estoque', 'figure'),
            Output('grafico-estoque-populares', 'figure'),
            Output('grafico-categorias-estoque-baixo-visao-geral', 'figure'),
            Output('tabela-previsao-estoque-container', 'children'),  # MUDANÇA: usar função compacta
            Output('grafico-produtos-sem-venda-grupo', 'figure'),
            Output('tabela-sugestao-compras-container', 'children'),
        ],
        [
            Input('dropdown-categoria-filtro', 'value'),
            Input('dropdown-grupo-filtro', 'value'),
            Input('input-nome-produto-filtro', 'value'),
            Input('span-config-atual-limite-baixo', 'children'),
            Input('span-config-atual-limite-medio', 'children'),
            Input('span-excluidos-grupos', 'children'),
            Input('span-excluidos-categorias', 'children'),
            Input('span-excluidos-produtos-codigos', 'children')
        ]
    )
    def atualizar_dashboard_filtrado(categoria_selecionada, grupo_selecionado, nome_produto_filtrado,
                                    limite_baixo_str_span, limite_medio_str_span,
                                    ignore_exc_grp, ignore_exc_cat, ignore_exc_prod):

        # ───────────────────────────────
        # 1) Validação de dataframe vazio
        # ───────────────────────────────
        if df_global_original is None or df_global_original.empty:
            fig_vazia = criar_figura_vazia("Sem Dados")
            tabela_vazia = criar_tabela_produtos_criticos(pd.DataFrame(), 'tabela-vazia', "Estoque Baixo")
            # 10 elementos (sem os 4 cards de resumo)
            return (fig_vazia, fig_vazia, tabela_vazia, fig_vazia, fig_vazia,
                    fig_vazia, fig_vazia, fig_vazia, fig_vazia, html.Div())

        # ───────────────────────────────
        # 2) Filtros de exclusão
        # ───────────────────────────────
        config_exclusao = carregar_configuracoes_exclusao()
        dff = df_global_original.copy()
        grupos_a_excluir = config_exclusao.get("excluir_grupos", [])
        categorias_a_excluir = config_exclusao.get("excluir_categorias", [])
        produtos_codigos_excluir = [str(p) for p in config_exclusao.get("excluir_produtos_codigos", [])]

        if grupos_a_excluir:
            dff = dff[~dff['Grupo'].isin(grupos_a_excluir)]
        if categorias_a_excluir:
            dff = dff[~dff['Categoria'].isin(categorias_a_excluir)]
        if produtos_codigos_excluir:
            dff = dff[~dff['Código'].astype(str).isin(produtos_codigos_excluir)]

        # ───────────────────────────────
        # 3) Filtros interativos (categoria / grupo / produto)
        # ───────────────────────────────
        dff_filtrado = dff.copy()
        if categoria_selecionada:
            dff_filtrado = dff_filtrado[dff_filtrado['Categoria'] == categoria_selecionada]
        if grupo_selecionado:
            dff_filtrado = dff_filtrado[dff_filtrado['Grupo'] == grupo_selecionado]
        if nome_produto_filtrado and nome_produto_filtrado.strip():
            dff_filtrado = dff_filtrado[dff_filtrado['Produto'].str.contains(nome_produto_filtrado,
                                                                            case=False, na=False)]

        # ───────────────────────────────
        # 4) Validação pós‑filtro
        # ───────────────────────────────
        if dff_filtrado.empty:
            fig_vazia = criar_figura_vazia("Sem dados com os filtros atuais")
            tabela_vazia = criar_tabela_produtos_criticos(pd.DataFrame(), 'tabela-vazia-filtros', "Estoque Baixo")
            return (fig_vazia, fig_vazia, tabela_vazia, fig_vazia, fig_vazia,
                    fig_vazia, fig_vazia, fig_vazia, fig_vazia, html.Div())

        # ───────────────────────────────
        # 5) Cálculos & Gráficos principais
        # ───────────────────────────────
        fig_colunas_resumo = criar_grafico_colunas_estoque_por_grupo(dff_filtrado)
        fig_estoque_grupo = criar_grafico_estoque_por_grupo(dff_filtrado)
        fig_top_n = criar_grafico_top_n_produtos_estoque(dff_filtrado, n=7)

        config_niveis = carregar_definicoes_niveis_estoque()
        limite_baixo = config_niveis.get("limite_estoque_baixo", 10)
        limite_medio = config_niveis.get("limite_estoque_medio", 100)

        fig_niveis = criar_grafico_niveis_estoque(dff_filtrado, limite_baixo, limite_medio)
        fig_populares = criar_grafico_estoque_produtos_populares(dff_filtrado, n=7, abreviar_nomes=True)

        df_estoque_baixo = identificar_produtos_estoque_baixo(dff_filtrado, limite_baixo)
        tabela_estoque_baixo = criar_tabela_produtos_criticos(
            df_estoque_baixo,
            id_tabela='tabela-alerta-estoque-baixo-geral-cb',
            titulo_alerta=f"Alerta: Estoque Baixo (≤ {limite_baixo:g})",
            altura_tabela='400px')

        fig_categorias_baixo = criar_grafico_categorias_com_estoque_baixo(df_estoque_baixo)
        
        # MUDANÇA: Usar a função compacta correta
        tabela_previsao = criar_tabela_previsao_estoque_compacta(dff_filtrado)

        fig_sem_venda_grupo = criar_grafico_produtos_sem_venda_por_grupo(dff_filtrado)

        # MUDANÇA: Usar as funções corrigidas da sugestão de compras
        df_sugestao = gerar_sugestao_compras(dff_filtrado, limite_baixo, limite_medio)
        tabela_sugestao = criar_tabela_sugestao_compras(df_sugestao)

        # ───────────────────────────────
        # 6) Retorno (10 elementos)
        # ───────────────────────────────
        return (
            fig_colunas_resumo,
            fig_estoque_grupo,
            tabela_estoque_baixo,
            fig_top_n,
            fig_niveis,
            fig_populares,
            fig_categorias_baixo,
            tabela_previsao,        # MUDANÇA: função compacta
            fig_sem_venda_grupo,
            tabela_sugestao         # MUDANÇA: função corrigida
        )


    # --- Callbacks de filtros e modais ---
    @app.callback(
        [Output('dropdown-grupo-filtro', 'value', allow_duplicate=True),
         Output('dropdown-categoria-filtro', 'value', allow_duplicate=True),
         Output('input-nome-produto-filtro', 'value', allow_duplicate=True)],
        Input('btn-resetar-filtros', 'n_clicks'),
        prevent_initial_call=True
    )
    def resetar_todos_filtros(n_clicks):
        if n_clicks and n_clicks > 0:
            return None, None, ''
        return no_update, no_update, no_update
    
    @app.callback(
        Output("offcanvas-filtros-estoque-geral", "is_open"),
        Input("btn-toggle-painel-esquerdo", "n_clicks"),
        State("offcanvas-filtros-estoque-geral", "is_open"),
        prevent_initial_call=True
    )
    def toggle_filtros_offcanvas(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("modal-configuracoes", "is_open"),
        [Input("btn-abrir-modal-config", "n_clicks"), 
         Input("btn-fechar-modal-config", "n_clicks")],
        [State("modal-configuracoes", "is_open")],
        prevent_initial_call=True
    )
    def toggle_modal_configuracoes(n_abrir, n_fechar, is_open):
        if n_abrir or n_fechar:
            return not is_open
        return is_open

    # --- Callbacks de Configurações (salvando e atualizando) ---
    @app.callback(
        [Output('div-status-config-niveis', 'children'),
         Output('span-config-atual-limite-baixo', 'children'),
         Output('span-config-atual-limite-medio', 'children'),
         Output('input-limite-config-baixo', 'value'),
         Output('input-limite-config-medio', 'value')],
        Input('btn-salvar-config-niveis', 'n_clicks'),
        [State('input-limite-config-baixo', 'value'), State('input-limite-config-medio', 'value')],
        prevent_initial_call=True
    )
    def salvar_configuracoes_niveis(n_clicks, limite_baixo_input, limite_medio_input):
        if n_clicks is None or limite_baixo_input is None or limite_medio_input is None: return no_update, no_update, no_update, no_update, no_update
        sucesso, msg_retorno = salvar_definicoes_niveis_estoque(limite_baixo_input, limite_medio_input)
        cor_alerta = "success" if sucesso else "danger"
        status_msg = dbc.Alert(msg_retorno, color=cor_alerta, dismissable=True, duration=7000)
        config_recarregada = carregar_definicoes_niveis_estoque()
        val_baixo, val_medio = config_recarregada.get("limite_estoque_baixo"), config_recarregada.get("limite_estoque_medio")
        return status_msg, str(val_baixo), str(val_medio), val_baixo, val_medio

    @app.callback(
        [Output('div-status-salvar-exclusoes', 'children'),
         Output('span-excluidos-grupos', 'children'),
         Output('span-excluidos-categorias', 'children'),
         Output('span-excluidos-produtos-codigos', 'children'),
         Output('dropdown-excluir-grupos', 'value'),
         Output('dropdown-excluir-categorias', 'value'),
         Output('dropdown-excluir-produtos-codigos', 'value')],
        Input('btn-salvar-exclusoes', 'n_clicks'),
        [State('dropdown-excluir-grupos', 'value'), State('dropdown-excluir-categorias', 'value'), State('dropdown-excluir-produtos-codigos', 'value')],
        prevent_initial_call=True
    )
    def salvar_config_exclusoes(n_clicks, grupos_sel, categorias_sel, produtos_cod_sel):
        if n_clicks is None: return no_update, no_update, no_update, no_update, no_update, no_update, no_update
        sucesso, msg_retorno = salvar_configuracoes_exclusao(grupos_sel, categorias_sel, produtos_cod_sel)
        cor_alerta = "success" if sucesso else "danger"
        status_msg = dbc.Alert(msg_retorno, color=cor_alerta, dismissable=True, duration=7000)
        config_exc_rec = carregar_configuracoes_exclusao()
        grupos, cats, prods = config_exc_rec.get("excluir_grupos", []), config_exc_rec.get("excluir_categorias", []), config_exc_rec.get("excluir_produtos_codigos", [])
        return (status_msg, ", ".join(grupos) if grupos else "Nenhum", ", ".join(cats) if cats else "Nenhuma", ", ".join(map(str, prods)) if prods else "Nenhum", grupos, cats, prods)
    
    # --- Callbacks de Modais de Gráficos (Donut e Níveis) ---
    @app.callback(
        [Output("modal-grafico-donut-popup", "is_open"),
         Output("grafico-donut-modal", "figure")],
        [Input("card-clicavel-grafico-donut", "n_clicks"), Input("btn-fechar-modal-donut", "n_clicks")],
        [State("modal-grafico-donut-popup", "is_open"), State('dropdown-categoria-filtro', 'value'), State('dropdown-grupo-filtro', 'value'), State('input-nome-produto-filtro', 'value')],
        prevent_initial_call=True
    )
    def toggle_modal_grafico_donut(n_abrir, n_fechar, is_open, cat_sel, grp_sel, prod_sel):
        ctx = dash.callback_context
        triggered_id = ctx.triggered_id if ctx.triggered_id else None
        figura, abrir_modal = no_update, is_open
        if triggered_id == "card-clicavel-grafico-donut":
            abrir_modal = not is_open
            if abrir_modal and df_global_original is not None and not df_global_original.empty:
                dff = df_global_original.copy()
                config_exc = carregar_configuracoes_exclusao()
                if config_exc["excluir_grupos"]: dff = dff[~dff['Grupo'].isin(config_exc["excluir_grupos"])]
                if config_exc["excluir_categorias"]: dff = dff[~dff['Categoria'].isin(config_exc["excluir_categorias"])]
                if config_exc["excluir_produtos_codigos"]: dff = dff[~dff['Código'].astype(str).isin([str(p) for p in config_exc["excluir_produtos_codigos"]])]
                if cat_sel: dff = dff[dff['Categoria'] == cat_sel]
                if grp_sel: dff = dff[dff['Grupo'] == grp_sel]
                if prod_sel and prod_sel.strip() != "": dff = dff[dff['Produto'].str.contains(prod_sel, case=False, na=False)]
                figura = criar_grafico_top_n_produtos_estoque(dff, n=7, height=600)
        elif triggered_id == "btn-fechar-modal-donut":
            abrir_modal = False
        return abrir_modal, figura
    
    @app.callback(
        [Output("modal-grafico-niveis-popup", "is_open"),
         Output("grafico-niveis-modal", "figure")],
        [Input("card-clicavel-grafico-niveis", "n_clicks"), Input("btn-fechar-modal-niveis", "n_clicks")],
        [State("modal-grafico-niveis-popup", "is_open"), State('dropdown-categoria-filtro', 'value'), State('dropdown-grupo-filtro', 'value'), State('input-nome-produto-filtro', 'value'), State('span-config-atual-limite-baixo', 'children'), State('span-config-atual-limite-medio', 'children')],
        prevent_initial_call=True
    )
    def toggle_modal_grafico_niveis(n_abrir, n_fechar, is_open, cat_sel, grp_sel, prod_sel, lim_b, lim_m):
        ctx = dash.callback_context
        triggered_id = ctx.triggered_id if ctx.triggered_id else None
        figura, abrir_modal = no_update, is_open
        if triggered_id == "card-clicavel-grafico-niveis":
            abrir_modal = not is_open
            if abrir_modal and df_global_original is not None and not df_global_original.empty:
                dff_modal = df_global_original.copy()
                config_exc = carregar_configuracoes_exclusao()
                if config_exc["excluir_grupos"]: dff_modal = dff_modal[~dff_modal['Grupo'].isin(config_exc["excluir_grupos"])]
                if config_exc["excluir_categorias"]: dff_modal = dff_modal[~dff_modal['Categoria'].isin(config_exc["excluir_categorias"])]
                if config_exc["excluir_produtos_codigos"]: dff_modal = dff_modal[~dff_modal['Código'].astype(str).isin([str(p) for p in config_exc["excluir_produtos_codigos"]])]
                if cat_sel: dff_modal = dff_modal[dff_modal['Categoria'] == cat_sel]
                if grp_sel: dff_modal = dff_modal[dff_modal['Grupo'] == grp_sel]
                if prod_sel and prod_sel.strip() != "": dff_modal = dff_modal[dff_modal['Produto'].str.contains(prod_sel, case=False, na=False)]
                config_niveis = carregar_definicoes_niveis_estoque()
                lim_b_val = float(lim_b) if lim_b and str(lim_b).replace('.', '', 1).isdigit() else config_niveis.get("limite_estoque_baixo", 10)
                lim_m_val = float(lim_m) if lim_m and str(lim_m).replace('.', '', 1).isdigit() else config_niveis.get("limite_estoque_medio", 100)
                figura = criar_grafico_niveis_estoque(dff_modal, lim_b_val, lim_m_val, height=600)
        elif triggered_id == "btn-fechar-modal-niveis":
            abrir_modal = False
        return abrir_modal, figura
    
    @app.callback(
        Output('tabela-detalhes-nivel-estoque-modal-container', 'children'),
        Input('grafico-niveis-modal', 'clickData'),
        [State("modal-grafico-niveis-popup", "is_open"), State('dropdown-categoria-filtro', 'value'), State('dropdown-grupo-filtro', 'value'), State('input-nome-produto-filtro', 'value'), State('span-config-atual-limite-baixo', 'children'), State('span-config-atual-limite-medio', 'children')],
        prevent_initial_call=True
    )
    def atualizar_tabela_detalhes_nivel(click_data, is_open, cat_sel, grp_sel, prod_sel, lim_b, lim_m):
        if not is_open or not click_data: return ""
        try:
            nivel_clicado = click_data['points'][0]['x'].split()[0].lower()
            config_niveis = carregar_definicoes_niveis_estoque()
            lim_b_val = float(lim_b) if lim_b and str(lim_b).replace('.', '', 1).isdigit() else config_niveis.get("limite_estoque_baixo", 10)
            lim_m_val = float(lim_m) if lim_m and str(lim_m).replace('.', '', 1).isdigit() else config_niveis.get("limite_estoque_medio", 100)
            dff = df_global_original.copy()
            config_exc = carregar_configuracoes_exclusao()
            if config_exc["excluir_grupos"]: dff = dff[~dff['Grupo'].isin(config_exc["excluir_grupos"])]
            if config_exc["excluir_categorias"]: dff = dff[~dff['Categoria'].isin(config_exc["excluir_categorias"])]
            if config_exc["excluir_produtos_codigos"]: dff = dff[~dff['Código'].astype(str).isin([str(p) for p in config_exc["excluir_produtos_codigos"]])]
            if cat_sel: dff = dff[dff['Categoria'] == cat_sel]
            if grp_sel: dff = dff[dff['Grupo'] == grp_sel]
            if prod_sel and prod_sel.strip() != "": dff = dff[dff['Produto'].str.contains(prod_sel, case=False, na=False)]
            dff['Estoque'] = pd.to_numeric(dff['Estoque'], errors='coerce').dropna()
            
            df_nivel_selecionado = pd.DataFrame()
            if nivel_clicado == "baixo": df_nivel_selecionado = dff[dff['Estoque'] <= lim_b_val]
            elif nivel_clicado in ["médio", "medio"]: df_nivel_selecionado = dff[(dff['Estoque'] > lim_b_val) & (dff['Estoque'] <= lim_m_val)]
            elif nivel_clicado == "alto": df_nivel_selecionado = dff[dff['Estoque'] > lim_m_val]
            else: return dbc.Alert("Nível não reconhecido.", color="warning")

            if df_nivel_selecionado.empty: return dbc.Alert("Nenhum produto encontrado para este nível com os filtros atuais.", color="info")
            # Reutilizando a função de tabela de estoque baixo para exibir os dados
            return criar_tabela_produtos_criticos(df_nivel_selecionado[['Produto', 'Estoque']], id_tabela='tabela-modal-detalhes', titulo_alerta=f"Produtos no Nível {nivel_clicado.capitalize()}", altura_tabela='400px')
        except (KeyError, IndexError, AttributeError):
            return ""

    @app.callback(
        [Output("modal-grafico-populares-popup", "is_open"),
         Output("grafico-populares-modal", "figure")],
        [Input("card-clicavel-populares", "n_clicks"), 
         Input("btn-fechar-modal-populares", "n_clicks")],
        [State("modal-grafico-populares-popup", "is_open"),
         State('dropdown-categoria-filtro', 'value'),
         State('dropdown-grupo-filtro', 'value'),
         State('input-nome-produto-filtro', 'value')],
        prevent_initial_call=True
    )
    def toggle_modal_grafico_populares(n_abrir, n_fechar, is_open, cat_sel, grp_sel, prod_sel):
        ctx = dash.callback_context
        triggered_id = ctx.triggered_id if ctx.triggered_id else None
        
        abrir_modal = is_open
        figura = no_update

        if triggered_id == "card-clicavel-populares":
            abrir_modal = not is_open
            if abrir_modal and df_global_original is not None:
                dff = df_global_original.copy()
                if cat_sel: dff = dff[dff['Categoria'] == cat_sel]
                if grp_sel: dff = dff[dff['Grupo'] == grp_sel]
                if prod_sel and prod_sel.strip() != "": dff = dff[dff['Produto'].str.contains(prod_sel, case=False, na=False)]
                
                figura = criar_grafico_estoque_produtos_populares(dff, n=7, abreviar_nomes=False)

        elif triggered_id == "btn-fechar-modal-populares":
            abrir_modal = False

        return abrir_modal, figura
    
    @app.callback(
    [Output("modal-produtos-sem-venda-popup", "is_open"),
     Output("titulo-grupo-sem-venda", "children"),
     Output("tabela-produtos-sem-venda-grupo-modal-container", "children")],
    [Input("card-clicavel-sem-venda", "n_clicks"),
     Input("btn-fechar-modal-sem-venda", "n_clicks"),
     Input("grafico-produtos-sem-venda-grupo", "clickData")],
    [State("modal-produtos-sem-venda-popup", "is_open"),
     State('dropdown-categoria-filtro', 'value'),
     State('dropdown-grupo-filtro', 'value'),
     State('input-nome-produto-filtro', 'value')],
    prevent_initial_call=True
    )
    def toggle_modal_produtos_sem_venda(n_cliques_card, n_fechar, click_data, is_open, cat_sel, grp_sel, prod_sel):
        ctx = dash.callback_context
        triggered_id = ctx.triggered_id if ctx.triggered_id else None
        
        abrir_modal = is_open
        titulo = ""
        conteudo_tabela = html.Div()
        
        if triggered_id == "btn-fechar-modal-sem-venda":
            abrir_modal = False
        elif triggered_id == "card-clicavel-sem-venda" or (triggered_id == "grafico-produtos-sem-venda-grupo" and click_data):
            abrir_modal = not is_open if triggered_id == "card-clicavel-sem-venda" else True
            
            if abrir_modal and df_global_original is not None:
                # Aplicar filtros
                dff = df_global_original.copy()
                config_exc = carregar_configuracoes_exclusao()
                if config_exc["excluir_grupos"]: 
                    dff = dff[~dff['Grupo'].isin(config_exc["excluir_grupos"])]
                if config_exc["excluir_categorias"]: 
                    dff = dff[~dff['Categoria'].isin(config_exc["excluir_categorias"])]
                if config_exc["excluir_produtos_codigos"]: 
                    dff = dff[~dff['Código'].astype(str).isin([str(p) for p in config_exc["excluir_produtos_codigos"]])]
                if cat_sel: 
                    dff = dff[dff['Categoria'] == cat_sel]
                if grp_sel: 
                    dff = dff[dff['Grupo'] == grp_sel]
                if prod_sel and prod_sel.strip(): 
                    dff = dff[dff['Produto'].str.contains(prod_sel, case=False, na=False)]
                
                # Determinar o grupo clicado
                grupo_selecionado = None
                if click_data and 'points' in click_data:
                    try:
                        # Extrair nome do grupo do click data
                        grupo_clicado = click_data['points'][0]['label']
                        # Encontrar o grupo completo correspondente
                        grupos_disponiveis = dff['Grupo'].unique()
                        for grupo in grupos_disponiveis:
                            if grupo_clicado in grupo.replace(r'^\d+\s*', '', 1):
                                grupo_selecionado = grupo
                                break
                    except:
                        pass
                
                # Filtrar produtos sem venda
                dff['VendaMensal'] = pd.to_numeric(dff['VendaMensal'], errors='coerce').fillna(0)
                dff['Estoque'] = pd.to_numeric(dff['Estoque'], errors='coerce').fillna(0)
                df_sem_venda = dff[(dff['VendaMensal'] == 0) & (dff['Estoque'] > 0)]
                
                if grupo_selecionado:
                    df_sem_venda = df_sem_venda[df_sem_venda['Grupo'] == grupo_selecionado]
                    titulo = f"Produtos sem venda no grupo: {grupo_selecionado}"
                else:
                    titulo = "Todos os produtos sem venda"
                
                if not df_sem_venda.empty:
                    # Ordenar por estoque decrescente
                    df_sem_venda = df_sem_venda.sort_values('Estoque', ascending=False)
                    conteudo_tabela = criar_tabela_produtos_criticos(
                        df_sem_venda[['Produto', 'Estoque']],
                        id_tabela='tabela-produtos-sem-venda-modal',
                        titulo_alerta=f"Total: {len(df_sem_venda)} produtos",
                        altura_tabela='400px'
                    )
                else:
                    conteudo_tabela = dbc.Alert("Nenhum produto sem venda encontrado para este grupo.", color="info")
        
        return abrir_modal, titulo, conteudo_tabela


    def criar_tabela_previsao_estoque_compacta(df, dias_maximos=60):
        """Cria uma versão compacta da tabela de previsão de estoque com SCROLL (sem paginação)."""
        
        if df is None or df.empty or 'DiasEstoque' not in df.columns or 'Produto' not in df.columns or 'Estoque' not in df.columns:
            return dbc.Alert("Dados incompletos para previsão", color="warning", className="text-center")
        
        df_plot = df.copy()
        df_plot['DiasEstoque'] = pd.to_numeric(df_plot['DiasEstoque'], errors='coerce')
        df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce')
        
        # Filtrar produtos com previsão válida (0 < dias <= 60) e estoque > 0
        df_filtrado = df_plot[
            (df_plot['DiasEstoque'] > 0) & 
            (df_plot['DiasEstoque'] <= dias_maximos) &
            (df_plot['Estoque'] > 0) &
            (df_plot['DiasEstoque'].notna())
        ]
        
        if df_filtrado.empty:
            return dbc.Alert(f"Nenhum produto crítico (≤{dias_maximos} dias)", color="info", className="text-center")
        
        # Ordenar por dias de estoque (crescente) - MOSTRAR TODOS (sem limit)
        df_filtrado = df_filtrado.sort_values('DiasEstoque', ascending=True)
        
        # Formatar colunas
        df_filtrado['DiasEstoque'] = df_filtrado['DiasEstoque'].round(1)
        df_filtrado['Estoque'] = df_filtrado['Estoque'].round(0)
        
        # Criar tabela mais compacta
        colunas = [
            {"name": "Produto", "id": "Produto"},
            {"name": "Dias", "id": "DiasEstoque", "type": "numeric"},
            {"name": "Qtd", "id": "Estoque", "type": "numeric"}
        ]
        
        estilo_compacto = {
            'style_header': {
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'fontSize': '12px',
                'padding': '4px',
                'position': 'sticky',
                'top': 0,
                'zIndex': 1
            },
            'style_cell': {
                'textAlign': 'left',
                'padding': '4px',
                'fontSize': '11px',
                'border': '1px solid #f0f0f0',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0
            },
            'style_data_conditional': [
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgba(0,0,0,0.025)'
                },
                {
                    'if': {'column_id': 'DiasEstoque', 'filter_query': '{DiasEstoque} <= 7'},
                    'backgroundColor': 'rgba(220, 53, 69, 0.2)',
                    'fontWeight': 'bold'
                },
                {
                    'if': {'column_id': 'DiasEstoque', 'filter_query': '{DiasEstoque} > 7 && {DiasEstoque} <= 30'},
                    'backgroundColor': 'rgba(255, 193, 7, 0.2)'
                }
            ]
        }
        
        return dash_table.DataTable(
            id='tabela-previsao-compacta',
            columns=colunas,
            data=df_filtrado.to_dict('records'),
            # MUDANÇA: Removido page_size para mostrar todos com scroll
            style_table={
                'height': '400px',  # Altura fixa
                'overflowY': 'auto',  # Scroll vertical
                'overflowX': 'auto',  # Scroll horizontal se necessário
                'border': '1px solid #dee2e6',
                'borderRadius': '0.25rem'
            },
            **estilo_compacto
        )

        """Cria uma versão compacta da tabela de previsão de estoque."""
        
        if df is None or df.empty or 'DiasEstoque' not in df.columns or 'Produto' not in df.columns or 'Estoque' not in df.columns:
            return dbc.Alert("Dados incompletos para previsão", color="warning", className="text-center")
        
        df_plot = df.copy()
        df_plot['DiasEstoque'] = pd.to_numeric(df_plot['DiasEstoque'], errors='coerce')
        df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce')
        
        # Filtrar produtos com previsão válida (0 < dias <= 60) e estoque > 0
        df_filtrado = df_plot[
            (df_plot['DiasEstoque'] > 0) & 
            (df_plot['DiasEstoque'] <= dias_maximos) &
            (df_plot['Estoque'] > 0) &
            (df_plot['DiasEstoque'].notna())
        ]
        
        if df_filtrado.empty:
            return dbc.Alert(f"Nenhum produto crítico (≤{dias_maximos} dias)", color="info", className="text-center")
        
        # Ordenar por dias de estoque (crescente) e pegar apenas o top 10
        df_filtrado = df_filtrado.sort_values('DiasEstoque', ascending=True).head(10)
        
        # Formatar colunas
        df_filtrado['DiasEstoque'] = df_filtrado['DiasEstoque'].round(1)
        df_filtrado['Estoque'] = df_filtrado['Estoque'].round(0)
        
        # Criar tabela mais compacta
        colunas = [
            {"name": "Produto", "id": "Produto"},
            {"name": "Dias", "id": "DiasEstoque", "type": "numeric"},
            {"name": "Qtd", "id": "Estoque", "type": "numeric"}
        ]
        
        estilo_compacto = {
            'style_header': {
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'fontSize': '12px',
                'padding': '4px'
            },
            'style_cell': {
                'textAlign': 'left',
                'padding': '4px',
                'fontSize': '11px',
                'border': '1px solid #f0f0f0'
            },
            'style_data_conditional': [
                {
                    'if': {'column_id': 'DiasEstoque', 'filter_query': '{DiasEstoque} <= 7'},
                    'backgroundColor': 'rgba(220, 53, 69, 0.2)',
                    'fontWeight': 'bold'
                },
                {
                    'if': {'column_id': 'DiasEstoque', 'filter_query': '{DiasEstoque} > 7 && {DiasEstoque} <= 30'},
                    'backgroundColor': 'rgba(255, 193, 7, 0.2)'
                }
            ]
        }
        
        return dash_table.DataTable(
            id='tabela-previsao-compacta',
            columns=colunas,
            data=df_filtrado.to_dict('records'),
            page_size=8,  # Menor para caber no espaço
            style_table={'height': '300px', 'overflowY': 'auto'},
            **estilo_compacto
        )

    # CALLBACK PARA ATUALIZAR O HEADER COM DADOS FILTRADOS
    @app.callback(
        [Output('header-total-skus', 'children'),
        Output('header-estoque-total', 'children'),
        Output('header-categorias', 'children'),
        Output('header-grupos', 'children')],
        [Input('dropdown-categoria-filtro', 'value'),
        Input('dropdown-grupo-filtro', 'value'),
        Input('input-nome-produto-filtro', 'value'),
        Input('span-excluidos-grupos', 'children'),
        Input('span-excluidos-categorias', 'children'),
        Input('span-excluidos-produtos-codigos', 'children')]
    )
    def atualizar_header_metricas(categoria_selecionada, grupo_selecionado, nome_produto_filtrado,
                                ignore_exc_grp, ignore_exc_cat, ignore_exc_prod):
        
        if df_global_original is None or df_global_original.empty:
            return "0", "0", "0", "0"
        
        # Aplicar filtros de exclusão
        config_exclusao = carregar_configuracoes_exclusao()
        dff = df_global_original.copy()
        grupos_a_excluir = config_exclusao.get("excluir_grupos", [])
        categorias_a_excluir = config_exclusao.get("excluir_categorias", [])
        produtos_codigos_excluir = [str(p) for p in config_exclusao.get("excluir_produtos_codigos", [])]

        if grupos_a_excluir:
            dff = dff[~dff['Grupo'].isin(grupos_a_excluir)]
        if categorias_a_excluir:
            dff = dff[~dff['Categoria'].isin(categorias_a_excluir)]
        if produtos_codigos_excluir:
            dff = dff[~dff['Código'].astype(str).isin(produtos_codigos_excluir)]

        # Aplicar filtros interativos
        dff_filtrado = dff.copy()
        if categoria_selecionada:
            dff_filtrado = dff_filtrado[dff_filtrado['Categoria'] == categoria_selecionada]
        if grupo_selecionado:
            dff_filtrado = dff_filtrado[dff_filtrado['Grupo'] == grupo_selecionado]
        if nome_produto_filtrado and nome_produto_filtrado.strip():
            dff_filtrado = dff_filtrado[dff_filtrado['Produto'].str.contains(nome_produto_filtrado,
                                                                            case=False, na=False)]
        
        if dff_filtrado.empty:
            return "0", "0", "0", "0"
        
        # Calcular métricas filtradas
        total_skus = dff_filtrado['Código'].nunique()
        qtd_total_estoque = pd.to_numeric(dff_filtrado['Estoque'], errors='coerce').fillna(0).sum()
        num_categorias = dff_filtrado['Categoria'].nunique()
        num_grupos = dff_filtrado['Grupo'].nunique()
        
        return (f"{total_skus:,}", 
                f"{int(qtd_total_estoque):,}", 
                f"{num_categorias:,}", 
                f"{num_grupos:,}")
#----------------------------------------------------------------------
# 5. INICIALIZAÇÃO DA PÁGINA
#----------------------------------------------------------------------
def get_layout(app):
    """Retorna o layout principal da página de estoque."""
    if CONFIG_ESTOQUE['df_global'] is None:
        CONFIG_ESTOQUE['df_global'] = carregar_produtos_com_hierarquia(CONFIG_ESTOQUE['caminho_arquivo_csv'])
    
    return criar_layout_principal(
        df_completo=CONFIG_ESTOQUE['df_global'],
        nome_arquivo=CONFIG_ESTOQUE['caminho_arquivo_csv'],
        page_size_tabela=20
    )

def register_callbacks(app):
    """Registra todos os callbacks da página de estoque."""
    if CONFIG_ESTOQUE['df_global'] is None:
        CONFIG_ESTOQUE['df_global'] = carregar_produtos_com_hierarquia(CONFIG_ESTOQUE['caminho_arquivo_csv'])
    
    registrar_callbacks_gerais(app, CONFIG_ESTOQUE['df_global'])