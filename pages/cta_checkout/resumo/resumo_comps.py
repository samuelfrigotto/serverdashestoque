from dash import html, dcc
import dash_bootstrap_components as dbc
from pages.cta_checkout.resumo import resumo
from assets.static import Settings

pageTag = "CCresumo_"
layout = html.Div(
    [
        dcc.Store(id=f"{pageTag}update", data=-99, storage_type=Settings.StoreConfig),
        html.Div(id=f"{pageTag}header"),
        html.Div(id=f"{pageTag}body"),
    ]
)
