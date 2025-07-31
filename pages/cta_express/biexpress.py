from app import app
from dash import Input, Output
from pages.cta_express.cubagem import cubagem_comps
from pages.cta_express.entregas import entregas_comps
from pages.cta_express.temp_entregas import temp_entregas_comps
from pages.cta_express.km import km_comps
from pages.cta_express.resumo import resumo_comps
from pages.cta_express.estoque import estoque_comps

pageTag = "expressBI_"

# Flag para controle de callbacks
estoque_callbacks_registrados = False

@app.callback(
    Output(f"{pageTag}content", "children"),
    Input(f"{pageTag}url", "pathname"),
    prevent_initial_call=True
)
def urlRefresh(pathname):
    global estoque_callbacks_registrados
    
    match pathname:
        case "/cta_express":
            return resumo_comps.layout
        case "/cta_express/estoque":
            if not estoque_callbacks_registrados:
                from pages.cta_express.estoque.estoque import register_callbacks
                register_callbacks(app)
                estoque_callbacks_registrados = True
            return estoque_comps.get_estoque_layout(app)
        case "/cta_express/resumo":
            return resumo_comps.layout
        case "/cta_express/cubagem":
            return cubagem_comps.layout
        case "/cta_express/entregas":
            return entregas_comps.layout
        case "/cta_express/temp_entregas":
            return temp_entregas_comps.layout
        case "/cta_express/km":
            return km_comps.layout