
import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc, no_update
from app import app, session_dataframes_cta_express as sessionDF

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
    criar_grafico_produtos_sem_venda_grupo
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

    # Cards de gráficos seguindo padrão do projeto
    altura_graficos_padrao = '410px'
    
    grafico_estoque_grupo_card = dbc.Card(
        dbc.CardBody(
            dcc.Graph(
                id=f'{pageTag}grafico-estoque-grupo', 
                config={'displayModeBar': False}, 
                style={'height': '530px'}
            )
        ), 
        className="shadow-sm h-100"
    )
    
    grafico_estoque_populares_card = html.Div(
        dbc.Card(
            dbc.CardBody(
                dcc.Graph(
                    id=f'{pageTag}grafico-estoque-populares', 
                    config={'displayModeBar': False}, 
                    style={'height': altura_graficos_padrao}
                )
            )
        ),
        id=f'{pageTag}card-clicavel-populares',
        style={'cursor': 'pointer'},
        className="shadow-sm h-100"
    )
    
    grafico_treemap_card = dbc.Card(
        dbc.CardBody(
            dcc.Graph(
                id=f'{pageTag}grafico-treemap-estoque', 
                config={'displayModeBar': False}
            )
        ), 
        className="shadow-sm h-100"
    )
    
    grafico_top_produtos_card = html.Div(
        dbc.Card([
            dbc.CardBody(
                dcc.Graph(
                    id=f'{pageTag}grafico-top-produtos', 
                    config={'displayModeBar': True}, 
                    style={'height': altura_graficos_padrao}
                )
            )
        ], className="shadow-sm h-100 clickable-card"), 
        id=f"{pageTag}card-clicavel-grafico-donut", 
        style={'cursor': 'pointer'}
    )
    
    grafico_niveis_card = html.Div(
        dbc.Card([
            dbc.CardBody(
                dcc.Graph(
                    id=f'{pageTag}grafico-niveis-estoque', 
                    config={'displayModeBar': True}, 
                    style={'height': '530px'}
                )
            )
        ], className="shadow-sm h-100 clickable-card"), 
        id=f"{pageTag}card-clicavel-grafico-niveis", 
        style={'cursor': 'pointer'}
    )
    
    tabela_estoque_baixo_card = dbc.Card([
        dbc.CardBody(
            html.Div(id=f'{pageTag}container-tabela-alerta-estoque-baixo')
        )
    ], className="shadow-sm h-100", style={'height': '450px'})
    
    grafico_categorias_baixo_card = dbc.Card([
        dbc.CardBody(
            dcc.Graph(
                id=f'{pageTag}grafico-categorias-estoque-baixo', 
                config={'displayModeBar': False}
            )
        )
    ], className="shadow-sm h-100", style={'height': '400px'})
    
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
            dbc.CardBody(
                dcc.Graph(id=f'{pageTag}grafico-produtos-sem-venda')
            ),
            className="shadow-sm"
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

    # Layout principal seguindo padrão do projeto
    layout_principal = html.Div([
        dbc.Row([
            dbc.Col(grafico_estoque_grupo_card, width=12, lg=7),
            dbc.Col(grafico_niveis_card, width=12, lg=5),
        ], className="g-2 mb-2", align="stretch"),

        html.Hr(className="my-2"),
        dbc.Row([
            dbc.Col(grafico_estoque_populares_card, width=12, lg=6),
            dbc.Col(grafico_top_produtos_card, width=12, lg=6),
        ], className="g-2 mb-2", align="stretch"),

        html.Hr(className="my-2"),
        dbc.Row([
            dbc.Col(previsao_estoque_card, width=12, lg=3),
            dbc.Col(grafico_treemap_card, width=12, lg=9),
        ], className="g-2 mb-2", align="stretch"),

        html.Hr(className="my-2"),
        dbc.Row([
            dbc.Col(grafico_categorias_baixo_card, width=12, lg=8),
            dbc.Col(tabela_estoque_baixo_card, width=12, lg=4)
        ], className="mb-2", align="stretch"),
        
        html.Hr(className="my-2"),
        dbc.Row([
            dbc.Col(grafico_sem_venda_card, width=12)
        ], className="mb-2"),
        
        dbc.Row([
            dbc.Col(tabela_sugestao_compras_card, width=12)
        ], className="mb-2"),
    ], className="p-2")

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
    def atualizar_dashboard_filtrado(categoria_selecionada, grupo_selecionado, nome_produto_filtrado,
                                    limite_baixo_str, limite_medio_str,
                                    ignore_exc_grp, ignore_exc_cat, ignore_exc_prod,
                                    session_data):
        """Atualiza dashboard com filtros aplicados seguindo padrão do projeto."""
        
        # Obter dados da sessão
        session_id = session_data.get("session_id", "estoque_default") if session_data else "estoque_default"
        
        if f"{session_id}_estoque" not in sessionDF:
            # Criar figuras vazias se não há dados
            from .estoque_graficos import criar_figura_vazia
            fig_vazia = criar_figura_vazia("Sem Dados")
            tabela_vazia = criar_tabela_produtos_criticos(pd.DataFrame(), 'tabela-vazia', "Estoque Baixo")
            return (fig_vazia, fig_vazia, tabela_vazia, fig_vazia, fig_vazia,
                    fig_vazia, fig_vazia, fig_vazia, fig_vazia, html.Div())

        df_global_original = sessionDF[f"{session_id}_estoque"]
        
        # Aplicar filtros de exclusão
        config_exclusao = carregar_configuracoes_exclusao()
        dff = aplicar_filtros_exclusao(df_global_original, config_exclusao)
        
        # Aplicar filtros interativos
        dff_filtrado = aplicar_filtros_interativos(
            dff, 
            categoria_selecionada, 
            grupo_selecionado, 
            nome_produto_filtrado
        )
        
        if dff_filtrado.empty:
            from .estoque_graficos import criar_figura_vazia
            fig_vazia = criar_figura_vazia("Sem dados com os filtros atuais")
            tabela_vazia = criar_tabela_produtos_criticos(pd.DataFrame(), 'tabela-vazia-filtros', "Estoque Baixo")
            return (fig_vazia, fig_vazia, tabela_vazia, fig_vazia, fig_vazia,
                    fig_vazia, fig_vazia, fig_vazia, fig_vazia, html.Div())

        # Obter configurações de níveis
        config_niveis = carregar_definicoes_niveis_estoque()
        limite_baixo = config_niveis.get("limite_estoque_baixo", 10)
        limite_medio = config_niveis.get("limite_estoque_medio", 100)

        # Criar gráficos
        fig_treemap = criar_grafico_treemap_estoque_grupo(dff_filtrado)
        fig_estoque_grupo = criar_grafico_estoque_por_grupo(dff_filtrado)
        fig_top_produtos = criar_grafico_top_produtos_estoque(dff_filtrado, n=7)
        fig_niveis = criar_grafico_niveis_estoque(dff_filtrado, limite_baixo, limite_medio)
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