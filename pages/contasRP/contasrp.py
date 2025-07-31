from app import app
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from assets.static import packCode


pageTag = "contasrp_"


@app.callback(
    Output(f"{pageTag}content", "children"), Input(f"{pageTag}url", "pathname")
)
def urlRefresh(pathname):
    match pathname:
        case "/contasrp":
            return resumo_comps.layout
        case "/contasrp/resumo":
            return resumo_comps.layout
        case "/contasrp/cubagem":
            return cubagem_comps.layout
        case "/contasrp/entregas":
            return entregas_comps.layout
        case "/contasrp/temp_entregas":
            return temp_entregas_comps.layout
        case "/contasrp/km":
            return km_comps.layout
