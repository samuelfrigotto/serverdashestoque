from app import app
from app import session_dataframes_cta_express as sessionDF
from dash import Input, Output, State, dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc
from utils import conversores
import pandas as pd
from assets.static import packCode, Colors, supportClass
from stylesDocs.style import styleConfig
from pages.cta_express.cta_express_globals import variables_data

pageTag: str = "CEKM_"
styleColors = styleConfig(Colors.themecolor)
testTemplate = {
    "paper_bgcolor": styleColors.back_pri_color,
    "plot_bgcolor": styleColors.back_pri_color,
    "font": {"color": styleColors.text_color, "size": 10},
    "xaxis": {
        "gridcolor": styleColors.border_color,
        "zerolinecolor": styleColors.border_color,
        "tickangle": 45,
        "title_font": {"size": 12},
        "tickfont": {"size": 10},
    },
    "yaxis": {
        "gridcolor": styleColors.border_color,
        "zerolinecolor": styleColors.border_color,
        "title_font": {"size": 12},
        "tickfont": {"size": 10},
    },
    "margin": {"l": 30, "r": 30, "t": 30, "b": 30},
}


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
    Output(f"{pageTag}header", "children"),
    Input(f"{pageTag}update", "data"),
    State("session_data", "data"),
)
def showHeader(initData, session_data):
    session_id = session_data.get("session_id", "")

    if initData == 1 and session_id:
        df_resumo = sessionDF[f"{session_id}_resumo"]
        df_detalhamento = sessionDF[f"{session_id}_detalhamento"]
        print(df_resumo.columns)
        metricsDict: dict = {
            "Nº Entregas": {
                "icone": "bi bi-truck",
                "valor": conversores.MetricInteiroValores(
                    df_resumo[variables_data.Num_Entregas].sum()
                ),
            },
            "KM Rodado": {
                "icone": "bi bi-geo-alt",
                "valor": conversores.MetricInteiroValores(
                    df_resumo[variables_data.Num_KM_Rodado].sum()
                ),
            },
            "Média KM Entrega": {
                "icone": "bi bi-geo-alt",
                "valor": conversores.MetricInteiroValores(
                    df_resumo[variables_data.Num_KM_Rodado].sum()
                    / df_resumo[variables_data.Num_Entregas].sum()
                ),
            },
            "Horas em Trânsito": {
                "icone": "bi bi-clock",
                "valor": conversores.MetricInteiroValores(
                    df_resumo[variables_data.TEMPO_Translado].sum() / 60
                ),
            },
            "Horas em Atendimento": {
                "icone": "bi bi-clock",
                "valor": conversores.MetricInteiroValores(
                    (
                        df_resumo[variables_data.TEMPO_Atendimento].sum()
                        + df_resumo[variables_data.TEMPO_AteNegativado].sum()
                    )
                    / 60
                ),
            },
        }

        filters: dict = {
            f"{pageTag}fil_cidade": {
                "distValue": df_detalhamento[variables_data.Desc_Cidade].unique(),
                "labelName": "Cidade",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_rota": {
                "distValue": df_detalhamento[variables_data.Desc_Rota].unique(),
                "labelName": "Rota",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_bairro": {
                "distValue": df_detalhamento[variables_data.Desc_Bairro].unique(),
                "labelName": "Bairro",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_motorista": {
                "distValue": df_detalhamento[variables_data.Desc_Motorista].unique(),
                "labelName": "Motorista",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_placa": {
                "distValue": df_resumo[variables_data.Desc_Placa].unique(),
                "labelName": "Placa",
                "valueDefault": "Todos",
            },
        }
        return packCode.HeaderDash(
            "Quilometragem",
            f"Período de análise: {pd.to_datetime(df_detalhamento[variables_data.DT_Emissao]).min().strftime('%d/%m/%Y')} a {pd.to_datetime(df_detalhamento[variables_data.DT_Emissao]).max().strftime('%d/%m/%Y')}",
            pageTag,
            metricsDict,
            True,
            filters,
            5,
            8,
        )


@app.callback(
    [
        Output(f"{pageTag}body", "children"),
        Output(f"{pageTag}metrics", "children"),
    ],
    [
        Input(f"{pageTag}fil_cidade", "value"),
        Input(f"{pageTag}fil_rota", "value"),
        Input(f"{pageTag}fil_bairro", "value"),
        Input(f"{pageTag}fil_motorista", "value"),
        Input(f"{pageTag}fil_placa", "value"),
    ],
    State("session_data", "data"),
)
def showBody(
    fil_cidade,
    fil_rota,
    fil_bairro,
    fil_motorista,
    fil_placa,
    session_data,
):
    session_id = session_data.get("session_id", "")
    df_detalhamento = sessionDF[f"{session_id}_detalhamento"]
    df_resumo = sessionDF[f"{session_id}_resumo"]

    if "Todos" not in fil_cidade and len(fil_cidade) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=variables_data.Desc_Cidade, filtro=fil_cidade
        )
    if "Todos" not in fil_rota and len(fil_rota) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=variables_data.Desc_Rota, filtro=fil_rota
        )
    if "Todos" not in fil_bairro and len(fil_bairro) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=variables_data.Desc_Bairro, filtro=fil_bairro
        )
    if "Todos" not in fil_motorista and len(fil_motorista) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento,
            tabela=variables_data.Desc_Motorista,
            filtro=fil_motorista,
        )
    if "Todos" not in fil_placa and len(fil_placa) > 0:
        df_resumo = conversores.FiltrarColuna(
            df=df_resumo, tabela=variables_data.Desc_Placa, filtro=fil_placa
        )

    metricsDict: dict = {
        "Nº Entregas": {
            "icone": "bi bi-truck",
            "valor": conversores.MetricInteiroValores(
                df_resumo[variables_data.Num_Entregas].sum()
            ),
        },
        "KM Rodado": {
            "icone": "bi bi-geo-alt",
            "valor": conversores.MetricInteiroValores(
                df_resumo[variables_data.Num_KM_Rodado].sum()
            ),
        },
        "Média KM Entrega": {
            "icone": "bi bi-geo-alt",
            "valor": conversores.MetricInteiroValores(
                df_resumo[variables_data.Num_KM_Rodado].sum()
                / df_resumo[variables_data.Num_Entregas].sum()
            ),
        },
        "Horas em Trânsito": {
            "icone": "bi bi-clock",
            "valor": conversores.MetricInteiroValores(
                df_resumo[variables_data.TEMPO_Translado].sum() / 60
            ),
        },
        "Horas em Atendimento": {
            "icone": "bi bi-clock",
            "valor": conversores.MetricInteiroValores(
                (
                    df_resumo[variables_data.TEMPO_Atendimento].sum()
                    + df_resumo[variables_data.TEMPO_AteNegativado].sum()
                )
                / 60
            ),
        },
    }

    return loadCharts(df_resumo, df_detalhamento), supportClass.dictHeaderDash(
        pageTag, metricsDict
    )


@app.callback(
    Output(f"{pageTag}update", "data"),
    State(f"{pageTag}update", "data"),
    Input("session_data", "data"),
)
def initOperacoes(upData, session_data):
    return 1


def loadCharts(df_resumo, df_detalhamento) -> html.Div:
    pxGraficos = 380

    dfvlro = df_resumo[[variables_data.Desc_Motorista, variables_data.Num_KM_Rodado]]

    dfvlro = dfvlro[dfvlro[variables_data.Num_KM_Rodado] != 0]
    dfvlro = dfvlro.groupby(variables_data.Desc_Motorista).sum().reset_index()

    if len(dfvlro[variables_data.Desc_Motorista]) < 7:
        figDash1 = px.pie(
            dfvlro,
            names=variables_data.Desc_Motorista,
            values=variables_data.Num_KM_Rodado,
            height=pxGraficos,
            title="Distribuição de KM - Motorista",
            hole=0.5,
        )
        figDash1.update_layout(
            testTemplate,
            xaxis_title="KM Rodado",
            yaxis_title="Motorista",
        )
        conversores.format_hover(
            figDash1, dfvlro, "Motorista", "KM Rodado", variables_data.Num_KM_Rodado
        )
        figDash1.update_traces(
            pull=0.01,
        )
    else:
        figDash1 = px.bar(
            dfvlro,
            x=variables_data.Desc_Motorista,
            y=variables_data.Num_KM_Rodado,
            height=pxGraficos,
            title="KM Rodado por Motorista",
        )
        figDash1.update_layout(
            testTemplate,
            xaxis_title="KM Rodado",
            yaxis_title="Motorista",
        )

    dfvlro_dt = (
        df_resumo[
            [
                variables_data.DT_Carga,
                variables_data.Num_KM_Rodado,
                variables_data.Desc_Motorista,
            ]
        ]
        .groupby([variables_data.Desc_Motorista, variables_data.DT_Carga])
        .sum()
        .reset_index()
    )
    dfvlro_dt[variables_data.DT_Carga] = pd.to_datetime(
        dfvlro_dt[variables_data.DT_Carga]
    )
    dfvlro_dt = dfvlro_dt[dfvlro_dt[variables_data.Num_KM_Rodado] != 0]

    figDash2 = px.line(
        dfvlro_dt,
        x=variables_data.DT_Carga,
        y=variables_data.Num_KM_Rodado,
        color=variables_data.Desc_Motorista,
        height=pxGraficos,
        title="Km Rodado por dia",
        line_shape="linear",
        markers=True,
        labels={"desc_Motorista": "Motorista"},
    )

    figDash2.update_layout(
        testTemplate,
        xaxis_title="Data Carga",
        yaxis_title="KM Rodado",
    )

    kmrodado = df_resumo[[variables_data.Desc_Placa, variables_data.Num_KM_Rodado]]  #
    kmrodado = kmrodado.groupby(variables_data.Desc_Placa).sum().reset_index()
    kmrodado = kmrodado[kmrodado[variables_data.Num_KM_Rodado] != 0]  #

    if len(kmrodado[variables_data.Desc_Placa]) < 7:
        figDash3 = px.pie(
            kmrodado,
            names=variables_data.Desc_Placa,
            values=variables_data.Num_KM_Rodado,
            height=pxGraficos,
            title="Distribuição de KM - Veículo",
            hole=0.5,
        )
        figDash3.update_layout(
            testTemplate,
            xaxis_title="KM Rodado",
            yaxis_title="Veículo",
        )
        conversores.format_hover(
            figDash3, kmrodado, "Veículo", "KM Rodado", variables_data.Num_KM_Rodado
        )
        figDash3.update_traces(
            pull=0.01,
        )
    else:
        figDash3 = px.bar(
            dfvlro,
            x=variables_data.Desc_Motorista,
            y=variables_data.Num_KM_Rodado,
            height=pxGraficos,
            title="KM Rodado por Veículo",
        )
        figDash3.update_layout(
            testTemplate,
            xaxis_title="KM Rodado",
            yaxis_title="Veículo",
        )

    placa_km_entregas = df_resumo[
        [
            variables_data.Desc_Placa,
            variables_data.Num_KM_Rodado,  #
            variables_data.Num_Entregas,
        ]
    ]
    placa_km_entregas = (
        placa_km_entregas.groupby(variables_data.Desc_Placa)
        .agg({variables_data.Num_KM_Rodado: "sum", variables_data.Num_Entregas: "sum"})
        .reset_index()
    )
    placa_km_entregas["MediakmEntrega"] = (
        placa_km_entregas[variables_data.Num_KM_Rodado]
        / placa_km_entregas[variables_data.Num_Entregas]
    )

    placa_km_entregas = placa_km_entregas[
        placa_km_entregas[variables_data.Num_KM_Rodado] >= 1
    ]

    figDash4 = px.area(
        placa_km_entregas,
        x=variables_data.Desc_Placa,
        y="MediakmEntrega",
        title="Média de KM por Entrega por Veículo",
        height=pxGraficos,
        color_discrete_sequence=["#2f4b7c"],
        line_shape="spline",
    )
    figDash4.update_traces(fillcolor="#add8e6", line_color="#6495ed")

    figDash4.update_layout(
        testTemplate,
        xaxis_title="Veículo (Placa)",
        yaxis_title="Média de KM por Entrega",
        hovermode="x unified",
        xaxis={"tickangle": 0},
    )

    figDash4.update_traces(
        text=placa_km_entregas["MediakmEntrega"].round(2),
        textposition="top center",
        texttemplate="%{text:.2f}",
    )
    df_merged = pd.merge(
        df_resumo[[variables_data.Guid_Carga, variables_data.Num_KM_Rodado]],  #
        df_detalhamento[[variables_data.Guid_Carga, variables_data.Desc_Cidade]],
        on=variables_data.Guid_Carga,
        how="inner",
    )

    df_merged = df_merged.drop_duplicates(
        subset=[variables_data.Guid_Carga, variables_data.Desc_Cidade]
    )

    km_por_cidade = (
        df_merged.groupby(variables_data.Desc_Cidade)[variables_data.Num_KM_Rodado]  #
        .sum()
        .reset_index()
    )
    km_por_cidade = km_por_cidade[km_por_cidade[variables_data.Num_KM_Rodado] != 0]  #

    figDash5 = px.bar(
        km_por_cidade,
        x=variables_data.Num_KM_Rodado,  #
        y=variables_data.Desc_Cidade,
        height=pxGraficos,
        title="KM Rodado por Cidade",
        color=variables_data.Desc_Cidade,
        color_discrete_sequence=[
            "#cce5ff",
            "#99ccff",
            "#66b2ff",
            "#3385ff",
            "#0066cc",
            "#003f5c",
        ],
        orientation="h",
        log_x=True,
    )

    figDash5.update_layout(testTemplate)
    entrega = df_resumo[[variables_data.Desc_Placa, variables_data.Num_Entregas]]
    entrega = entrega.groupby(variables_data.Desc_Placa).sum().reset_index()
    entrega = entrega[entrega[variables_data.Num_Entregas] != 0]

    figDash6 = px.bar(
        entrega,
        x=variables_data.Num_Entregas,
        y=variables_data.Desc_Placa,
        orientation="h",
        height=pxGraficos,
        title="Entregas por Veículo",
        color_discrete_sequence=[
            "#cce5ff",
            "#99ccff",
            "#66b2ff",
            "#3385ff",
            "#0066cc",
            "#003f5c",
        ],
        text=variables_data.Num_Entregas,
    )

    figDash6.update_layout(
        testTemplate,
        xaxis_title="Quantidade de Entregas",
        yaxis_title="Veículo (Placa)",
        hovermode="y unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0),
        showlegend=True,
    )

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=figDash1),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id="btn-det-fig1",
                                        class_name="botao-detalhes rounded",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=figDash2),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id="btn-det-fig2",
                                        class_name="botao-detalhes rounded",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=8,
                    ),
                ],
                class_name="mt-0 g-1",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=figDash3),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id="btn-det-fig3",
                                        class_name="botao-detalhes rounded",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=figDash4),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id="btn-det-fig4",
                                        class_name="botao-detalhes rounded",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=8,
                    ),
                ],
                class_name="mt-0 g-1",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=figDash5),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id="btn-det-fig5",
                                        class_name="botao-detalhes rounded",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=figDash6),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id="btn-det-fig6",
                                        class_name="botao-detalhes rounded",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=8,
                    ),
                ],
                class_name="mt-0 g-1",
            ),
        ]
    )
