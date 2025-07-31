from dash import html, dcc
from assets.static import Settings

pageTag = "CEestoque_"

def get_estoque_layout(app):
    """Retorna o layout do estoque sem inicializar callbacks"""
    from pages.cta_express.estoque.estoque import get_layout
    content_layout = get_layout(app)
    
    return html.Div([
        dcc.Location(id=f"{pageTag}url", refresh=False),
        dcc.Store(id=f"{pageTag}update", data=-99, storage_type=Settings.StoreConfig),
        html.Div(id=f"{pageTag}header"),
        content_layout
    ])