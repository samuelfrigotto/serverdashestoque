from app import app
from app import session_dataframes_cta_express as sessionDF
from dash import Input, Output, State, dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from assets.static import packCode, Colors, Graphcs
from stylesDocs.style import styleConfig
import plotly.graph_objects as go
from pages.cta_express.cta_express_globals import variables_data
from pages.cta_express.resumo import utils
from utils import conversores


pageTag: str = "CEresumo_"
styleColors = styleConfig(Colors.themecolor)
pxGraficos = Graphcs.pxGraficos
globalTemplate = Graphcs.globalTemplate


@app.callback(
    Output(f"{pageTag}header", "children"),
    Output(f"{pageTag}body", "children"),
    Input(f"{pageTag}update", "data"),
    State("session_data", "data"),
)
def showHeader(initData, session_data):
    session_id = session_data.get("session_id", "")

    if initData == 1 and session_id:
        df_detalhamento: pd.DataFrame = sessionDF[f"{session_id}_detalhamento"]
        df_entregas_unicas = df_detalhamento.drop_duplicates(
            subset=[variables_data.Guid_Carga, variables_data.Cod_Cliente]
        )
        metricsDict: dict = {
            "Nº Entregas": {
                "icone": "bi bi-truck",
                "valor": conversores.MetricInteiroValores(df_entregas_unicas.shape[0]),
            },
            "Nº NFe's Entregues": {
                "icone": "bi bi-receipt-cutoff",
                "valor": conversores.MetricInteiroValores(
                    df_detalhamento[variables_data.Num_NFE].unique().size
                ),
            },
            "Cubagem Entregue": {
                "icone": "bi bi-box",
                "valor": conversores.MetricInteiroValores(
                    df_detalhamento[variables_data.Valor_Cubagem].sum()
                ),
            },
            "Valor Total": {
                "icone": "bi bi-cash-stack",
                "valor": conversores.MetricInteiroValores(
                    df_detalhamento[variables_data.Valor_Venda].sum()
                ),
            },
        }
        return packCode.HeaderDash(
            "CTA Express",
            f"Período de análise: {pd.to_datetime(df_detalhamento[variables_data.DT_Emissao]).min().strftime('%d/%m/%Y')} a {pd.to_datetime(df_detalhamento[variables_data.DT_Emissao]).max().strftime('%d/%m/%Y')}",
            pageTag=pageTag,
            lstMetric=metricsDict,
            MetricsWidth=8,
        ), loadCharts(session_id)


@app.callback(
    Output(f"{pageTag}update", "data"),
    State(f"{pageTag}update", "data"),
    Input("session_data", "data"),
)
def initOperacoes(upData, session_data):
    return 1


def fig1(df_resumo):
    dfentregas = (
        df_resumo.groupby([variables_data.Desc_Motorista])
        .agg({variables_data.Valor_Cubagem: "sum", variables_data.Num_Entregas: "sum"})
        .reset_index()
    )
    dfentregas["Entregas"] = dfentregas[variables_data.Num_Entregas].apply(
        conversores.moedaCorrente
    )
    if len(dfentregas[variables_data.Desc_Motorista]) > 7:
        figDash1 = px.bar(
            dfentregas,
            color_discrete_sequence=globalTemplate["colorway"],
            x=variables_data.Desc_Motorista,
            y=variables_data.Num_Entregas,
            title="Número de entregas por motorista",
            labels={
                variables_data.Desc_Motorista: "Motorista",
                variables_data.Num_Entregas: "Entregas",
            },
            height=pxGraficos,
        )
        figDash1.update_layout(globalTemplate)
        media_valor = dfentregas[variables_data.Num_Entregas].mean()
        media_venda = conversores.MetricInteiroValores(media_valor)
        figDash1.add_shape(
            type="line",
            x0=-0.5,
            y0=media_valor,
            x1=len(dfentregas) - 0.5,
            y1=media_valor,
            line=dict(color="red", dash="dot"),
        )

        figDash1.add_annotation(
            x=len(dfentregas) - 0.5,
            y=media_valor,
            text=f"Média: {media_venda}",
            showarrow=False,
            font=dict(color="red"),
            xanchor="left",
        )
    else:
        figDash1 = px.pie(
            dfentregas,
            names=variables_data.Desc_Motorista,
            values=variables_data.Num_Entregas,
            title="Número de entregas por motorista",
            height=pxGraficos,
            labels={
                variables_data.Desc_Motorista: "Motorista",
                variables_data.Num_Entregas: "Entregas",
            },
            hole=0.2,
            color_discrete_sequence=Colors.DEFAULT_COLORS,
        )
        figDash1.update_layout(globalTemplate)
        figDash1.update_traces(
            pull=[0.05] * len(dfentregas),
            textinfo="percent+label",
            textposition="outside",
        )
        figDash1.update_layout(
            showlegend=False,
        )

    return {"fig": figDash1, "dataframe": dfentregas}


def fig2(df_resumo):
    dfcubagem = df_resumo[[variables_data.Valor_Cubagem, variables_data.Desc_Placa]]
    dfcubagem = (
        dfcubagem.groupby(variables_data.Desc_Placa)[variables_data.Valor_Cubagem]
        .sum()
        .reset_index()
    )
    dfcubagem = dfcubagem[dfcubagem[variables_data.Valor_Cubagem] > 0]
    dfcubagem["Cubos"] = dfcubagem[variables_data.Valor_Cubagem].apply(
        conversores.outrosValores
    )

    figDash2 = px.bar(
        dfcubagem,
        title="Cubagem por Veículo",
        color_discrete_sequence=globalTemplate["colorway"],
        x=variables_data.Desc_Placa,
        y=variables_data.Valor_Cubagem,
        height=pxGraficos,
        labels={
            variables_data.Desc_Placa: "Placa do Veículo",
            variables_data.Valor_Cubagem: "Cubagem",
        },
        hover_data={
            "Cubos": True,
            variables_data.Valor_Cubagem: False,
            variables_data.Desc_Placa: True,
        },
    )
    figDash2.update_traces()
    figDash2.update_layout(globalTemplate)
    media_valor = dfcubagem[variables_data.Valor_Cubagem].mean()
    media_venda = conversores.MetricOutrosValores(media_valor)
    figDash2.add_shape(
        type="line",
        x0=-0.5,
        y0=media_valor,
        x1=len(dfcubagem) - 0.5,
        y1=media_valor,
        line=dict(color="red", dash="dot"),
    )

    figDash2.add_annotation(
        x=len(dfcubagem) - 0.5,
        y=media_valor,
        text=f"Média: {media_venda}",
        showarrow=False,
        font=dict(color="red"),
        xanchor="left",
    )

    return figDash2


def fig3(df_resumo):

    dfvlr = df_resumo[
        [variables_data.Desc_Motorista, variables_data.Valor_Venda]
    ].copy()

    dfvlr = dfvlr.groupby([variables_data.Desc_Motorista]).sum().reset_index()
    # dfvlr = dfvlr.sort_values(by=variables_data.Valor_Venda, ascending=True)

    dfvlr["Valor"] = dfvlr[variables_data.Valor_Venda].apply(conversores.moedaCorrente)

    figDash3 = px.bar(
        dfvlr,
        color_discrete_sequence=globalTemplate["colorway"],
        x=variables_data.Desc_Motorista,
        y=variables_data.Valor_Venda,
        title="Valor (R$) total por motorista",
        height=pxGraficos,
        labels={
            variables_data.Desc_Motorista: "Motorista",
            variables_data.Valor_Venda: "Valor (R$)",
        },
        hover_data={
            "Valor": True,
            variables_data.Valor_Venda: False,
            variables_data.Desc_Motorista: True,
        },
    )

    figDash3.update_traces(
        textfont=dict(size=12),
        marker_line=dict(width=0),
        marker=dict(line=dict(width=1)),
    )
    figDash3.update_layout(globalTemplate)
    media_valor = dfvlr[variables_data.Valor_Venda].mean()
    media_venda = conversores.moedaCorrente(media_valor)

    figDash3.add_shape(
        type="line",
        x0=-0.5,
        y0=media_valor,
        x1=len(dfvlr) - 0.5,
        y1=media_valor,
        line=dict(color="red", dash="dot"),
    )

    figDash3.add_annotation(
        x=len(dfvlr) - 0.5,
        y=media_valor,
        text=f"Média: {media_venda}",
        showarrow=False,
        font=dict(color="red"),
        xanchor="left",
    )
    return figDash3


def fig4(df_resumo):

    dfkm = df_resumo[
        [
            variables_data.Num_KM_Rodado,
            variables_data.Desc_Placa,
            variables_data.Desc_Motorista,
        ]
    ]
    dfkm = (
        dfkm.groupby([variables_data.Desc_Placa])[variables_data.Num_KM_Rodado]
        .sum()
        .reset_index()
    )
    dfkm = dfkm[dfkm[variables_data.Num_KM_Rodado] > 0]
    dfkm = dfkm.sort_values(by=variables_data.Num_KM_Rodado, ascending=True)
    dfkm["Quilometros"] = dfkm[variables_data.Num_KM_Rodado].apply(
        conversores.outrosValores
    )

    figDash4 = px.bar(
        dfkm,
        color_discrete_sequence=globalTemplate["colorway"],
        x=variables_data.Desc_Placa,
        y=variables_data.Num_KM_Rodado,
        title="Km por Placa de Veículo",
        height=pxGraficos,
        labels={
            variables_data.Desc_Placa: "Placa",
            variables_data.Num_KM_Rodado: "Km",
        },
        hover_data={
            "Quilometros": True,
            variables_data.Desc_Placa: True,
            variables_data.Num_KM_Rodado: False,
        },
    )

    figDash4.update_layout(
        globalTemplate,
        showlegend=False,
    )
    return figDash4


def fig5(df_resumo):
    dftempo = df_resumo[
        [
            variables_data.Desc_Motorista,
            variables_data.TEMPO_Translado,
            variables_data.TEMPO_Atendimento,
            variables_data.TEMPO_Ocioso,
            variables_data.TEMPO_AteNegativado,
        ]
    ]
    col_name = {
        variables_data.Desc_Motorista: "Motorista",
        variables_data.TEMPO_Translado: "Translado",
        variables_data.TEMPO_Atendimento: "Atendimento",
        variables_data.TEMPO_Ocioso: "Pausa",
        variables_data.TEMPO_AteNegativado: "Negativado",
    }

    dftempo = dftempo.groupby([variables_data.Desc_Motorista]).sum().reset_index()
    colunas_tempo = [
        variables_data.TEMPO_Translado,
        variables_data.TEMPO_Atendimento,
        variables_data.TEMPO_Ocioso,
        variables_data.TEMPO_AteNegativado,
    ]

    dftempo[colunas_tempo] = dftempo[colunas_tempo].div(60)

    dftempo = dftempo[~(dftempo[colunas_tempo].sum(axis=1) == 0)]

    my_colors = ["#FF8A08", "#EB5B00", "#FFE31A", "#FF0000"]

    figDash5 = go.Figure()

    for i, coluna in enumerate(
        [
            variables_data.TEMPO_Translado,
            variables_data.TEMPO_Atendimento,
            variables_data.TEMPO_Ocioso,
            variables_data.TEMPO_AteNegativado,
        ]
    ):
        figDash5.add_trace(
            go.Scatter(
                x=dftempo[variables_data.Desc_Motorista],
                y=dftempo[coluna],
                mode="lines+markers",
                name=col_name.get(coluna, coluna),
                line=dict(color=my_colors[i], width=2),
                marker=dict(size=8),
                line_shape="spline",
                hovertemplate=(
                    "<b>Motorista:</b> %{x}<br>"
                    "<b>{label}:</b> %{y:.2f} horas<br>"
                    "<extra></extra>"
                ).replace("{label}", col_name.get(coluna, coluna)),
            )
        )
    figDash5.update_layout(globalTemplate)
    figDash5.update_layout(
        title="Distribuição de Horas por Motorista",
        xaxis_title="Motorista",
        yaxis_title="Horas",
        height=500,
        legend=dict(title="Descrição"),
    )
    return figDash5


def fig6(df_detalhamento):
    dfto = df_detalhamento[
        [
            variables_data.Desc_Cidade,
            variables_data.TP_Desc_Operacao,
            variables_data.Valor_Venda,
        ]
    ].copy()

    dfto = (
        dfto.groupby([variables_data.Desc_Cidade, variables_data.TP_Desc_Operacao])[
            variables_data.Valor_Venda
        ]
        .sum()
        .reset_index()
    )

    total_venda = dfto.groupby(variables_data.Desc_Cidade)[
        variables_data.Valor_Venda
    ].transform("sum")
    dfto["percent"] = (dfto[variables_data.Valor_Venda] / total_venda) * 100
    dfto["percent_text"] = dfto["percent"].apply(lambda x: f"{x:.2f}%")
    dfto[variables_data.TP_Desc_Operacao] = pd.Categorical(
        dfto[variables_data.TP_Desc_Operacao],
        categories=["VENDA", "BONIFICACAO"],
        ordered=True,
    )

    dfto["Valor"] = dfto[variables_data.Valor_Venda].apply(conversores.moedaCorrente)
    dfto = dfto.groupby(variables_data.TP_Desc_Operacao, group_keys=False).apply(
        lambda df: df.sort_values(by=variables_data.Desc_Cidade)
    )

    ordered_cities = sorted(dfto[variables_data.Desc_Cidade].unique())

    figDash6 = px.line(
        dfto,
        x=variables_data.Desc_Cidade,
        y=variables_data.Valor_Venda,
        title="Vendas por Cidade",
        color=variables_data.TP_Desc_Operacao,
        log_y=True,
        height=pxGraficos,
        labels={
            variables_data.TP_Desc_Operacao: "Tipo de Operação",
            "BONIFICACAO": "BONIFICAÇÃO",
            "VENDA": "VENDA",
            variables_data.Desc_Cidade: "Cidade",
            variables_data.Valor_Venda: "Valor da Venda",
        },
        color_discrete_map={
            "BONIFICACAO": "#FF0000",
            "VENDA": "#06D001",
        },
        hover_data={
            "Valor": True,
            variables_data.Valor_Venda: False,
            variables_data.TP_Desc_Operacao: False,
            variables_data.Desc_Cidade: True,
        },
        markers=True,
        line_shape="spline",
        category_orders={variables_data.Desc_Cidade: ordered_cities},
    )

    figDash6.update_traces(
        mode="markers+lines",
        text=dfto["percent_text"],
        textposition="top center",
        # fill="tonexty",
        # opacity=0.3,
    )

    figDash6.update_layout(
        globalTemplate,
        showlegend=True,
    )
    return figDash6


def fig7(df_detalhamento: pd.DataFrame):
    try:
        dfmapa = df_detalhamento[
            [
                variables_data.Desc_Cidade,
                variables_data.cliente_lat,
                variables_data.cliente_log,
                variables_data.Valor_Venda,
                variables_data.Desc_Cliente,
                variables_data.Valor_Cubagem,
            ]
        ].copy()

        dfmapa = dfmapa[
            (dfmapa[variables_data.cliente_lat] != 0)
            & (dfmapa[variables_data.cliente_log] != 0)
        ]
        dfmapa[variables_data.cliente_lat] = pd.to_numeric(
            dfmapa[variables_data.cliente_lat], errors="coerce"
        )
        dfmapa[variables_data.cliente_log] = pd.to_numeric(
            dfmapa[variables_data.cliente_log], errors="coerce"
        )
        dfmapa[variables_data.Valor_Venda] = pd.to_numeric(
            dfmapa[variables_data.Valor_Venda], errors="coerce"
        )

        dfmapa = dfmapa.dropna(
            subset=[
                variables_data.cliente_lat,
                variables_data.cliente_log,
                variables_data.Valor_Venda,
            ]
        )

        dfmapa["Valor"] = dfmapa[variables_data.Valor_Venda].apply(
            conversores.moedaCorrente
        )
        dfmapa["Cubagem"] = dfmapa[variables_data.Valor_Cubagem].apply(
            conversores.outrosValores
        )

        figDash7 = utils.create_choropleth_map(dfmapa)

    except Exception as e:
        print(f"Erro ao processar os dados: {e}")
        figDash7 = None
    return figDash7

def loadCharts(session_id: str) -> html.Div:
    df_resumo: pd.DataFrame = sessionDF[f"{session_id}_resumo"]
    df_detalhamento: pd.DataFrame = sessionDF[f"{session_id}_detalhamento"]
    df_resumo[variables_data.Desc_Motorista] = df_resumo[
        variables_data.Desc_Motorista
    ].apply(conversores.abreviar)
    df_detalhamento[variables_data.Desc_Cidade] = df_detalhamento[
        variables_data.Desc_Cidade
    ].apply(conversores.abreviar)

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=fig1(df_resumo)["fig"]),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig1",
                                        class_name="botao-detalhes rounded",
                                    ),
                                    packCode.detailModal(
                                        "Detalhes:",
                                        fig1(df_resumo)["fig"],
                                        fig1(df_resumo)["dataframe"],
                                        pageTag,
                                        "1",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=fig3(df_resumo)),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig3",
                                        class_name="botao-detalhes rounded",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=6,
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
                                    dcc.Graph(
                                        figure=fig7(df_detalhamento),
                                        config={"responsive": True},
                                        style={
                                            "height": "100%",
                                            "width": "100%",
                                            "minHeight": "500",
                                        },
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                                style={"minHeight": "508px"},
                            ),
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=fig5(df_resumo)),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig5",
                                        class_name="botao-detalhes rounded",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=6,
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
                                    dcc.Graph(figure=fig6(df_detalhamento)),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig6",
                                        class_name="botao-detalhes rounded",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=12,
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
                                    dcc.Graph(figure=fig4(df_resumo)),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig4",
                                        class_name="botao-detalhes rounded",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=fig2(df_resumo)),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig2",
                                        class_name="botao-detalhes rounded",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=6,
                    ),
                ],
                class_name="mt-0 g-1",
            ),
        ]
    )

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
for i in range(1, 7):
    create_modal_callback(i)
