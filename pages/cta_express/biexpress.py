"""
pages/cta_express/biexpress.py
Roteamento principal do CTA Express com correção de bugs
"""

from app import app
from dash import Input, Output
from pages.cta_express.cubagem import cubagem_comps
from pages.cta_express.entregas import entregas_comps
from pages.cta_express.temp_entregas import temp_entregas_comps
from pages.cta_express.km import km_comps
from pages.cta_express.resumo import resumo_comps
from pages.cta_express.estoque import estoque_comps

pageTag = "expressBI_"

# Flag global para controle de callbacks - correção do bug
_callbacks_registrados = {
    'estoque': False
}

@app.callback(
    Output(f"{pageTag}content", "children"),
    Input(f"{pageTag}url", "pathname"),
    prevent_initial_call=True
)
def urlRefresh(pathname):
    """
    Roteamento principal com correção de bug de inicialização.
    Garante que os callbacks sejam registrados apenas uma vez.
    """
    global _callbacks_registrados
    
    match pathname:
        case "/cta_express":
            return resumo_comps.layout
            
        case "/cta_express/estoque":
            # Correção do bug: registrar callbacks na primeira chamada
            if not _callbacks_registrados['estoque']:
                try:
                    from pages.cta_express.estoque.estoque import register_callbacks
                    register_callbacks(app)
                    _callbacks_registrados['estoque'] = True
                    print("Callbacks do estoque registrados com sucesso")
                except Exception as e:
                    print(f"Erro ao registrar callbacks do estoque: {e}")
                    # Em caso de erro, ainda retorna o layout mas sem callbacks
            
            # Retorna o layout do estoque
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
            
        case _:
            # Rota padrão
            return resumo_comps.layout

def reset_callbacks():
    """
    Função para resetar o estado dos callbacks (útil para desenvolvimento).
    """
    global _callbacks_registrados
    _callbacks_registrados = {
        'estoque': False
    }