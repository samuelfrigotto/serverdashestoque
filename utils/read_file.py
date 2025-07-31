import os
import sys
import pandas as pd
import json
from io import StringIO

if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath("index.py"))


def read_csv(caminho_csv: str) -> pd.DataFrame:
    try:
        csv_path = os.path.join(base_path, "db", caminho_csv)
        return pd.read_csv(
            filepath_or_buffer=csv_path,
            dayfirst=True,
            sep=";",
            decimal=",",
            encoding="utf8",
            low_memory=False,
            on_bad_lines="skip",
        )
    except Exception as e:
        print(e)
        return pd.DataFrame()


def read_json(caminho_json: str) -> pd.DataFrame:
    try:
        json_path = os.path.join(base_path, "db", caminho_json)
        with open(json_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
        key = next(iter(json_data))
        data = json_data[key]
        df = pd.DataFrame(data)

        return df
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {json_path}")
    except ValueError as e:
        print(f"Erro ao decodificar JSON: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    return pd.DataFrame()
