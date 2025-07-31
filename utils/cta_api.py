import requests
import json
from datetime import datetime

# Definir a URL base e o ID
BIExpress = "http://159.112.183.102:9021/api/v3.0.0/GetBIExpress/"

def GetBIExpress(id: int, token: str, guid: str, dtDe: str, dtA: str):
    params = {"token": token, "guid": guid, "datDe": dtDe, "datA": dtA}
    print(f"enviando requisição as {datetime.now().time()}")
    response = requests.get(f"{BIExpress}{id}", params=params, verify=False)
    print(f"recebemos requisição as {datetime.now().time()}")

    if response.status_code == 200:
        response.encoding = 'utf-8'
        print(response)
        return json.loads(json.dumps(response.json(), ensure_ascii=False))
    else:
        print(f"Erro: {response.status_code} - {response.text}")
