from dash import html, dcc
from pages.cta_checkout.conferente import conferente
from assets.static import Settings

pageTag = "CCconferente_"
layout = html.Div(
    [
        dcc.Store(id=f"{pageTag}update", data=-99, storage_type=Settings.StoreConfig),
        html.Div(id=f"{pageTag}header"),
        html.Div(id=f"{pageTag}body"),
    ]
)
