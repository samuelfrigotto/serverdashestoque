"""
pages/cta_express/estoque/estoque_componentes.py
Módulo responsável pelos componentes da interface do estoque
"""
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from assets.static import packCode, supportClass
from utils import conversores
from .estoque_data import EstoqueColumns, carregar_definicoes_niveis_estoque, carregar_configuracoes_exclusao
from .estoque_analise import calcular_metricas_header, preparar_opcoes_exclusao

def criar_cabecalho_estoque(df_completo):
    """Cria cabeçalho do estoque seguindo padrão do projeto."""
    if df_completo is None or df_completo.empty:
        metricsDict = {
            "Total de SKUs": {"icone": "bi bi-upc-scan", "valor": "0"},
            "Estoque Total": {"icone": "bi bi-archive-fill", "valor": "0"},
            "Categorias": {"icone": "bi bi-tags-fill", "valor": "0"},
            "Grupos": {"icone": "bi bi-diagram-3-fill", "valor": "0"},
        }
    else:
        metricsDict = calcular_metricas_header(df_completo)

    # Criar header customizado com botões de filtros e configurações
    return dbc.Row([
        dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([
                        dbc.Row(
                            html.H3("Controle de Estoque", style={"fontSize": "24px"}),
                            class_name="p-0 g-0 m-0",
                        ),
                        dbc.Row(html.Hr()),
                        dbc.Row(
                            html.H6("Dados atualizados conforme filtros aplicados", style={"fontSize": "15px"}),
                            class_name="p-0 g-0 m-0",
                        ),
                    ], align="center", width=3),
                    dbc.Col(
                        dbc.Row(
                            supportClass.dictHeaderDash("CEestoque_", metricsDict),
                            id="CEestoque_metrics",
                        ),
                        width=8,
                    ),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button(
                                [html.I(className="bi bi-funnel-fill me-1"), "Filtros"],
                                id="CEestoque_btn-toggle-painel-esquerdo",
                                color="primary",
                                size="sm",
                                className="shadow-sm"
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-gear-fill me-1"), "Config"],
                                id="CEestoque_btn-abrir-modal-config",
                                color="secondary",
                                size="sm",
                                className="shadow-sm"
                            ),
                        ], vertical=True, className="w-100")
                    ], align="center", width=1),
                ])
            ])
        ], class_name="g-0"),
    ], class_name="g-0")


def criar_painel_filtros(df_completo):
    """Cria painel de filtros seguindo padrão do projeto."""
    opcoes_categoria, opcoes_grupo = [], []
    
    if df_completo is not None and not df_completo.empty:
        opcoes_categoria = [
            {'label': str(cat), 'value': str(cat)} 
            for cat in sorted(df_completo[EstoqueColumns.CATEGORIA].dropna().unique())
        ]
        opcoes_grupo = [
            {'label': str(grp), 'value': str(grp)} 
            for grp in sorted(df_completo[EstoqueColumns.GRUPO].dropna().unique())
        ]

    return html.Div([
        html.H5("Filtros", className="mb-3"),
        html.Div([
            dbc.Label("Grupo:", className="fw-bold"), 
            dcc.Dropdown(
                id='CEestoque_dropdown-grupo-filtro', 
                options=opcoes_grupo, 
                value=None, 
                multi=False, 
                placeholder="Todos os Grupos"
            )
        ], className="mb-3"),
        html.Div([
            dbc.Label("Categoria:", className="fw-bold"), 
            dcc.Dropdown(
                id='CEestoque_dropdown-categoria-filtro', 
                options=opcoes_categoria, 
                value=None, 
                multi=False, 
                placeholder="Todas as Categorias"
            )
        ], className="mb-3"),
        html.Div([
            dbc.Label("Nome do Produto:", className="fw-bold"), 
            dcc.Input(
                id='CEestoque_input-nome-produto-filtro', 
                type='text', 
                placeholder='Buscar por nome...', 
                debounce=True, 
                className="form-control"
            )
        ], className="mb-3"),
        dbc.Button(
            "Resetar Todos os Filtros", 
            id="CEestoque_btn-resetar-filtros", 
            color="warning", 
            outline=True, 
            className="w-100 mb-4"
        ),
    ])

def criar_offcanvas_filtros(df_completo):
    """Cria offcanvas de filtros seguindo padrão do projeto."""
    return dbc.Offcanvas(
        criar_painel_filtros(df_completo),
        id="CEestoque_offcanvas-filtros",
        title="Filtros e Resumo",
        is_open=False,
        placement="start",
        backdrop=False,
        scrollable=True,
        style={'width': '350px'},
    )

def criar_conteudo_configuracoes(df_completo_para_opcoes):
    """Cria conteúdo de configurações seguindo padrão do projeto."""
    config_niveis_atuais = carregar_definicoes_niveis_estoque()
    valor_inicial_baixo = config_niveis_atuais.get("limite_estoque_baixo")
    valor_inicial_medio = config_niveis_atuais.get("limite_estoque_medio")

    config_exclusao_atuais = carregar_configuracoes_exclusao()
    grupos_excluidos_atuais = config_exclusao_atuais.get("excluir_grupos", [])
    categorias_excluidas_atuais = config_exclusao_atuais.get("excluir_categorias", [])
    produtos_excluidos_atuais_codigos = config_exclusao_atuais.get("excluir_produtos_codigos", [])

    opcoes_grupos_excluir, opcoes_categorias_excluir, opcoes_produtos_excluir = preparar_opcoes_exclusao(df_completo_para_opcoes)

    card_definicoes_niveis = dbc.Card([
        dbc.CardHeader(html.H5("Definições de Níveis de Estoque", className="my-2")),
        dbc.CardBody([
            html.P("Defina os valores para as faixas de Estoque Baixo, Médio e Alto."),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Estoque Baixo é: Estoque ≤", className="fw-bold"),
                    dcc.Input(
                        id="CEestoque_input-limite-config-baixo", 
                        type="number", 
                        min=0, 
                        step=1, 
                        value=valor_inicial_baixo, 
                        className="form-control mb-2", 
                        style={'maxWidth': '150px'}
                    ),
                ], md=6),
                dbc.Col([
                    dbc.Label("Estoque Médio é: > Baixo e ≤", className="fw-bold"),
                    dcc.Input(
                        id="CEestoque_input-limite-config-medio", 
                        type="number", 
                        min=0, 
                        step=1, 
                        value=valor_inicial_medio, 
                        className="form-control mb-2", 
                        style={'maxWidth': '150px'}
                    ),
                ], md=6)
            ], className="mb-3"),
            html.P(html.Small(["Estoque Alto será: Estoque > Limite Médio"]), className="text-muted mt-1"),
            dbc.Button(
                "Salvar Definições de Níveis", 
                id="CEestoque_btn-salvar-config-niveis", 
                color="primary", 
                className="mt-2 mb-3"
            ),
            html.Div(id="CEestoque_div-status-config-niveis", className="mt-2"),
            html.Div([
                html.H6("Definições de Níveis Atuais:", className="mt-3"),
                dbc.Row([
                    dbc.Col(html.Strong("Limite Estoque Baixo (≤):"), width="auto", className="pe-0"), 
                    dbc.Col(html.Span(id="CEestoque_span-config-atual-limite-baixo", children=str(valor_inicial_baixo)))
                ]),
                dbc.Row([
                    dbc.Col(html.Strong("Limite Estoque Médio (> Baixo e ≤):"), width="auto", className="pe-0"), 
                    dbc.Col(html.Span(id="CEestoque_span-config-atual-limite-medio", children=str(valor_inicial_medio)))
                ]),
            ], className="mt-3 p-3 border rounded bg-light")
        ])
    ], className="h-100 shadow-sm")

    card_excluir_itens = dbc.Card([
        dbc.CardHeader(html.H5("Excluir Itens da Visualização Principal", className="my-2")),
        dbc.CardBody([
            html.P("Selecione itens para não exibir na aba 'Visão Geral do Estoque'."),
            dbc.Label("Grupos a Excluir:", className="fw-bold"),
            dcc.Dropdown(
                id='CEestoque_dropdown-excluir-grupos', 
                options=opcoes_grupos_excluir, 
                value=grupos_excluidos_atuais, 
                multi=True, 
                placeholder="Selecione Grupos"
            ),
            html.Br(),
            dbc.Label("Categorias a Excluir:", className="fw-bold"),
            dcc.Dropdown(
                id='CEestoque_dropdown-excluir-categorias', 
                options=opcoes_categorias_excluir, 
                value=categorias_excluidas_atuais, 
                multi=True, 
                placeholder="Selecione Categorias"
            ),
            html.Br(),
            dbc.Label("Produtos (por Código) a Excluir:", className="fw-bold"),
            dcc.Dropdown(
                id='CEestoque_dropdown-excluir-produtos-codigos', 
                options=opcoes_produtos_excluir, 
                value=produtos_excluidos_atuais_codigos, 
                multi=True, 
                searchable=True, 
                placeholder="Busque e selecione Produtos"
            ),
            dbc.Button(
                "Salvar Exclusões", 
                id="CEestoque_btn-salvar-exclusoes", 
                color="danger", 
                className="mt-3 mb-3"
            ),
            html.Div(id="CEestoque_div-status-salvar-exclusoes", className="mt-2"),
            html.Div([
                html.H6("Itens Atualmente Excluídos:", className="mt-3"),
                dbc.Row([
                    dbc.Col(html.Strong("Grupos:"), width="auto", className="pe-0"), 
                    dbc.Col(html.Span(
                        id="CEestoque_span-excluidos-grupos", 
                        children=", ".join(grupos_excluidos_atuais) if grupos_excluidos_atuais else "Nenhum"
                    ))
                ]),
                dbc.Row([
                    dbc.Col(html.Strong("Categorias:"), width="auto", className="pe-0"), 
                    dbc.Col(html.Span(
                        id="CEestoque_span-excluidos-categorias", 
                        children=", ".join(categorias_excluidas_atuais) if categorias_excluidas_atuais else "Nenhuma"
                    ))
                ]),
                dbc.Row([
                    dbc.Col(html.Strong("Produtos (Códigos):"), width="auto", className="pe-0"), 
                    dbc.Col(html.Span(
                        id="CEestoque_span-excluidos-produtos-codigos", 
                        children=", ".join(produtos_excluidos_atuais_codigos) if produtos_excluidos_atuais_codigos else "Nenhum"
                    ))
                ]),
            ], className="mt-3 p-3 border rounded bg-light")
        ])
    ], className="h-100 shadow-sm")

    return html.Div([
        dbc.Row([ 
            dbc.Col(card_definicoes_niveis, width=12, lg=6, className="mb-4"), 
            dbc.Col(card_excluir_itens, width=12, lg=6, className="mb-4")    
        ], className="g-3") 
    ])

def criar_modal_configuracoes(df_completo):
    """Cria modal de configurações seguindo padrão do projeto."""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Configurações Gerais")),
        dbc.ModalBody(criar_conteudo_configuracoes(df_completo)),
        dbc.ModalFooter(
            dbc.Button(
                "Fechar", 
                id="CEestoque_btn-fechar-modal-config", 
                className="ms-auto", 
                n_clicks=0, 
                color="secondary"
            )
        ),
    ], id="CEestoque_modal-configuracoes", size="xl", is_open=False, centered=True)

def criar_tabela_produtos_criticos(df_produtos, id_tabela, titulo_alerta, page_size=5, altura_tabela='300px'):
    """Cria tabela de produtos críticos seguindo padrão do projeto."""
    if df_produtos.empty:
        return dbc.Alert(f"{titulo_alerta}: Nenhum produto encontrado.", color="info", className="mt-2")

    colunas_para_dash = [
        {"name": "Produto", "id": EstoqueColumns.PRODUTO}, 
        {"name": "Estoque Atual", "id": EstoqueColumns.ESTOQUE}
    ]
    dados_para_tabela = df_produtos[[EstoqueColumns.PRODUTO, EstoqueColumns.ESTOQUE]].to_dict('records')
    page_size_real = max(1, len(dados_para_tabela))

    return html.Div([
        html.H6(titulo_alerta, className="mt-3 text-danger fw-bold"),
        dash_table.DataTable(
            id=id_tabela, 
            columns=colunas_para_dash, 
            data=dados_para_tabela, 
            page_size=page_size_real,
            style_table={
                'height': altura_tabela, 
                'overflowY': 'auto', 
                'overflowX': 'auto', 
                'width': '100%', 
                'border': '1px solid #dee2e6', 
                'borderRadius': '0.25rem'
            },
            style_header={
                'backgroundColor': '#f8f9fa', 
                'fontWeight': 'bold', 
                'borderBottom': '2px solid #dee2e6', 
                'padding': '8px', 
                'textAlign': 'left', 
                'position': 'sticky', 
                'top': 0, 
                'zIndex': 1
            },
            style_cell={
                'textAlign': 'left', 
                'padding': '8px', 
                'borderRight': '1px solid #f0f0f0', 
                'borderBottom': '1px solid #f0f0f0', 
                'overflow': 'hidden', 
                'textOverflow': 'ellipsis', 
                'maxWidth': 0
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': EstoqueColumns.PRODUTO}, 
                    'minWidth': '200px', 
                    'width': '70%'
                }, 
                {
                    'if': {'column_id': EstoqueColumns.ESTOQUE}, 
                    'textAlign': 'right', 
                    'minWidth': '80px', 
                    'width': '30%'
                }
            ],
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'}, 
                    'backgroundColor': 'rgba(0,0,0,0.025)'
                }, 
                {
                    'if': {
                        'filter_query': f'{{{EstoqueColumns.ESTOQUE}}} <= 0', 
                        'column_id': EstoqueColumns.ESTOQUE
                    }, 
                    'backgroundColor': 'rgba(220, 53, 69, 0.7)', 
                    'color': 'white', 
                    'fontWeight': 'bold'
                }
            ]
        )
    ])

def criar_tabela_sugestao_compras(df_sugestao):
    """Cria tabela de sugestão de compras seguindo padrão do projeto."""
    if df_sugestao.empty:
        return dbc.Alert("Nenhuma sugestão de compra encontrada. Todos os produtos estão com estoque adequado.", color="success")
    
    # Contar produtos por prioridade para estatísticas
    stats_prioridade = df_sugestao['Prioridade'].value_counts()
    forte_rec = stats_prioridade.get('Forte Recomendação', 0)
    recomendado = stats_prioridade.get('Recomendado', 0)
    monitorar = stats_prioridade.get('Monitorar', 0)
    
    colunas = [
        {"name": "Prioridade", "id": "Prioridade"},
        {"name": "Código", "id": EstoqueColumns.CODIGO},
        {"name": "Produto", "id": EstoqueColumns.PRODUTO},
        {"name": "Estoque Atual", "id": EstoqueColumns.ESTOQUE, "type": "numeric"},
        {"name": "Venda Mensal", "id": EstoqueColumns.VENDA_MENSAL, "type": "numeric"},
        {"name": "Dias Estoque", "id": EstoqueColumns.DIAS_ESTOQUE, "type": "numeric"},
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
                'if': {'column_id': EstoqueColumns.DIAS_ESTOQUE, 'filter_query': f'{{{EstoqueColumns.DIAS_ESTOQUE}}} <= 7'},
                'backgroundColor': 'rgba(220, 53, 69, 0.3)',
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': EstoqueColumns.DIAS_ESTOQUE, 'filter_query': f'{{{EstoqueColumns.DIAS_ESTOQUE}}} > 7 && {{{EstoqueColumns.DIAS_ESTOQUE}}} <= 30'},
                'backgroundColor': 'rgba(255, 193, 7, 0.3)'
            }
        ]
    }
    
    return html.Div([
        html.H5("Sugestão de Compras", className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Badge(f"Forte Recomendação: {forte_rec}", color="danger", className="me-2"),
                dbc.Badge(f"Recomendado: {recomendado}", color="warning", className="me-2"),
                dbc.Badge(f"Monitorar: {monitorar}", color="info", className="me-2"),
            ], className="mb-3")
        ]),
        
        html.P("Sugestões baseadas em venda mensal e dias de estoque restantes", className="text-muted mb-3"),
        
        dash_table.DataTable(
            id='CEestoque_tabela-sugestao-compras',
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

def criar_tabela_previsao_estoque_compacta(df, dias_maximos=60):
    """Cria versão compacta da tabela de previsão de estoque."""
    if (df is None or df.empty or 
        EstoqueColumns.DIAS_ESTOQUE not in df.columns or 
        EstoqueColumns.PRODUTO not in df.columns or 
        EstoqueColumns.ESTOQUE not in df.columns):
        return dbc.Alert("Dados incompletos para previsão", color="warning", className="text-center")
    
    df_plot = df.copy()
    df_plot[EstoqueColumns.DIAS_ESTOQUE] = pd.to_numeric(df_plot[EstoqueColumns.DIAS_ESTOQUE], errors='coerce')
    df_plot[EstoqueColumns.ESTOQUE] = pd.to_numeric(df_plot[EstoqueColumns.ESTOQUE], errors='coerce')
    
    # Filtrar produtos com previsão válida
    df_filtrado = df_plot[
        (df_plot[EstoqueColumns.DIAS_ESTOQUE] > 0) & 
        (df_plot[EstoqueColumns.DIAS_ESTOQUE] <= dias_maximos) &
        (df_plot[EstoqueColumns.ESTOQUE] > 0) &
        (df_plot[EstoqueColumns.DIAS_ESTOQUE].notna())
    ]
    
    if df_filtrado.empty:
        return dbc.Alert(f"Nenhum produto crítico (≤{dias_maximos} dias)", color="info", className="text-center")
    
    # Ordenar por dias de estoque crescente
    df_filtrado = df_filtrado.sort_values(EstoqueColumns.DIAS_ESTOQUE, ascending=True)
    
    # Formatar colunas
    df_filtrado[EstoqueColumns.DIAS_ESTOQUE] = df_filtrado[EstoqueColumns.DIAS_ESTOQUE].round(1)
    df_filtrado[EstoqueColumns.ESTOQUE] = df_filtrado[EstoqueColumns.ESTOQUE].round(0)
    
    # Criar tabela mais compacta
    colunas = [
        {"name": "Produto", "id": EstoqueColumns.PRODUTO},
        {"name": "Dias", "id": EstoqueColumns.DIAS_ESTOQUE, "type": "numeric"},
        {"name": "Qtd", "id": EstoqueColumns.ESTOQUE, "type": "numeric"}
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
                'if': {'column_id': EstoqueColumns.DIAS_ESTOQUE, 'filter_query': f'{{{EstoqueColumns.DIAS_ESTOQUE}}} <= 7'},
                'backgroundColor': 'rgba(220, 53, 69, 0.2)',
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': EstoqueColumns.DIAS_ESTOQUE, 'filter_query': f'{{{EstoqueColumns.DIAS_ESTOQUE}}} > 7 && {{{EstoqueColumns.DIAS_ESTOQUE}}} <= 30'},
                'backgroundColor': 'rgba(255, 193, 7, 0.2)'
            }
        ]
    }
    
    return dash_table.DataTable(
        id='CEestoque_tabela-previsao-compacta',
        columns=colunas,
        data=df_filtrado.to_dict('records'),
        style_table={
            'height': '400px',
            'overflowY': 'auto',
            'overflowX': 'auto',
            'border': '1px solid #dee2e6',
            'borderRadius': '0.25rem'
        },
        **estilo_compacto
    )