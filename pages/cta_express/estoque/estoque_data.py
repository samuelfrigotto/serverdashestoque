"""
pages/cta_express/estoque/estoque_data.py
Módulo responsável pelo carregamento e gerenciamento de dados do estoque
"""

import pandas as pd
import json
import os
from utils import conversores
from utils import read_file

# Constantes para colunas de dados
class EstoqueColumns:
    CODIGO = "Código"
    PRODUTO = "Produto"
    UNIDADE = "Un"
    ESTOQUE = "Estoque"
    VENDA_MENSAL = "VendaMensal"
    CUSTO_ESTOQUE = "CustoEstoque"
    DIAS_ESTOQUE = "DiasEstoque"
    CATEGORIA = "Categoria"
    GRUPO = "Grupo"

# Configuração global do estoque
CONFIG_ESTOQUE = {
    'caminho_arquivo_csv': "./pages/cta_express/estoque/data/DAMI29-05.csv",
    'config_file_path': "./pages/cta_express/estoque/dashboard_config.json"
}

# Valores padrão para configurações
VALORES_PADRAO_NIVEIS = {
    "limite_estoque_baixo": 10,
    "limite_estoque_medio": 100
}

VALORES_PADRAO_EXCLUSAO = {
    "excluir_grupos": [],
    "excluir_categorias": [],
    "excluir_produtos_codigos": []
}

def _limpar_valor_numerico(serie_valores): 
    """Converte uma série de strings para numérico, tratando separadores e erros."""
    if not pd.api.types.is_string_dtype(serie_valores):
        serie_valores = serie_valores.astype(str)
    
    serie_limpa = serie_valores.str.replace('.', '', regex=False) 
    serie_limpa = serie_limpa.str.replace(',', '.', regex=False)
    return pd.to_numeric(serie_limpa, errors='coerce')

def carregar_dados_estoque():
    """
    Carrega os dados de estoque do CSV, seguindo o padrão do projeto.
    Retorna DataFrame com dados processados ou DataFrame vazio em caso de erro.
    """
    try:
        caminho_arquivo = CONFIG_ESTOQUE['caminho_arquivo_csv']
        
        # Verificar se o arquivo existe
        if not os.path.exists(caminho_arquivo):
            print(f"Arquivo não encontrado: {caminho_arquivo}")
            return pd.DataFrame()
        
        # Carregar dados usando padrão similar ao read_file.py
        df_full = pd.read_csv(
            caminho_arquivo,
            delimiter=';',
            encoding='latin-1',
            skiprows=4,
            usecols=[0, 1, 2, 4, 6, 7, 8],
            header=None,
            low_memory=False,
            dtype=str
        )
        
        # Renomear colunas seguindo padrão do projeto
        df_full.columns = [
            EstoqueColumns.CODIGO, 
            EstoqueColumns.UNIDADE, 
            'Produto_Original', 
            'VendaMensal_Original', 
            'CustoEstoque_Original', 
            'Estoque_Original', 
            'DiasEstoque_Original'
        ]
        
        # Processar hierarquia (categoria e grupo)
        df_full['CategoriaExtraida'] = pd.NA
        df_full['GrupoExtraido'] = pd.NA

        PREFIXO_CATEGORIA = "* Total Categoria :"
        PREFIXO_GRUPO = "* Total GRUPO :"

        for index, row in df_full.iterrows():
            produto_original_strip = row['Produto_Original'].strip() if pd.notna(row['Produto_Original']) else ''
            
            if produto_original_strip.startswith(PREFIXO_CATEGORIA):
                nome_categoria = produto_original_strip[len(PREFIXO_CATEGORIA):].strip()
                df_full.loc[index, 'CategoriaExtraida'] = nome_categoria
            
            if produto_original_strip.startswith(PREFIXO_GRUPO):
                nome_grupo = produto_original_strip[len(PREFIXO_GRUPO):].strip()
                df_full.loc[index, 'GrupoExtraido'] = nome_grupo
        
        # Propagar categoria e grupo
        df_full[EstoqueColumns.CATEGORIA] = df_full['CategoriaExtraida'].bfill()
        df_full[EstoqueColumns.GRUPO] = df_full['GrupoExtraido'].bfill()

        # Filtrar apenas produtos válidos
        df_produtos = df_full.copy()
        df_produtos.dropna(subset=[EstoqueColumns.CODIGO], inplace=True)
        df_produtos[EstoqueColumns.CODIGO] = df_produtos[EstoqueColumns.CODIGO].str.strip()
        df_produtos = df_produtos[df_produtos[EstoqueColumns.CODIGO] != '']

        # Remover linhas de totais
        df_produtos['Produto_Original_strip'] = df_produtos['Produto_Original'].str.strip()
        df_produtos = df_produtos[~df_produtos['Produto_Original_strip'].str.startswith(PREFIXO_CATEGORIA, na=False)]
        df_produtos = df_produtos[~df_produtos['Produto_Original_strip'].str.startswith(PREFIXO_GRUPO, na=False)]
        
        # Selecionar colunas finais
        df_produtos = df_produtos[[
            EstoqueColumns.CODIGO, 
            EstoqueColumns.UNIDADE, 
            'Produto_Original',
            'Estoque_Original', 
            'VendaMensal_Original', 
            'CustoEstoque_Original', 
            'DiasEstoque_Original',
            EstoqueColumns.CATEGORIA, 
            EstoqueColumns.GRUPO
        ]].copy()
        
        # Renomear colunas finais
        df_produtos.rename(columns={
            'Produto_Original': EstoqueColumns.PRODUTO, 
            'Estoque_Original': EstoqueColumns.ESTOQUE,
            'VendaMensal_Original': EstoqueColumns.VENDA_MENSAL,
            'CustoEstoque_Original': EstoqueColumns.CUSTO_ESTOQUE,
            'DiasEstoque_Original': EstoqueColumns.DIAS_ESTOQUE
        }, inplace=True)

        # Converter valores numéricos usando conversores do projeto
        df_produtos[EstoqueColumns.ESTOQUE] = _limpar_valor_numerico(df_produtos[EstoqueColumns.ESTOQUE])
        df_produtos[EstoqueColumns.VENDA_MENSAL] = _limpar_valor_numerico(df_produtos[EstoqueColumns.VENDA_MENSAL])
        df_produtos[EstoqueColumns.CUSTO_ESTOQUE] = _limpar_valor_numerico(df_produtos[EstoqueColumns.CUSTO_ESTOQUE])
        df_produtos[EstoqueColumns.DIAS_ESTOQUE] = _limpar_valor_numerico(df_produtos[EstoqueColumns.DIAS_ESTOQUE])

        print(f"Dados de estoque carregados: {len(df_produtos)} produtos")
        return df_produtos
        
    except Exception as e:
        print(f"Erro ao carregar dados de estoque: {e}")
        return pd.DataFrame()

def _carregar_config_completa():
    """Carrega configuração completa do JSON."""
    config_path = CONFIG_ESTOQUE['config_file_path']
    
    if not os.path.exists(config_path):
        return {**VALORES_PADRAO_NIVEIS, **VALORES_PADRAO_EXCLUSAO}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except (json.JSONDecodeError, Exception) as e:
        print(f"Erro ao ler arquivo de configuração: {e}")
        return {**VALORES_PADRAO_NIVEIS, **VALORES_PADRAO_EXCLUSAO}

def _salvar_config_completa(config_data):
    """Salva configuração completa no JSON."""
    try:
        config_path = CONFIG_ESTOQUE['config_file_path']
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar configuração: {e}")
        return False

def carregar_definicoes_niveis_estoque():
    """Carrega definições de níveis de estoque."""
    config_completa = _carregar_config_completa()
    niveis = {}
    niveis["limite_estoque_baixo"] = int(config_completa.get(
        "limite_estoque_baixo", 
        VALORES_PADRAO_NIVEIS["limite_estoque_baixo"]
    ))
    niveis["limite_estoque_medio"] = int(config_completa.get(
        "limite_estoque_medio", 
        VALORES_PADRAO_NIVEIS["limite_estoque_medio"]
    ))

    # Validar valores
    if not (isinstance(niveis["limite_estoque_baixo"], int) and 
            isinstance(niveis["limite_estoque_medio"], int) and 
            niveis["limite_estoque_baixo"] >= 0 and 
            niveis["limite_estoque_medio"] >= 0 and 
            niveis["limite_estoque_medio"] > niveis["limite_estoque_baixo"]):
        return VALORES_PADRAO_NIVEIS.copy()
    
    return niveis

def salvar_definicoes_niveis_estoque(limite_baixo, limite_medio):
    """Salva definições de níveis de estoque."""
    try:
        val_limite_baixo = int(limite_baixo)
        val_limite_medio = int(limite_medio)

        if val_limite_baixo < 0:
            return False, "Limite para Estoque Baixo não pode ser negativo."
        if val_limite_medio <= val_limite_baixo:
            return False, "Limite para Estoque Médio deve ser maior que o Limite para Estoque Baixo."

        config_completa = _carregar_config_completa()
        config_completa["limite_estoque_baixo"] = val_limite_baixo
        config_completa["limite_estoque_medio"] = val_limite_medio
        
        if _salvar_config_completa(config_completa):
            return True, "Definições de níveis de estoque salvas com sucesso!"
        else:
            return False, "Falha ao salvar o arquivo de configuração."
            
    except (ValueError, TypeError):
        return False, "Valores inválidos. Os limites devem ser números inteiros."
    except Exception as e:
        return False, f"Erro inesperado ao salvar níveis: {str(e)}"

def carregar_configuracoes_exclusao():
    """Carrega configurações de exclusão."""
    config_completa = _carregar_config_completa()
    exclusoes = {}
    exclusoes["excluir_grupos"] = config_completa.get(
        "excluir_grupos", 
        VALORES_PADRAO_EXCLUSAO["excluir_grupos"]
    )
    exclusoes["excluir_categorias"] = config_completa.get(
        "excluir_categorias", 
        VALORES_PADRAO_EXCLUSAO["excluir_categorias"]
    )
    exclusoes["excluir_produtos_codigos"] = config_completa.get(
        "excluir_produtos_codigos", 
        VALORES_PADRAO_EXCLUSAO["excluir_produtos_codigos"]
    )
    
    # Validar tipos
    for key in exclusoes:
        if not isinstance(exclusoes[key], list):
            exclusoes[key] = VALORES_PADRAO_EXCLUSAO.get(key, [])
            
    return exclusoes

def salvar_configuracoes_exclusao(grupos_excluir, categorias_excluir, produtos_codigos_excluir):
    """Salva configurações de exclusão."""
    try:
        lista_grupos = grupos_excluir if grupos_excluir is not None else []
        lista_categorias = categorias_excluir if categorias_excluir is not None else []
        lista_produtos_codigos = produtos_codigos_excluir if produtos_codigos_excluir is not None else []

        # Converter para string
        lista_grupos = [str(g) for g in lista_grupos]
        lista_categorias = [str(c) for c in lista_categorias]
        lista_produtos_codigos = [str(p) for p in lista_produtos_codigos]

        config_completa = _carregar_config_completa()
        config_completa["excluir_grupos"] = lista_grupos
        config_completa["excluir_categorias"] = lista_categorias
        config_completa["excluir_produtos_codigos"] = lista_produtos_codigos

        if _salvar_config_completa(config_completa):
            return True, "Configurações de exclusão salvas com sucesso!"
        else:
            return False, "Falha ao salvar o arquivo de configuração."

    except Exception as e:
        return False, f"Erro inesperado ao salvar exclusões: {str(e)}"

def aplicar_filtros_exclusao(df, config_exclusao):
    """Aplica filtros de exclusão no DataFrame."""
    if df is None or df.empty:
        return df
    
    dff = df.copy()
    
    grupos_a_excluir = config_exclusao.get("excluir_grupos", [])
    categorias_a_excluir = config_exclusao.get("excluir_categorias", [])    
    produtos_codigos_excluir = [str(p) for p in config_exclusao.get("excluir_produtos_codigos", [])]

    if grupos_a_excluir:
        dff = dff[~dff[EstoqueColumns.GRUPO].isin(grupos_a_excluir)]
    if categorias_a_excluir:
        dff = dff[~dff[EstoqueColumns.CATEGORIA].isin(categorias_a_excluir)]
    if produtos_codigos_excluir:
        dff = dff[~dff[EstoqueColumns.CODIGO].astype(str).isin(produtos_codigos_excluir)]
    
    return dff

def aplicar_filtros_interativos(df, categoria_sel=None, grupo_sel=None, produto_sel=None):
    
    """Aplica filtros interativos no DataFrame."""
    if df is None or df.empty:
        return df
    
    dff_filtrado = df.copy()
    
    if categoria_sel:
        dff_filtrado = dff_filtrado[dff_filtrado[EstoqueColumns.CATEGORIA] == categoria_sel]
    if grupo_sel:
        dff_filtrado = dff_filtrado[dff_filtrado[EstoqueColumns.GRUPO] == grupo_sel]
    if produto_sel and produto_sel.strip():
        dff_filtrado = dff_filtrado[dff_filtrado[EstoqueColumns.PRODUTO].str.contains(produto_sel, case=False, na=False)]
    
    return dff_filtrado



def aplicar_filtros_exclusao_header(df, fil_excluir_grupos, fil_excluir_categorias, 
                                   fil_excluir_produtos, limite_baixo_filtro, limite_medio_filtro):
    """Aplica filtros de exclusão do HeaderDash no DataFrame."""
    if df is None or df.empty:
        return df
    
    dff = df.copy()
    
    # Excluir grupos selecionados
    if fil_excluir_grupos and "Nenhum" not in fil_excluir_grupos and len(fil_excluir_grupos) > 0:
        dff = dff[~dff[EstoqueColumns.GRUPO].isin(fil_excluir_grupos)]
    
    # Excluir categorias selecionadas
    if fil_excluir_categorias and "Nenhuma" not in fil_excluir_categorias and len(fil_excluir_categorias) > 0:
        dff = dff[~dff[EstoqueColumns.CATEGORIA].isin(fil_excluir_categorias)]
    
    # Excluir produtos selecionados
    if fil_excluir_produtos and "Nenhum" not in fil_excluir_produtos and len(fil_excluir_produtos) > 0:
        dff = dff[~dff[EstoqueColumns.PRODUTO].isin(fil_excluir_produtos)]
    
    # Os limites de estoque são apenas para definir classificações, não para excluir
    # Eles serão usados nos gráficos e análises, mas não filtram dados aqui
    
    return dff