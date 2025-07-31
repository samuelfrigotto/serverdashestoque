import pandas as pd
from app import app
from app import session_dataframes_cta_express as sessionDF
from dash import Input, Output, State, dcc, dash, html, callback_context
from assets.static import packCode, Colors, supportClass, Graphcs
from pages.cta_express.cta_express_globals import variables_data
import dash_bootstrap_components as dbc
from utils import conversores
import plotly.express as px
import plotly.graph_objects as go
from stylesDocs.style import styleConfig
import locale

pageTag: str = "CEcubagem_"
styleColors = styleConfig(Colors.themecolor)
globalTemplate = Graphcs.globalTemplate

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
        df_resumo: pd.DataFrame = sessionDF[f"{session_id}_resumo"]
        df_detalhamento: pd.DataFrame = sessionDF[f"{session_id}_detalhamento"]
        df_entregas_unicas = (
            df_detalhamento.groupby(variables_data.Guid_Carga)[
                variables_data.Cod_Cliente
            ]
            .nunique()
            .reset_index()
        )
        df_entregas_unicas = df_entregas_unicas[variables_data.Cod_Cliente].sum()

        metricsDict: dict = {
            "Nº Entregas": {
                "icone": "bi bi-truck",
                "valor": conversores.MetricInteiroValores(df_entregas_unicas),
            },
            "Cubagem Total": {
                "icone": "bi bi-box",
                "valor": conversores.MetricInteiroValores(
                    df_resumo[variables_data.Valor_Cubagem].sum()
                ),
            },
            "Valor Total": {
                "icone": "bi bi-cash-stack",
                "valor": conversores.MetricInteiroValores(
                    df_detalhamento[variables_data.Valor_Venda].sum()
                ),
            },
            "Notas Fiscais": {
                "icone": "bi bi-receipt-cutoff",
                "valor": conversores.inteiroValores(
                    df_detalhamento[variables_data.Num_NFE].unique().size
                ),
            },
        }

        filters: dict = {
            f"{pageTag}fil_cidade": {
                "distValue": df_detalhamento[variables_data.Desc_Cidade].unique(),
                "labelName": f"{pageTag}Cidade",
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
                "distValue": df_detalhamento[variables_data.Desc_Placa].unique(),
                "labelName": "Placa",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_supervisor": {
                "distValue": df_detalhamento[variables_data.Desc_Supervisor].unique(),
                "labelName": "Supervisor",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_vendedor": {
                "distValue": df_detalhamento[variables_data.Desc_Vendedor].unique(),
                "labelName": "Vendedor",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_grupo": {
                "distValue": df_detalhamento[variables_data.Desc_Grupo].unique(),
                "labelName": "Grupo",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_sku": {
                "distValue": df_detalhamento[variables_data.Desc_Cod_Produto].unique(),
                "labelName": "Produto",
                "valueDefault": "Todos",
            },
        }
        return packCode.HeaderDash(
            "Cubagem",
            f"Período de análise: {pd.to_datetime(df_detalhamento[variables_data.DT_Emissao]).min().strftime('%d/%m/%Y')} a {pd.to_datetime(df_detalhamento[variables_data.DT_Emissao]).max().strftime('%d/%m/%Y')}",
            pageTag,
            metricsDict,
            True,
            filters,
            4,
            7,
        )

@app.callback(
    [Output(f"{pageTag}body", "children"), Output(f"{pageTag}metrics", "children")],
    [
        Input(f"{pageTag}fil_cidade", "value"),
        Input(f"{pageTag}fil_rota", "value"),
        Input(f"{pageTag}fil_bairro", "value"),
        Input(f"{pageTag}fil_motorista", "value"),
        Input(f"{pageTag}fil_supervisor", "value"),
        Input(f"{pageTag}fil_vendedor", "value"),
        Input(f"{pageTag}fil_grupo", "value"),
        Input(f"{pageTag}fil_sku", "value"),
        Input(f"{pageTag}fil_placa", "value"),
    ],
    State("session_data", "data"),
)
def showBody(
    fil_cidade,
    fil_rota,
    fil_bairro,
    fil_motorista,
    fil_supervisor,
    fil_vendedor,
    fil_grupo,
    fil_sku,
    fil_placa,
    session_data,
):
    session_id = session_data.get("session_id", "")

    df_detalhamento: pd.DataFrame = sessionDF[f"{session_id}_detalhamento"]

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
    if "Todos" not in fil_supervisor and len(fil_supervisor) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento,
            tabela=variables_data.Desc_Supervisor,
            filtro=fil_supervisor,
        )
    if "Todos" not in fil_vendedor and len(fil_vendedor) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=variables_data.Desc_Vendedor, filtro=fil_vendedor
        )
    if "Todos" not in fil_grupo and len(fil_grupo) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=variables_data.Desc_Grupo, filtro=fil_grupo
        )
    if "Todos" not in fil_sku and len(fil_sku) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=variables_data.Desc_Cod_Produto, filtro=fil_sku
        )
    if "Todos" not in fil_placa and len(fil_placa) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=variables_data.Desc_Placa, filtro=fil_placa
        )

    df_entregas_unicas = (
        df_detalhamento.groupby(variables_data.Guid_Carga)[variables_data.Cod_Cliente]
        .nunique()
        .reset_index()
    )
    df_entregas_unicas = df_entregas_unicas[variables_data.Cod_Cliente].sum()
    metricsDict: dict = {
        "Nº Entregas": {
            "icone": "bi bi-truck",
            "valor": conversores.MetricInteiroValores(df_entregas_unicas),
        },
        "Cubagem Total": {
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
        "Notas Fiscais": {
            "icone": "bi bi-receipt-cutoff",
            "valor": conversores.inteiroValores(
                df_detalhamento[variables_data.Num_NFE].unique().size
            ),
        },
    }

    return loadCharts(df_detalhamento), supportClass.dictHeaderDash(
        pageTag, metricsDict
    )

@app.callback(
    Output(f"{pageTag}update", "data"),
    State(f"{pageTag}update", "data"),
    Input("session_data", "data"),
)
def initOperacoes(upData, session_data):
    return 1

def fig1(df_detalhamento: pd.DataFrame):
    df_top20 = df_detalhamento[
        [variables_data.Valor_Cubagem, variables_data.Desc_Cod_Cliente]
    ]
    df_top20 = (
        df_top20.groupby(variables_data.Desc_Cod_Cliente)[variables_data.Valor_Cubagem]
        .sum()
        .reset_index()
    )
    df_top20 = df_top20.sort_values(
        by=variables_data.Valor_Cubagem, ascending=False
    ).head(20)
    df_top20 = df_top20.sort_values(by=variables_data.Valor_Cubagem, ascending=True)

    df_top20["Cubagem"] = df_top20[variables_data.Valor_Cubagem].apply(
        conversores.outrosValores
    )

    figDash1 = px.bar(
        df_top20,
        height=816,
        x=variables_data.Valor_Cubagem,
        y=variables_data.Desc_Cod_Cliente,
        title="Top 20 Clientes por Cubagem",
        labels={
            variables_data.Desc_Cod_Cliente: "Cliente",
            variables_data.Valor_Cubagem: "Cubagem Total",
        },
        text="Cubagem",
        orientation="h",
        color=variables_data.Valor_Cubagem,
        color_continuous_scale=Colors.ORANGE_COLORS,
        hover_data={
            variables_data.Valor_Cubagem: False,
            "Cubagem": True,
        },
    )

    figDash1.update_traces(text=None)

    figDash1.update_layout(globalTemplate)
    figDash1.update_layout(
        {
            "xaxis": {
                "gridcolor": styleColors.border_color,
            },
            "yaxis": {
                "gridcolor": styleColors.back_pri_color,
            },
        }
    )

    return figDash1, df_top20


def fig2(df_detalhamento: pd.DataFrame):
    cubagem_mot = (
        df_detalhamento.groupby(variables_data.Desc_Motorista)
        .agg(
            {
                variables_data.Valor_Cubagem: "sum",
                variables_data.Valor_Cubagem_Devolvida: "sum",
            }
        )
        .reset_index()
    )

    cubagem_mot["CUBAGEM_EFETIVA"] = (
        cubagem_mot[variables_data.Valor_Cubagem]
        - cubagem_mot[variables_data.Valor_Cubagem_Devolvida]
    ).round()

    cubagem_mot["Cubagem"] = cubagem_mot["CUBAGEM_EFETIVA"].apply(
        conversores.outrosValores
    )

    if len(cubagem_mot[variables_data.Desc_Motorista]) > 7:
        figDash2 = px.bar(
            cubagem_mot,
            color_discrete_sequence=globalTemplate["colorway"],
            x=variables_data.Desc_Motorista,
            y="CUBAGEM_EFETIVA",
            title="Cubagem Efetiva por Motorista",
            labels={
                variables_data.Desc_Motorista: "Motorista",
                "CUBAGEM_EFETIVA": "Cubagem Efetiva",
            },
            height=400,
            hover_data={
                "CUBAGEM_EFETIVA": False,
                "Cubagem": True,
            },
        )

        figDash2.update_layout(globalTemplate)

        media_valor = cubagem_mot["CUBAGEM_EFETIVA"].mean()
        media_formatada = conversores.outrosValores(media_valor)

        figDash2.add_shape(
            type="line",
            x0=-0.5,
            y0=media_valor,
            x1=len(cubagem_mot) - 0.5,
            y1=media_valor,
            line=dict(color="red", dash="dot"),
        )

        figDash2.add_annotation(
            x=len(cubagem_mot) - 0.5,
            y=media_valor,
            text=f"Média: {media_formatada}",
            showarrow=False,
            font=dict(color="red"),
            xanchor="left",
        )

    else:
        color_sequence = Colors.DISTINCT_GRAPH_COLORS
        colors = (color_sequence * (len(cubagem_mot) // len(color_sequence) + 1))[: len(cubagem_mot)]

        figDash2 = go.Figure(
            data=[
                go.Pie(
                    labels=cubagem_mot[variables_data.Desc_Motorista],
                    values=cubagem_mot["CUBAGEM_EFETIVA"],
                    textfont=dict(size=10, color="black"),
                    sort=False,
                    direction="clockwise",
                    textposition="outside",
                    marker=dict(color_discrete_sequence=Colors.DEFAULT_COLORS),
                    textinfo="label+percent",
                    showlegend=False,
                )
            ]
        )

        figDash2.update_layout(globalTemplate)
        figDash2.update_layout(
            title="Cubagem Efetiva Motorista",
            height=400,
        )

    return figDash2, cubagem_mot


def fig3(df_detalhamento: pd.DataFrame):
    cub_devolvida = (
        df_detalhamento.groupby(variables_data.Desc_Motorista)
        .agg({variables_data.Valor_Cubagem_Devolvida: "sum"})
        .reset_index()
    )

    cub_devolvida["Cubagem"] = cub_devolvida[variables_data.Valor_Cubagem_Devolvida].apply(
        conversores.outrosValores
    )

    if len(cub_devolvida[variables_data.Desc_Motorista]) > 7:
        figDash3 = px.bar(
            cub_devolvida,
            color_discrete_sequence=globalTemplate["colorway"],
            x=variables_data.Desc_Motorista,
            y=variables_data.Valor_Cubagem_Devolvida,
            title="Cubagem Devolvida por Motorista",
            labels={
                variables_data.Desc_Motorista: "Motorista",
                variables_data.Valor_Cubagem_Devolvida: "Cubagem Devolvida",
            },
            height=400,
            hover_data={
                variables_data.Valor_Cubagem_Devolvida: False,
                "Cubagem": True,
            },
        )

        figDash3.update_layout(globalTemplate)

        media_valor = cub_devolvida[variables_data.Valor_Cubagem_Devolvida].mean()
        media_formatada = conversores.outrosValores(media_valor)

        figDash3.add_shape(
            type="line",
            x0=-0.5,
            y0=media_valor,
            x1=len(cub_devolvida) - 0.5,
            y1=media_valor,
            line=dict(color="red", dash="dot"),
        )

        figDash3.add_annotation(
            x=len(cub_devolvida) - 0.5,
            y=media_valor,
            text=f"Média: {media_formatada}",
            showarrow=False,
            font=dict(color="red"),
            xanchor="left",
        )

    else:
        color_sequence = Colors.DISTINCT_GRAPH_COLORS
        colors = (color_sequence * (len(cub_devolvida) // len(color_sequence) + 1))[: len(cub_devolvida)]

        figDash3 = go.Figure(
            data=[
                go.Pie(
                    labels=cub_devolvida[variables_data.Desc_Motorista],
                    values=cub_devolvida[variables_data.Valor_Cubagem_Devolvida],
                    textfont=dict(size=10, color="black"),
                    textposition="outside",
                    sort=False,
                    direction="clockwise",
                    marker=dict(colors=colors),
                    textinfo="label+percent",
                    showlegend=False,
                )
            ]
        )

        figDash3.update_layout(globalTemplate)
        figDash3.update_layout(
            title="Cubagem Devolvida por Motorista",
            height=400,
        )

    return figDash3, cub_devolvida


def fig4(df_detalhamento: pd.DataFrame):
    cubagem_efetiva = (
        df_detalhamento[variables_data.Valor_Cubagem].sum()
        - df_detalhamento[variables_data.Valor_Cubagem_Devolvida].sum()
    ).round()
    cubagem_devolvida = df_detalhamento[variables_data.Valor_Cubagem_Devolvida].sum()
    labels = ["Cubagem Devolvida", "Cubagem Efetiva",]
    values = [cubagem_devolvida, cubagem_efetiva]

    figDash4 = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            textinfo="label+percent",
            showlegend=False,
            sort=False,
            textposition="outside",
            direction="clockwise",
            textfont=dict(size=10, color="black"),
            marker=dict(colors=["#8B0000", Colors.colorGraphcs]),
        )
    )

    figDash4.update_layout(globalTemplate)

    figDash4.update_layout(
        title="Cubagem Efetiva",
        height=400,
    )
    return figDash4


def fig5(df_detalhamento: pd.DataFrame):
    df_detalhamento[variables_data.TP_TipoOperacao] = df_detalhamento[
        variables_data.TP_TipoOperacao
    ].replace({0: "Venda", 1: "Bonificação", 2: "Troca"})
    cubagem_por_tipo = (
        df_detalhamento.groupby(variables_data.TP_TipoOperacao)
        .agg({variables_data.Valor_Cubagem: "sum"})
        .reset_index()
    ).round()
    cubagem_por_tipo = cubagem_por_tipo.sort_values(
        by=variables_data.Valor_Cubagem, ascending=True
    )

    figDash5 = go.Figure(
        data=[
            go.Pie(
                labels=cubagem_por_tipo[variables_data.TP_TipoOperacao],
                values=cubagem_por_tipo[variables_data.Valor_Cubagem],
                hole=0.5,
                textinfo="label+percent",
                showlegend=False,
                sort=False,
                marker=dict(colors=["#8B0000", Colors.colorGraphcs, "#F2D600"]),
                textposition="outside",
                direction="clockwise",
                textfont=dict(size=10, color="black"),
            )
        ]
    )

    figDash5.update_layout(globalTemplate)

    figDash5.update_layout(
        title="Cubagem por Operação",
        height=400,
    )
    return figDash5


def fig6(df_detalhamento: pd.DataFrame):

    dfdevol = df_detalhamento[
        [variables_data.Desc_Motorista, variables_data.Valor_Cubagem_Devolvida]
    ]
    dfdevol = dfdevol.groupby([variables_data.Desc_Motorista]).sum().reset_index()
    dfdevol["Cubagem"] = dfdevol[variables_data.Valor_Cubagem_Devolvida].apply(
        conversores.outrosValores)
    figDash6 = px.bar(
        dfdevol,
        x=variables_data.Desc_Motorista,
        y=variables_data.Valor_Cubagem_Devolvida,
        title="Devolução por Motorista",
        color_discrete_sequence=globalTemplate["colorway"],
        labels={
            variables_data.Valor_Cubagem_Devolvida: "Cubagem Devolvida",
            variables_data.Desc_Motorista: "Motorista",
        },
        hover_data={
                variables_data.Valor_Cubagem_Devolvida: False,
                "Cubagem": True,
            },
    )
    figDash6.update_layout(globalTemplate)

    figDash6.update_traces()

    figDash6.update_layout(
        xaxis=dict(title="Motorista", tickangle=45, showgrid=False),
        yaxis=dict(title="Cubagem Devolvida", showgrid=True),
        showlegend=False,
    )
    media_valor = dfdevol[variables_data.Valor_Cubagem_Devolvida].mean()
    media_venda = conversores.MetricInteiroValores(media_valor)

    figDash6.add_shape(
        type="line",
        x0=-0.5,
        y0=media_valor,
        x1=len(dfdevol) - 0.5,
        y1=media_valor,
        line=dict(color="red", dash="dot"),
    )

    figDash6.add_annotation(
        x=len(dfdevol) - 0.5,
        y=media_valor,
        text=f"Média: {media_venda}",
        showarrow=False,
        font=dict(color="red"),
        xanchor="left",
    )
    return figDash6, dfdevol


def fig7(df_detalhamento: pd.DataFrame):
    dfdevol = df_detalhamento[
        [variables_data.Desc_Grupo, variables_data.Valor_Cubagem_Devolvida]
    ]
    dfdevol = dfdevol.groupby([variables_data.Desc_Grupo]).sum().reset_index()
    dfdevol = dfdevol[dfdevol[variables_data.Valor_Cubagem_Devolvida] > 1]
    dfdevol["Cubagem"] = dfdevol[variables_data.Valor_Cubagem_Devolvida].apply(
        conversores.outrosValores)
    figDash7 = px.bar(
        dfdevol,
        x=variables_data.Desc_Grupo,
        y=variables_data.Valor_Cubagem_Devolvida,
        title="Devolução por Grupo",
        labels={
            variables_data.Valor_Cubagem_Devolvida: "Cubagem Devolvida",
            variables_data.Desc_Grupo: "Grupo",
        },
        hover_data={
                variables_data.Valor_Cubagem_Devolvida: False,
                "Cubagem": True,
        },
        color_discrete_sequence=globalTemplate["colorway"],
    )

    figDash7.update_layout(globalTemplate)

    figDash7.update_traces()

    figDash7.update_layout(
        xaxis=dict(title="Grupo", tickangle=45, showgrid=False),
        yaxis=dict(title="Devolução Cubagem", showgrid=True),
        showlegend=False,
    )
    media_valor = dfdevol[variables_data.Valor_Cubagem_Devolvida].mean()
    media_venda = conversores.MetricInteiroValores(media_valor)

    figDash7.add_shape(
        type="line",
        x0=-0.5,
        y0=media_valor,
        x1=len(dfdevol) - 0.5,
        y1=media_valor,
        line=dict(color="red", dash="dot"),
    )

    figDash7.add_annotation(
        x=len(dfdevol) - 0.5,
        y=media_valor,
        text=f"Média: {media_venda}",
        showarrow=False,
        font=dict(color="red"),
        xanchor="left",
    )
    return figDash7, dfdevol


def fig8(df_detalhamento: pd.DataFrame):

    dfcubagem = df_detalhamento.groupby(
        [variables_data.Cod_Cliente, variables_data.Desc_Motorista]
    ).agg({variables_data.Valor_Cubagem: "sum", variables_data.Num_NFE: "nunique"})
    dfcubagem = dfcubagem.groupby([variables_data.Desc_Motorista]).sum().reset_index()
    dfcubagem["CUBAGEM_MEDIA"] = (
        dfcubagem[variables_data.Valor_Cubagem] / dfcubagem[variables_data.Num_NFE]
    )
    dfcubagem["Cubagem Média"] = dfcubagem["CUBAGEM_MEDIA"].apply(
        conversores.outrosValores)

    figDash8 = px.bar(
        dfcubagem,
        x=variables_data.Desc_Motorista,
        y="CUBAGEM_MEDIA",
        title="Cubagem Média por Entrega",
        labels={
            "CUBAGEM_MEDIA": "Cubagem Média",
            variables_data.Desc_Motorista: "Motorista",
        },
        hover_data={
                variables_data.Desc_Motorista: True,
                variables_data.Valor_Cubagem: False,
                "CUBAGEM_MEDIA": True,
                "Cubagem Média": False,
        },
        color_discrete_sequence=globalTemplate["colorway"],
    )

    figDash8.update_layout(globalTemplate)

    figDash8.update_traces()

    figDash8.update_layout(
        xaxis=dict(title="Motorista", tickangle=45, showgrid=False),
        yaxis=dict(title="Cubagem Média", showgrid=True),
        showlegend=False,
    )
    media_valor = dfcubagem["CUBAGEM_MEDIA"].mean()
    media_venda = conversores.MetricInteiroValores(media_valor)

    figDash8.add_shape(
        type="line",
        x0=-0.5,
        y0=media_valor,
        x1=len(dfcubagem) - 0.5,
        y1=media_valor,
        line=dict(color="red", dash="dot"),
    )

    figDash8.add_annotation(
        x=len(dfcubagem) - 0.5,
        y=media_valor,
        text=f"Média: {media_venda}",
        showarrow=False,
        font=dict(color="red"),
        xanchor="left",
    )
    return figDash8, dfcubagem


def fig9(df_detalhamento: pd.DataFrame):
    dfcubdev = df_detalhamento[
        [variables_data.Desc_Grupo, variables_data.Valor_Cubagem]
    ]
    dfcubdev = dfcubdev.groupby([variables_data.Desc_Grupo]).sum().reset_index()
    dfcubdev = dfcubdev.sort_values(by=variables_data.Desc_Grupo)
    dfcubdev = dfcubdev[dfcubdev[variables_data.Valor_Cubagem] > 1]
    dfcubdev["Cubagem"] = dfcubdev[
        variables_data.Valor_Cubagem
    ].apply(conversores.outrosValores)

    figDash9 = px.line(
        dfcubdev,
        x=variables_data.Desc_Grupo,
        y=variables_data.Valor_Cubagem,
        title="Cubagem por Grupo",
        labels={
            variables_data.Valor_Cubagem: "Cubagem Total",
            variables_data.Desc_Grupo: "Grupo",
        },
        hover_data={
            variables_data.Valor_Cubagem: False,
            "Cubagem": True,
            variables_data.Desc_Grupo: True,
        },
        markers=True,
        log_y=True,
        line_shape="spline",
        color_discrete_sequence=globalTemplate["colorway"],
    )

    figDash9.update_layout(globalTemplate)

    figDash9.update_traces(
        textposition="top center",
        textfont=dict(size=9, color="black"),
        line=dict(color=Graphcs.defaultColor, width=2),
        marker=dict(size=9, symbol="circle", color=Graphcs.defaultColor),
    )

    figDash9.update_layout(
        xaxis=dict(title="Grupos", tickangle=45, showgrid=False),
        yaxis=dict(title="Cubagem Total", showgrid=True),
    )
    return figDash9, dfcubdev


def fig10(df_detalhamento: pd.DataFrame):

    dfvlr = df_detalhamento[[variables_data.Desc_Cidade, variables_data.Valor_Cubagem]]
    dfvlr = dfvlr.groupby([variables_data.Desc_Cidade]).sum().reset_index()
    dfvlr["Cubagem Total"] = dfvlr[variables_data.Valor_Cubagem].apply(
        conversores.outrosValores
    )

    figDash10 = px.line(
        dfvlr,
        x=variables_data.Desc_Cidade,
        y=variables_data.Valor_Cubagem,
        title="Cubagem por cidade",
        labels={
            variables_data.Valor_Cubagem: "Cubagem Total",
            variables_data.Desc_Cidade: "Nome da Cidade",
        },
        hover_data={
            variables_data.Desc_Cidade: True,
            "Cubagem Total": False,
            variables_data.Valor_Cubagem: True,
        },
        markers=True,
        log_y=False,
        line_shape="spline",
    )

    figDash10.update_layout(globalTemplate)

    figDash10.update_traces(
        textposition="top center",
        textfont=dict(size=9, color="black"),
        line=dict(color=Graphcs.defaultColor, width=2),
        marker=dict(size=9, symbol="circle", color=Graphcs.defaultColor),
    )
    figDash10.update_layout(
        xaxis=dict(title="Cidade", showgrid=False),
        yaxis=dict(title="Cubagem Total", showgrid=True),
    )
    return figDash10, dfvlr


def fig11(df_detalhamento: pd.DataFrame):
    dfveic = df_detalhamento[[variables_data.Desc_Placa, variables_data.Valor_Cubagem]]
    dfveic = dfveic.groupby([variables_data.Desc_Placa]).sum().reset_index()
    dfveic["Cubagem Total"] = dfveic[variables_data.Valor_Cubagem].apply(
        conversores.outrosValores
    )

    figDash11 = px.line(
        dfveic,
        x=variables_data.Desc_Placa,
        y=variables_data.Valor_Cubagem,
        title="Cubagem por Veículo",
        labels={
            variables_data.Valor_Cubagem: "Cubagem Total",
            variables_data.Desc_Placa: "Placa do Veículo",
        },
        hover_data={
            variables_data.Desc_Placa: True,
            variables_data.Valor_Cubagem: True,
            "Cubagem Total": False,
        },
        markers=True,
        log_y=True,
        line_shape="spline",
    )

    figDash11.update_layout(globalTemplate)

    figDash11.update_traces(
        textposition="top center",
        textfont=dict(size=9, color="black"),
        line=dict(color=Graphcs.defaultColor, width=2),
        marker=dict(size=9, symbol="circle", color=Graphcs.defaultColor),
    )
    figDash11.update_layout(
        xaxis=dict(title="Veículo", showgrid=False),
        yaxis=dict(title="Cubagem Total", showgrid=True),
        height=400,
    )
    return figDash11, dfveic


def fig12(df_detalhamento: pd.DataFrame):
    Devol_Motivo = (
        df_detalhamento.groupby(variables_data.Desc_Motivo_Devolucao)
        .agg({variables_data.Valor_Cubagem_Devolvida: "sum"})
        .reset_index()
    )
    Devol_Motivo = Devol_Motivo[
        Devol_Motivo[variables_data.Valor_Cubagem_Devolvida] > 0
    ]
    Devol_Motivo["Cubagem Devolvida"] = Devol_Motivo[variables_data.Valor_Cubagem_Devolvida].apply(
        conversores.outrosValores)

    figDash12 = go.Figure(
        go.Pie(
            labels=Devol_Motivo[variables_data.Desc_Motivo_Devolucao],
            values=Devol_Motivo[variables_data.Valor_Cubagem_Devolvida],
            hole=0.5,
            textinfo="label+percent",
            customdata=Devol_Motivo["Cubagem Devolvida"],
            texttemplate="%{label}<br>%{percent}",
            hovertemplate="<b>%{label}</b><br>Cubagem Devolvida: %{customdata}<br>%{percent}",
            showlegend=False,
            marker=dict(colors=Colors.DISTINCT_GRAPH_COLORS),
            sort=False,
            textposition="outside",
            direction="clockwise",
            textfont=dict(size=10, color="black"),
        )
    )

    figDash12.update_layout(globalTemplate)

    figDash12.update_layout(
        title="Cubagem Devolvida por Motivo",
        height=400,
    )

    return figDash12, Devol_Motivo

def fig13(df_detalhamento: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:

    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

    cubagem_data = (
        df_detalhamento.groupby(variables_data.DT_Emissao)
        .agg({variables_data.Valor_Cubagem: "sum"})
        .reset_index()
    )

    cubagem_data[variables_data.DT_Emissao] = pd.to_datetime(
        cubagem_data[variables_data.DT_Emissao]
    )
    cubagem_data["Data"] = cubagem_data[
        variables_data.DT_Emissao
    ].dt.strftime("%d %B")

    cubagem_data["Cubagem"] = cubagem_data[
        variables_data.Valor_Cubagem
    ].apply(conversores.outrosValores)

    figDash13 = px.bar(
        cubagem_data,
        x="Data",
        y=variables_data.Valor_Cubagem,
        title="Quantidade de Cubagem por Dia",
        labels={
            variables_data.Valor_Cubagem: "Quantidade de Cubagem",
            "Data": "Data",
        },
        hover_data={
            "Cubagem": True,
            "Data": True,
            variables_data.Valor_Cubagem: False,
        },
        color_discrete_sequence=globalTemplate["colorway"],
    )

    figDash13.update_layout(globalTemplate)

    figDash13.update_traces(
        textposition="outside",
        textfont=dict(size=10, color="black"),
    )

    figDash13.update_layout(
        xaxis=dict(title="Data", showgrid=False),
        yaxis=dict(title="Quantidade de Cubagem", showgrid=True),
    )

    media_valor = cubagem_data[variables_data.Valor_Cubagem].mean()
    media_venda = conversores.MetricInteiroValores(media_valor)

    figDash13.add_shape(
        type="line",
        x0=-0.5,
        y0=media_valor,
        x1=len(cubagem_data) - 0.5,
        y1=media_valor,
        line=dict(color="red", dash="dot"),
    )

    figDash13.add_annotation(
        x=len(cubagem_data) - 0.5,
        y=media_valor,
        text=f"Média: {media_venda}",
        showarrow=False,
        font=dict(color="red"),
        xanchor="left",
    )

    return figDash13, cubagem_data

def loadCharts(df_detalhamento: pd.DataFrame) -> html.Div:
    df_detalhamento[variables_data.Desc_Motorista] = df_detalhamento[
        variables_data.Desc_Motorista
    ].apply(conversores.abreviar)
    df_detalhamento[variables_data.Desc_Grupo] = df_detalhamento[
        variables_data.Desc_Grupo
    ].apply(conversores.abreviar)
    df_detalhamento[variables_data.Desc_Cod_Cliente] = df_detalhamento[
        variables_data.Desc_Cod_Cliente
    ].apply(lambda x: conversores.abreviar(x, 20))

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=fig1(df_detalhamento)[0]),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig1",
                                        class_name="botao-detalhes rounded",
                                        n_clicks=0,
                                        target=f"modal-{pageTag}-det-fig1",
                                    ),
                                    packCode.detailModal(
                                        "Top 20 Clientes por cubagem",
                                        fig1(df_detalhamento)[0],
                                        fig1(df_detalhamento)[1],
                                        pageTag,
                                        "1",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=5,
                    ),
                    dbc.Col(
                        [
                            dbc.Row(
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardHeader(
                                            [
                                                dcc.Graph(
                                                    figure=fig2(df_detalhamento)[0]
                                                ),
                                                dbc.Button(
                                                    "Ver detalhes",
                                                    color="primary",
                                                    size="sm",
                                                    id=f"btn-{pageTag}-det-fig2",
                                                    class_name="botao-detalhes rounded",
                                                    n_clicks=0,
                                                    target=f"modal-{pageTag}-det-fig2",
                                                ),
                                                packCode.detailModal(
                                                    "Cubagem Efetiva por Motorista",
                                                    fig2(df_detalhamento)[0],
                                                    fig2(df_detalhamento)[1],
                                                    pageTag,
                                                    "2",
                                                ),
                                            ],
                                            class_name="shadow-sm p-1 card-com-hover",
                                        )
                                    )
                                ),
                                class_name="mb-1",
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardHeader(
                                            [
                                                dcc.Graph(
                                                    figure=fig3(df_detalhamento)[0]
                                                ),
                                                dbc.Button(
                                                    "Ver detalhes",
                                                    color="primary",
                                                    size="sm",
                                                    id=f"btn-{pageTag}-det-fig3",
                                                    class_name="botao-detalhes rounded",
                                                    n_clicks=0,
                                                    target=f"modal-{pageTag}-det-fig3",
                                                ),
                                                packCode.detailModal(
                                                    "Cubagem Devolvida por Motorista",
                                                    fig3(df_detalhamento)[0],
                                                    fig3(df_detalhamento)[1],
                                                    pageTag,
                                                    "3",
                                                ),
                                            ],
                                            class_name="shadow-sm p-1 card-com-hover",
                                        )
                                    )
                                )
                            ),
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Row(
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardHeader(
                                            [
                                                dcc.Graph(figure=fig5(df_detalhamento)),
                                            ],
                                            class_name="shadow-sm p-1 card-com-hover",
                                        )
                                    )
                                ),
                                class_name="mb-1",
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardHeader(
                                            [
                                                dcc.Graph(figure=fig4(df_detalhamento)),
                                            ],
                                            class_name="shadow-sm p-1 card-com-hover",
                                        )
                                    )
                                )
                            ),
                        ],
                        width=3,
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
                                    dcc.Graph(figure=fig6(df_detalhamento)[0]),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig6",
                                        class_name="botao-detalhes rounded",
                                        n_clicks=0,
                                        target=f"modal-{pageTag}-det-fig6",
                                    ),
                                    packCode.detailModal(
                                        "Devolução por Motorista",
                                        fig6(df_detalhamento)[0],
                                        fig6(df_detalhamento)[1],
                                        pageTag,
                                        "6",
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
                                    dcc.Graph(figure=fig7(df_detalhamento)[0]),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig7",
                                        class_name="botao-detalhes rounded",
                                        n_clicks=0,
                                        target=f"modal-{pageTag}-det-fig7",
                                    ),
                                    packCode.detailModal(
                                        "Devolução por Grupo",
                                        fig7(df_detalhamento)[0],
                                        fig7(df_detalhamento)[1],
                                        pageTag,
                                        "7",
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
                                    dcc.Graph(figure=fig8(df_detalhamento)[0]),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig8",
                                        class_name="botao-detalhes rounded",
                                        n_clicks=0,
                                        target=f"modal-{pageTag}-det-fig8",
                                    ),
                                    packCode.detailModal(
                                        "Cubagem Média por Entrega",
                                        fig8(df_detalhamento)[0],
                                        fig8(df_detalhamento)[1],
                                        pageTag,
                                        "8",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=4,
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
                                    dcc.Graph(figure=fig9(df_detalhamento)[0]),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig9",
                                        class_name="botao-detalhes rounded",
                                        n_clicks=0,
                                        target=f"modal-{pageTag}-det-fig9",
                                    ),
                                    packCode.detailModal(
                                        "Cubagem por Grupo",
                                        fig9(df_detalhamento)[0],
                                        fig9(df_detalhamento)[1],
                                        pageTag,
                                        "9",
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
                                    dcc.Graph(figure=fig10(df_detalhamento)[0]),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig10",
                                        class_name="botao-detalhes rounded",
                                        n_clicks=0,
                                        target="modal-{pageTag}-det-fig10",
                                    ),
                                    packCode.detailModal(
                                        "Cubagem por Cidade",
                                        fig10(df_detalhamento)[0],
                                        fig10(df_detalhamento)[1],
                                        pageTag,
                                        "10",
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
                                    dcc.Graph(figure=fig11(df_detalhamento)[0]),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig11",
                                        class_name="botao-detalhes rounded",
                                        n_clicks=0,
                                        target=f"modal-{pageTag}-det-fig11",
                                    ),
                                    packCode.detailModal(
                                        "Cubagem por Veículo",
                                        fig11(df_detalhamento)[0],
                                        fig11(df_detalhamento)[1],
                                        pageTag,
                                        "11",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=8,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardHeader(
                                [
                                    dcc.Graph(figure=fig12(df_detalhamento)[0]),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig12",
                                        class_name="botao-detalhes rounded",
                                        n_clicks=0,
                                        target=f"modal-{pageTag}-det-fig12",
                                    ),
                                    packCode.detailModal(
                                        "Cubagem Devolvida por Motivo",
                                        fig12(df_detalhamento)[0],
                                        fig12(df_detalhamento)[1],
                                        pageTag,
                                        "12",
                                    ),
                                ],
                                class_name="shadow-sm p-1 card-com-hover",
                            )
                        ),
                        width=4,
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
                                    dcc.Graph(figure=fig13(df_detalhamento)[0]),
                                    dbc.Button(
                                        "Ver detalhes",
                                        color="primary",
                                        size="sm",
                                        id=f"btn-{pageTag}-det-fig13",
                                        class_name="botao-detalhes rounded",
                                        n_clicks=0,
                                        target=f"modal-{pageTag}-det-fig13",
                                    ),
                                    packCode.detailModal(
                                        "Quantidade Cubagem por Dia",
                                        fig13(df_detalhamento)[0],
                                        fig13(df_detalhamento)[1],
                                        pageTag,
                                        "13",
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
for i in range(1, 14):
    create_modal_callback(i)
