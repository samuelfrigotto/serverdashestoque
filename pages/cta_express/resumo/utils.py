import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from pages.cta_express.cta_express_globals import variables_data
from utils import conversores


def create_choropleth_map(dfmapa: pd.DataFrame):
    df_agg = dfmapa.copy()

    center_lat = df_agg[variables_data.cliente_lat].mean()
    center_lon = df_agg[variables_data.cliente_log].mean()

    if not df_agg.empty:
        lat_range = np.ptp(df_agg[variables_data.cliente_lat])
        lon_range = np.ptp(df_agg[variables_data.cliente_log])
        range_sum = lat_range + lon_range

        if range_sum < 0.5:
            zoom_level = 11
        elif range_sum < 1:
            zoom_level = 10
        elif range_sum < 2:
            zoom_level = 9
        elif range_sum < 4:
            zoom_level = 8
        elif range_sum < 8:
            zoom_level = 7
        elif range_sum < 15:
            zoom_level = 6
        else:
            zoom_level = 5
    else:
        zoom_level = 6.5

    df_agg = (
        df_agg.groupby(
            [
                variables_data.cliente_lat,
                variables_data.cliente_log,
                variables_data.Desc_Cidade,
                variables_data.Desc_Cliente,
            ]
        )
        .agg({variables_data.Valor_Venda: "sum", variables_data.Valor_Cubagem: "sum"})
        .reset_index()
    )

    df_agg["Valor"] = df_agg[variables_data.Valor_Venda].apply(
        conversores.moedaCorrente
    )
    df_agg["Cliente"] = df_agg[variables_data.Desc_Cliente]
    df_agg["Cubagem"] = df_agg[variables_data.Valor_Cubagem].apply(
        conversores.MetricOutrosValores
    )

    heatmap = px.density_mapbox(
        df_agg,
        lat=variables_data.cliente_lat,
        lon=variables_data.cliente_log,
        z=variables_data.Valor_Venda,
        radius=25,
        mapbox_style="open-street-map",
        zoom=zoom_level,
        center={"lat": center_lat, "lon": center_lon},
        height=500,
        color_continuous_scale="Inferno",
        hover_data={
            "Cliente": True,
            "Valor": True,
            "Cubagem": True,
            variables_data.Valor_Venda: False,
            variables_data.cliente_lat: False,
            variables_data.cliente_log: False,
        },
    )

    heatmap.update_traces(opacity=0.7)

    df_city_labels = dfmapa.groupby(variables_data.Desc_Cidade, as_index=False).agg(
        {variables_data.cliente_lat: "mean", variables_data.cliente_log: "mean"}
    )

    scatter = go.Scattermapbox(
        lat=dfmapa[variables_data.cliente_lat],
        lon=dfmapa[variables_data.cliente_log],
        mode="markers",
        marker=go.scattermapbox.Marker(size=10, symbol="circle", color="Orange"),
        name="Pontos Individuais",
        visible=False,
        showlegend=False,
        customdata=dfmapa[
            ["Valor", variables_data.Desc_Cidade, variables_data.Desc_Cliente]
        ],
        hovertemplate="<b>%{customdata[2]}</b><br>Cidade: %{customdata[1]}<br>Venda: %{customdata[0]}<extra></extra>",
    )

    city_labels = go.Scattermapbox(
        lat=df_city_labels[variables_data.cliente_lat],
        lon=df_city_labels[variables_data.cliente_log],
        mode="text",
        text=df_city_labels[variables_data.Desc_Cidade],
        textfont=dict(size=12, color="black"),
        name="Cidades",
        showlegend=False,
    )

    fig = go.Figure(data=[heatmap.data[0], scatter, city_labels])

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            zoom=zoom_level,
            center={"lat": center_lat, "lon": center_lon},
        ),
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        title=dict(
            text="Concentração das Vendas",
            font=dict(size=16, color="black"),
            x=0.5,
            xanchor="center",
            y=0.97,
        ),
        paper_bgcolor="white",
        updatemenus=[
            dict(
                buttons=[
                    dict(
                        args=[{"visible": [True, False, True]}],
                        label="Heatmap",
                        method="update",
                    ),
                    dict(
                        args=[{"visible": [False, True, True]}],
                        label="Pontos Individuais",
                        method="update",
                    ),
                ],
                direction="down",
                showactive=True,
                x=0.1,
                y=1.15,
            )
        ],
    )

    return fig
