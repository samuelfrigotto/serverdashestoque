from dash import html, dcc
import dash_bootstrap_components as dbc
from pages.cta_express.resumo import resumo
from assets.static import Settings

pageTag = "CEresumo_"
layout = html.Div(
    [
        dcc.Store(id=f"{pageTag}update", data=-99, storage_type=Settings.StoreConfig),
        html.Div(
            id=f"{pageTag}header",
            style={
                "position": "sticky",
                "top": "52px",
                "zIndex": "1000",
            },
        ),
        html.Div(id=f"{pageTag}body"),
    ],
)
