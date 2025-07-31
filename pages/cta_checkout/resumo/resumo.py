from app import app
from app import session_dataframes_cta_checkout as sessionDF
from dash import Input, Output, State, dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc
from utils import conversores, read_file
import pandas as pd
from assets.static import packCode, Colors
from stylesDocs.style import styleConfig
import plotly.graph_objects as go

pageTag: str = "CCresumo_"
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
    "margin": {"l": 50, "r": 30, "t": 30, "b": 100},
}


@app.callback(
    Output(f"{pageTag}header", "children"),
    Output(f"{pageTag}body", "children"),
    Input(f"{pageTag}update", "data"),
    State("session_data", "data"),
)
def showHeader(initData, session_data):
    session_id = session_data.get("session_id", "")

    if initData == 1 and session_id:
        df_resumo = sessionDF[f"{session_id}_resumo"]
        df_detalhamento = sessionDF[f"{session_id}_detalhamento"]
        metricsDict: dict = {
            "Nº Entregas": {
                "icone": "bi bi-truck",
                "valor": conversores.inteiroValores(
                    conversores.ContagemDist(df_resumo, "NR_ENTREGAS")
                ),
            },
            "Cubagem Total": {
                "icone": "bi bi-box",
                "valor": conversores.inteiroValores(
                    conversores.outrosValores(df_resumo["CUBAGEM"].sum())
                ),
            },
            "Valor Total": {
                "icone": "bi bi-cash-stack",
                "valor": conversores.inteiroValores(
                    conversores.moedaCorrenteInteiro(df_detalhamento["VL_VENDA"].sum())
                ),
            },
            "KM Rodado": {
                "icone": None,
                "valor": conversores.inteiroValores(
                    conversores.inteiroValores(df_resumo["KM_RODADO"].sum())
                ),
            },
            "Tempo total": {
                "icone": "bi bi-stopwatch",
                "valor": conversores.Formatar_hora(
                    df_resumo["TP_TRANSLADO"].sum()
                    + df_resumo["TP_ATENDIMENTO"].sum()
                    + df_resumo["TP_OCIOSO"].sum()
                    + df_resumo["TP_ATENEGATIVADO"].sum()
                ),
            },
        }

        # "CTA Express - Resumo", pageTag, metricsDict, False
        return packCode.HeaderDash(
            title="CTA CHECKOUT",
            Descricao="Resumo",
            pageTag=pageTag,
            lstMetric=metricsDict,
        ), loadCharts(session_id)


@app.callback(
    Output(f"{pageTag}update", "data"),
    State(f"{pageTag}update", "data"),
    Input("session_data", "data"),
)
def initOperacoes(upData, session_data):
    session_id = session_data.get("session_id", "")
    if f"{session_id}_resumo" not in sessionDF:
        sessionDF[f"{session_id}_resumo"] = read_file.read_json("resumo.json")
    if f"{session_id}_detalhamento" not in sessionDF:
        sessionDF[f"{session_id}_detalhamento"] = read_file.read_json(
            "detalhamento.json"
        )
    return 1


def loadCharts(session_id: str) -> html.Div:
    df_resumo = sessionDF[f"{session_id}_resumo"]
    df_detalhamento = sessionDF[f"{session_id}_detalhamento"]
    pxGraficos = 350

    dfentregas = df_resumo[["M_DESCRICAO", "NR_ENTREGAS"]]
    dfentregas = dfentregas.groupby(["M_DESCRICAO"]).sum().reset_index()
    figDash1 = px.bar(
        dfentregas,
        x="M_DESCRICAO",
        y="NR_ENTREGAS",
        height=pxGraficos,
        title="Nº Entregas por motorista",
    )
    figDash1.update_layout(testTemplate)

    valor_atual= conversores.inteiroValores(
                    df_resumo["CUBAGEM"].sum())
    limite_min = 40000
    limite_max = 150000
    figDash2 = go.Figure(
        go.Indicator(
        mode="gauge+number",  # Mostra o medidor e o número
        value=valor_atual,  # Valor a ser exibido
        title={"text": "Progresso"},  # Título do medidor
        gauge={
            "axis": {"range": [limite_min, limite_max]},  # Intervalo do medidor
            "bar": {"color": "blue"},  # Cor da barra de progresso
            "steps": [
                {"range": [0, 70000], "color": "red"},  # Intervalo 0-50 em vermelho
                {"range": [70000, 120000], "color": "yellow"},  # Intervalo 50-75 em amarelo
                {"range": [120000, 150000], "color": "green"},  # Intervalo 75-100 em verde
            ],
            "threshold": {
                "line": {"color": "blue", "width": 4},  # Linha de destaque
                "thickness": 0.75,
                "value": 85,  # Valor que marca o limite de destaque
            },
        },
    )
)


    figDash2.update_layout(
    height=400,  # Altura do gráfico
    title=dict(
        text="Meta Cubagem",  # Título geral do gráfico
        font=dict(size=20),  # Tamanho da fonte do título
        x=0.5  # Centraliza o título
    ),
)
    figDash2.update_layout()



    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=figDash1),
                                    
                                ],
                                class_name="shadow-sm p-1 rounded",
                            )
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=figDash2),
                                    
                                ],
                                class_name="shadow-sm p-1 rounded",
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
                                    dcc.Graph(figure=figDash3),
                                    
                                ],
                                class_name="shadow-sm p-1 rounded",
                            )
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=figDash4),
                                    
                                ],
                                class_name="shadow-sm p-1 rounded",
                            )
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=figDash5),
                                    
                                ],
                                class_name="shadow-sm p-1 rounded",
                            )
                        ),
                        width=4,
                    ),
                ],
                class_name="mt-0 g-1",
            ),
        ]
    )
