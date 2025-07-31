from dash import html, dcc
from assets.static import Settings
from pages.cta_checkout.montador import montador

pageTag = "CCmontador_"
layout = html.Div(
    [
        dcc.Store(id=f"{pageTag}update", data=-99, storage_type=Settings.StoreConfig),
        html.Div(id=f"{pageTag}header"),
        html.Div(id=f"{pageTag}body"),
    ]
)
