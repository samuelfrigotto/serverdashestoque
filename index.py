from app import app
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from pages.cta_express import biexpress_comps
from pages.cta_checkout import checkout_comps
from pages.loading import loading_comps
from stylesDocs.style import styleConfig
from assets.static import Colors, Settings
import urllib.parse
import os
import sys
from urllib.parse import urlparse, parse_qs
import uuid


if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

css_path = os.path.join(base_path, "assets", "dynamic.css")
os.makedirs(os.path.dirname(css_path), exist_ok=True)

dynamic_css = styleConfig(Colors.themecolor).get_css()
with open(css_path, "w") as css_file:
    css_file.write(dynamic_css)

app.layout = dbc.Container(
    [
        dcc.Store(id="session_data", storage_type=Settings.StoreConfig),
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
    ],
    className="p-2",
    fluid=True,
)


@app.callback(
    Output("session_data", "data"),
    [Input("url", "href")],
    [State("session_data", "data")],
)
def update_session_data(href, session_data):
    if not session_data:
        parsed_url = urlparse(href)
        params = parse_qs(parsed_url.query)
        session_id = params.get("session_id", [str(uuid.uuid4())])[0]
        session_data = {"session_id": session_id, "pathname": "/loading"}
        print(session_data)

    if href:
        parsed_url = urllib.parse.urlparse(href)
        pathname = parsed_url.path or "/loading"
        if pathname == "/":
            pathname = "/loading"
        params = urllib.parse.parse_qs(parsed_url.query)
        session_data.update({"pathname": pathname, "params": params})
    return session_data


@app.callback(Output("page-content", "children"), Input("session_data", "data"))
def display_page(session_data):
    pathname = session_data.get("pathname", "")
    print(f"pathname recebido: {pathname}")  # 👈 adicione isso aqui

    if "/cta_express" in pathname:
        return biexpress_comps.layout
    elif "/loading" in pathname:
        return loading_comps.layout
    elif "/cta_checkout" in pathname:
        return checkout_comps.layout
    else:
        return html.H1("Página não encontrada!")


server = app.server

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=8051)
