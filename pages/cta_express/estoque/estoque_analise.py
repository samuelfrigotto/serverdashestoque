"""
pages/cta_express/estoque/estoque_analysis.py
Módulo responsável pela análise de dados de estoque
"""

import pandas as pd
from utils import conversores
from .estoque_data import EstoqueColumns

def identificar_produtos_estoque_baixo(df_estoque, limite_estoque_baixo):
    """
    Identifica produtos com estoque baixo seguindo padrão do projeto.
    """
    if df_estoque is None or df_estoque.empty or EstoqueColumns.ESTOQUE not in df_estoque.columns:
        return pd.DataFrame()

    try:
        limite = float(limite_estoque_baixo)
    except (ValueError, TypeError):
        print(f"Limite de estoque baixo inválido: {limite_estoque_baixo}")
        return pd.DataFrame()

    df_copia = df_estoque.copy()
    df_copia['EstoqueNum'] = pd.to_numeric(df_copia[EstoqueColumns.ESTOQUE], errors='coerce')
    
    df_baixo = df_copia[
        (df_copia['EstoqueNum'].notna()) & 
        (df_copia['EstoqueNum'] <= limite)
    ].copy()
    
    return df_baixo.drop(columns=['EstoqueNum'], errors='ignore')

def gerar_sugestao_compras(df, limite_baixo=10, limite_medio=100, dias_estoque_alerta=30):
    """
    Gera sugestões de compra baseadas no estoque e vendas.
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    df_analise = df.copy()
    
    # Converter colunas para numérico usando padrão do projeto
    df_analise[EstoqueColumns.ESTOQUE] = pd.to_numeric(
        df_analise[EstoqueColumns.ESTOQUE], errors='coerce'
    ).fillna(0)
    df_analise[EstoqueColumns.VENDA_MENSAL] = pd.to_numeric(
        df_analise[EstoqueColumns.VENDA_MENSAL], errors='coerce'
    ).fillna(0)
    df_analise[EstoqueColumns.DIAS_ESTOQUE] = pd.to_numeric(
        df_analise[EstoqueColumns.DIAS_ESTOQUE], errors='coerce'
    ).fillna(0)
    
    # Filtrar apenas produtos com vendas
    df_relevantes = df_analise[df_analise[EstoqueColumns.VENDA_MENSAL] > 0].copy()
    
    if df_relevantes.empty:
        return pd.DataFrame()
    
    def determinar_prioridade(row):
        estoque = row[EstoqueColumns.ESTOQUE]
        dias = row[EstoqueColumns.DIAS_ESTOQUE]
        
        # Critérios específicos seguindo padrão do projeto
        estoque_critico = estoque <= limite_baixo
        estoque_medio = limite_baixo < estoque <= limite_medio
        
        dias_muito_criticos = dias <= 15
        dias_criticos = 15 < dias <= dias_estoque_alerta
        dias_atenção = dias_estoque_alerta < dias <= 45
        
        # Forte recomendação: casos críticos
        if estoque_critico and dias_muito_criticos:
            return 'Forte Recomendação'
        
        # Recomendado: situações problemáticas
        elif (estoque_critico or dias_criticos or 
              (estoque_medio and dias_atenção) or 
              (estoque_critico and dias <= 30)):
            return 'Recomendado'
        
        # Monitorar: situações controladas
        else:
            return 'Monitorar'
    
    df_relevantes['Prioridade'] = df_relevantes.apply(determinar_prioridade, axis=1)
    
    def calcular_sugestao_compra(row):
        venda_diaria = row[EstoqueColumns.VENDA_MENSAL] / 30
        estoque_atual = row[EstoqueColumns.ESTOQUE]
        
        # Definir dias de cobertura baseado na prioridade
        if row['Prioridade'] == 'Forte Recomendação':
            dias_cobertura_desejados = 60
        elif row['Prioridade'] == 'Recomendado':
            dias_cobertura_desejados = 45
        else:
            dias_cobertura_desejados = 30
        
        # Calcular estoque ideal
        estoque_ideal = venda_diaria * dias_cobertura_desejados
        quantidade_necessaria = estoque_ideal - estoque_atual
        
        if quantidade_necessaria <= 0:
            return 0
        
        # Arredondar para múltiplos de 5
        quantidade_sugerida = max(5, int(quantidade_necessaria / 5) * 5)
        return quantidade_sugerida
    
    # Calcular quantidade sugerida
    df_relevantes['QtdSugerida'] = df_relevantes.apply(calcular_sugestao_compra, axis=1)
    
    # Filtrar apenas produtos que precisam de compra
    df_relevantes = df_relevantes[df_relevantes['QtdSugerida'] > 0].copy()
    
    if df_relevantes.empty:
        return pd.DataFrame()
    
    # Criar coluna formatada seguindo padrão do projeto
    df_relevantes['SugestaoCompraFormatada'] = df_relevantes.apply(
        lambda row: f"{conversores.inteiroValores(row['QtdSugerida'])} {row[EstoqueColumns.UNIDADE]}" 
        if pd.notna(row[EstoqueColumns.UNIDADE]) and str(row[EstoqueColumns.UNIDADE]).strip() != ''
        else f"{conversores.inteiroValores(row['QtdSugerida'])} un",
        axis=1
    )
    
    # Ordenar por prioridade
    ordem_prioridade = ['Forte Recomendação', 'Recomendado', 'Monitorar']
    df_relevantes['PrioridadeOrdem'] = df_relevantes['Prioridade'].map({
        p: i for i, p in enumerate(ordem_prioridade)
    })
    df_relevantes = df_relevantes.sort_values(
        by=['PrioridadeOrdem', 'QtdSugerida', EstoqueColumns.DIAS_ESTOQUE],
        ascending=[True, False, True]
    )
    
    # Selecionar colunas para retorno
    colunas_retorno = [
        EstoqueColumns.CODIGO, 
        EstoqueColumns.PRODUTO, 
        EstoqueColumns.UNIDADE, 
        EstoqueColumns.ESTOQUE, 
        EstoqueColumns.VENDA_MENSAL,
        EstoqueColumns.DIAS_ESTOQUE, 
        'Prioridade', 
        'SugestaoCompraFormatada'
    ]
    
    df_final = df_relevantes[colunas_retorno].copy()
    df_final.rename(columns={'SugestaoCompraFormatada': 'Sugestão Compra'}, inplace=True)
    
    return df_final

def calcular_metricas_header(df_filtrado):
    """
    Calcula métricas para o header seguindo padrão do projeto.
    """
    if df_filtrado is None or df_filtrado.empty:
        return {
            "Total de SKUs": {"icone": "bi bi-upc-scan", "valor": "0"},
            "Estoque Total": {"icone": "bi bi-archive-fill", "valor": "0"},
            "Categorias": {"icone": "bi bi-tags-fill", "valor": "0"},
            "Grupos": {"icone": "bi bi-diagram-3-fill", "valor": "0"},
        }
    
    # Calcular métricas usando conversores do projeto
    total_skus = df_filtrado[EstoqueColumns.CODIGO].nunique()
    qtd_total_estoque = pd.to_numeric(
        df_filtrado[EstoqueColumns.ESTOQUE], errors='coerce'
    ).fillna(0).sum()
    num_categorias = df_filtrado[EstoqueColumns.CATEGORIA].nunique()
    num_grupos = df_filtrado[EstoqueColumns.GRUPO].nunique()
    
    return {
        "Total de SKUs": {
            "icone": "bi bi-upc-scan",
            "valor": conversores.MetricInteiroValores(total_skus)
        },
        "Estoque Total": {
            "icone": "bi bi-archive-fill",
            "valor": conversores.MetricInteiroValores(int(qtd_total_estoque))
        },
        "Categorias": {
            "icone": "bi bi-tags-fill",
            "valor": conversores.MetricInteiroValores(num_categorias)
        },
        "Grupos": {
            "icone": "bi bi-diagram-3-fill",
            "valor": conversores.MetricInteiroValores(num_grupos)
        },
    }

def preparar_opcoes_filtros(df_completo):
    """
    Prepara opções para filtros seguindo padrão do projeto.
    """
    if df_completo is None or df_completo.empty:
        return [], []
    
    opcoes_categoria = [
        {'label': str(cat), 'value': str(cat)} 
        for cat in sorted(df_completo[EstoqueColumns.CATEGORIA].dropna().unique())
    ]
    opcoes_grupo = [
        {'label': str(grp), 'value': str(grp)} 
        for grp in sorted(df_completo[EstoqueColumns.GRUPO].dropna().unique())
    ]
    
    return opcoes_categoria, opcoes_grupo

def preparar_opcoes_exclusao(df_completo):
    """
    Prepara opções para exclusões seguindo padrão do projeto.
    """
    if df_completo is None or df_completo.empty:
        return [], [], []
    
    opcoes_grupos_excluir = [
        {'label': str(grp), 'value': str(grp)} 
        for grp in sorted(df_completo[EstoqueColumns.GRUPO].dropna().unique())
    ]
    opcoes_categorias_excluir = [
        {'label': str(cat), 'value': str(cat)} 
        for cat in sorted(df_completo[EstoqueColumns.CATEGORIA].dropna().unique())
    ]
    
    produtos_unicos = df_completo.drop_duplicates(subset=[EstoqueColumns.CODIGO])
    opcoes_produtos_excluir = sorted([
        {
            'label': f"{row[EstoqueColumns.PRODUTO]} (Cód: {row[EstoqueColumns.CODIGO]})", 
            'value': str(row[EstoqueColumns.CODIGO])
        } 
        for index, row in produtos_unicos.iterrows() 
        if pd.notna(row[EstoqueColumns.CODIGO]) and str(row[EstoqueColumns.CODIGO]).strip() != ''
    ], key=lambda x: x['label'])
    
    return opcoes_grupos_excluir, opcoes_categorias_excluir, opcoes_produtos_excluir

def obter_produtos_previsao_estoque(df, dias_maximos=60):
    """
    Obtém produtos com previsão de estoque crítica.
    """
    if (df is None or df.empty or 
        EstoqueColumns.DIAS_ESTOQUE not in df.columns or 
        EstoqueColumns.PRODUTO not in df.columns or 
        EstoqueColumns.ESTOQUE not in df.columns):
        return pd.DataFrame()
    
    df_plot = df.copy()
    df_plot[EstoqueColumns.DIAS_ESTOQUE] = pd.to_numeric(
        df_plot[EstoqueColumns.DIAS_ESTOQUE], errors='coerce'
    )
    df_plot[EstoqueColumns.ESTOQUE] = pd.to_numeric(
        df_plot[EstoqueColumns.ESTOQUE], errors='coerce'
    )
    
    # Filtrar produtos com previsão válida
    df_filtrado = df_plot[
        (df_plot[EstoqueColumns.DIAS_ESTOQUE] > 0) & 
        (df_plot[EstoqueColumns.DIAS_ESTOQUE] <= dias_maximos) &
        (df_plot[EstoqueColumns.ESTOQUE] > 0) &
        (df_plot[EstoqueColumns.DIAS_ESTOQUE].notna())
    ]
    
    if df_filtrado.empty:
        return pd.DataFrame()
    
    # Ordenar por dias de estoque crescente
    df_filtrado = df_filtrado.sort_values(EstoqueColumns.DIAS_ESTOQUE, ascending=True)
    
    # Formatar colunas usando conversores do projeto
    df_filtrado[EstoqueColumns.DIAS_ESTOQUE] = df_filtrado[EstoqueColumns.DIAS_ESTOQUE].round(1)
    df_filtrado[EstoqueColumns.ESTOQUE] = df_filtrado[EstoqueColumns.ESTOQUE].round(0)
    
    return df_filtrado

def calcular_estatisticas_nivel_estoque(df, limite_baixo, limite_medio):
    """
    Calcula estatísticas por nível de estoque.
    """
    if df is None or df.empty or EstoqueColumns.ESTOQUE not in df.columns:
        return {"Baixo": 0, "Médio": 0, "Alto": 0}
    
    df_plot = df.copy()
    df_plot['EstoqueNum'] = pd.to_numeric(df_plot[EstoqueColumns.ESTOQUE], errors='coerce')
    
    try:
        lim_b = float(limite_baixo)
        lim_m = float(limite_medio)
    except (ValueError, TypeError):
        return {"Baixo": 0, "Médio": 0, "Alto": 0}
    
    baixo = len(df_plot[df_plot['EstoqueNum'] <= lim_b])
    medio = len(df_plot[(df_plot['EstoqueNum'] > lim_b) & (df_plot['EstoqueNum'] <= lim_m)])
    alto = len(df_plot[df_plot['EstoqueNum'] > lim_m])
    
    return {"Baixo": baixo, "Médio": medio, "Alto": alto}