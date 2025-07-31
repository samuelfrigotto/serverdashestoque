import pandas as pd


def moedaCorrente(Valor: float):
    try:
        Valor_formatado = f"{Valor:,.2f}"
        Valor_formatado = (
            Valor_formatado.replace(",", "v").replace(".", ",").replace("v", ".")
        )
        return f"R$ {Valor_formatado}"
    except:
        return f"R$ {Valor}"


def moedaCorrenteInteiro(Valor: float):
    try:
        Valor_formatado = f"{Valor:,.0f}"
        Valor_formatado = (
            Valor_formatado.replace(",", "v").replace(".", ",").replace("v", ".")
        )
        return f"R$ {Valor_formatado}"
    except:
        return f"R$ {Valor}"


def outrosValores(Valor):
    try:
        Valor_formatado = f"{Valor:,.2f}"
        Valor_formatado = (
            Valor_formatado.replace(",", "v").replace(".", ",").replace("v", ".")
        )
        return f"{Valor_formatado}"
    except:
        return f"{Valor}"


def percentValores(Valor):
    try:
        Valor_formatado = f"{Valor:,.2f}%"
        Valor_formatado = (
            Valor_formatado.replace(",", "v").replace(".", ",").replace("v", ".")
        )
        return f"{Valor_formatado}"
    except:
        return f"{Valor}%"


def getFloat(Valor: str) -> float:
    Valor = Valor.replace(",", ".")
    float_val = float(Valor)
    return float_val


def inteiroValores(Valor):
    try:
        return int(Valor)
    except:
        return f"{Valor}"


def MetricOutrosValores(Valor):
    try:
        Valor_formatado = f"{Valor:,.2f}"
        Valor_formatado = (
            Valor_formatado.replace(",", "v").replace(".", ",").replace("v", ".")
        )
        return f"{Valor_formatado}"
    except:
        return f"{Valor}"


def MetricInteiroValores(Valor):
    try:
        Valor_formatado = f"{Valor:,.0f}"
        Valor_formatado = (
            Valor_formatado.replace(",", "v").replace(".", ",").replace("v", ".")
        )
        return f"{Valor_formatado}"
    except:
        return f"{Valor}"


def MetricMoedaInteiroValores(Valor):
    try:
        Valor_formatado = f"R$ {Valor:,.0f}"
        Valor_formatado = (
            Valor_formatado.replace(",", "v").replace(".", ",").replace("v", ".")
        )
        return f"{Valor_formatado}"
    except:
        return f"{Valor}"


def ContagemDist(df: pd.DataFrame, colunas) -> int:
    return df[colunas].unique().size


def formatar_valor_resumido(valor):
    try:
        if abs(valor) >= 1_000_000_000:
            valor_formatado = f"{valor / 1_000_000_000:.1f} Bi"
        elif abs(valor) >= 1_000_000:
            valor_formatado = f"{valor / 1_000_000:.1f} Mi"
        elif abs(valor) >= 1_000:
            valor_formatado = f"{valor / 1_000:.1f} K"
        else:
            valor_formatado = f"R$ {valor:,.0f}"

        valor_formatado = (
            valor_formatado.replace(",", "v").replace(".", ",").replace("v", ".")
        )
        return valor_formatado
    except Exception as e:
        return str(valor)


def Formatar_hora(minutos: int) -> str:
    dias = minutos // (24 * 60)
    horas = (minutos % (24 * 60)) // 60
    minutos_restantes = minutos % 60
    segundos = 0

    if dias > 0:
        return f"{dias}d {horas:02}:{minutos_restantes:02}:{segundos:02}"
    else:
        return f"{horas:02}:{minutos_restantes:02}:{segundos:02}"


def format_hover(
    fig, df, col_label, col_value_label, col_value, locale_col="valor_formatado"
):
    df[locale_col] = df[col_value].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    fig.update_traces(
        customdata=df[[locale_col]],
        hovertemplate=f"<b>{col_label}:</b> %{{label}}<br><b>{col_value_label}:</b> %{{customdata[0]}}<extra></extra>",
    )


def abreviar(texto, limite: int = 15):
    if len(texto) > limite:
        return texto[: limite - 3] + "..."
    return texto


def selloutConvert(df: pd.DataFrame) -> pd.DataFrame:
    try:

        sellout_D = df[df["Tipo Operação"].isin(["COR", "VEN", "TRO"])]
        df = None
        sellout_D = sellout_D[
            "Distribuidora",
            "Data",
            "Vendedor Pedido",
            "Supervisor Pedido",
            "Vendedor Cadastro",
            "Supervisor Cadastro",
            "Cidade",
            "Tipo Operação",
            "Produto",
            "Quantidade",
            "Caixa Física",
            "Valor Venda",
            "Valor Custo",
            "Tab.Venda",
            "Grupo",
            "Categoria",
            "Marca",
            "Cluster",
            "Canal",
            "Mes&Ano",
            "Quantidade Devolvida",
            "Caixa Fisica Devolvida",
            "Valor Devolvido",
            "Caixa Unitária",
            "Caixa Unitária Devolvida",
            "Meta Caixa Unitária",
            "Ano",
            " Adf. Fin.",
            "Cob. Bol.",
            "Cortado",
            "Eliminado",
            "Substituído",
        ]
        sellout_D = sellout_D[sellout_D["Tipo Operação"].isin(["COR", "VEN", "TRO"])]
    except:
        sellout_D = sellout_D
    sellout_D["Caixa Unitária"] = (
        sellout_D["Caixa Unitária"]
        .astype(str)
        .apply(lambda x: x.replace(",", ".") if isinstance(x, str) else x)
    )
    sellout_D["Caixa Unitária"] = sellout_D["Caixa Unitária"].astype(float)

    sellout_D["Data"] = pd.to_datetime(
        sellout_D["Data"], errors="coerce", format="%d/%m/%Y"
    )

    sellout_D["Meta Caixa Unitária"] = (
        sellout_D["Meta Caixa Unitária"]
        .astype(str)
        .apply(lambda x: x.replace(",", ".") if isinstance(x, str) else x)
    )
    sellout_D["Meta Caixa Unitária"] = sellout_D["Meta Caixa Unitária"].astype(float)

    sellout_D["Caixa Física"] = (
        sellout_D["Caixa Física"]
        .astype(str)
        .apply(lambda x: x.replace(",", ".") if isinstance(x, str) else x)
    )
    sellout_D["Caixa Física"] = sellout_D["Caixa Física"].astype(float)

    sellout_D["Valor Venda"] = (
        sellout_D["Valor Venda"]
        .astype(str)
        .apply(lambda x: x.replace(",", ".") if isinstance(x, str) else x)
    )
    sellout_D["Valor Venda"] = sellout_D["Valor Venda"].astype(float)

    sellout_D["Valor Devolvido"] = (
        sellout_D["Valor Devolvido"]
        .astype(str)
        .apply(lambda x: x.replace(",", ".") if isinstance(x, str) else x)
    )
    sellout_D["Valor Devolvido"] = sellout_D["Valor Devolvido"].astype(float)

    sellout_D["Valor Custo"] = (
        sellout_D["Valor Custo"]
        .astype(str)
        .apply(lambda x: x.replace(",", ".") if isinstance(x, str) else x)
    )
    sellout_D["Valor Custo"] = sellout_D["Valor Custo"].astype(float)

    sellout_D["Quantidade"] = (
        sellout_D["Quantidade"]
        .astype(str)
        .apply(lambda x: x.replace(",", ".") if isinstance(x, str) else x)
    )
    sellout_D["Quantidade"] = sellout_D["Quantidade"].astype(float)

    sellout_D["Quantidade Devolvida"] = (
        sellout_D["Quantidade Devolvida"]
        .astype(str)
        .apply(lambda x: x.replace(",", ".") if isinstance(x, str) else x)
    )
    sellout_D["Quantidade Devolvida"] = sellout_D["Quantidade Devolvida"].astype(float)

    sellout_D["Caixa Unitária Devolvida"] = (
        sellout_D["Caixa Unitária Devolvida"]
        .astype(str)
        .apply(lambda x: x.replace(",", ".") if isinstance(x, str) else x)
    )
    sellout_D["Caixa Unitária Devolvida"] = sellout_D[
        "Caixa Unitária Devolvida"
    ].astype(float)
    try:
        sellout_D["Meta Valor"] = (
            sellout_D["Meta Valor"]
            .astype(str)
            .apply(lambda x: x.replace(",", ".") if isinstance(x, str) else x)
        )
        sellout_D["Meta Valor"] = sellout_D["Meta Valor"].astype(float)
    except:
        sellout_D["Meta Valor"] = sellout_D["Meta Valor"].astype(float)

    colunas_texto = sellout_D.select_dtypes(include=["object", "datetime64"]).columns
    sellout_D = sellout_D.groupby(list(colunas_texto)).sum().reset_index()

    return sellout_D


def FiltrarColuna(df, tabela, filtro):
    df = df[df[tabela].isin(filtro)]
    return df
