"""
pages/cta_express/estoque/estoque_comps.py
Componente de layout do estoque seguindo padrão do projeto
"""

from dash import html, dcc
from assets.static import Settings

pageTag = "CEestoque_"

def get_estoque_layout(app):
    """
    Retorna o layout do estoque seguindo padrão do projeto.
    Corrige o problema de carregamento de dados na primeira visita.
    """
    from .estoque import get_layout
    
    # Layout principal seguindo padrão do projeto
    layout = html.Div([
        dcc.Location(id=f"{pageTag}url", refresh=False),
        dcc.Store(id=f"{pageTag}update", data=-99, storage_type=Settings.StoreConfig),
        
        # Usar o layout principal do módulo estoque
        get_layout(app)
    ])
    
    return layout