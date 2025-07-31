from dash import html, dcc
import dash_bootstrap_components as dbc
from pages.cta_express.temp_entregas import temp_entregas
from assets.static import Settings

pageTag = "CETPentregas_"
layout = html.Div(
    [
        dcc.Store(id=f"{pageTag}update", data=-99, storage_type=Settings.StoreConfig),
        html.Div(id=f"{pageTag}header"),
        dbc.Row([html.Div(id=f"{pageTag}row_dash1")], class_name="mt-2"),
        dbc.Row([html.Div(id=f"{pageTag}row_dash2")], class_name="mt-2"),
    ]
)
