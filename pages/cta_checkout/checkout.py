from app import app
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from pages.cta_checkout.resumo import resumo_comps
from pages.cta_checkout.montador import montador_comps
from pages.cta_checkout.conferente import conferente_comps
from assets.static import packCode


pageTag = "checkout_"


@app.callback(
    Output(f"{pageTag}content", "children"), Input(f"{pageTag}url", "pathname")
)
def urlRefresh(pathname):
   match pathname:
        case "/cta_checkout":
            return resumo_comps.layout
        case "/cta_checkout/resumo":
            return resumo_comps.layout
        case "/cta_checkout/montador":
            return montador_comps.layout
        case "/cta_checkout/conferente":
            return conferente_comps.layout
        