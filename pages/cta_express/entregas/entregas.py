from app import app
import dash
from app import session_dataframes_cta_express as sessionDF
from dash import Input, Output, State, dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc
from utils import conversores, read_file
import pandas as pd
import plotly.graph_objects as go
from assets.static import packCode, Colors, supportClass
from stylesDocs.style import styleConfig
from pages.cta_express.cta_express_globals import variables_data
from assets.static import packCode, Colors, Graphcs
import locale


pageTag: str = "CEentregas_"
styleColors = styleConfig(Colors.themecolor)
pxGraficos = Graphcs.pxGraficos
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
                "distValue": df_detalhamento[variables_data.Desc_Produto].unique(),
                "labelName": "Produto",
                "valueDefault": "Todos",
            },
        }
        return packCode.HeaderDash(
            "Entregas",
            "Dashboard das entregas",
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
    df_resumo: pd.DataFrame = sessionDF[f"{session_id}_resumo"]
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
            df=df_detalhamento, tabela=variables_data.Desc_Produto, filtro=fil_sku
        )
    if "Todos" not in fil_placa and len(fil_placa) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=variables_data.Desc_Placa, filtro=fil_placa
        )

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

    return loadCharts(df_detalhamento, df_resumo), supportClass.dictHeaderDash(
        pageTag, metricsDict
    )


@app.callback(
    Output(f"{pageTag}update", "data"),
    State(f"{pageTag}update", "data"),
    Input("session_data", "data"),
)
def initOperacoes(upData, session_data):
    # session_id = session_data.get("session_id", "")
    # if f"{session_id}_resumo" not in sessionDF:
    #    sessionDF[f"{session_id}_resumo"] = read_file.read_json("resumo.json")
    # if f"{session_id}_detalhamento" not in sessionDF:
    #    sessionDF[f"{session_id}_detalhamento"] = read_file.read_json(
    #        "detalhamento.json"
    #    )
    return 1


def fig1(df_detalhamento: pd.DataFrame):
    entregas_unicas = df_detalhamento.drop_duplicates(
        subset=[variables_data.Guid_Carga, variables_data.Cod_Cliente]
    )

    top20_entregas = (
        entregas_unicas.groupby(
            [variables_data.Cod_Cliente, variables_data.Desc_Cod_Cliente]
        )[variables_data.Guid_Carga]
        .count()
        .reset_index()
    )

    top20_entregas = (
        top20_entregas.sort_values(by=variables_data.Guid_Carga, ascending=False)
        .head(20)
        .sort_values(by=variables_data.Guid_Carga, ascending=True)
    )
    top20_entregas["Entregas Totais"] = top20_entregas[variables_data.Guid_Carga].apply(
        conversores.outrosValores
    )

    figDash1 = px.bar(
        top20_entregas,
        x=variables_data.Guid_Carga,
        y=variables_data.Desc_Cod_Cliente,
        orientation="h",
        color=variables_data.Guid_Carga,
        color_continuous_scale=Colors.ORANGE_COLORS,
        title="Top 20 Clientes por Entregas",
        labels={
            variables_data.Desc_Cod_Cliente: "Cliente",
            variables_data.Guid_Carga: "Entregas Totais",
        },
        hover_data={
            variables_data.Cod_Cliente: False,
            variables_data.Guid_Carga: True,
        },
        height=816,
    )

    figDash1.update_layout(
        template=globalTemplate,
        title_font=dict(size=18),
        bargap=0.2,
        xaxis=dict(
            title="Entregas Totais",
            showgrid=True,
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            title="Clientes",
            showgrid=False,
            tickfont=dict(size=12),
        ),
    )

    return figDash1


def fig2(df_detalhamento: pd.DataFrame):
    entregas_mot = df_detalhamento.drop_duplicates(
        subset=[variables_data.Guid_Carga, variables_data.Cod_Cliente]
    )

    entregas_mot = (
        entregas_mot.groupby([variables_data.Desc_Motorista])[variables_data.Guid_Carga]
        .count()
        .reset_index()
    )

    entregas_mot["Entregas Totais"] = entregas_mot[variables_data.Guid_Carga].apply(
        conversores.outrosValores
    )

    figDash2 = px.bar(
        entregas_mot,
        x=variables_data.Desc_Motorista,
        y=variables_data.Guid_Carga,
        labels={
            variables_data.Desc_Motorista: "Motorista",
        },
        hover_data={
            "Entregas Totais": True,
            variables_data.Desc_Motorista: True,
            variables_data.Guid_Carga: False,
        },
        title="Entregas por Motorista",
    )

    figDash2.update_traces(
        marker_color="#FF9900",
        marker_line=dict(width=0),
    )

    figDash2.update_layout(
        template=globalTemplate,
        height=400,
        title_font=dict(size=18),
        margin=dict(l=50, r=20, t=70, b=50),
        xaxis_title="Motorista",
        yaxis_title="Quantidade de Entregas",
        showlegend=False,
    )

    return figDash2


def fig3(df_detalhamento: pd.DataFrame):
    entregas_cid = df_detalhamento.drop_duplicates(
        subset=[variables_data.Guid_Carga, variables_data.Cod_Cliente]
    )

    entregas_cid = (
        entregas_cid.groupby([variables_data.Desc_Cidade])[variables_data.Guid_Carga]
        .count()
        .reset_index()
        .sort_values(by=variables_data.Guid_Carga, ascending=True)
        .reset_index(drop=True)
    )
    entregas_cid["Entregas"] = entregas_cid[
        variables_data.Guid_Carga
    ].apply(conversores.outrosValores)

    figDash3 = px.bar(
        entregas_cid,
        x=variables_data.Guid_Carga,
        y=variables_data.Desc_Cidade,
        orientation="h",
        title="Entregas por Cidade",
        labels={
            variables_data.Desc_Cidade: "Cidade",
            variables_data.Guid_Carga: "Entregas",
        },
        hover_data={
            "Cidade": True,
            "Entregas": True,
        },
        color_discrete_sequence=globalTemplate["colorway"],
        height=400,
    )

    figDash3.update_traces(
        texttemplate="%{x}", textposition="outside", marker_line_width=0
    )

    figDash3.update_layout(
        globalTemplate,
        title_font=dict(size=18),
        margin=dict(l=20, r=20, t=70, b=40),
        xaxis_title="Quantidade de Entregas",
        yaxis_title="Cidade",
        showlegend=False,
    )

    return figDash3


def fig4(df_detalhamento: pd.DataFrame):
    entregas_prod = df_detalhamento.drop_duplicates(
        subset=[
            variables_data.Guid_Carga,
            variables_data.Cod_Cliente,
            variables_data.Cod_Produto,
            variables_data.Desc_Cod_Produto,
        ]
    )

    entregas_prod = (
        entregas_prod.groupby(
            [variables_data.Cod_Produto, variables_data.Desc_Cod_Produto]
        )[variables_data.Guid_Carga]
        .count()
        .reset_index()
        .sort_values(by=variables_data.Guid_Carga, ascending=False)
        .head(20)
    )

    figDash4 = px.bar(
        entregas_prod,
        y=variables_data.Desc_Cod_Produto,
        x=variables_data.Guid_Carga,
        text=entregas_prod[variables_data.Guid_Carga],
        color=variables_data.Guid_Carga,
        color_continuous_scale=px.colors.diverging.Portland,
        height=816,
        title="Top 20 Produtos por Entregas",
        labels={
            variables_data.Guid_Carga: "Entregas Totais",
            variables_data.Desc_Cod_Produto: "Produto (Descrição)",
        },
        hover_data={
            variables_data.Cod_Produto: True,
            variables_data.Desc_Cod_Produto: True,
            variables_data.Guid_Carga: True,
        },
        orientation="h",
    )

    figDash4.update_traces(
        textposition="inside",
        textfont=dict(size=12),
    )

    figDash4.update_layout(
        template=globalTemplate,
        title_font=dict(size=18),
        bargap=0.2,
        xaxis=dict(
            title="Entregas Totais",
            showgrid=True,
            autorange="reversed",
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            title="Produto",
            showgrid=False,
            autorange="reversed",
            tickfont=dict(size=12),
        ),
        coloraxis_colorbar=dict(title="Entregas"),
    )

    return figDash4


def fig5(df_detalhamento: pd.DataFrame, df_resumo: pd.DataFrame):
    entregas_peso = (
        df_detalhamento.groupby(
            [variables_data.Cod_Cliente, variables_data.Desc_Motorista]
        )[variables_data.Guid_Carga]
        .nunique()
        .reset_index()
        .groupby(variables_data.Desc_Motorista)[variables_data.Guid_Carga]
        .sum()
        .reset_index()
    )
    peso_por_mot = (
        df_resumo.groupby(variables_data.Desc_Motorista)[variables_data.Valor_Peso]
        .sum()
        .reset_index()
    )
    entregas_peso = entregas_peso.merge(
        peso_por_mot, on=variables_data.Desc_Motorista, how="left"
    )
    entregas_peso["PESO_POR_ENTREGA"] = (
        entregas_peso[variables_data.Valor_Peso]
        / entregas_peso[variables_data.Guid_Carga]
    )
    entregas_peso["PESO_POR_ENTREGA"] = entregas_peso["PESO_POR_ENTREGA"].fillna(0)

    entregas_peso["PESO_POR_ENTREGA"] = entregas_peso["PESO_POR_ENTREGA"].apply(
        conversores.outrosValores
    )
    entregas_peso = entregas_peso.sort_values(by="PESO_POR_ENTREGA", ascending=True)

    figDash5 = px.bar(
        entregas_peso,
        x=variables_data.Desc_Motorista,
        y="PESO_POR_ENTREGA",
        text="PESO_POR_ENTREGA",
        color=variables_data.Desc_Motorista,
        color_discrete_sequence=["#BB1818"],
        title="Peso por entrega",
        labels={
            "PESO_POR_ENTREGA": "Peso por entrega (KG)",
            variables_data.Desc_Motorista: "Motorista",
        },
        hover_data={
            variables_data.Guid_Carga: True,
            variables_data.Valor_Peso: True,
            "PESO_POR_ENTREGA": True,
        },
    )

    figDash5.update_traces(textposition="outside", textfont=dict(size=12))

    figDash5.update_layout(
        template=globalTemplate,
        showlegend=False,
        title_font=dict(size=18),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            showgrid=True,
            tickfont=dict(size=12),
        ),
        margin=dict(l=40, r=20, t=70, b=40),
    )

    return figDash5


def fig6(df_detalhamento: pd.DataFrame, df_resumo: pd.DataFrame):
    entregas_volume = (
        df_detalhamento.groupby(
            [variables_data.Cod_Cliente, variables_data.Desc_Motorista]
        )[variables_data.Guid_Carga]
        .nunique()
        .reset_index()
        .groupby(variables_data.Desc_Motorista)[variables_data.Guid_Carga]
        .sum()
        .reset_index()
    )
    volume_por_mot = (
        df_resumo.groupby(variables_data.Desc_Motorista)["qtd_Volume"]
        .sum()
        .reset_index()
    )
    entregas_volume = entregas_volume.merge(
        volume_por_mot, on=variables_data.Desc_Motorista, how="left"
    )
    entregas_volume["VOLUME_POR_ENTREGA"] = (
        entregas_volume["qtd_Volume"] / entregas_volume[variables_data.Guid_Carga]
    )
    entregas_volume["VOLUME_POR_ENTREGA"] = entregas_volume[
        "VOLUME_POR_ENTREGA"
    ].fillna(0)
    entregas_volume["VOLUME_POR_ENTREGA"] = entregas_volume["VOLUME_POR_ENTREGA"].apply(
        conversores.inteiroValores
    )
    entregas_volume = entregas_volume.sort_values(
        by="VOLUME_POR_ENTREGA", ascending=True
    )

    figDash6 = px.bar(
        entregas_volume,
        x=variables_data.Desc_Motorista,
        y="VOLUME_POR_ENTREGA",
        text="VOLUME_POR_ENTREGA",
        color=variables_data.Desc_Motorista,
        color_discrete_sequence=px.colors.sequential.OrRd,
        title="Volume por entrega",
        labels={
            "VOLUME_POR_ENTREGA": "Volume por entrega",
            variables_data.Desc_Motorista: "Motorista",
        },
        hover_data={
            variables_data.Guid_Carga: True,
            "qtd_Volume": True,
            "VOLUME_POR_ENTREGA": True,
        },
    )

    figDash6.update_traces(textposition="outside", textfont=dict(size=12))

    figDash6.update_layout(
        template=globalTemplate,
        showlegend=False,
        title_font=dict(size=18),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            showgrid=True,
            tickfont=dict(size=12),
        ),
        margin=dict(l=40, r=20, t=70, b=40),
    )

    return figDash6


def fig7(df_detalhamento: pd.DataFrame, df_resumo: pd.DataFrame):
    entregas_tpatend = (
        df_detalhamento.groupby(
            [variables_data.Cod_Cliente, variables_data.Desc_Motorista]
        )[variables_data.Guid_Carga]
        .nunique()
        .reset_index()
        .groupby(variables_data.Desc_Motorista)[variables_data.Guid_Carga]
        .sum()
        .reset_index()
    )
    tpatend_por_mot = (
        df_resumo.groupby(variables_data.Desc_Motorista)[
            variables_data.TEMPO_Atendimento
        ]
        .sum()
        .reset_index()
    )
    entregas_tpatend = entregas_tpatend.merge(
        tpatend_por_mot, on=variables_data.Desc_Motorista, how="left"
    )
    entregas_tpatend["TPATEND_POR_ENTREGA"] = (
        entregas_tpatend[variables_data.TEMPO_Atendimento]
        / entregas_tpatend[variables_data.Guid_Carga]
    )
    entregas_tpatend["TPATEND_POR_ENTREGA"] = entregas_tpatend[
        "TPATEND_POR_ENTREGA"
    ].fillna(0)
    entregas_tpatend["TPATEND_POR_ENTREGA"] = entregas_tpatend[
        "TPATEND_POR_ENTREGA"
    ].apply(conversores.outrosValores)
    entregas_tpatend = entregas_tpatend.sort_values(
        by=variables_data.Desc_Motorista, ascending=True
    )

    figDash7 = px.line(
        entregas_tpatend,
        x=variables_data.Desc_Motorista,
        y="TPATEND_POR_ENTREGA",
        text="TPATEND_POR_ENTREGA",
        markers=True,
        line_shape="spline",
        title="Tempo em Atendimento (Minutos)",
        labels={
            "TPATEND_POR_ENTREGA": "Tempo por Entrega (min)",
            variables_data.Desc_Motorista: "Motorista",
        },
        hover_data={
            variables_data.Guid_Carga: True,
            variables_data.TEMPO_Atendimento: True,
            "TPATEND_POR_ENTREGA": True,
        },
    )

    figDash7.update_traces(
        line_color="black",
        line=dict(width=2),
        marker=dict(size=8, symbol="circle", color="blue"),
        textposition="top center",
        textfont=dict(size=9, color="black"),
    )

    figDash7.update_layout(
        template=globalTemplate,
        title_font=dict(size=18),
        xaxis=dict(title="Motorista", showgrid=False),
        yaxis=dict(title="Tempo Atendimento", showgrid=True),
        margin=dict(l=40, r=20, t=70, b=40),
        showlegend=False,
    )

    return figDash7


def fig8(df_detalhamento: pd.DataFrame, df_resumo: pd.DataFrame):
    entregas_km = (
        df_detalhamento.groupby(
            [variables_data.Cod_Cliente, variables_data.Desc_Motorista]
        )[variables_data.Guid_Carga]
        .nunique()
        .reset_index()
        .groupby(variables_data.Desc_Motorista)[variables_data.Guid_Carga]
        .sum()
        .reset_index()
    )
    km_por_mot = (
        df_resumo.groupby(variables_data.Desc_Motorista)[variables_data.Num_KM_Rodado]
        .sum()
        .reset_index()
    )
    entregas_km = entregas_km.merge(
        km_por_mot, on=variables_data.Desc_Motorista, how="left"
    )
    entregas_km["KM_POR_ENTREGA"] = (
        entregas_km[variables_data.Num_KM_Rodado]
        / entregas_km[variables_data.Guid_Carga]
    )
    entregas_km["KM_POR_ENTREGA"] = entregas_km["KM_POR_ENTREGA"].fillna(0)
    entregas_km["KM_POR_ENTREGA"] = entregas_km["KM_POR_ENTREGA"].apply(
        conversores.outrosValores
    )
    entregas_km = entregas_km.sort_values(
        by=variables_data.Desc_Motorista, ascending=True
    )

    figDash8 = px.line(
        entregas_km,
        x=variables_data.Desc_Motorista,
        y="KM_POR_ENTREGA",
        text="KM_POR_ENTREGA",
        markers=True,
        line_shape="spline",
        title="KM Rodado por entrega",
        labels={
            "KM_POR_ENTREGA": "KM Rodado por Entrega",
            variables_data.Desc_Motorista: "Motorista",
        },
        hover_data={
            variables_data.Guid_Carga: True,
            variables_data.Num_KM_Rodado: True,
            "KM_POR_ENTREGA": True,
        },
    )

    figDash8.update_traces(
        line_color="black",
        line=dict(width=2),
        marker=dict(size=8, symbol="circle", color="blue"),
        textposition="top center",
        textfont=dict(size=9, color="black"),
    )

    figDash8.update_layout(
        template=globalTemplate,
        title_font=dict(size=18),
        xaxis=dict(title="Motorista", showgrid=False),
        yaxis=dict(title="KM Rodado", showgrid=True),
        margin=dict(l=40, r=20, t=70, b=40),
        showlegend=False,
    )

    return figDash8


def fig9(df_detalhamento: pd.DataFrame):
    entregas_vlr = (
        df_detalhamento.groupby(variables_data.Desc_Motorista)[
            variables_data.Valor_Venda
        ]
        .sum()
        .reset_index()
    )

    entregas_vlr["VALOR_TEXTO"] = entregas_vlr[variables_data.Valor_Venda].apply(
        conversores.MetricMoedaInteiroValores
    )
    entregas_vlr[variables_data.Valor_Venda] = entregas_vlr[
        variables_data.Valor_Venda
    ].apply(conversores.inteiroValores)

    figDash9 = px.line(
        entregas_vlr,
        x=variables_data.Desc_Motorista,
        y=variables_data.Valor_Venda,
        text="VALOR_TEXTO",
        markers=True,
        line_shape="spline",
        title="Valor Entregue",
        labels={
            variables_data.Valor_Venda: "Valor Entregue",
            variables_data.Desc_Motorista: "Motorista",
        },
        hover_data={variables_data.Valor_Venda: True, "VALOR_TEXTO": True},
    )

    text_positions = ["top right"] + ["top left"] * (len(entregas_vlr) - 1)

    figDash9.update_traces(
        textposition=text_positions,
        textfont=dict(size=9, color="black"),
        fill="tozeroy",
        fillcolor="rgba(255, 140, 0, 0.2)",
        line=dict(color="black", width=2),
        marker=dict(size=9, symbol="circle", color="blue"),
    )

    figDash9.update_layout(
        template=globalTemplate,
        title_font=dict(size=18),
        xaxis=dict(title="Motorista", showgrid=False),
        yaxis=dict(title="Valor Entregue", showgrid=True),
        height=500,
        showlegend=False,
        margin=dict(l=40, r=20, t=70, b=40),
    )

    return figDash9


def fig10(df_detalhamento: pd.DataFrame):
    entregas_data = (
        df_detalhamento.groupby(variables_data.DT_Emissao)[variables_data.Guid_Carga]
        .count()
        .reset_index()
    )
    entregas_data[variables_data.DT_Emissao] = pd.to_datetime(
        entregas_data[variables_data.DT_Emissao]
    )
    entregas_data["DATA_FORMATADA"] = entregas_data[
        variables_data.DT_Emissao
    ].dt.strftime("%d/%m")
    entregas_data["QTD_ENTREGAS"] = entregas_data[variables_data.Guid_Carga]

    figDash10 = px.bar(
        entregas_data,
        x="DATA_FORMATADA",
        y="QTD_ENTREGAS",
        text="QTD_ENTREGAS",
        title="Quantidade de Entregas por Dia",
        labels={
            "QTD_ENTREGAS": "Quantidade de Entregas",
            "DATA_FORMATADA": "Data",
        },
        hover_data={
            variables_data.DT_Emissao: True,
            "QTD_ENTREGAS": True,
        },
    )

    figDash10.update_traces(
        textposition="outside",
        textfont=dict(size=10, color="black"),
        marker=dict(color="orange", line=dict(color="black", width=2)),
    )

    figDash10.update_layout(
        template=globalTemplate,
        title_font=dict(size=18),
        xaxis=dict(title="Data", showgrid=False),
        yaxis=dict(title="Quantidade de Entregas", showgrid=True),
        margin=dict(l=40, r=20, t=70, b=40),
        showlegend=False,
    )

    return figDash10


def fig11(df_detalhamento: pd.DataFrame):
    entregas_data = (
        df_detalhamento.groupby(variables_data.DT_Emissao)[variables_data.Guid_Carga]
        .count()
        .reset_index()
        .rename(columns={variables_data.Guid_Carga: "Quantidade de Entregas"})
    )

    entregas_data[variables_data.DT_Emissao] = pd.to_datetime(
        entregas_data[variables_data.DT_Emissao]
    )
    entregas_data["Data Formatada"] = entregas_data[
        variables_data.DT_Emissao
    ].dt.strftime("%d/%m")

    fig = px.bar(
        entregas_data,
        x="Data Formatada",
        y="Quantidade de Entregas",
        text="Quantidade de Entregas",
        title="Quantidade de Entregas por Dia",
        labels={
            "Data Formatada": "Data",
            "Quantidade de Entregas": "Quantidade de Entregas",
        },
        hover_data={variables_data.DT_Emissao: True},
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(size=10, color="black"),
        marker=dict(color="orange", line=dict(color="black", width=2)),
    )

    fig.update_layout(
        template=globalTemplate,
        title_font=dict(size=18),
        xaxis=dict(title="Data", showgrid=False),
        yaxis=dict(title="Quantidade de Entregas", showgrid=True),
        margin=dict(l=40, r=20, t=70, b=40),
        showlegend=False,
    )

    return fig


def loadCharts(df_detalhamento: pd.DataFrame, df_resumo: pd.DataFrame) -> html.Div:
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
                                    dcc.Graph(figure=fig1(df_detalhamento)),
                                ],
                                class_name="shadow-sm p-1 rounded",
                            )
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Row(
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardHeader(
                                            [
                                                dcc.Graph(figure=fig2(df_detalhamento)),
                                            ],
                                            class_name="shadow-sm p-1 rounded",
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
                                                dcc.Graph(figure=fig3(df_detalhamento)),
                                            ],
                                            class_name="shadow-sm p-1 rounded",
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
                                                dcc.Graph(figure=fig4(df_detalhamento)),
                                            ],
                                            class_name="shadow-sm p-1 rounded",
                                        )
                                    )
                                ),
                                class_name="mt-0",
                            ),
                        ],
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
                                    dcc.Graph(figure=fig5(df_detalhamento, df_resumo)),
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
                                    dcc.Graph(figure=fig6(df_detalhamento, df_resumo)),
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
                                    dcc.Graph(figure=fig7(df_detalhamento, df_resumo)),
                                ],
                                class_name="shadow-sm p-1 rounded",
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
                                    dcc.Graph(figure=fig8(df_detalhamento, df_resumo)),
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
                                    dcc.Graph(figure=fig9(df_detalhamento)),
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
                                    dcc.Graph(figure=fig10(df_detalhamento)),
                                ],
                                class_name="shadow-sm p-1 rounded",
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
                                    dcc.Graph(figure=fig11(df_detalhamento)),
                                ],
                                class_name="shadow-sm p-1 rounded",
                            )
                        ),
                        width=12,
                    ),
                ],
                class_name="mt-0 g-1",
            ),
        ]
    )
