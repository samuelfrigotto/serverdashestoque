
import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc, no_update, callback_context
from app import app, session_dataframes_cta_express as sessionDF
from dash import dash_table
from utils import conversores
from .estoque_data import aplicar_filtros_exclusao_header
from .estoque_graficos import criar_figura_vazia

# Importar módulos do estoque
from .estoque_data import (
    carregar_dados_estoque, 
    carregar_definicoes_niveis_estoque,
    salvar_definicoes_niveis_estoque,
    carregar_configuracoes_exclusao,
    salvar_configuracoes_exclusao,
    aplicar_filtros_exclusao,
    aplicar_filtros_interativos,
    EstoqueColumns
)
from .estoque_analise import (
    identificar_produtos_estoque_baixo,
    gerar_sugestao_compras,
    calcular_metricas_header,
    preparar_opcoes_filtros,
    obter_produtos_previsao_estoque
)

from .estoque_graficos import (
    criar_grafico_estoque_por_grupo,
    criar_grafico_top_produtos_estoque,
    criar_grafico_niveis_estoque,
    criar_grafico_categorias_estoque_baixo,
    criar_grafico_estoque_produtos_populares,
    criar_grafico_treemap_estoque_grupo,
    criar_grafico_produtos_sem_venda_grupo,
    criar_figura_vazia
)
from .estoque_componentes import (
    criar_cabecalho_estoque,
    criar_offcanvas_filtros,
    criar_modal_configuracoes,
    criar_tabela_produtos_criticos,
    criar_tabela_sugestao_compras,
    criar_tabela_previsao_estoque_compacta
)

# Configurações seguindo padrão do projeto
pageTag = "CEestoque_"

def get_layout(app):
    """Retorna layout principal do estoque seguindo padrão do projeto."""
    # Carregar dados na inicialização
    df_estoque = carregar_dados_estoque()
    
    if df_estoque.empty:
        return html.Div([
            dbc.Alert("Erro ao carregar dados de estoque. Verifique o arquivo de dados.", color="danger")
        ])
    
    # Armazenar dados na sessão seguindo padrão do projeto
    session_id = "estoque_default"  # Usar ID padrão para estoque
    sessionDF[f"{session_id}_estoque"] = df_estoque
    
    # Criar layout principal
    layout_principal = dbc.Container([
        # Store para controle de dados
        dcc.Store(id=f"{pageTag}update", data=1),
        dcc.Store(id=f"{pageTag}session_data", data={"session_id": session_id}),
        
        # Header
        html.Div(id=f"{pageTag}header"),
        
        # Conteúdo principal
        html.Div(id=f"{pageTag}body"),
        
        # Componentes "invisíveis"
        criar_offcanvas_filtros(df_estoque),
        criar_modal_configuracoes(df_estoque)
        
    ], fluid=True, className="p-0")
    
    return layout_principal

def criar_conteudo_principal(df_completo):
    """Cria conteúdo principal seguindo padrão do projeto."""
    if df_completo is None or df_completo.empty:
        return dbc.Alert("Dados de estoque não carregados.", color="danger")

    # Cards de gráficos seguindo padrão do projeto com alturas padronizadas
    altura_graficos_padrao = '410px'
    altura_graficos_grandes = '520px'
    
    grafico_estoque_grupo_card = dbc.Card(
        dbc.CardBody([
            dcc.Graph(
                id=f'{pageTag}grafico-estoque-grupo', 
                config={'displayModeBar': False}, 
                style={'height': altura_graficos_grandes}
            ),
            dbc.Button(
                "Ver detalhes",
                color="primary",
                size="sm",
                id=f"btn-{pageTag}-det-fig1",
                class_name="botao-detalhes rounded",
                style={
                    'position': 'absolute', 
                    'bottom': '10px', 
                    'right': '10px',
                    'z-index': '10',
                    'opacity': '0.8'
                }
            ),
        ], className="position-relative"), 
        className="shadow-sm h-100 card-com-hover"
    )
    
    grafico_estoque_populares_card = html.Div(
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    id=f'{pageTag}grafico-estoque-populares', 
                    config={'displayModeBar': False}, 
                    style={'height': altura_graficos_padrao}
                ),
                dbc.Button(
                    "Ver detalhes",
                    color="primary",
                    size="sm",
                    id=f"btn-{pageTag}-det-fig2",
                    class_name="botao-detalhes rounded",
                    style={
                        'position': 'absolute', 
                        'bottom': '10px', 
                        'right': '10px',
                        'z-index': '10',
                        'opacity': '0.8'
                    }
                ),
            ], className="position-relative")
        ),
        id=f'{pageTag}card-clicavel-populares',
        style={'cursor': 'pointer'},
        className="shadow-sm h-100 card-com-hover"
    )
    
    grafico_treemap_card = dbc.Card(
        dbc.CardBody([
            dcc.Graph(
                id=f'{pageTag}grafico-treemap-estoque', 
                config={'displayModeBar': False},
                style={'height': '430px'}
            ),
            dbc.Button(
                "Ver detalhes",
                color="primary",
                size="sm",
                id=f"btn-{pageTag}-det-fig3",
                class_name="botao-detalhes rounded",
                style={
                    'position': 'absolute', 
                    'bottom': '10px', 
                    'right': '10px',
                    'z-index': '10',
                    'opacity': '0.8'
                }
            ),
        ], className="position-relative"), 
        className="shadow-sm h-100 card-com-hover"
    )
    
    grafico_top_produtos_card = html.Div(
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(
                    id=f'{pageTag}grafico-top-produtos', 
                    config={'displayModeBar': True}, 
                    style={'height': altura_graficos_padrao}
                ),
                dbc.Button(
                    "Ver detalhes",
                    color="primary",
                    size="sm",
                    id=f"btn-{pageTag}-det-fig4",
                    class_name="botao-detalhes rounded",
                    style={
                        'position': 'absolute', 
                        'bottom': '10px', 
                        'right': '10px',
                        'z-index': '10',
                        'opacity': '0.8'
                    }
                ),
            ], className="position-relative")
        ], className="shadow-sm h-100 clickable-card card-com-hover"), 
        id=f"{pageTag}card-clicavel-grafico-donut", 
        style={'cursor': 'pointer'}
    )
    
    grafico_niveis_card = html.Div(
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(
                    id=f'{pageTag}grafico-niveis-estoque', 
                    config={'displayModeBar': True}, 
                    style={'height': altura_graficos_grandes}
                ),
                dbc.Button(
                    "Ver detalhes",
                    color="primary",
                    size="sm",
                    id=f"btn-{pageTag}-det-fig5",
                    class_name="botao-detalhes rounded",
                    style={
                        'position': 'absolute', 
                        'bottom': '10px', 
                        'right': '10px',
                        'z-index': '10',
                        'opacity': '0.8'
                    }
                ),
            ], className="position-relative")
        ], className="shadow-sm h-100 clickable-card card-com-hover"), 
        id=f"{pageTag}card-clicavel-grafico-niveis", 
        style={'cursor': 'pointer'}
    )
    
    tabela_estoque_baixo_card = dbc.Card([
        dbc.CardBody(
            html.Div(id=f'{pageTag}container-tabela-alerta-estoque-baixo')
        )
    ], className="shadow-sm h-100", style={'height': '450px'})
    
    grafico_categorias_baixo_card = dbc.Card([
        dbc.CardBody([
            dcc.Graph(
                id=f'{pageTag}grafico-categorias-estoque-baixo', 
                config={'displayModeBar': False},
                style={'height': '370px'}
            ),
            dbc.Button(
                "Ver detalhes",
                color="primary",
                size="sm",
                id=f"btn-{pageTag}-det-fig6",
                class_name="botao-detalhes rounded",
                style={
                    'position': 'absolute', 
                    'bottom': '10px', 
                    'right': '10px',
                    'z-index': '10',
                    'opacity': '0.8'
                }
            ),
        ], className="position-relative")
    ], className="shadow-sm h-100 card-com-hover")
    
    # Card previsão de estoque compacta
    previsao_estoque_card = dbc.Card(
        dbc.CardBody([
            html.H5("Previsão de Estoque", className="mb-3 text-center fw-bold"),
            html.Div(id=f'{pageTag}tabela-previsao-estoque-container')
        ], style={'height': '450px'}),
        className="shadow-sm h-100"
    )
    
    # Card produtos sem venda
    grafico_sem_venda_card = html.Div(
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    id=f'{pageTag}grafico-produtos-sem-venda',
                    config={'displayModeBar': False},
                    style={'height': '400px'}
                ),
                dbc.Button(
                    "Ver detalhes",
                    color="primary",
                    size="sm",
                    id=f"btn-{pageTag}-det-fig7",
                    class_name="botao-detalhes rounded",
                    style={
                        'position': 'absolute', 
                        'bottom': '10px', 
                        'right': '10px',
                        'z-index': '10',
                        'opacity': '0.8'
                    }
                ),
            ], className="position-relative"),
            className="shadow-sm card-com-hover"
        ),
        id=f'{pageTag}card-clicavel-sem-venda',
        style={'cursor': 'pointer'}
    )
    
    # Card sugestão de compras
    tabela_sugestao_compras_card = dbc.Card(
        dbc.CardBody(
            html.Div(id=f'{pageTag}tabela-sugestao-compras-container')
        ),
        className="shadow-sm"
    )

    # Layout principal com proporções corrigidas
    layout_principal = html.Div([
        
        # Primeira linha: Gráfico de linha (grupo) + Gráfico de níveis
        dbc.Row([
            dbc.Col(grafico_estoque_grupo_card, width=12, lg=7),
            dbc.Col(grafico_niveis_card, width=12, lg=5),
        ], className="g-3 mb-3", align="stretch"),

        # Segunda linha: Estoque vs Vendas + Top produtos donut
        dbc.Row([
            dbc.Col(grafico_estoque_populares_card, width=12, lg=6),
            dbc.Col(grafico_top_produtos_card, width=12, lg=6),
        ], className="g-3 mb-3", align="stretch"),

        # Terceira linha: Previsão + Treemap
        dbc.Row([
            dbc.Col(previsao_estoque_card, width=12, lg=3),
            dbc.Col(grafico_treemap_card, width=12, lg=9),
        ], className="g-3 mb-3", align="stretch"),

        # Quarta linha: Categorias estoque baixo + Tabela produtos críticos
        dbc.Row([
            dbc.Col(grafico_categorias_baixo_card, width=12, lg=8),
            dbc.Col(tabela_estoque_baixo_card, width=12, lg=4)
        ], className="g-3 mb-3", align="stretch"),
        
        # Quinta linha: Produtos sem venda
        dbc.Row([
            dbc.Col(grafico_sem_venda_card, width=12)
        ], className="g-3 mb-3"),
        
        # Sexta linha: Sugestão de compras
        dbc.Row([
            dbc.Col(tabela_sugestao_compras_card, width=12)
        ], className="g-3 mb-3"),
        
        # Modais dos gráficos (invisíveis)
        html.Div([
            # Modal 1 - Estoque por Grupo
            dbc.Modal([
                dbc.ModalHeader("Detalhes: Volume de Estoque por Grupo"),
                dbc.ModalBody(html.Div(id=f"{pageTag}modal-content-1")),
                dbc.ModalFooter(
                    dbc.Button("Fechar", id=f"close-modal-{pageTag}-det-fig1", className="ml-auto")
                ),
            ], id=f"modal-{pageTag}-det-fig1", size="xl", is_open=False, scrollable=True),
            
            # Modal 2 - Estoque vs Vendas  
            dbc.Modal([
                dbc.ModalHeader("Detalhes: Estoque vs Vendas"),
                dbc.ModalBody(html.Div(id=f"{pageTag}modal-content-2")),
                dbc.ModalFooter(
                    dbc.Button("Fechar", id=f"close-modal-{pageTag}-det-fig2", className="ml-auto")
                ),
            ], id=f"modal-{pageTag}-det-fig2", size="xl", is_open=False, scrollable=True),
            
            # Modal 3 - Treemap
            dbc.Modal([
                dbc.ModalHeader("Detalhes: Distribuição por Grupo"),
                dbc.ModalBody(html.Div(id=f"{pageTag}modal-content-3")),
                dbc.ModalFooter(
                    dbc.Button("Fechar", id=f"close-modal-{pageTag}-det-fig3", className="ml-auto")
                ),
            ], id=f"modal-{pageTag}-det-fig3", size="xl", is_open=False, scrollable=True),
            
            # Modal 4 - Top Produtos
            dbc.Modal([
                dbc.ModalHeader("Detalhes: Top Produtos por Estoque"),
                dbc.ModalBody(html.Div(id=f"{pageTag}modal-content-4")),
                dbc.ModalFooter(
                    dbc.Button("Fechar", id=f"close-modal-{pageTag}-det-fig4", className="ml-auto")
                ),
            ], id=f"modal-{pageTag}-det-fig4", size="xl", is_open=False, scrollable=True),
            
            # Modal 5 - Níveis de Estoque
            dbc.Modal([
                dbc.ModalHeader("Detalhes: Produtos por Nível de Estoque"),
                dbc.ModalBody(html.Div(id=f"{pageTag}modal-content-5")),
                dbc.ModalFooter(
                    dbc.Button("Fechar", id=f"close-modal-{pageTag}-det-fig5", className="ml-auto")
                ),
            ], id=f"modal-{pageTag}-det-fig5", size="xl", is_open=False, scrollable=True),
            
            # Modal 6 - Categorias Estoque Baixo
            dbc.Modal([
                dbc.ModalHeader("Detalhes: Categorias com Estoque Baixo"),
                dbc.ModalBody(html.Div(id=f"{pageTag}modal-content-6")),
                dbc.ModalFooter(
                    dbc.Button("Fechar", id=f"close-modal-{pageTag}-det-fig6", className="ml-auto")
                ),
            ], id=f"modal-{pageTag}-det-fig6", size="xl", is_open=False, scrollable=True),
            
            # Modal 7 - Produtos Sem Venda
            dbc.Modal([
                dbc.ModalHeader("Detalhes: Produtos Sem Venda por Grupo"),
                dbc.ModalBody(html.Div(id=f"{pageTag}modal-content-7")),
                dbc.ModalFooter(
                    dbc.Button("Fechar", id=f"close-modal-{pageTag}-det-fig7", className="ml-auto")
                ),
            ], id=f"modal-{pageTag}-det-fig7", size="xl", is_open=False, scrollable=True),
        ])
    ], className="p-3")

    return layout_principal


def register_callbacks(app):
    """Registra todos os callbacks do estoque seguindo padrão do projeto."""
    
    # Callback principal de inicialização
    @app.callback(
        [Output(f"{pageTag}header", "children"),
         Output(f"{pageTag}body", "children")],
        [Input(f"{pageTag}update", "data")],
        [State(f"{pageTag}session_data", "data")]
    )
    def inicializar_estoque(update_data, session_data):
        """Inicializa o estoque seguindo padrão do projeto."""
        if not update_data or not session_data:
            return html.Div(), html.Div()
        
        session_id = session_data.get("session_id", "estoque_default")
        
        # Verificar se dados estão na sessão
        if f"{session_id}_estoque" not in sessionDF:
            df_estoque = carregar_dados_estoque()
            if df_estoque.empty:
                return (
                    dbc.Alert("Erro ao carregar dados", color="danger"),
                    html.Div()
                )
            sessionDF[f"{session_id}_estoque"] = df_estoque
        else:
            df_estoque = sessionDF[f"{session_id}_estoque"]
        
        # Criar header e corpo
        header = criar_cabecalho_estoque(df_estoque)
        body = criar_conteudo_principal(df_estoque)
        
        return header, body
    

     # CORREÇÃO: Adicionar callback do collapse seguindo padrão dos outros componentes
    @app.callback(
        Output(f"{pageTag}collapse-filters", "is_open"),
        Input(f"{pageTag}collapse-button", "n_clicks"),
        State(f"{pageTag}collapse-filters", "is_open"),
    )
    def toggle_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
    

    @app.callback(
        [Output(f"{pageTag}metrics", "children")],
        [
            Input(f"{pageTag}fil_excluir_grupo", "value"),
            Input(f"{pageTag}fil_excluir_categoria", "value"), 
            Input(f"{pageTag}fil_excluir_produto", "value"),
            # Usar limites dos filtros do HeaderDash
            Input(f"{pageTag}fil_limite_baixo", "value"),
            Input(f"{pageTag}fil_limite_medio", "value"),
        ],
        [State(f"{pageTag}session_data", "data")]
    )
    def atualizar_metricas_completo(fil_excluir_grupos, fil_excluir_categorias, 
                                   fil_excluir_produtos, limite_baixo_filtro, limite_medio_filtro,
                                   session_data):
        """Atualiza métricas usando filtros de exclusão + inputs livres de limites."""
        from assets.static import supportClass
        
        session_id = session_data.get("session_id", "estoque_default") if session_data else "estoque_default"
        
        if f"{session_id}_estoque" not in sessionDF:
            return [html.Div()]
        
        df_estoque = sessionDF[f"{session_id}_estoque"]
        
        # Aplicar filtros de exclusão das configurações primeiro
        config_exclusao = carregar_configuracoes_exclusao()
        df_filtrado = aplicar_filtros_exclusao(df_estoque, config_exclusao)
        
        # Validar e usar limites dos filtros
        try:
            limite_baixo = int(limite_baixo_filtro) if limite_baixo_filtro else 10
            limite_medio = int(limite_medio_filtro) if limite_medio_filtro else 100
            
            # Validação lógica: médio deve ser maior que baixo
            if limite_medio <= limite_baixo:
                limite_medio = limite_baixo + 10
                
        except (ValueError, TypeError):
            limite_baixo, limite_medio = 10, 100
        
        # Aplicar filtros de exclusão do HeaderDash
        df_filtrado = aplicar_filtros_exclusao_header(
            df_filtrado, fil_excluir_grupos, fil_excluir_categorias,
            fil_excluir_produtos, limite_baixo, limite_medio
        )
        
        # Calcular métricas atualizadas
        metricsDict = calcular_metricas_header(df_filtrado)
        
        return [supportClass.dictHeaderDash(pageTag, metricsDict)]
    

    # Callback principal de atualização de gráficos
    @app.callback(
        [
            Output(f'{pageTag}grafico-treemap-estoque', 'figure'),
            Output(f'{pageTag}grafico-estoque-grupo', 'figure'),
            Output(f'{pageTag}container-tabela-alerta-estoque-baixo', 'children'),
            Output(f'{pageTag}grafico-top-produtos', 'figure'),
            Output(f'{pageTag}grafico-niveis-estoque', 'figure'),
            Output(f'{pageTag}grafico-estoque-populares', 'figure'),
            Output(f'{pageTag}grafico-categorias-estoque-baixo', 'figure'),
            Output(f'{pageTag}tabela-previsao-estoque-container', 'children'),
            Output(f'{pageTag}grafico-produtos-sem-venda', 'figure'),
            Output(f'{pageTag}tabela-sugestao-compras-container', 'children'),
        ],
        [
        
            # CORREÇÃO: Filtros de exclusão + limites do HeaderDash
            Input(f"{pageTag}fil_excluir_grupo", "value"),
            Input(f"{pageTag}fil_excluir_categoria", "value"), 
            Input(f"{pageTag}fil_excluir_produto", "value"),
            Input(f"{pageTag}fil_limite_baixo", "value"),
            Input(f"{pageTag}fil_limite_medio", "value"),
            Input(f'{pageTag}dropdown-categoria-filtro', 'value'),
            Input(f'{pageTag}dropdown-grupo-filtro', 'value'),
            Input(f'{pageTag}input-nome-produto-filtro', 'value'),
            Input(f'{pageTag}span-config-atual-limite-baixo', 'children'),
            Input(f'{pageTag}span-config-atual-limite-medio', 'children'),
            Input(f'{pageTag}span-excluidos-grupos', 'children'),
            Input(f'{pageTag}span-excluidos-categorias', 'children'),
            Input(f'{pageTag}span-excluidos-produtos-codigos', 'children')
        ],
        [State(f"{pageTag}session_data", "data")]
    )
    def atualizar_dashboard_filtrado(fil_excluir_grupos, fil_excluir_categorias, 
                                            fil_excluir_produtos, limite_baixo_filtro, limite_medio_filtro,
                                            categoria_selecionada, grupo_selecionado, nome_produto_filtrado,
                                            limite_baixo_str, limite_medio_str,
                                            ignore_exc_grp, ignore_exc_cat, ignore_exc_prod,
                                            session_data):
        """Atualiza dashboard com filtros aplicados seguindo padrão do projeto."""
        
        # Obter dados da sessão
        session_id = session_data.get("session_id", "estoque_default") if session_data else "estoque_default"
        
        if f"{session_id}_estoque" not in sessionDF:
            # Criar figuras vazias se não há dados
            fig_vazia = criar_figura_vazia("Sem Dados")
            tabela_vazia = criar_tabela_produtos_criticos(pd.DataFrame(), 'tabela-vazia', "Estoque Baixo")
            return (fig_vazia, fig_vazia, tabela_vazia, fig_vazia, fig_vazia,
                    fig_vazia, fig_vazia, fig_vazia, fig_vazia, html.Div())

        df_global_original = sessionDF[f"{session_id}_estoque"]
        
        # 1. Aplicar filtros de exclusão das configurações
        config_exclusao = carregar_configuracoes_exclusao()
        dff = aplicar_filtros_exclusao(df_global_original, config_exclusao)
        
        # 2. Aplicar filtros de exclusão do HeaderDash
        dff = aplicar_filtros_exclusao_header(
            dff, fil_excluir_grupos, fil_excluir_categorias,
            fil_excluir_produtos, limite_baixo_filtro, limite_medio_filtro
        )
        
        # 3. Aplicar filtros interativos adicionais (offcanvas) - esses mantêm lógica de inclusão
        dff_filtrado = aplicar_filtros_interativos(
            dff, 
            categoria_selecionada, 
            grupo_selecionado, 
            nome_produto_filtrado
        )
        
        if dff_filtrado.empty:
            fig_vazia = criar_figura_vazia("Nenhum produto restante após filtros")
            tabela_vazia = criar_tabela_produtos_criticos(pd.DataFrame(), 'tabela-vazia-filtros', "Estoque Baixo")
            return (fig_vazia, fig_vazia, tabela_vazia, fig_vazia, fig_vazia,
                    fig_vazia, fig_vazia, fig_vazia, fig_vazia, html.Div())

        # Usar limites dos filtros (ou fallback para configurações)
        try:
            limite_baixo = int(limite_baixo_filtro) if limite_baixo_filtro else 10
            limite_medio = int(limite_medio_filtro) if limite_medio_filtro else 100
            
            # Validação: limite baixo deve ser menor que limite médio
            if limite_baixo >= limite_medio:
                limite_medio = limite_baixo + 10
                
        except (ValueError, TypeError):
            config_niveis = carregar_definicoes_niveis_estoque()
            limite_baixo = config_niveis.get("limite_estoque_baixo", 10)
            limite_medio = config_niveis.get("limite_estoque_medio", 100)

        # Criar gráficos
        fig_treemap = criar_grafico_treemap_estoque_grupo(dff_filtrado)
        fig_estoque_grupo = criar_grafico_estoque_por_grupo(dff_filtrado)
        fig_top_produtos = criar_grafico_top_produtos_estoque(dff_filtrado, n=7)
        fig_niveis = criar_grafico_niveis_estoque(dff_filtrado, limite_baixo, limite_medio, height=520)
        fig_populares = criar_grafico_estoque_produtos_populares(dff_filtrado, n=7, abreviar_nomes=True)
        fig_sem_venda = criar_grafico_produtos_sem_venda_grupo(dff_filtrado)

        # Criar tabelas
        df_estoque_baixo = identificar_produtos_estoque_baixo(dff_filtrado, limite_baixo)
        tabela_estoque_baixo = criar_tabela_produtos_criticos(
            df_estoque_baixo,
            id_tabela=f'{pageTag}tabela-alerta-estoque-baixo',
            titulo_alerta=f"Alerta: Estoque Baixo (≤ {limite_baixo:g})",
            altura_tabela='400px'
        )
        
        fig_categorias_baixo = criar_grafico_categorias_estoque_baixo(df_estoque_baixo)
        
        tabela_previsao = criar_tabela_previsao_estoque_compacta(dff_filtrado)
        
        df_sugestao = gerar_sugestao_compras(dff_filtrado, limite_baixo, limite_medio)
        tabela_sugestao = criar_tabela_sugestao_compras(df_sugestao)

        return (
            fig_treemap,
            fig_estoque_grupo,
            tabela_estoque_baixo,
            fig_top_produtos,
            fig_niveis,
            fig_populares,
            fig_categorias_baixo,
            tabela_previsao,
            fig_sem_venda,
            tabela_sugestao
        )

    # Callbacks de filtros
    @app.callback(
        [Output(f'{pageTag}dropdown-grupo-filtro', 'value', allow_duplicate=True),
         Output(f'{pageTag}dropdown-categoria-filtro', 'value', allow_duplicate=True),
         Output(f'{pageTag}input-nome-produto-filtro', 'value', allow_duplicate=True)],
        Input(f'{pageTag}btn-resetar-filtros', 'n_clicks'),
        prevent_initial_call=True
    )
    def resetar_filtros(n_clicks):
        """Reseta todos os filtros seguindo padrão do projeto."""
        if n_clicks and n_clicks > 0:
            return None, None, ''
        return no_update, no_update, no_update
    
    @app.callback(
        Output(f"{pageTag}offcanvas-filtros", "is_open"),
        Input("CEestoque_btn-toggle-painel-esquerdo", "n_clicks"),
        State(f"{pageTag}offcanvas-filtros", "is_open"),
        prevent_initial_call=True
    )
    def toggle_filtros_offcanvas(n_clicks, is_open):
        """Toggle do offcanvas de filtros seguindo padrão do projeto."""
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output(f"{pageTag}modal-configuracoes", "is_open"),
        [Input("CEestoque_btn-abrir-modal-config", "n_clicks"), 
         Input(f"{pageTag}btn-fechar-modal-config", "n_clicks")],
        [State(f"{pageTag}modal-configuracoes", "is_open")],
        prevent_initial_call=True
    )
    def toggle_modal_configuracoes(n_abrir, n_fechar, is_open):
        """Toggle do modal de configurações seguindo padrão do projeto."""
        if n_abrir or n_fechar:
            return not is_open
        return is_open

        # Callbacks de configurações
    @app.callback(
        [Output(f'{pageTag}div-status-config-niveis', 'children'),
         Output(f'{pageTag}span-config-atual-limite-baixo', 'children'),
         Output(f'{pageTag}span-config-atual-limite-medio', 'children'),
         Output(f'{pageTag}input-limite-config-baixo', 'value'),
         Output(f'{pageTag}input-limite-config-medio', 'value')],
        Input(f'{pageTag}btn-salvar-config-niveis', 'n_clicks'),
        [State(f'{pageTag}input-limite-config-baixo', 'value'), 
         State(f'{pageTag}input-limite-config-medio', 'value')],
        prevent_initial_call=True
    )
    def salvar_configuracoes_niveis(n_clicks, limite_baixo_input, limite_medio_input):
        """Salva configurações de níveis seguindo padrão do projeto."""
        if n_clicks is None or limite_baixo_input is None or limite_medio_input is None: 
            return no_update, no_update, no_update, no_update, no_update
        
        sucesso, msg_retorno = salvar_definicoes_niveis_estoque(limite_baixo_input, limite_medio_input)
        cor_alerta = "success" if sucesso else "danger"
        status_msg = dbc.Alert(msg_retorno, color=cor_alerta, dismissable=True, duration=7000)
        
        config_recarregada = carregar_definicoes_niveis_estoque()
        val_baixo = config_recarregada.get("limite_estoque_baixo")
        val_medio = config_recarregada.get("limite_estoque_medio")
        
        return status_msg, str(val_baixo), str(val_medio), val_baixo, val_medio

    @app.callback(
        [Output(f'{pageTag}div-status-salvar-exclusoes', 'children'),
         Output(f'{pageTag}span-excluidos-grupos', 'children'),
         Output(f'{pageTag}span-excluidos-categorias', 'children'),
         Output(f'{pageTag}span-excluidos-produtos-codigos', 'children'),
         Output(f'{pageTag}dropdown-excluir-grupos', 'value'),
         Output(f'{pageTag}dropdown-excluir-categorias', 'value'),
         Output(f'{pageTag}dropdown-excluir-produtos-codigos', 'value')],
        Input(f'{pageTag}btn-salvar-exclusoes', 'n_clicks'),
        [State(f'{pageTag}dropdown-excluir-grupos', 'value'), 
         State(f'{pageTag}dropdown-excluir-categorias', 'value'), 
         State(f'{pageTag}dropdown-excluir-produtos-codigos', 'value')],
        prevent_initial_call=True
    )
    def salvar_config_exclusoes(n_clicks, grupos_sel, categorias_sel, produtos_cod_sel):
        """Salva configurações de exclusões seguindo padrão do projeto."""
        if n_clicks is None: 
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        sucesso, msg_retorno = salvar_configuracoes_exclusao(grupos_sel, categorias_sel, produtos_cod_sel)
        cor_alerta = "success" if sucesso else "danger"
        status_msg = dbc.Alert(msg_retorno, color=cor_alerta, dismissable=True, duration=7000)
        
        config_exc_rec = carregar_configuracoes_exclusao()
        grupos = config_exc_rec.get("excluir_grupos", [])
        cats = config_exc_rec.get("excluir_categorias", [])
        prods = config_exc_rec.get("excluir_produtos_codigos", [])
        
        return (
            status_msg, 
            ", ".join(grupos) if grupos else "Nenhum", 
            ", ".join(cats) if cats else "Nenhuma", 
            ", ".join(map(str, prods)) if prods else "Nenhum", 
            grupos, 
            cats, 
            prods
        )

   

    # Criar callbacks para cada modal
    def create_modal_callback(modal_id):
        @app.callback(
            Output(f"modal-{pageTag}-det-fig{modal_id}", "is_open"),
            [
                Input(f"btn-{pageTag}-det-fig{modal_id}", "n_clicks"),
                Input(f"close-modal-{pageTag}-det-fig{modal_id}", "n_clicks"),
            ],
            [State(f"modal-{pageTag}-det-fig{modal_id}", "is_open")],
        )
        def toggle_modal(n1, n2, is_open):
            if n1 or n2:
                return not is_open
            return is_open

    # Criar callbacks para cada modal
    for i in range(1, 8):
        create_modal_callback(i)
    

    # Callbacks para conteúdo dos modais
    @app.callback(
        Output(f"{pageTag}modal-content-1", "children"),
        Input(f"btn-{pageTag}-det-fig1", "n_clicks"),
        State(f"{pageTag}session_data", "data"),
        prevent_initial_call=True
    )
    def modal_content_estoque_grupo(n_clicks, session_data):
        if not n_clicks:
            return html.Div()
        
        session_id = session_data.get("session_id", "estoque_default") if session_data else "estoque_default"
        if f"{session_id}_estoque" not in sessionDF:
            return dbc.Alert("Dados não encontrados", color="warning")
            
        df_estoque = sessionDF[f"{session_id}_estoque"]
        
        # Análise detalhada por grupo
        df_analise = df_estoque.groupby(EstoqueColumns.GRUPO).agg({
            EstoqueColumns.ESTOQUE: ['sum', 'mean', 'count'],
            EstoqueColumns.CODIGO: 'nunique'
        }).round(2)
        
        df_analise.columns = ['Total_Estoque', 'Media_Estoque', 'Qtd_Registros', 'SKUs_Unicos']
        df_analise = df_analise.reset_index().sort_values('Total_Estoque', ascending=False)
        
        # Formatar valores
        df_analise['Total_Formatado'] = df_analise['Total_Estoque'].apply(conversores.MetricInteiroValores)
        df_analise['Media_Formatada'] = df_analise['Media_Estoque'].apply(lambda x: f"{x:.1f}")
        df_analise['SKUs_Formatados'] = df_analise['SKUs_Unicos'].apply(conversores.MetricInteiroValores)
        
        return html.Div([
            html.H5("Análise Detalhada por Grupo", className="mb-4"),
            dash_table.DataTable(
                columns=[
                    {"name": "Grupo", "id": EstoqueColumns.GRUPO},
                    {"name": "Total Estoque", "id": "Total_Formatado"},
                    {"name": "Média Estoque", "id": "Media_Formatada"},
                    {"name": "SKUs Únicos", "id": "SKUs_Formatados"},
                ],
                data=df_analise.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.05)'}
                ]
            )
        ])

    @app.callback(
        Output(f"{pageTag}modal-content-5", "children"),
        [Input(f"btn-{pageTag}-det-fig5", "n_clicks")],
        [State(f"{pageTag}session_data", "data"),
         State(f"{pageTag}fil_limite_baixo", "value"),
         State(f"{pageTag}fil_limite_medio", "value")],
        prevent_initial_call=True
    )
    def modal_content_niveis_estoque(n_clicks, session_data, limite_baixo, limite_medio):
        if not n_clicks:
            return html.Div()
            
        session_id = session_data.get("session_id", "estoque_default") if session_data else "estoque_default"
        print(f"DEBUG: Modal níveis - Session ID: {session_id}")
        print(f"DEBUG: Chaves disponíveis em sessionDF: {list(sessionDF.keys())}")
        
        if f"{session_id}_estoque" not in sessionDF:
            return dbc.Alert("Dados não encontrados", color="warning")
            
        df_estoque = sessionDF[f"{session_id}_estoque"]
        print(f"DEBUG: DataFrame shape: {df_estoque.shape}")
        print(f"DEBUG: Colunas disponíveis: {df_estoque.columns.tolist()}")
        
        # Aplicar filtros de exclusão das configurações primeiro (como no callback principal)
        from .estoque_data import carregar_configuracoes_exclusao, aplicar_filtros_exclusao
        config_exclusao = carregar_configuracoes_exclusao()
        df_estoque = aplicar_filtros_exclusao(df_estoque, config_exclusao)
        
        # Usar limites dos filtros
        try:
            limite_baixo = int(limite_baixo) if limite_baixo else 10
            limite_medio = int(limite_medio) if limite_medio else 100
        except:
            limite_baixo, limite_medio = 10, 100
            
        print(f"DEBUG: Limites - Baixo: {limite_baixo}, Médio: {limite_medio}")
            
        # Classificar produtos por nível
        def classificar_nivel(estoque):
            try:
                estoque_val = float(estoque)
                if pd.isna(estoque_val) or estoque_val <= limite_baixo:
                    return "Baixo"
                elif estoque_val <= limite_medio:
                    return "Médio"
                else:
                    return "Alto"
            except:
                return "Baixo"
        
        df_estoque[EstoqueColumns.ESTOQUE] = pd.to_numeric(df_estoque[EstoqueColumns.ESTOQUE], errors='coerce').fillna(0)
        df_estoque['Nivel'] = df_estoque[EstoqueColumns.ESTOQUE].apply(classificar_nivel)
        
        # Criar tabs para cada nível
        tabs_content = []
        cores_nivel = {"Baixo": "danger", "Médio": "warning", "Alto": "success"}
        
        # Debug: verificar distribuição de níveis
        print(f"DEBUG: Distribuição de níveis: {df_estoque['Nivel'].value_counts().to_dict()}")
        
        for nivel in ["Baixo", "Médio", "Alto"]:
            df_nivel = df_estoque[df_estoque['Nivel'] == nivel].copy()
            print(f"DEBUG: Nível {nivel} tem {len(df_nivel)} produtos")
            if not df_nivel.empty:
                df_nivel = df_nivel.sort_values(EstoqueColumns.ESTOQUE, ascending=False)
                df_nivel['Estoque_Formatado'] = df_nivel[EstoqueColumns.ESTOQUE].apply(conversores.MetricInteiroValores)
                
                tab_content = dbc.Tab(
                    label=f"{nivel} ({len(df_nivel)} produtos)",
                    tab_id=f"tab-{nivel.lower()}",
                    children=[
                        html.Div([
                            html.P(f"Produtos com estoque {nivel.lower()}", className="mt-3 mb-3"),
                            dash_table.DataTable(
                                columns=[
                                    {"name": "Código", "id": EstoqueColumns.CODIGO},
                                    {"name": "Produto", "id": EstoqueColumns.PRODUTO},
                                    {"name": "Grupo", "id": EstoqueColumns.GRUPO},
                                    {"name": "Estoque", "id": "Estoque_Formatado"},
                                ],
                                data=df_nivel[[EstoqueColumns.CODIGO, EstoqueColumns.PRODUTO, 
                                              EstoqueColumns.GRUPO, "Estoque_Formatado"]].to_dict('records'),
                                page_size=10,
                                style_table={'overflowX': 'auto'},
                                style_cell={'textAlign': 'left', 'padding': '8px'},
                                style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.05)'}
                                ]
                            )
                        ])
                    ]
                )
                tabs_content.append(tab_content)
        
        # Se nenhuma tab foi criada, mostrar mensagem
        if not tabs_content:
            return html.Div([
                html.H5("Produtos por Nível de Estoque", className="mb-4"),
                dbc.Alert("Nenhum produto encontrado para classificação", color="info")
            ])
        
        # Criar tabs para cada nível
        tabs_content = []
        for nivel in ["Baixo", "Médio", "Alto"]:
            df_nivel = df_estoque[df_estoque['Nivel'] == nivel].copy()
            if not df_nivel.empty:
                df_nivel = df_nivel.sort_values(EstoqueColumns.ESTOQUE, ascending=False)
                df_nivel['Estoque_Formatado'] = df_nivel[EstoqueColumns.ESTOQUE].apply(conversores.MetricInteiroValores)
                
                tab_content = dbc.Tab(
                    label=f"{nivel} ({len(df_nivel)} produtos)",
                    tab_id=f"tab-{nivel.lower()}",
                    children=[
                        html.Div([
                            html.P(f"Produtos com estoque {nivel.lower()}", className="mt-3 mb-3"),
                            dash_table.DataTable(
                                columns=[
                                    {"name": "Código", "id": EstoqueColumns.CODIGO},
                                    {"name": "Produto", "id": EstoqueColumns.PRODUTO},
                                    {"name": "Grupo", "id": EstoqueColumns.GRUPO},
                                    {"name": "Estoque", "id": "Estoque_Formatado"},
                                ],
                                data=df_nivel[[EstoqueColumns.CODIGO, EstoqueColumns.PRODUTO, 
                                              EstoqueColumns.GRUPO, "Estoque_Formatado"]].to_dict('records'),
                                page_size=10,
                                style_table={'overflowX': 'auto'},
                                style_cell={'textAlign': 'left', 'padding': '8px'},
                                style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.05)'}
                                ]
                            )
                        ])
                    ]
                )
                tabs_content.append(tab_content)
        
        return html.Div([
            html.H5("Produtos por Nível de Estoque", className="mb-4"),
            html.P(f"Critérios: Baixo ≤ {limite_baixo}, Médio ≤ {limite_medio}, Alto > {limite_medio}", 
                   className="text-muted mb-3"),
            html.Div([
                dbc.Tabs(
                    tabs_content, 
                    active_tab="tab-baixo" if any(tab.tab_id == "tab-baixo" for tab in tabs_content) else tabs_content[0].tab_id
                )
            ], style={
                "color": "#000000 !important",
                "--bs-nav-tabs-link-color": "#000000 !important",
                "--bs-nav-tabs-link-hover-color": "#0056b3 !important",
                "--bs-nav-tabs-link-active-color": "#ffffff !important",
                "--bs-nav-tabs-link-active-bg": "#007bff !important"
            })
        ])

    @app.callback(
        Output(f"{pageTag}modal-content-2", "children"),
        Input(f"btn-{pageTag}-det-fig2", "n_clicks"),
        State(f"{pageTag}session_data", "data"),
        prevent_initial_call=True
    )
    def modal_content_estoque_populares(n_clicks, session_data):
        if not n_clicks:
            return html.Div()
            
        session_id = session_data.get("session_id", "estoque_default") if session_data else "estoque_default"
        if f"{session_id}_estoque" not in sessionDF:
            return dbc.Alert("Dados não encontrados", color="warning")
            
        df_estoque = sessionDF[f"{session_id}_estoque"]
        
        # Análise de correlação estoque vs vendas
        df_analise = df_estoque.copy()
        df_analise[EstoqueColumns.ESTOQUE] = pd.to_numeric(df_analise[EstoqueColumns.ESTOQUE], errors='coerce').fillna(0)
        df_analise[EstoqueColumns.VENDA_MENSAL] = pd.to_numeric(df_analise[EstoqueColumns.VENDA_MENSAL], errors='coerce').fillna(0)
        df_analise['Eficiencia_Vendas'] = df_analise[EstoqueColumns.VENDA_MENSAL] / (df_analise[EstoqueColumns.ESTOQUE] + 1)
        
        # Classificar produtos
        top_vendas = df_analise.nlargest(10, EstoqueColumns.VENDA_MENSAL)
        top_estoque = df_analise.nlargest(10, EstoqueColumns.ESTOQUE)
        top_eficiencia = df_analise.nlargest(10, 'Eficiencia_Vendas')
        
        # Formatar dados
        for df_temp in [top_vendas, top_estoque, top_eficiencia]:
            if not df_temp.empty:
                df_temp['Venda_Formatada'] = df_temp[EstoqueColumns.VENDA_MENSAL].apply(conversores.MetricInteiroValores)
                df_temp['Estoque_Formatado'] = df_temp[EstoqueColumns.ESTOQUE].apply(conversores.MetricInteiroValores)
                df_temp['Eficiencia_Formatada'] = df_temp['Eficiencia_Vendas'].apply(lambda x: f"{x:.2f}")
        
        print(f"DEBUG: Top vendas: {len(top_vendas)}, Top estoque: {len(top_estoque)}, Top eficiência: {len(top_eficiencia)}")
        
        return html.Div([
            html.H5("Análise: Estoque vs Vendas", className="mb-4"),
            dbc.Tabs([
                dbc.Tab(label=f"Top Vendas ({len(top_vendas)})", tab_id="tab-vendas", children=[
                    html.Div([
                        html.P("Produtos com maior volume de vendas mensais", className="mt-3 mb-3"),
                        criar_tabela_modal(top_vendas, [EstoqueColumns.CODIGO, EstoqueColumns.PRODUTO, EstoqueColumns.GRUPO, 'Venda_Formatada', 'Estoque_Formatado'], 
                                         ['Código', 'Produto', 'Grupo', 'Vendas', 'Estoque'])
                    ])
                ]),
                dbc.Tab(label=f"Top Estoque ({len(top_estoque)})", tab_id="tab-estoque", children=[
                    html.Div([
                        html.P("Produtos com maior estoque atual", className="mt-3 mb-3"),
                        criar_tabela_modal(top_estoque, [EstoqueColumns.CODIGO, EstoqueColumns.PRODUTO, EstoqueColumns.GRUPO, 'Estoque_Formatado', 'Venda_Formatada'],
                                         ['Código', 'Produto', 'Grupo', 'Estoque', 'Vendas'])
                    ])
                ]),
                dbc.Tab(label=f"Mais Eficientes ({len(top_eficiencia)})", tab_id="tab-eficiencia", children=[
                    html.Div([
                        html.P("Produtos com melhor relação vendas/estoque", className="mt-3 mb-3"),
                        criar_tabela_modal(top_eficiencia, [EstoqueColumns.CODIGO, EstoqueColumns.PRODUTO, EstoqueColumns.GRUPO, 'Eficiencia_Formatada', 'Venda_Formatada'],
                                         ['Código', 'Produto', 'Grupo', 'Eficiência', 'Vendas'])
                    ])
                ])
            ], active_tab="tab-vendas")
        ], style={
            "color": "#000000 !important",
            "--bs-nav-tabs-link-color": "#000000 !important",
            "--bs-nav-tabs-link-hover-color": "#0056b3 !important", 
            "--bs-nav-tabs-link-active-color": "#ffffff !important",
            "--bs-nav-tabs-link-active-bg": "#007bff !important"
        })

    @app.callback(
        Output(f"{pageTag}modal-content-4", "children"),
        Input(f"btn-{pageTag}-det-fig4", "n_clicks"),
        State(f"{pageTag}session_data", "data"),
        prevent_initial_call=True
    )
    def modal_content_top_produtos(n_clicks, session_data):
        if not n_clicks:
            return html.Div()
            
        session_id = session_data.get("session_id", "estoque_default") if session_data else "estoque_default"
        if f"{session_id}_estoque" not in sessionDF:
            return dbc.Alert("Dados não encontrados", color="warning")
            
        df_estoque = sessionDF[f"{session_id}_estoque"]
        
        # Análise completa dos top produtos
        top_produtos = df_estoque.nlargest(20, EstoqueColumns.ESTOQUE).copy()
        top_produtos['Estoque_Formatado'] = top_produtos[EstoqueColumns.ESTOQUE].apply(conversores.MetricInteiroValores)
        top_produtos['Venda_Formatada'] = top_produtos[EstoqueColumns.VENDA_MENSAL].apply(conversores.MetricInteiroValores)
        top_produtos['Dias_Formatados'] = top_produtos[EstoqueColumns.DIAS_ESTOQUE].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
        
        # Estatísticas gerais
        total_estoque = df_estoque[EstoqueColumns.ESTOQUE].sum()
        estoque_top20 = top_produtos[EstoqueColumns.ESTOQUE].sum()
        percentual_concentracao = (estoque_top20 / total_estoque * 100) if total_estoque > 0 else 0
        
        return html.Div([
            html.H5("Top 20 Produtos com Maior Estoque", className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Concentração", className="card-title"),
                            html.H4(f"{percentual_concentracao:.1f}%", className="text-primary"),
                            html.P("do estoque total", className="text-muted small")
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Valor Total", className="card-title"),
                            html.H4(conversores.MetricInteiroValores(estoque_top20), className="text-success"),
                            html.P("unidades em estoque", className="text-muted small")
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Grupos", className="card-title"),
                            html.H4(top_produtos[EstoqueColumns.GRUPO].nunique(), className="text-info"),
                            html.P("grupos diferentes", className="text-muted small")
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            dash_table.DataTable(
                columns=[
                    {"name": "Posição", "id": "rank"},
                    {"name": "Código", "id": EstoqueColumns.CODIGO},
                    {"name": "Produto", "id": EstoqueColumns.PRODUTO},
                    {"name": "Grupo", "id": EstoqueColumns.GRUPO},
                    {"name": "Estoque", "id": "Estoque_Formatado"},
                    {"name": "Venda Mensal", "id": "Venda_Formatada"},
                    {"name": "Dias Estoque", "id": "Dias_Formatados"}
                ],
                data=[{**row, 'rank': i+1} for i, row in enumerate(
                    top_produtos[[EstoqueColumns.CODIGO, EstoqueColumns.PRODUTO, EstoqueColumns.GRUPO, 
                                 "Estoque_Formatado", "Venda_Formatada", "Dias_Formatados"]].to_dict('records')
                )],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '8px'},
                style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.05)'},
                    {'if': {'column_id': 'rank'}, 'textAlign': 'center', 'fontWeight': 'bold'}
                ]
            )
        ])

    @app.callback(
        Output(f"{pageTag}modal-content-3", "children"),
        Input(f"btn-{pageTag}-det-fig3", "n_clicks"),
        State(f"{pageTag}session_data", "data"),
        prevent_initial_call=True
    )
    def modal_content_treemap(n_clicks, session_data):
        if not n_clicks:
            return html.Div()
            
        session_id = session_data.get("session_id", "estoque_default") if session_data else "estoque_default"
        if f"{session_id}_estoque" not in sessionDF:
            return dbc.Alert("Dados não encontrados", color="warning")
            
        df_estoque = sessionDF[f"{session_id}_estoque"]
        
        # Análise hierárquica por grupo
        analise_grupos = df_estoque.groupby(EstoqueColumns.GRUPO).agg({
            EstoqueColumns.ESTOQUE: ['sum', 'mean', 'count'],
            EstoqueColumns.CODIGO: 'nunique',
            EstoqueColumns.VENDA_MENSAL: 'sum'
        }).round(2)
        
        analise_grupos.columns = ['Total_Estoque', 'Media_Estoque', 'Produtos', 'SKUs', 'Total_Vendas']
        analise_grupos = analise_grupos.reset_index().sort_values('Total_Estoque', ascending=False)
        
        # Calcular percentuais
        total_geral = analise_grupos['Total_Estoque'].sum()
        analise_grupos['Percentual'] = (analise_grupos['Total_Estoque'] / total_geral * 100).round(1)
        analise_grupos['Percentual_Acum'] = analise_grupos['Percentual'].cumsum().round(1)
        
        # Formatar valores
        for col in ['Total_Estoque', 'Total_Vendas', 'SKUs']:
            analise_grupos[f'{col}_Fmt'] = analise_grupos[col].apply(conversores.MetricInteiroValores)
        analise_grupos['Media_Fmt'] = analise_grupos['Media_Estoque'].apply(lambda x: f"{x:.1f}")
        
        return html.Div([
            html.H5("Distribuição Hierárquica por Grupo", className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Análise ABC", className="mb-3"),
                            html.P("Classificação por concentração de estoque:", className="text-muted small mb-2"),
                            html.Div([
                                dbc.Badge("Classe A", color="success", className="me-2"),
                                html.Small("80% do estoque"),
                            ], className="mb-2"),
                            html.Div([
                                dbc.Badge("Classe B", color="warning", className="me-2"),
                                html.Small("15% do estoque"),
                            ], className="mb-2"),
                            html.Div([
                                dbc.Badge("Classe C", color="secondary", className="me-2"),
                                html.Small("5% do estoque"),
                            ])
                        ])
                    ])
                ], width=12, lg=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Top 3 Grupos", className="mb-3"),
                            html.Div([
                                html.Div([
                                    html.Strong(f"1º {analise_grupos.iloc[0][EstoqueColumns.GRUPO]}"),
                                    html.Br(),
                                    html.Small(f"{analise_grupos.iloc[0]['Percentual']:.1f}% do estoque", className="text-muted")
                                ], className="mb-2"),
                                html.Div([
                                    html.Strong(f"2º {analise_grupos.iloc[1][EstoqueColumns.GRUPO] if len(analise_grupos) > 1 else 'N/A'}"),
                                    html.Br(),
                                    html.Small(f"{analise_grupos.iloc[1]['Percentual']:.1f}% do estoque" if len(analise_grupos) > 1 else "N/A", className="text-muted")
                                ], className="mb-2"),
                                html.Div([
                                    html.Strong(f"3º {analise_grupos.iloc[2][EstoqueColumns.GRUPO] if len(analise_grupos) > 2 else 'N/A'}"),
                                    html.Br(),
                                    html.Small(f"{analise_grupos.iloc[2]['Percentual']:.1f}% do estoque" if len(analise_grupos) > 2 else "N/A", className="text-muted")
                                ])
                            ])
                        ])
                    ])
                ], width=12, lg=8)
            ], className="mb-4"),
            
            dash_table.DataTable(
                columns=[
                    {"name": "Grupo", "id": EstoqueColumns.GRUPO},
                    {"name": "Total Estoque", "id": "Total_Estoque_Fmt"},
                    {"name": "% Individual", "id": "Percentual", "type": "numeric", "format": {"specifier": ".1f"}},
                    {"name": "% Acumulado", "id": "Percentual_Acum", "type": "numeric", "format": {"specifier": ".1f"}},
                    {"name": "Média por SKU", "id": "Media_Fmt"},
                    {"name": "SKUs Únicos", "id": "SKUs_Fmt"},
                    {"name": "Total Vendas", "id": "Total_Vendas_Fmt"}
                ],
                data=analise_grupos.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '8px'},
                style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.05)'},
                    {'if': {'column_id': 'Percentual', 'filter_query': '{Percentual} >= 20'}, 'backgroundColor': '#d4edda', 'fontWeight': 'bold'},
                    {'if': {'column_id': 'Percentual_Acum', 'filter_query': '{Percentual_Acum} <= 80'}, 'backgroundColor': '#d4edda'}
                ]
            )
        ])

    @app.callback(
        Output(f"{pageTag}modal-content-6", "children"),
        Input(f"btn-{pageTag}-det-fig6", "n_clicks"),
        State(f"{pageTag}session_data", "data"),
        prevent_initial_call=True
    )
    def modal_content_categorias_baixo(n_clicks, session_data):
        if not n_clicks:
            return html.Div()
            
        session_id = session_data.get("session_id", "estoque_default") if session_data else "estoque_default"
        if f"{session_id}_estoque" not in sessionDF:
            return dbc.Alert("Dados não encontrados", color="warning")
            
        df_estoque = sessionDF[f"{session_id}_estoque"]
        
        # Identificar produtos com estoque baixo
        df_baixo = identificar_produtos_estoque_baixo(df_estoque, 10)  # usar limite padrão
        
        if df_baixo.empty:
            return dbc.Alert("Nenhum produto com estoque baixo encontrado!", color="success")
        
        # Análise por categoria
        analise_cat = df_baixo.groupby(EstoqueColumns.CATEGORIA).agg({
            EstoqueColumns.CODIGO: 'nunique',
            EstoqueColumns.ESTOQUE: ['sum', 'mean'],
            EstoqueColumns.VENDA_MENSAL: 'sum'
        }).round(2)
        
        analise_cat.columns = ['Produtos_Baixos', 'Estoque_Total', 'Estoque_Medio', 'Vendas_Total']
        analise_cat = analise_cat.reset_index().sort_values('Produtos_Baixos', ascending=False)
        
        # Top categorias críticas
        top_categorias = analise_cat.head(5)
        
        return html.Div([
            html.H5("Análise Detalhada: Categorias com Estoque Baixo", className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(str(len(analise_cat)), className="text-danger"),
                            html.P("Categorias Afetadas", className="mb-0")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(conversores.MetricInteiroValores(analise_cat['Produtos_Baixos'].sum()), className="text-warning"),
                            html.P("Produtos Críticos", className="mb-0")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(analise_cat['Categoria'].iloc[0] if not analise_cat.empty else "N/A", className="text-info"),
                            html.P("Categoria Mais Crítica", className="mb-0")
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),
            
            html.H6("Ranking Completo por Categoria", className="mb-3"),
            dash_table.DataTable(
                columns=[
                    {"name": "Posição", "id": "rank"},
                    {"name": "Categoria", "id": EstoqueColumns.CATEGORIA},
                    {"name": "Produtos Críticos", "id": "Produtos_Baixos"},
                    {"name": "Estoque Total", "id": "Estoque_Total_Fmt"},
                    {"name": "Estoque Médio", "id": "Estoque_Medio_Fmt"},
                    {"name": "Vendas Mensais", "id": "Vendas_Total_Fmt"}
                ],
                data=[{
                    **row, 
                    'rank': i+1,
                    'Estoque_Total_Fmt': conversores.MetricInteiroValores(row['Estoque_Total']),
                    'Estoque_Medio_Fmt': f"{row['Estoque_Medio']:.1f}",
                    'Vendas_Total_Fmt': conversores.MetricInteiroValores(row['Vendas_Total'])
                } for i, row in enumerate(analise_cat.to_dict('records'))],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '8px'},
                style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.05)'},
                    {'if': {'column_id': 'rank'}, 'textAlign': 'center', 'fontWeight': 'bold'},
                    {'if': {'row_index': [0, 1, 2]}, 'backgroundColor': 'rgba(220, 53, 69, 0.1)'}
                ]
            )
        ])

    @app.callback(
        Output(f"{pageTag}modal-content-7", "children"),
        Input(f"btn-{pageTag}-det-fig7", "n_clicks"),
        State(f"{pageTag}session_data", "data"),
        prevent_initial_call=True
    )
    def modal_content_sem_venda(n_clicks, session_data):
        if not n_clicks:
            return html.Div()
            
        session_id = session_data.get("session_id", "estoque_default") if session_data else "estoque_default"
        if f"{session_id}_estoque" not in sessionDF:
            return dbc.Alert("Dados não encontrados", color="warning")
            
        df_estoque = sessionDF[f"{session_id}_estoque"]
        
        # Produtos sem venda
        df_estoque[EstoqueColumns.VENDA_MENSAL] = pd.to_numeric(df_estoque[EstoqueColumns.VENDA_MENSAL], errors='coerce').fillna(0)
        df_sem_venda = df_estoque[df_estoque[EstoqueColumns.VENDA_MENSAL] <= 0].copy()
        
        print(f"DEBUG: Total produtos: {len(df_estoque)}")
        print(f"DEBUG: Produtos sem venda: {len(df_sem_venda)}")
        print(f"DEBUG: Valores de venda únicos: {sorted(df_estoque[EstoqueColumns.VENDA_MENSAL].unique())}")
        
        if df_sem_venda.empty:
            return dbc.Alert("Todos os produtos têm vendas registradas!", color="success")
        
        # Análise por grupo
        analise_grupo = df_sem_venda.groupby(EstoqueColumns.GRUPO).agg({
            EstoqueColumns.CODIGO: 'nunique',
            EstoqueColumns.ESTOQUE: ['sum', 'mean']
        }).round(2)
        
        analise_grupo.columns = ['Produtos_Sem_Venda', 'Estoque_Parado', 'Estoque_Medio']
        analise_grupo = analise_grupo.reset_index().sort_values('Produtos_Sem_Venda', ascending=False)
        
        # Produtos individuais ordenados por estoque
        produtos_detalhados = df_sem_venda.nlargest(20, EstoqueColumns.ESTOQUE).copy()
        produtos_detalhados['Estoque_Fmt'] = produtos_detalhados[EstoqueColumns.ESTOQUE].apply(conversores.MetricInteiroValores)
        
        valor_estoque_parado = df_sem_venda[EstoqueColumns.ESTOQUE].sum()
        total_produtos_sem_venda = len(df_sem_venda)
        
        return html.Div([
            html.H5("Análise: Produtos Sem Movimento", className="mb-4"),
            dbc.Alert([
                html.I(className="bi bi-exclamation-triangle me-2"),
                f"Encontrados {conversores.MetricInteiroValores(total_produtos_sem_venda)} produtos sem vendas, ",
                f"representando {conversores.MetricInteiroValores(valor_estoque_parado)} unidades paradas em estoque."
            ], color="warning", className="mb-4"),
            
            dbc.Tabs([
                dbc.Tab(label=f"Por Grupo ({len(analise_grupo)})", tab_id="tab-grupo", children=[
                    html.Div([
                        html.P("Distribuição de produtos sem venda por grupo", className="mt-3 mb-3"),
                        dash_table.DataTable(
                            columns=[
                                {"name": "Grupo", "id": EstoqueColumns.GRUPO},
                                {"name": "Produtos Sem Venda", "id": "Produtos_Sem_Venda"},
                                {"name": "Estoque Parado", "id": "Estoque_Parado_Fmt"},
                                {"name": "Estoque Médio", "id": "Estoque_Medio_Fmt"}
                            ],
                            data=[{
                                **row,
                                'Estoque_Parado_Fmt': conversores.MetricInteiroValores(row['Estoque_Parado']),
                                'Estoque_Medio_Fmt': f"{row['Estoque_Medio']:.1f}"
                            } for row in analise_grupo.to_dict('records')],
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left', 'padding': '8px'},
                            style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                            style_data_conditional=[
                                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.05)'}
                            ]
                        )
                    ])
                ]),
                dbc.Tab(label=f"Top 20 Produtos ({len(produtos_detalhados)})", tab_id="tab-produtos", children=[
                    html.Div([
                        html.P("Produtos sem venda com maior estoque", className="mt-3 mb-3"),
                        dash_table.DataTable(
                            columns=[
                                {"name": "Ranking", "id": "rank"},
                                {"name": "Código", "id": EstoqueColumns.CODIGO},
                                {"name": "Produto", "id": EstoqueColumns.PRODUTO},
                                {"name": "Grupo", "id": EstoqueColumns.GRUPO},
                                {"name": "Estoque", "id": "Estoque_Fmt"}
                            ],
                            data=[{**row, 'rank': i+1} for i, row in enumerate(
                                produtos_detalhados[[EstoqueColumns.CODIGO, EstoqueColumns.PRODUTO, 
                                                   EstoqueColumns.GRUPO, 'Estoque_Fmt']].to_dict('records')
                            )],
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left', 'padding': '8px'},
                            style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                            style_data_conditional=[
                                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.05)'},
                                {'if': {'column_id': 'rank'}, 'textAlign': 'center', 'fontWeight': 'bold'}
                            ]
                        )
                    ])
                ])
            ], active_tab="tab-grupo")
        ], style={
            "color": "#000000 !important",
            "--bs-nav-tabs-link-color": "#000000 !important",
            "--bs-nav-tabs-link-hover-color": "#0056b3 !important",
            "--bs-nav-tabs-link-active-color": "#ffffff !important", 
            "--bs-nav-tabs-link-active-bg": "#007bff !important"
        })

def criar_tabela_modal(df, colunas_ids, colunas_nomes):
    """Helper function to create modal tables."""
    return dash_table.DataTable(
        columns=[{"name": nome, "id": col_id} for nome, col_id in zip(colunas_nomes, colunas_ids)],
        data=df[colunas_ids].to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '8px'},
        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.05)'}
        ]
    )