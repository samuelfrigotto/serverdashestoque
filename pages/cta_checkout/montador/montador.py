from app import app
from app import session_dataframes_cta_checkout as sessionDF
from dash import Input, Output, State, dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc
from utils import conversores, read_file
import pandas as pd
import plotly.graph_objects as go
from assets.static import packCode, Colors, supportClass
from stylesDocs.style import styleConfig

Desc_Cidade = "C_CIDADE"
Desc_Bairro = "C_BAIRRO"
Desc_Cliente = "C_DESCRICAO_CLIENTE"
Desc_Produto = "P_DESCRICAO_PRODUTO"
Desc_Grupo = "G_DESCRICAO_GRUPO"
Desc_Supervisor = "SUP_DESCRICAO_SUPERVISOR"
Desc_Motorista = "M_DESCRICAO"
Desc_Placa = "PLACA_VEICULO"
Desc_Rota = "R_DESCRICAO_ROTA"
Desc_Vendedor = "V_DESCRICAO_VENDEDOR"
Valor_Cubagem = "CUBAGEM"
Guid_Carga = "GUID_CARGA"
Cod_Cliente = "CD_CLIENTE"
Numero_NF = "NR_NFR"
Valor_Venda = "VL_VENDA"






pageTag: str = "CCmontador_"
styleColors = styleConfig("dark")
globalTemplate: dict = {
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
            subset=[Guid_Carga, Cod_Cliente]
        )
        metricsDict: dict = {
            "Nº Entregas": {
                "icone": "bi bi-truck",
                "valor": conversores.MetricInteiroValores(df_entregas_unicas.shape[0]),
            },
            "Nº NFe's Entregues": {
                "icone": "bi bi-receipt-cutoff",
                "valor": conversores.MetricInteiroValores(
                    df_detalhamento[Numero_NF].unique().size
                ),
            },
            "Cubagem Entregue": {
                "icone": "bi bi-box",
                "valor": conversores.MetricInteiroValores(
                    df_detalhamento[Valor_Cubagem].sum()
                ),
            },
            "Valor Total": {
                "icone": "bi bi-cash-stack",
                "valor": conversores.MetricInteiroValores(
                    df_detalhamento[Valor_Venda].sum()
                ),
            },
        }

        filters: dict = {
            f"{pageTag}fil_cidade": {
                "distValue": df_detalhamento[Desc_Cidade].unique(),
                "labelName": "Cidade",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_rota": {
                "distValue": df_detalhamento[Desc_Rota].unique(),
                "labelName": "Rota",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_bairro": {
                "distValue": df_detalhamento[Desc_Bairro].unique(),
                "labelName": "Bairro",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_motorista": {
                "distValue": df_detalhamento[Desc_Motorista].unique(),
                "labelName": "Motorista",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_placa": {
                "distValue": df_detalhamento[Desc_Placa].unique(),
                "labelName": "Placa",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_supervisor": {
                "distValue": df_detalhamento[Desc_Supervisor].unique(),
                "labelName": "Supervisor",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_vendedor": {
                "distValue": df_detalhamento[Desc_Vendedor].unique(),
                "labelName": "Vendedor",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_grupo": {
                "distValue": df_detalhamento[Desc_Grupo].unique(),
                "labelName": "Grupo",
                "valueDefault": "Todos",
            },
            f"{pageTag}fil_sku": {
                "distValue": df_detalhamento[Desc_Produto].unique(),
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
    if "Todos" not in fil_cidade and len(fil_cidade) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=Desc_Cidade, filtro=fil_cidade
        )
    if "Todos" not in fil_rota and len(fil_rota) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=Desc_Rota, filtro=fil_rota
        )
    if "Todos" not in fil_bairro and len(fil_bairro) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=Desc_Bairro, filtro=fil_bairro
        )
    if "Todos" not in fil_motorista and len(fil_motorista) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=Desc_Motorista, filtro=fil_motorista
        )
    if "Todos" not in fil_supervisor and len(fil_supervisor) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=Desc_Supervisor, filtro=fil_supervisor
        )
    if "Todos" not in fil_vendedor and len(fil_vendedor) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=Desc_Vendedor, filtro=fil_vendedor
        )
    if "Todos" not in fil_grupo and len(fil_grupo) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=Desc_Grupo, filtro=fil_grupo
        )
    if "Todos" not in fil_sku and len(fil_sku) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=Desc_Produto, filtro=fil_sku
        )
    if "Todos" not in fil_placa and len(fil_placa) > 0:
        df_detalhamento = conversores.FiltrarColuna(
            df=df_detalhamento, tabela=Desc_Placa, filtro=fil_placa
        )

    df_entregas_unicas = df_detalhamento.drop_duplicates(
            subset=[Guid_Carga, Cod_Cliente]
        )
    
    metricsDict: dict = {
        "Nº Entregas": {
            "icone": "bi bi-truck",
            "valor":  conversores.MetricInteiroValores(df_entregas_unicas.shape[0]),
        },
        "Nº NFe's Entregues": {
            "icone": "bi bi-receipt-cutoff",
            "valor": conversores.MetricInteiroValores(
                df_detalhamento[Numero_NF].unique().size
            ),
        },
        "Cubagem Entregue": {
            "icone": "bi bi-box",
            "valor": conversores.MetricInteiroValores(df_detalhamento[Valor_Cubagem].sum()),
        },
        "Valor Total": {
            "icone": "bi bi-cash-stack",
            "valor": conversores.MetricInteiroValores(
                df_detalhamento[Valor_Venda].sum()
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
    session_id = session_data.get("session_id", "")
    if f"{session_id}_resumo" not in sessionDF:
        sessionDF[f"{session_id}_resumo"] = read_file.read_json("resumo.json")
    if f"{session_id}_detalhamento" not in sessionDF:
        sessionDF[f"{session_id}_detalhamento"] = read_file.read_json(
            "detalhamento.json"
        )
    return 1


def loadCharts(df_detalhamento: pd.DataFrame,) -> html.Div:
    df_resumo = read_file.read_json("resumo.json")

    
    top20_entregas = df_detalhamento.drop_duplicates(subset=[Guid_Carga, Cod_Cliente])
    top20_entregas = top20_entregas.groupby([Cod_Cliente, Desc_Cliente])[Guid_Carga].count().reset_index()
    top20_entregas["Qtd_Entregas"] = top20_entregas[Guid_Carga]
    top20_entregas = top20_entregas.sort_values(by="Qtd_Entregas", ascending=False)
    top20_entregas = top20_entregas.head(20)
    
    top20_entregas = top20_entregas.sort_values(by="Qtd_Entregas", ascending=True)
    
    figDash1 = px.bar(
        top20_entregas,
        height=816,
        x="Qtd_Entregas",
        y=Desc_Cliente,
        title="Top 20 Clientes por Entregas", 
        labels={Desc_Cliente: "Cliente", "Qtd_Entregas": "Entrega total"},
        text=top20_entregas["Qtd_Entregas"].round(),
        orientation="h",
        color="Qtd_Entregas",  
        color_discrete_sequence=["#671669FF", '#942D96FF',"#AA31ACFF","#BC32BEFF"]
    )
    
    figDash1.update_traces(
    textposition="inside",  # Posicionar texto dentro da barra
    textfont=dict(color="white", size=12),  # Ajustar cor e tamanho do texto
)

    figDash1.update_layout(
        xaxis_title="Entrega Total",
        yaxis_title="Cliente", 
        plot_bgcolor="rgba(240, 240, 240, 1)",  
        paper_bgcolor="rgba(240, 240, 240, 1)",  
        
    )
    
    Entregas_mot=df_detalhamento.drop_duplicates(subset=[Guid_Carga, Cod_Cliente])
    Entregas_mot = Entregas_mot.groupby([Cod_Cliente, Desc_Cliente, Desc_Motorista])[Guid_Carga].count().reset_index()
    Entregas_mot = Entregas_mot.sort_values(by=Desc_Motorista).reset_index(drop=True)
    Entregas_mot[Desc_Motorista] = Entregas_mot[Desc_Motorista].apply(conversores.abreviar)

    

    
    pull_values = [0.05] * len(Entregas_mot)

    figDash2 = go.Figure(
    data=[go.Pie(
    labels=Entregas_mot[Desc_Motorista],
    values=Entregas_mot[Guid_Carga],
    pull=pull_values,
    textinfo="label+percent",
    textfont=dict(size=10, color="black"),
    sort=False,
    direction="clockwise",
    textposition="outside",
    marker=dict(colors=px.colors.qualitative.Prism),
    hovertemplate="Motorista: %{label}<br>Qtde Entregas: %{value}<extra></extra>"

    )]
    )


    figDash2.update_traces(
    textinfo="label+percent+value",  
    textfont=dict(size=10, color="black"),  
    textposition="outside",  
    
)

    figDash2.update_layout(
    height=400,
    showlegend=False,  
    title=dict(text="Entregas por Motorista", x=0, font=dict(size=18)),
    plot_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo do gráfico
    paper_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo fora do gráfico
)
    Entregas_cid=df_detalhamento.drop_duplicates(subset=[Guid_Carga, Cod_Cliente])
    Entregas_cid = Entregas_cid.groupby([Cod_Cliente, Desc_Cliente, Desc_Motorista,Desc_Cidade])[Guid_Carga].count().reset_index()
    Entregas_cid[Desc_Cidade] = Entregas_cid[Desc_Cidade].apply(conversores.abreviar)
    Entregas_cid = Entregas_cid.sort_values(by=Desc_Cidade).reset_index(drop=True)
    
        
    pull_values = [0.05] * len(Entregas_mot)

    figDash3 = go.Figure(
    data=[go.Pie(
    labels=Entregas_cid[Desc_Cidade],
    values=Entregas_cid[Guid_Carga],
    pull=pull_values,
    textinfo="label+percent+value", 
    textfont=dict(size=10, color="black"),
    sort=False,
    direction="clockwise",
    textposition="outside",
    marker=dict(colors=px.colors.qualitative.Prism_r),
    hovertemplate="Cidade: %{label}<br>Qtde Entregas: %{value}<extra></extra>"
    )]  
    )


    figDash3.update_traces(
    textinfo="label+percent+value",  
    textfont=dict(size=10, color="black"),  
    textposition="outside",  
    
)

    figDash3.update_layout(
    height=400,
    showlegend=False,  
    title=dict(text="Entregas por Cidade", x=0, font=dict(size=18)),
    plot_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo do gráfico
    paper_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo fora do gráfico
)
    
    
    Entregas_prod = df_detalhamento.drop_duplicates(subset=[Guid_Carga, Cod_Cliente, "CD_SKU", Desc_Produto])
    Entregas_prod = (
    Entregas_prod.groupby(["CD_SKU", Desc_Produto])[Guid_Carga]
    .count()
    .reset_index()
)
    Entregas_prod = Entregas_prod.sort_values(by=Guid_Carga, ascending=False).head(20)
    


    figDash4 = px.bar(
    Entregas_prod,
    height=816,
    y=Desc_Produto,
    x=Guid_Carga,
    title="Top 20 Produtos por Entregas",
    labels={Guid_Carga: "Entregas Totais", Desc_Produto: "Produto (Descrição)"},
    text=Guid_Carga,
    color=Guid_Carga,  
    color_discrete_sequence=["#240F55FF", '#231D74FF',"#2F42ADFF","#3771C9FF"]
    
)

    figDash4.update_layout(
    xaxis=dict(
        title="Entregas Totais", 
        showgrid=False,
        autorange="reversed",
        tickfont=dict(size=12),
    ),
    yaxis=dict(
        title="Produto (Descrição)",
        showgrid=False,
        autorange="reversed",  
        tickfont=dict(size=12),  
    ),
    title_font=dict(size=18),  
    bargap=0.2,
    plot_bgcolor="rgba(240, 240, 240, 1)",  
    paper_bgcolor="rgba(240, 240, 240, 1)",  
)

    figDash4.update_traces(
    textposition="inside",  
    textfont=dict(color="white", size=12),  
)
        
    entregas_cub=df_detalhamento.groupby([Cod_Cliente,Desc_Cidade]).agg({Valor_Cubagem:"sum",Guid_Carga:"nunique"})
    entregas_cub= entregas_cub.groupby([Desc_Cidade]).sum().reset_index()
    entregas_cub["CUBAGEM_POR_ENTREGA"] = entregas_cub[Valor_Cubagem] / entregas_cub[Guid_Carga]    
    entregas_cub = entregas_cub.sort_values(by="CUBAGEM_POR_ENTREGA", ascending=True)
    entregas_cub[Desc_Cidade] = entregas_cub[Desc_Cidade].apply(conversores.abreviar)
    entregas_cub["CUBAGEM_POR_ENTREGA"] = entregas_cub["CUBAGEM_POR_ENTREGA"].apply(conversores.inteiroValores
)

    
    figDash5 = px.bar(
    entregas_cub,
    x=Desc_Cidade,  
    y="CUBAGEM_POR_ENTREGA",  
    title="Cubagem por entrega",
    labels={"CUBAGEM_POR_ENTREGA": "Cubagem por entrega", Desc_Cidade: "Cidade"},
    text="CUBAGEM_POR_ENTREGA", 
    color=Desc_Cidade,  
    color_discrete_sequence=["#141E29"],
     
)
    figDash5.update_traces()


    figDash5.update_layout(
    showlegend=False,
    title=dict(font=dict(size=18)),  # Ajuste de fonte do título
    plot_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo do gráfico
    paper_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo fora do gráfico
)

   
    entregas_peso = df_detalhamento.groupby([Cod_Cliente, Desc_Motorista, "CD_MOT"]).agg({
    Guid_Carga: "nunique" 
}).reset_index()
    entregas_peso = entregas_peso.groupby([Desc_Motorista, "CD_MOT"]).agg({
    Guid_Carga: "sum"  # Soma do número de entregas por descrição e motorista
}).reset_index()
    peso_por_mot = df_resumo.groupby("CD_MOT").agg({
    "PESO": "sum"  # Soma do peso por motorista
}).reset_index()
    entregas_peso = entregas_peso.merge(peso_por_mot, on="CD_MOT", how="left")
    if "PESO" in entregas_peso.columns:
        entregas_peso["PESO_POR_ENTREGA"] = entregas_peso["PESO"] / entregas_peso[Guid_Carga]
    else:
        entregas_peso["PESO_POR_ENTREGA"] = 0  # Preencher com 0 se não houver peso
    entregas_peso = entregas_peso.sort_values(by="PESO_POR_ENTREGA", ascending=True)
    entregas_peso[Desc_Motorista] = entregas_peso[Desc_Motorista].apply(conversores.abreviar)
    entregas_peso["PESO_POR_ENTREGA"] = entregas_peso["PESO_POR_ENTREGA"].apply(conversores.inteiroValores)
    
    figDash6 = px.bar(
    entregas_peso,
    x=Desc_Motorista,  
    y="PESO_POR_ENTREGA",  
    title="Peso por entrega",
    labels={"PESO_POR_ENTREGA": "Peso por entrega (KG)", Desc_Motorista: "Motorista"},
    text="PESO_POR_ENTREGA", 
    color=Desc_Motorista,  
    color_discrete_sequence=["#BB1818"],
     
)
    figDash6.update_traces()


    figDash6.update_layout(
    showlegend=False,
    title=dict(font=dict(size=18)),  # Ajuste de fonte do título
    plot_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo do gráfico
    paper_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo fora do gráfico
)

    entregas_volume = df_detalhamento.groupby([Cod_Cliente, Desc_Motorista, "CD_MOT"]).agg({
    Guid_Carga: "nunique" 
}).reset_index()
    entregas_volume = entregas_volume.groupby([Desc_Motorista, "CD_MOT"]).agg({
    Guid_Carga: "sum"  # Soma do número de entregas por descrição e motorista
}).reset_index()
    volume_por_mot = df_resumo.groupby("CD_MOT").agg({
    "VOLUMES": "sum"  # Soma do volume por motorista
}).reset_index()
    entregas_volume = entregas_volume.merge(volume_por_mot, on="CD_MOT", how="left")
    if "VOLUMES" in entregas_volume.columns:
        entregas_volume["VOLUME_POR_ENTREGA"] = entregas_volume["VOLUMES"] / entregas_volume[Guid_Carga]
    else:
        entregas_volume["VOLUME_POR_ENTREGA"] = 0  # Preencher com 0 se não houver peso
    entregas_volume = entregas_volume.sort_values(by="VOLUME_POR_ENTREGA", ascending=True)
    entregas_volume[Desc_Motorista] = entregas_volume[Desc_Motorista].apply(conversores.abreviar)
    entregas_volume["VOLUME_POR_ENTREGA"] = entregas_volume["VOLUME_POR_ENTREGA"].apply(conversores.inteiroValores)
    
    figDash7 = px.bar(
    entregas_volume,
    x=Desc_Motorista,  
    y="VOLUME_POR_ENTREGA",  
    title="Volume por entrega",
    labels={"VOLUME_POR_ENTREGA": "Volume por entrega", Desc_Motorista: "Motorista"},
    text="VOLUME_POR_ENTREGA", 
    color=Desc_Motorista,  
    color_discrete_sequence=["#0DDFC3"],
     
)
    figDash7.update_traces(
     
)


    figDash7.update_layout(   
    showlegend=False,
    title=dict(font=dict(size=18)),  # Ajuste de fonte do título
    plot_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo do gráfico
    paper_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo fora do gráfico
)

    entregas_tpatend = df_detalhamento.groupby([Cod_Cliente, Desc_Motorista, "CD_MOT"]).agg({
    Guid_Carga: "nunique" 
}).reset_index()
    entregas_tpatend = entregas_tpatend.groupby([Desc_Motorista, "CD_MOT"]).agg({
    Guid_Carga: "sum"  
}).reset_index()
    tpatend_por_mot = df_resumo.groupby("CD_MOT").agg({
    "TP_ATENDIMENTO": "sum"  
}).reset_index()
    entregas_tpatend = entregas_tpatend.merge(tpatend_por_mot, on="CD_MOT", how="left")
    if "TP_ATENDIMENTO" in entregas_tpatend.columns:
        entregas_tpatend["TPATEND_POR_ENTREGA"] = entregas_tpatend["TP_ATENDIMENTO"] / entregas_tpatend[Guid_Carga]
    else:
        entregas_tpatend["TPATEND_POR_ENTREGA"] = 0  
    entregas_tpatend = entregas_tpatend.sort_values(by=Desc_Motorista, ascending=True)
    entregas_tpatend[Desc_Motorista] = entregas_tpatend[Desc_Motorista].apply(conversores.abreviar)
    entregas_tpatend["TPATEND_POR_ENTREGA"] = entregas_tpatend["TPATEND_POR_ENTREGA"].apply(conversores.inteiroValores)
    
    figDash8 = px.line(
    entregas_tpatend,
    x=Desc_Motorista,  
    y="TPATEND_POR_ENTREGA",  
    title="Tempo em Atendimento (Minutos)",
    labels={"TPATEND_POR_ENTREGA": "Tempo em Atendimento", Desc_Motorista: "Motorista"},
    text="TPATEND_POR_ENTREGA", 
    markers=True, 
    
     
)

    figDash8.update_traces(
    line_color="black", 
    line=dict(width=2),  
    textposition="top center",  
    marker=dict(size=8, symbol="circle", color="blue"),  
    textfont=dict(size=9, color="black")  
)

    figDash8.update_layout(
    xaxis=dict(title="Motorista", showgrid=False),  
    yaxis=dict(title="Tempo Atendimento", showgrid=False), 
    title_font=dict(size=18),
    plot_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo do gráfico
    paper_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo fora do gráfico  
    )

    entregas_km = df_detalhamento.groupby([Cod_Cliente, Desc_Motorista, "CD_MOT"]).agg({
    Guid_Carga: "nunique" 
}).reset_index()
    entregas_km = entregas_km.groupby([Desc_Motorista, "CD_MOT"]).agg({
    Guid_Carga: "sum"  
}).reset_index()
    km_por_mot = df_resumo.groupby("CD_MOT").agg({
    "KM_RODADO": "sum"  
}).reset_index()
    entregas_km = entregas_km.merge(km_por_mot, on="CD_MOT", how="left")
    if "KM_RODADO" in entregas_km.columns:
        entregas_km["KM_POR_ENTREGA"] = entregas_km["KM_RODADO"] / entregas_km[Guid_Carga]
    else:
        entregas_km["KM_POR_ENTREGA"] = 0  
    entregas_km = entregas_km.sort_values(by=Desc_Motorista, ascending=True)
    entregas_km["KM_POR_ENTREGA"] = entregas_km["KM_POR_ENTREGA"].apply(conversores.inteiroValores)
    entregas_km[Desc_Motorista] = entregas_km[Desc_Motorista].apply(conversores.abreviar)
    
    figDash9 = px.line(
    entregas_km,
    x=Desc_Motorista,  
    y="KM_POR_ENTREGA",  
    title="KM Rodado por entrega",
    labels={"KM_POR_ENTREGA": "KM Rodado", Desc_Motorista: "Motorista"},
    text="KM_POR_ENTREGA", 
    markers=True, 
    
     
)

    figDash9.update_traces(
    line_color="black", 
    line=dict(width=2),  
    textposition="top center",  
    marker=dict(size=8, symbol="circle", color="blue"),  
    textfont=dict(size=9, color="black")  
)

    figDash9.update_layout(
    xaxis=dict(title="Motorista", showgrid=False),  
    yaxis=dict(title="KM Rodado", showgrid=False), 
    title_font=dict(size=18),
    plot_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo do gráfico
    paper_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo fora do gráfico  
    )
    
    

    entregas_vlr = df_detalhamento.groupby(Desc_Motorista).agg({
    Valor_Venda: "sum"
}).reset_index()
    entregas_vlr[Valor_Venda] = entregas_vlr[Valor_Venda].apply(conversores.inteiroValores)
    entregas_vlr[Desc_Motorista] = entregas_vlr[Desc_Motorista].apply(conversores.abreviar)
    
    figDash10 = px.line(
    entregas_vlr,
    x=Desc_Motorista,  
    y=Valor_Venda,  
    title="Valor Entregue",
    labels={Valor_Venda: "Valor Entregue", Desc_Motorista: "Motorista"},
    text=Valor_Venda, 
    markers=True
     
)
    
    figDash10.update_traces(
    line_color="black", 
    line=dict(width=2),  
    textposition="top center",  
    marker=dict(size=8, symbol="circle", color="blue"),  
    textfont=dict(size=9, color="black")  
)


    figDash10.update_layout(
    xaxis=dict(title="Motorista", showgrid=False),  
    yaxis=dict(title="Valor Entregue", showgrid=False), 
    title_font=dict(size=18),
    plot_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo do gráfico
    paper_bgcolor="rgba(240, 240, 240, 1)",  # Cor de fundo fora do gráfico  
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
                                        dcc.Graph(figure=figDash2),
                                    ],
                                    class_name="shadow-sm p-1 rounded",
                                )
                            )),class_name="mb-1"
                        ),
                        dbc.Row(
                            dbc.Col(
                            dbc.Card(
                                dbc.CardHeader(
                                    [
                                        dcc.Graph(figure=figDash3),
                                    ],
                                    class_name="shadow-sm p-1 rounded",
                                )
                            ))
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        dbc.Row(dbc.Col(
                            dbc.Card(
                                dbc.CardHeader(
                                    [
                                        dcc.Graph(figure=figDash4),
                                    ],
                                    class_name="shadow-sm p-1 rounded",
                                )
                            )),class_name="mb-1"
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
                                dcc.Graph(figure=figDash5),
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
                                dcc.Graph(figure=figDash6),
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
                                dcc.Graph(figure=figDash7),
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
                                dcc.Graph(figure=figDash8),
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
                                dcc.Graph(figure=figDash9),
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
                                dcc.Graph(figure=figDash10),
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
