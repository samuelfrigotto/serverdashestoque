from app import app
from app import session_control as sessions
from app import session_dataframes_cta_express as sessionDF
from dash import html
from dash import Input, Output, State, html
import pandas as pd
import dash
import time
import json
from utils import cta_api
from datetime import datetime
from pages.cta_express.cta_express_globals import variables_data
from utils.conversores import getFloat
import random
from utils import read_file

pageTag = "loading_"

def lowercase_initial_keys(obj):
    if isinstance(obj, dict):
        return {
            k[0].lower() + k[1:] if k else k: lowercase_initial_keys(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [lowercase_initial_keys(item) for item in obj]
    else:
        return obj


@app.callback(
    Output("ret_loading", "children"),
    Output("url", "href"),
    Input(f"{pageTag}url", "search"),
)
def load_session(
    search,
):

    if not search or "?session_id=" not in search:
        return "Erro: Sessão inválida!", dash.no_update

    session_id = search.split("=")[1]

    if  "testebi" in search:
        sessions[session_id] = {
        "token": "",
        "dtDe": "01/12/2024",
        "dtA": "12/12/2024",
        "guid": session_id,
        "id": "3238",
        }
        session_data = sessions[session_id]
        with open('db/BITESTE.json', 'r', encoding='utf-8') as f:
            retornoLocalRaw = json.load(f)
            retornoLocal = lowercase_initial_keys(retornoLocalRaw)
        print(f"Fim as { datetime.now().time()} lendo detalhamento")
        sessionDF[f"{session_id}_detalhamento"] = pd.DataFrame(retornoLocal["itensNFe"])
        print(f"Lendo cargas { datetime.now().time()}")
        sessionDF[f"{session_id}_resumo"] = pd.DataFrame(retornoLocal["cargas"])
        print(f"Fim as { datetime.now().time()}")
        sessionDF[f"{session_id}_detalhamento"] = sessionDF[
            f"{session_id}_detalhamento"
        ].merge(
            sessionDF[f"{session_id}_resumo"][
                [
                    variables_data.Desc_Motorista,
                    variables_data.Desc_Placa,
                    variables_data.Guid_Carga,
                ]
            ],
            on=variables_data.Guid_Carga,
            how="left",
        )

        dt_emissao_df = sessionDF[f"{session_id}_detalhamento"][
        [variables_data.Guid_Carga, variables_data.DT_Emissao]
        ].drop_duplicates(subset=variables_data.Guid_Carga, keep='first').reset_index(drop=True)


        sessionDF[f"{session_id}_resumo"] = sessionDF[f"{session_id}_resumo"].merge(
        dt_emissao_df,
        on=variables_data.Guid_Carga,
        how="left"
        )

        sessionDF[f"{session_id}_detalhamento"][variables_data.cliente_lat]= sessionDF[f"{session_id}_detalhamento"][variables_data.cliente_lat].apply(getFloat)
        sessionDF[f"{session_id}_detalhamento"][variables_data.cliente_log]= sessionDF[f"{session_id}_detalhamento"][variables_data.cliente_log].apply(getFloat)

        return (
            html.Span(f"Carregamento finalizado!"),
            f"/cta_express?session_id={session_id}",
        )


    if session_id not in sessions:
        return "Não há informações para essa sessão. Tente novamente!", dash.no_update

    session_data = sessions[session_id]
    print(session_data)
    sessions.pop(session_id)
    id = session_data.get("id")
    token = session_data.get("token")
    dtDe = session_data.get("dtDe")
    dtA = session_data.get("dtA")
    guid = session_data.get("guid")
    print(f"inicio as { datetime.now().time()}")
    retorno = cta_api.GetBIExpress(id=id, token=token, dtDe=dtDe, dtA=dtA, guid=guid)
    print(f"Fim as { datetime.now().time()} lendo detalhamento")
    sessionDF[f"{session_id}_detalhamento"] = pd.DataFrame(retorno["itensNFe"])
    print(f"Lendo cargas { datetime.now().time()}")
    sessionDF[f"{session_id}_resumo"] = pd.DataFrame(retorno["cargas"])
    print(f"Fim as { datetime.now().time()}")
    sessionDF[f"{session_id}_detalhamento"] = sessionDF[
        f"{session_id}_detalhamento"
    ].merge(
        sessionDF[f"{session_id}_resumo"][
            [
                variables_data.Desc_Motorista,
                variables_data.Desc_Placa,
                variables_data.Guid_Carga,
            ]
        ],
        on=variables_data.Guid_Carga,
        how="left",
    )

    dt_emissao_df = sessionDF[f"{session_id}_detalhamento"][
    [variables_data.Guid_Carga, variables_data.DT_Emissao]
    ].drop_duplicates(subset=variables_data.Guid_Carga, keep='first').reset_index(drop=True)


    sessionDF[f"{session_id}_resumo"] = sessionDF[f"{session_id}_resumo"].merge(
    dt_emissao_df,
    on=variables_data.Guid_Carga,
    how="left"
    )

    sessionDF[f"{session_id}_detalhamento"][variables_data.cliente_lat]= sessionDF[f"{session_id}_detalhamento"][variables_data.cliente_lat].apply(getFloat)
    sessionDF[f"{session_id}_detalhamento"][variables_data.cliente_log]= sessionDF[f"{session_id}_detalhamento"][variables_data.cliente_log].apply(getFloat)

    return (
        html.Span(f"Carregamento finalizado, dados de {dtDe} a {dtA}"),
        f"/cta_express?session_id={guid}",
    )
