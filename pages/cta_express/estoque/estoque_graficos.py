"""
pages/cta_express/estoque/estoque_graficos.py
Módulo responsável pela criação de gráficos do estoque seguindo padrão do projeto
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from assets.static import packCode, Colors, Graphcs
from stylesDocs.style import styleConfig
from utils import conversores
from .estoque_data import EstoqueColumns

# Configurações seguindo padrão do projeto
pageTag = "CEestoque_"
styleColors = styleConfig(Colors.themecolor)
pxGraficos = Graphcs.pxGraficos
globalTemplate = Graphcs.globalTemplate

def criar_figura_vazia(titulo="Sem dados para exibir", height=None):
    """Cria figura vazia seguindo padrão do projeto."""
    fig = go.Figure()
    fig.update_layout(
        title_text=titulo,
        title_x=0.5,
        xaxis={"visible": False},
        yaxis={"visible": False},
        template=globalTemplate,
        annotations=[{
            "text": titulo, 
            "xref": "paper", 
            "yref": "paper",
            "x": 0.5,
            "y": 0.5,
            "showarrow": False, 
            "font": {"size": 16, "color": styleColors.text_color}
        }]
    )
    if height: 
        fig.update_layout(height=height)
    return fig

def criar_grafico_estoque_por_grupo(df):
    """Cria gráfico de estoque por grupo seguindo padrão do projeto."""
    if df.empty or EstoqueColumns.GRUPO not in df.columns or EstoqueColumns.ESTOQUE not in df.columns:
        return criar_figura_vazia("Volume de Estoque por Grupo (Sem Dados)")
    
    df_plot = df.copy()
    df_plot[EstoqueColumns.ESTOQUE] = pd.to_numeric(
        df_plot[EstoqueColumns.ESTOQUE], errors='coerce'
    ).fillna(0)
    
    df_agrupado = df_plot.groupby(EstoqueColumns.GRUPO, as_index=False)[EstoqueColumns.ESTOQUE].sum()
    df_agrupado = df_agrupado[df_agrupado[EstoqueColumns.ESTOQUE] > 0]
    
    if df_agrupado.empty:
        return criar_figura_vazia("Volume de Estoque por Grupo (Sem Estoque > 0)")

    # Ordenar seguindo padrão do projeto
    try:
        df_agrupado['OrdemNumerica'] = df_agrupado[EstoqueColumns.GRUPO].str.extract(r'^(\d+)').astype(float)
        df_agrupado = df_agrupado.sort_values(by='OrdemNumerica', ascending=True)
    except Exception:
        df_agrupado = df_agrupado.sort_values(by=EstoqueColumns.GRUPO, ascending=True)
    
    # Aplicar abreviação seguindo padrão do projeto
    df_agrupado[EstoqueColumns.GRUPO] = df_agrupado[EstoqueColumns.GRUPO].apply(
        conversores.abreviar
    )
    
    # Formatar valores para hover
    df_agrupado["Estoque_Formatado"] = df_agrupado[EstoqueColumns.ESTOQUE].apply(
        conversores.MetricInteiroValores
    )
    
    figDash1 = px.line(
        df_agrupado, 
        x=EstoqueColumns.GRUPO, 
        y=EstoqueColumns.ESTOQUE, 
        markers=True, 
        title='Volume de Estoque por Grupo',
        labels={
            EstoqueColumns.ESTOQUE: 'Quantidade Total em Estoque', 
            EstoqueColumns.GRUPO: 'Grupo'
        },
        hover_data={
            "Estoque_Formatado": True,
            EstoqueColumns.ESTOQUE: False,
            EstoqueColumns.GRUPO: True,
        },
        height=pxGraficos + 100,
        color_discrete_sequence=globalTemplate["colorway"],
        line_shape="spline"
    )
    
    figDash1.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(244, 124, 32, 0.2)'
    )
    
    figDash1.update_layout(globalTemplate)
    figDash1.update_layout(
        title_x=0.5,
        xaxis_title="Grupos de Produto",
        yaxis_title="Quantidade Total em Estoque",
        showlegend=False
    )
    
    return figDash1

def criar_grafico_top_produtos_estoque(df, n=7, height=None):
    """Cria gráfico top produtos por estoque seguindo padrão do projeto."""
    if df.empty or EstoqueColumns.PRODUTO not in df.columns or EstoqueColumns.ESTOQUE not in df.columns:
        return criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem Dados)", height=height)

    df_plot = df.copy()
    df_plot[EstoqueColumns.ESTOQUE] = pd.to_numeric(
        df_plot[EstoqueColumns.ESTOQUE], errors='coerce'
    ).fillna(0)
    df_com_estoque = df_plot[df_plot[EstoqueColumns.ESTOQUE] > 0].copy()

    if df_com_estoque.empty:
        return criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem Estoque > 0)", height=height)

    estoque_total_geral = df_com_estoque[EstoqueColumns.ESTOQUE].sum()
    top_n_df = df_com_estoque.nlargest(n, EstoqueColumns.ESTOQUE)
    
    if top_n_df.empty:
        return criar_figura_vazia(f"Top {n} Produtos por Estoque (Nenhum produto no Top N)", height=height)

    estoque_top_n_soma = top_n_df[EstoqueColumns.ESTOQUE].sum()
    estoque_outros = estoque_total_geral - estoque_top_n_soma
    
    # Aplicar abreviação seguindo padrão do projeto
    top_n_df = top_n_df.copy()
    top_n_df['NomeExibicao'] = top_n_df[EstoqueColumns.PRODUTO].apply(
        lambda x: conversores.abreviar(x, 25)
    )
    
    data_para_pie = []
    for _, row in top_n_df.iterrows():
        data_para_pie.append({
            'NomeExibicao': row['NomeExibicao'], 
            'Estoque': row[EstoqueColumns.ESTOQUE],
            'Estoque_Formatado': conversores.MetricInteiroValores(row[EstoqueColumns.ESTOQUE])
        })
    
    if estoque_outros > 0.001:
        data_para_pie.append({
            'NomeExibicao': 'Outros Produtos', 
            'Estoque': estoque_outros,
            'Estoque_Formatado': conversores.MetricInteiroValores(estoque_outros)
        })
    
    if not data_para_pie:
        return criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem dados para gráfico)", height=height)
        
    df_pie = pd.DataFrame(data_para_pie)
    
    # CORREÇÃO 3: Usar cores alaranjadas para o top produtos
    cores_alaranjadas = [
        '#FF7F0E',  # Laranja principal
        '#FF4500',  # Laranja vermelho
        '#FFB347',  # Laranja claro
        '#FF8C00',  # Laranja escuro
        '#FFA500',  # Laranja médio
        '#FF6347',  # Tomate
        '#FF9500',  # Laranja vibrante
        '#D2691E',  # Chocolate
        '#CD853F'   # Peru
    ]
        
    figDash2 = px.pie(
        df_pie, 
        values='Estoque', 
        names='NomeExibicao', 
        title=f'Top {n} Produtos com Maior Estoque', 
        hole=.4,
        labels={'Estoque': 'Quantidade em Estoque', 'NomeExibicao': 'Produto'},
        hover_data={
            "Estoque_Formatado": True,
            "Estoque": False,
        },
        color_discrete_sequence=cores_alaranjadas,
        height=height if height else pxGraficos
    )
    
    figDash2.update_traces(
        textposition='outside', 
        textinfo='percent+label',
        textfont=dict(size=10, color="black"),
        pull=[0.05 if nome != 'Outros Produtos' else 0 for nome in df_pie['NomeExibicao']]
    )
    
    figDash2.update_layout(globalTemplate)
    figDash2.update_layout(
        title_x=0.5,
        showlegend=False
    )
    
    return figDash2

def criar_grafico_niveis_estoque(df, limite_baixo=10, limite_medio=100, height=None):
    """Cria gráfico de níveis de estoque seguindo padrão do projeto."""
    if df.empty or EstoqueColumns.ESTOQUE not in df.columns:
        return criar_figura_vazia("Produtos por Nível de Estoque", height=height)

    df_plot = df.copy()
    df_plot['EstoqueNum'] = pd.to_numeric(df_plot[EstoqueColumns.ESTOQUE], errors='coerce')
    
    def _classificar_nivel_estoque(estoque_val, limite_baixo, limite_medio):
        try:
            lim_b = float(limite_baixo)
            lim_m = float(limite_medio)
        except (ValueError, TypeError):
            return 'Desconhecido'
        if pd.isna(estoque_val):
            return 'Desconhecido'
        try:
            val = float(estoque_val)
        except (ValueError, TypeError):
            return 'Desconhecido'
        if val <= lim_b:
            return f'Baixo (≤{lim_b:g})'
        elif val <= lim_m:
            return f'Médio ({lim_b:g} < E ≤ {lim_m:g})'
        else: 
            return f'Alto (>{lim_m:g})'
    
    df_plot['NivelEstoque'] = df_plot['EstoqueNum'].apply(
        lambda x: _classificar_nivel_estoque(x, limite_baixo, limite_medio)
    )
    
    contagem_niveis = df_plot['NivelEstoque'].value_counts().reset_index()
    contagem_niveis.columns = ['NivelEstoque', 'Contagem']
    
    if contagem_niveis.empty or contagem_niveis['Contagem'].sum() == 0:
        return criar_figura_vazia("Níveis de Estoque (Sem Produtos para Classificar)", height=height)

    # Formatar valores seguindo padrão do projeto
    contagem_niveis["Contagem_Formatada"] = contagem_niveis['Contagem'].apply(
        conversores.MetricInteiroValores
    )

    # CORREÇÃO 1: Cores diferenciadas em tons de laranja para cada nível
    mapa_cores = {
        f'Baixo (≤{float(limite_baixo):g})': '#FF4500',    # Laranja escuro/vermelho para baixo
        f'Médio ({float(limite_baixo):g} < E ≤ {float(limite_medio):g})': '#FF7F0E',  # Laranja médio
        f'Alto (>{float(limite_medio):g})': '#FFB347',     # Laranja claro para alto
        'Desconhecido': '#D3D3D3'
    }

    figDash3 = px.bar(
        contagem_niveis, 
        x='NivelEstoque', 
        y='Contagem', 
        title='Produtos por Nível de Estoque',
        labels={'Contagem': 'Nº de Produtos', 'NivelEstoque': 'Nível de Estoque'},
        text="Contagem_Formatada",
        hover_data={
            "Contagem_Formatada": True,
            "Contagem": False,
        },
        color='NivelEstoque',
        color_discrete_map=mapa_cores,
        height=height if height else pxGraficos
    )
    
    figDash3.update_traces(textposition='outside')
    figDash3.update_layout(globalTemplate)
    figDash3.update_layout(
        showlegend=False,
        title_x=0.5,
        xaxis_title=None,
        yaxis_title="Nº de Produtos",
        xaxis=dict(tickangle=0)
    )
    
    return figDash3

def criar_grafico_categorias_estoque_baixo(df_estoque_baixo, top_n=10):
    """Cria gráfico de categorias com estoque baixo seguindo padrão do projeto."""
    if (df_estoque_baixo is None or df_estoque_baixo.empty or 
        EstoqueColumns.CATEGORIA not in df_estoque_baixo.columns or 
        EstoqueColumns.CODIGO not in df_estoque_baixo.columns):
        return criar_figura_vazia(f"Categorias com Estoque Baixo (Sem Dados)")

    contagem_categorias = (
        df_estoque_baixo.groupby(EstoqueColumns.CATEGORIA)[EstoqueColumns.CODIGO]
        .nunique()
        .reset_index()
    )
    contagem_categorias.rename(
        columns={EstoqueColumns.CODIGO: 'NumeroDeProdutosBaixos'}, 
        inplace=True
    )
    contagem_categorias_top_n = contagem_categorias.nlargest(top_n, 'NumeroDeProdutosBaixos')
    
    if contagem_categorias_top_n.empty:
        return criar_figura_vazia(f"Categorias com Estoque Baixo (Sem produtos baixos)")

    contagem_categorias_top_n = contagem_categorias_top_n.sort_values(
        by='NumeroDeProdutosBaixos', ascending=True
    )
    
    # Aplicar abreviação e formatação seguindo padrão do projeto
    contagem_categorias_top_n[EstoqueColumns.CATEGORIA] = (
        contagem_categorias_top_n[EstoqueColumns.CATEGORIA].apply(conversores.abreviar)
    )
    contagem_categorias_top_n["Produtos_Formatado"] = (
        contagem_categorias_top_n['NumeroDeProdutosBaixos'].apply(conversores.MetricInteiroValores)
    )

    figDash4 = px.bar(
        contagem_categorias_top_n, 
        y=EstoqueColumns.CATEGORIA, 
        x='NumeroDeProdutosBaixos', 
        orientation='h',
        title=f'Top {top_n} Categorias por Nº de Produtos em Estoque Baixo',
        labels={
            'NumeroDeProdutosBaixos': 'Nº de Produtos Baixos', 
            EstoqueColumns.CATEGORIA: 'Categoria'
        },
        text="Produtos_Formatado",
        hover_data={
            "Produtos_Formatado": True,
            "NumeroDeProdutosBaixos": False,
        },
        color_discrete_sequence=globalTemplate["colorway"],
        height=pxGraficos
    )
    
    figDash4.update_traces(textposition='outside')
    figDash4.update_layout(globalTemplate)
    figDash4.update_layout(
        title_x=0.5
    )
    
    return figDash4

def criar_grafico_estoque_produtos_populares(df, n=7, abreviar_nomes=False):
    """Cria gráfico de estoque vs venda dos produtos populares seguindo padrão do projeto."""
    if (df is None or df.empty or
        EstoqueColumns.PRODUTO not in df.columns or
        EstoqueColumns.VENDA_MENSAL not in df.columns or
        EstoqueColumns.ESTOQUE not in df.columns):
        return criar_figura_vazia(f"Venda vs. Estoque dos Top {n} Produtos (Sem Dados)")

    df_plot = df.copy()
    df_plot['VendaMensalNum'] = pd.to_numeric(
        df_plot[EstoqueColumns.VENDA_MENSAL], errors='coerce'
    ).fillna(0)
    df_plot['EstoqueNum'] = pd.to_numeric(
        df_plot[EstoqueColumns.ESTOQUE], errors='coerce'
    ).fillna(0)

    # Agrupar por produto para evitar duplicatas
    df_agrupado = df_plot.groupby(EstoqueColumns.PRODUTO).agg({
        'VendaMensalNum': 'sum',
        'EstoqueNum': 'sum'
    }).reset_index()

    produtos_populares_df = df_agrupado[df_agrupado['VendaMensalNum'] > 0].nlargest(n, 'VendaMensalNum')

    if produtos_populares_df.empty:
        return criar_figura_vazia(f"Venda vs. Estoque dos Top {n} Produtos (Sem produtos com vendas)")

    produtos_populares_df = produtos_populares_df.sort_values(by='VendaMensalNum', ascending=False)
    
    # Resetar índice para garantir ordem consistente
    produtos_populares_df = produtos_populares_df.reset_index(drop=True)

    # Aplicar abreviação seguindo padrão do projeto
    if abreviar_nomes:
        x_axis_values = produtos_populares_df[EstoqueColumns.PRODUTO].apply(
            lambda x: conversores.abreviar(x, 10)
        )
    else:
        x_axis_values = produtos_populares_df[EstoqueColumns.PRODUTO].apply(
            lambda x: conversores.abreviar(x, 15)
        )
    
    # CORREÇÃO: Verificar e corrigir nomes duplicados após abreviação
    x_axis_values = x_axis_values.tolist()
    valores_unicos = []
    contadores = {}
    
    for i, valor in enumerate(x_axis_values):
        if valor in contadores:
            contadores[valor] += 1
            # Adiciona um sufixo numérico para tornar único
            valor_unico = f"{valor} ({contadores[valor]})"
        else:
            contadores[valor] = 0
            valor_unico = valor
        valores_unicos.append(valor_unico)
    
    x_axis_values = valores_unicos

    # Formatar valores para hover
    produtos_populares_df["Estoque_Formatado"] = produtos_populares_df['EstoqueNum'].apply(
        conversores.MetricInteiroValores
    )
    produtos_populares_df["Vendas_Formatado"] = produtos_populares_df['VendaMensalNum'].apply(
        conversores.MetricInteiroValores
    )

    figDash5 = go.Figure()

    # IMPORTANTE: Converter para lista para garantir alinhamento correto
    figDash5.add_trace(go.Bar(
        name='Estoque',
        x=x_axis_values,  # Já é uma lista
        y=produtos_populares_df['EstoqueNum'].tolist(),  # Converter para lista
        marker_color=globalTemplate["colorway"][0],
        customdata=produtos_populares_df["Estoque_Formatado"].tolist(),  # Converter para lista
        hovertemplate="<b>Estoque</b><br>Quantidade: %{customdata}<extra></extra>"
    ))

    figDash5.add_trace(go.Bar(
        name='Vendas no Mês',
        x=x_axis_values,  # Já é uma lista
        y=produtos_populares_df['VendaMensalNum'].tolist(),  # Converter para lista
        marker_color='#DC3545',
        customdata=produtos_populares_df["Vendas_Formatado"].tolist(),  # Converter para lista
        hovertemplate="<b>Vendas no Mês</b><br>Quantidade: %{customdata}<extra></extra>"
    ))

    figDash5.update_layout(globalTemplate)
    figDash5.update_layout(
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        title_text=f'Estoque vs. Venda Mensal (Top {produtos_populares_df.shape[0]} Produtos Populares)',
        title_x=0.5,
        xaxis_title=None,
        yaxis_title="Quantidade",
        showlegend=True,
        height=pxGraficos + 100,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            tickangle=45,
            tickmode='linear',
            automargin=True
        )
    )

    return figDash5

def criar_grafico_treemap_estoque_grupo(df_filtrado):
    """Cria treemap de estoque por grupo seguindo padrão do projeto."""
    titulo_grafico = "Estoque por Grupo (Treemap)"
    nova_altura_grafico = pxGraficos + 100

    if (df_filtrado.empty or 
        EstoqueColumns.GRUPO not in df_filtrado.columns or 
        EstoqueColumns.ESTOQUE not in df_filtrado.columns):
        return criar_figura_vazia(f"{titulo_grafico} - Sem dados", nova_altura_grafico)

    df_filtrado_copy = df_filtrado.copy()
    df_filtrado_copy[EstoqueColumns.ESTOQUE] = pd.to_numeric(
        df_filtrado_copy[EstoqueColumns.ESTOQUE], errors='coerce'
    ).fillna(0)
    
    # CORREÇÃO 4: Agrupar corretamente por grupo antes de criar o treemap
    df_agrupado = df_filtrado_copy.groupby(EstoqueColumns.GRUPO, as_index=False)[EstoqueColumns.ESTOQUE].sum()
    df_para_treemap = df_agrupado[df_agrupado[EstoqueColumns.ESTOQUE] > 0].copy()

    if df_para_treemap.empty:
        return criar_figura_vazia(f"{titulo_grafico} - Sem dados positivos", nova_altura_grafico)

    # Limpar o nome do grupo removendo números iniciais
    df_para_treemap['NomeGrupo'] = df_para_treemap[EstoqueColumns.GRUPO].str.replace(
        r'^\d+\s*', '', regex=True
    )
    
    # Formatar valores para hover seguindo padrão do projeto
    df_para_treemap['Estoque_Formatado'] = df_para_treemap[EstoqueColumns.ESTOQUE].apply(
        conversores.MetricInteiroValores
    )

    # Ordenar por estoque para garantir consistência
    df_para_treemap = df_para_treemap.sort_values(EstoqueColumns.ESTOQUE, ascending=False)

    figDash6 = px.treemap(
        df_para_treemap, 
        path=[px.Constant("Todos os Grupos"), 'NomeGrupo'], 
        values=EstoqueColumns.ESTOQUE, 
        title=titulo_grafico,
        color=EstoqueColumns.ESTOQUE,
        color_continuous_scale=Colors.ORANGE_COLORS,
        custom_data=['NomeGrupo', 'Estoque_Formatado', EstoqueColumns.ESTOQUE]
    )
    
    figDash6.update_traces(
        textinfo='label + percent root',
        hovertemplate='<b>%{customdata[0]}</b><br>Estoque: %{customdata[1]}<br>Valor Real: %{customdata[2]:,.0f}<extra></extra>',
        textposition='middle center',
        textfont=dict(family="Arial Black, sans-serif", size=11, color="black"),
        marker_line_width=1,
        marker_line_color='rgba(255,255,255,0.5)'
    )
    
    figDash6.update_layout(globalTemplate)
    figDash6.update_layout(
        height=nova_altura_grafico,
        title_font_size=18,
        title_x=0.5
    )
    
    return figDash6

def criar_grafico_produtos_sem_venda_grupo(df):
    """Cria treemap dos produtos sem venda agrupados por grupo seguindo padrão do projeto."""
    titulo_grafico = "Produtos Sem Venda por Grupo"
    nova_altura_grafico = pxGraficos + 50

    if (df.empty or 
        EstoqueColumns.GRUPO not in df.columns or 
        EstoqueColumns.VENDA_MENSAL not in df.columns or 
        EstoqueColumns.ESTOQUE not in df.columns):
        return criar_figura_vazia(f"{titulo_grafico} - Sem dados", nova_altura_grafico)

    df_plot = df.copy()
    df_plot[EstoqueColumns.VENDA_MENSAL] = pd.to_numeric(
        df_plot[EstoqueColumns.VENDA_MENSAL], errors='coerce'
    ).fillna(0)
    df_plot[EstoqueColumns.ESTOQUE] = pd.to_numeric(
        df_plot[EstoqueColumns.ESTOQUE], errors='coerce'
    ).fillna(0)

    # Filtrar apenas produtos sem venda e com estoque
    df_sem_venda = df_plot[
        (df_plot[EstoqueColumns.VENDA_MENSAL] == 0) & 
        (df_plot[EstoqueColumns.ESTOQUE] > 0)
    ].copy()

    if df_sem_venda.empty:
        return criar_figura_vazia(f"{titulo_grafico} - Nenhum produto sem venda", nova_altura_grafico)

    # Agrupar por grupo e contar produtos sem venda
    df_agrupado = df_sem_venda.groupby(EstoqueColumns.GRUPO).agg({
        EstoqueColumns.CODIGO: 'count',  # Contagem de produtos sem venda
        EstoqueColumns.ESTOQUE: 'sum'    # Soma do estoque parado
    }).reset_index()
    
    df_agrupado.columns = [EstoqueColumns.GRUPO, 'QtdProdutosSemVenda', 'EstoqueParado']
    df_agrupado['NomeGrupo'] = df_agrupado[EstoqueColumns.GRUPO].str.replace(
        r'^\d+\s*', '', regex=True
    )
    
    # Formatar valores para hover seguindo padrão do projeto
    df_agrupado['Produtos_Formatado'] = df_agrupado['QtdProdutosSemVenda'].apply(
        conversores.MetricInteiroValores
    )
    df_agrupado['EstoqueParado_Formatado'] = df_agrupado['EstoqueParado'].apply(
        conversores.MetricInteiroValores
    )

    figDash7 = px.treemap(
        df_agrupado, 
        path=[px.Constant("Todos os Grupos"), 'NomeGrupo'], 
        values='QtdProdutosSemVenda', 
        title=titulo_grafico,
        color='EstoqueParado',
        color_continuous_scale=px.colors.sequential.Reds,
        custom_data=['NomeGrupo', 'Produtos_Formatado', 'EstoqueParado_Formatado']
    )
    
    figDash7.update_traces(
        textinfo='label + value',
        hovertemplate='<b>%{customdata[0]}</b><br>Produtos sem venda: %{customdata[1]}<br>Estoque parado: %{customdata[2]}<extra></extra>',
        textposition='middle center',
        textfont=dict(family="Arial Black, sans-serif", size=11, color="black"),
        marker_line_width=1,
        marker_line_color='rgba(255,255,255,0.5)'
    )
    
    figDash7.update_layout(globalTemplate)
    figDash7.update_layout(
        height=nova_altura_grafico,
        title_font_size=18,
        title_x=0.5
    )
    
    return figDash7