import dash
from assets import static
import dash_bootstrap_components as dbc
from flask import request
import uuid
import json

app = dash.Dash(
    __name__,
    external_stylesheets=[
        static.Colors.theme,
        "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.11.1/font/bootstrap-icons.min.css",
    ],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks="initial_duplicate",
)
app.title = 'ServerBI - CTA Sistemas'
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        {%favicon%}
        {%css%}
        <script src='https://html2canvas.hertzen.com/dist/html2canvas.min.js'></script>
        <link rel='icon' type='image/png' href='/assets/imgs/cta.ico'>
        <meta name="viewport" content="width=device-width, initial-scale=0.8">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
server = app.server


@server.route("/set_biexpress", methods=["POST"])
def set_data():
    if not request.is_json:
        return {"status": "Erro", "message": "Requisição não é JSON"}
    data = request.json
    session_id = str(uuid.uuid4())
    session_control[session_id] = {
        "token": data.get("token"),
        "dtDe": data.get("dtDe"),
        "dtA": data.get("dtA"),
        "guid": session_id,
        "id": data.get("id"),
    }

    return {"status": "Sucesso", "session_id": session_id}

session_control = {}
session_dataframes_cta_express = {}
session_dataframes_cta_checkout = {}
