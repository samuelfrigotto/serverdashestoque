import dash_bootstrap_components as dbc
from dash import html, dcc
from urllib.parse import unquote


class Pictures:
    cta_logo_web = "https://ctasistemas.com.br/img/logo_cta.png"
    cta_logo_local = "/assets/logo_cta.png"


class Settings:
    StoreConfig = "memory"


class Colors:
    txt_primaria = ""
    txt_secondaria = ""
    NavColor = ""
    NavtxtColor = ""
    theme = dbc.themes.COSMO
    colorGraphcs = "#F47C20"
    themeName = "COSMO"
    themecolor = "light"
    themeDark = (False,)
    DEFAULT_COLORS = [
        "#FFCC99",
        "#FFF066",
        "#A0522D",
        "#FFBB73",
        "#FFEA33",
        "#8B4513",
        "#FFAA4D",
        "#FFE000",
        "#A0521D",
        "#FF991A",
        "#F2D600",
        "#7B3F00",
        "#EC8A00",
        "#E6CC00",
        "#5C3317",
        "#D77C00",
        "#D9BF00",
        "#4B2E2B",
        "#C26D00",
        "#CCB200",
        "#AD5E00",
        "#BF9900",
        "#6E2C00",
        "#994F00",
        "#B68E2B",
        "#7D5100",
        "#844100",
        "#A67A00",
        "#8B5A2B",
        "#997000",
        "#8C6600",
        "#996633",
        "#805C00",
        "#736200",
        "#734222",
        "#665800",
        "#594E00",
    ]
    ORANGE_COLORS = [
        "#ff991a",
        "#ec8a00",
        "#d77c00",
        "#c26d00",
        "#ad5e00",
        "#994f00",
        "#844100",
        "#703300",
        "#5b2600",
        "#471900",
    ]
    DISTINCT_GRAPH_COLORS = [
        colorGraphcs,  # Orange
        "#8B0000",  # Dark Red
        "#778899",  # Light Slate Gray
        "#FFC107",  # Amber
        "#6C757D",  # Gray neutral
        "#17A2B8",  # Cyan
        "#20C997",  # Teal
        "#198754",  # Muted Green
        "#6610F2",  # Violet
        "#0D6EFD",  # Blue
        "#E83E8C",  # Pink neutral
        "#343A40",  # Dark gray
        "#FF4C4C",  # Coral red
        "#A0522D",  # Sienna
        "#FF69B4",  # Hot Pink
        "#C0C0C0",  # Silver
        "#2E8B57",  # Sea Green
        "#4682B4",  # Steel Blue
        "#DAA520",  # Goldenrod
        "#708090",  # Slate Gray
        "#9932CC",  # Dark Orchid
        "#3CB371",  # Medium Sea Green
        "#D2691E",  # Chocolate
        "#BDB76B",  # Dark Khaki
        "#5F9EA0",  # Cadet Blue
        "#FF8C00",  # Dark Orange
        "#BC8F8F",  # Rosy Brown
        "#CD5C5C",  # Indian Red
        "#800080",  # Purple
    ]


class Graphcs:
    from stylesDocs.style import styleConfig

    defaultColor = Colors.colorGraphcs
    _styleColors = styleConfig(Colors.themecolor)
    globalTemplate = {
        "paper_bgcolor": _styleColors.back_pri_color,
        "plot_bgcolor": _styleColors.back_pri_color,
        "font": {"color": _styleColors.text_color, "size": 10},
        "xaxis": {
            "zerolinecolor": _styleColors.border_color,
            "tickangle": 45,
            "title_font": {"size": 12},
            "tickfont": {"size": 10},
        },
        "yaxis": {
            "gridcolor": _styleColors.border_color,
            "zerolinecolor": _styleColors.border_color,
            "title_font": {"size": 12},
            "tickfont": {"size": 10},
        },
        "margin": {"l": 30, "r": 30, "t": 30, "b": 30},
        "colorway": [defaultColor],
    }
    pxGraficos = 350


class packCode:
    def HeaderDash(
        title: str,
        Descricao: str,
        pageTag: str,
        lstMetric: dict,
        isFilter: bool = False,
        lstFilters: dict = [],
        ColFilters: int = 3,
        MetricsWidth: int = 5,
    ):
        return dbc.Row(
            [
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Row(
                                                            html.H3(
                                                                unquote(title),
                                                                style={
                                                                    "fontSize": "24px"
                                                                },
                                                            ),
                                                            class_name="p-0 g-0 m-0",
                                                        ),
                                                        dbc.Row(html.Hr()),
                                                        dbc.Row(
                                                            html.H6(
                                                                unquote(Descricao),
                                                                style={
                                                                    "fontSize": "15px"
                                                                },
                                                            ),
                                                            class_name="p-0 g-0 m-0",
                                                        ),
                                                    ]
                                                ),
                                            ],
                                            align="center",
                                            width=(
                                                12 - MetricsWidth - 1 if isFilter else 0
                                            ),
                                        ),
                                        dbc.Col(
                                            dbc.Row(
                                                supportClass.dictHeaderDash(
                                                    pageTag, lstMetric
                                                ),
                                                id=f"{pageTag}metrics",
                                            ),
                                            width=MetricsWidth,
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                [html.I(className="bi bi-funnel-fill")],
                                                id=f"{pageTag}collapse-button",
                                                color="success",
                                                n_clicks=0,
                                                class_name="w-100 shadow-sm rounded",
                                            ),
                                            class_name="mt-1 p-2",
                                            align="center",
                                            width=1,
                                            style=(
                                                {"display": "none"}
                                                if not isFilter
                                                else {"display": "block"}
                                            ),
                                        ),
                                    ]
                                ),
                                dbc.Collapse(
                                    (
                                        dbc.Row(html.Hr(), class_name="p-1"),
                                        dbc.Row(
                                            supportClass.dicFilters(
                                                lstFilters, ColFilters
                                            )
                                            if len(lstFilters) > 0
                                            else html.Div()
                                        ),
                                    ),
                                    id=f"{pageTag}collapse-filters",
                                ),
                            ]
                        )
                    ],
                    class_name="g-0",
                ),
            ],
            class_name="g-0",
        )

    def Navbar(Comps):
        return dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(src=Pictures.cta_logo_web, height="30px")
                                )
                            ],
                            align="center",
                            class_name="g-0",
                        ),
                        href="/",
                        style={"textDecoration": "none"},
                    ),
                    dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                    dbc.Collapse(
                        dbc.Row(
                            dbc.Nav(Comps, pills=True, fill=True),
                            class_name="ms-auto flex-nowrap mt-3 mt-md-0",
                            align="center",
                        ),
                        id="navbar-collapse",
                        is_open=False,
                        navbar=True,
                    ),
                ],
                class_name="g-0",
                fluid=True,
            ),
            color=Colors.themecolor,
            class_name="g-0",
        )

    def filtersProd(addID, df):
        df_grupo = df["Grupo"].unique()
        optionsgrupo = ["Todos"] + sorted(df_grupo)
        df_categoria = df["Categoria"].unique()
        optionscategoria = ["Todos"] + sorted(df_categoria)
        df_marca = df["Marca"].unique()
        optionsmarca = ["Todos"] + sorted(df_marca)

        return dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Grupo"),
                        dcc.Dropdown(
                            multi=True,
                            options=optionsgrupo,
                            value=["Todos"],
                            id=f"{addID}_filgrupo",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Label("Categoria"),
                        dcc.Dropdown(
                            multi=True,
                            options=optionscategoria,
                            value=["Todos"],
                            id=f"{addID}_filcategoria",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Label("Marca"),
                        dcc.Dropdown(
                            multi=True,
                            options=optionsmarca,
                            value=["Todos"],
                            id=f"{addID}_filmarca",
                        ),
                    ]
                ),
            ]
        )

    def filtersVend(addID, df):
        df_sup = df["Supervisor Cadastro"].unique()
        optionssup = ["Todos"] + sorted(df_sup)
        df_ven = df["Vendedor Cadastro"].unique()
        optionsven = ["Todos"] + sorted(df_ven)
        df_venVenda = df["Vendedor Pedido"].unique()
        optionsvenVenda = ["Todos"] + sorted(df_venVenda)

        return dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Supervisor Cadastro"),
                        dcc.Dropdown(
                            multi=True,
                            options=optionssup,
                            value=["Todos"],
                            id=f"{addID}_filsupCad",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Label("Vendedor Cadastro"),
                        dcc.Dropdown(
                            multi=True,
                            options=optionsven,
                            value=["Todos"],
                            id=f"{addID}_filvendCad",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Label("Vendedor Pedido"),
                        dcc.Dropdown(
                            multi=True,
                            options=optionsvenVenda,
                            value=["Todos"],
                            id=f"{addID}_filvendVenda",
                        ),
                    ]
                ),
            ]
        )

    def filtersCliente(addID, df):
        df_cidade = df["Cidade"].unique()
        optioncidade = ["Todos"] + sorted(df_cidade)
        df_canal = df["Canal"].unique()
        optioncanal = ["Todos"] + sorted(df_canal)
        df_cluster = df["Cluster"].unique()
        optioncluster = ["Todos"] + sorted(df_cluster)
        return [
            dbc.Row(html.Hr(), class_name="p-1"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Cidade"),
                            dcc.Dropdown(
                                multi=True,
                                options=optioncidade,
                                value=["Todos"],
                                id=f"{addID}_filcidade",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Canal"),
                            dcc.Dropdown(
                                multi=True,
                                options=optioncanal,
                                value=["Todos"],
                                id=f"{addID}_filcanal",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Cluster"),
                            dcc.Dropdown(
                                multi=True,
                                options=optioncluster,
                                value=["Todos"],
                                id=f"{addID}_filcluster",
                            ),
                        ]
                    ),
                ]
            ),
        ]

    def filters(addID, df):
        df_sup = df["Supervisor Cadastro"].unique()
        optionssup = ["Todos"] + sorted(df_sup)
        df_ven = df["Vendedor Cadastro"].unique()
        optionsven = ["Todos"] + sorted(df_ven)
        df_venVenda = df["Vendedor Pedido"].unique()
        optionsvenVenda = ["Todos"] + sorted(df_venVenda)
        df_grupo = df["Grupo"].unique()
        optionsgrupo = ["Todos"] + sorted(df_grupo)
        df_categoria = df["Categoria"].unique()
        optionscategoria = ["Todos"] + sorted(df_categoria)
        df_marca = df["Marca"].unique()
        optionsmarca = ["Todos"] + sorted(df_marca)

        df_cidade = df["Cidade"].unique()
        optioncidade = ["Todos"] + sorted(df_cidade)
        df_canal = df["Canal"].unique()
        optioncanal = ["Todos"] + sorted(df_canal)
        df_cluster = df["Cluster"].unique()
        optioncluster = ["Todos"] + sorted(df_cluster)
        return [
            dbc.Row(html.Hr(), class_name="p-1"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Supervisor Cadastro"),
                            dcc.Dropdown(
                                multi=True,
                                options=optionssup,
                                value="Todos",
                                id=f"{addID}_filsupCad",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Vendedor Cadastro"),
                            dcc.Dropdown(
                                multi=True,
                                options=optionsven,
                                value="Todos",
                                id=f"{addID}_filvendCad",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Vendedor Pedido"),
                            dcc.Dropdown(
                                multi=True,
                                options=optionsvenVenda,
                                value="Todos",
                                id=f"{addID}_filvendVenda",
                            ),
                        ]
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Grupo"),
                            dcc.Dropdown(
                                multi=True,
                                options=optionsgrupo,
                                value="Todos",
                                id=f"{addID}_filgrupo",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Categoria"),
                            dcc.Dropdown(
                                multi=True,
                                options=optionscategoria,
                                value="Todos",
                                id=f"{addID}_filcategoria",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Marca"),
                            dcc.Dropdown(
                                multi=True,
                                options=optionsmarca,
                                value="Todos",
                                id=f"{addID}_filmarca",
                            ),
                        ]
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Cidade"),
                            dcc.Dropdown(
                                multi=True,
                                options=optioncidade,
                                value="Todos",
                                id=f"{addID}_filcidade",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Canal"),
                            dcc.Dropdown(
                                multi=True,
                                options=optioncanal,
                                value="Todos",
                                id=f"{addID}_filcanal",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Cluster"),
                            dcc.Dropdown(
                                multi=True,
                                options=optioncluster,
                                value="Todos",
                                id=f"{addID}_filcluster",
                            ),
                        ]
                    ),
                ]
            ),
        ]

    def detailModal(title: str, fig, df, pageTag: str, figTag: str):
        return dbc.Modal(
            [
                dbc.ModalHeader(title),
                dbc.ModalBody(
                    [
                        dcc.Graph(figure=fig),
                        html.Hr(),
                        dbc.Table.from_dataframe(
                            df,
                            striped=True,
                            bordered=True,
                            hover=True,
                        ),
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Fechar",
                        id=f"close-modal-{pageTag}-det-fig{figTag}",
                        className="ml-auto",
                    )
                ),
            ],
            id=f"modal-{pageTag}-det-fig{figTag}",
            size="xl",
            is_open=False,
            scrollable=True,
        )


class supportClass:
    def dictHeaderDash(pageTag: str, lstMetric: dict):
        retMetrics = []
        for key, value in lstMetric.items():
            key_str = str(key)
            retMetrics.append(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    dbc.Col(
                                        html.H6(
                                            key_str,
                                            className="card-title",
                                            style={"fontSize": "15px"},
                                        ),
                                        width="auto",
                                    ),
                                    style={"justifyContent": "center"},
                                ),
                                dbc.Row(
                                    [
                                        (
                                            dbc.Col(
                                                html.I(
                                                    className=f"{value['icone']} fs-2 ms-1",
                                                    style={"fontSize": "1rem"},
                                                ),
                                                width="auto",
                                            )
                                            if value["icone"] is not None
                                            else html.Div()
                                        ),
                                        dbc.Col(
                                            html.H5(
                                                value["valor"],
                                                id=f"{pageTag}_metric_{key_str}",
                                                className="card-text p-0",
                                                style={
                                                    "fontSize": "15px",
                                                    "fontWeight": "bold",
                                                },
                                            ),
                                            width="auto",
                                        ),
                                    ],
                                    class_name="d-flex justify-content-between align-items-center",
                                ),
                            ],
                            class_name="p-1",
                        ),
                        className="shadow-sm rounded",
                    )
                )
            )
        return retMetrics

    # distValue, labelName: str, valueDefalt="Todos"
    def dicFilters(lstFilters: dict, columns_per_row: int = 3):
        rows = []
        current_row = []
        column_width = int(12 / columns_per_row)

        for idx, (key, value) in enumerate(lstFilters.items()):
            key_str = str(key)
            # Check if filter should be single-select
            is_multi = value.get("multi", True)  # Default to multi=True for backward compatibility
            
            if is_multi:
                dropdown_options = ["Todos"] + sorted(value["distValue"])
                dropdown_value = [value["valueDefault"]]
            else:
                dropdown_options = sorted(value["distValue"])
                dropdown_value = value["valueDefault"]
            
            current_row.append(
                dbc.Col(
                    [
                        dbc.Label(value["labelName"]),
                        dcc.Dropdown(
                            multi=is_multi,
                            options=dropdown_options,
                            value=dropdown_value,
                            id=key_str,
                        ),
                    ],
                    width=column_width,
                )
            )

            if (idx + 1) % columns_per_row == 0:
                rows.append(dbc.Row(current_row, className="mb-3"))
                current_row = []

        if current_row:
            rows.append(dbc.Row(current_row, className="mb-3"))

        return rows
