"""
pages/cta_express/estoque/estoque_graficos.py
Módulo responsável pela criação de gráficos do estoque
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from assets.static import Colors, Graphcs
from stylesDocs.style import styleConfig
from utils import conversores
from .estoque_data import EstoqueColumns

# Configurações de estilo seguindo padrão do projeto
styleColors = styleConfig(Colors.themecolor)
globalTemplate = Graphcs.globalTemplate

def criar_figura_vazia(titulo="Sem dados para exibir", height=None):
    """Cria figura vazia seguindo padrão do projeto."""
    fig = go.Figure()
    fig.update_layout(
        title_text=titulo,
        title_x=0.5,
        xaxis={"visible": False},
        yaxis={"visible": False},
        paper_bgcolor=styleColors.back_pri_color,
        plot_bgcolor=styleColors.back_pri_color,
        font={"color": styleColors.text_color},
        annotations=[{
            "text": titulo, 
            "xref": "paper", 
            "yref": "paper",
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

    # Tentar ordenar numericamente seguindo padrão do projeto
    try:
        df_agrupado['OrdemNumerica'] = df_agrupado[EstoqueColumns.GRUPO].str.extract(r'^(\d+)').astype(float)
        df_agrupado = df_agrupado.sort_values(by='OrdemNumerica', ascending=True)
    except Exception:
        df_agrupado = df_agrupado.sort_values(by=EstoqueColumns.GRUPO, ascending=True)
    
    # Aplicar abreviação seguindo padrão do projeto
    df_agrupado[EstoqueColumns.GRUPO] = df_agrupado[EstoqueColumns.GRUPO].apply(
        conversores.abreviar
    )
    
    fig = px.line(
        df_agrupado, 
        x=EstoqueColumns.GRUPO, 
        y=EstoqueColumns.ESTOQUE, 
        markers=True, 
        title='Volume de Estoque por Grupo',
        labels={
            EstoqueColumns.ESTOQUE: 'Quantidade Total em Estoque', 
            EstoqueColumns.GRUPO: 'Grupo'
        },
        height=Graphcs.pxGraficos
    )
    
    # Aplicar cores seguindo padrão do projeto
    fig.update_traces(
        line=dict(width=2.5, shape='spline', color=Graphcs.defaultColor),
        marker=dict(size=8, symbol='circle', color=Graphcs.defaultColor),
        fill='tozeroy',
        fillcolor=f'rgba(255, 127, 42, 0.2)'
    )
    
    fig.update_layout(globalTemplate)
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Grupos de Produto",
        yaxis_title="Quantidade Total em Estoque",
        showlegend=False
    )
    
    return fig

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
        lambda x: conversores.abreviar(x, 20)
    )
    
    data_para_pie = [
        {'NomeExibicao': row['NomeExibicao'], 'Estoque': row[EstoqueColumns.ESTOQUE]} 
        for _, row in top_n_df.iterrows()
    ]
    
    if estoque_outros > 0.001:
        data_para_pie.append({'NomeExibicao': 'Outros Produtos', 'Estoque': estoque_outros})
    
    if not data_para_pie:
        return criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem dados para gráfico)", height=height)
        
    df_pie = pd.DataFrame(data_para_pie)
        
    fig = px.pie(
        df_pie, 
        values='Estoque', 
        names='NomeExibicao', 
        title=f'Participação dos Top {n} Produtos no Estoque (+ Outros)', 
        hole=.4,
        labels={'Estoque': 'Quantidade em Estoque', 'NomeExibicao': 'Produto/Segmento'},
        color_discrete_sequence=Colors.ORANGE_COLORS
    )
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label', 
        insidetextorientation='radial',
        pull=[0.05 if nome != 'Outros Produtos' else 0 for nome in df_pie['NomeExibicao']]
    )
    
    fig.update_layout(globalTemplate)
    fig.update_layout(
        title_x=0.5,
        height=height if height else Graphcs.pxGraficos
    )
    
    return fig

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
            return 'Desconhecido (Limites Inválidos)'
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

    # Definir cores seguindo padrão do projeto
    mapa_cores = {
        f'Baixo (≤{float(limite_baixo):g})': Colors.colorGraphcs,
        f'Médio ({float(limite_baixo):g} < E ≤ {float(limite_medio):g})': '#FFA500',
        f'Alto (>{float(limite_medio):g})': '#FFD700',
        'Desconhecido': '#D3D3D3',
        'Desconhecido (Limites Inválidos)': '#A9A9A9'
    }

    fig = px.bar(
        contagem_niveis, 
        x='NivelEstoque', 
        y='Contagem', 
        title='Produtos por Nível de Estoque',
        labels={'Contagem': 'Nº de Produtos', 'NivelEstoque': 'Nível de Estoque'},
        color='NivelEstoque',
        color_discrete_map=mapa_cores
    )
    
    fig.update_traces(textposition='outside')
    fig.update_layout(globalTemplate)
    fig.update_layout(
        showlegend=False,
        title_x=0.5,
        xaxis_title=None,
        height=height if height else Graphcs.pxGraficos
    )
    
    return fig

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
    
    # Aplicar abreviação seguindo padrão do projeto
    contagem_categorias_top_n[EstoqueColumns.CATEGORIA] = (
        contagem_categorias_top_n[EstoqueColumns.CATEGORIA].apply(conversores.abreviar)
    )

    fig = px.bar(
        contagem_categorias_top_n, 
        y=EstoqueColumns.CATEGORIA, 
        x='NumeroDeProdutosBaixos', 
        orientation='h',
        title=f'Top {top_n} Categorias por Nº de Produtos em Estoque Baixo',
        labels={
            'NumeroDeProdutosBaixos': 'Nº de Produtos Baixos', 
            EstoqueColumns.CATEGORIA: 'Categoria'
        },
        color_discrete_sequence=[Graphcs.defaultColor]
    )
    
    fig.update_traces(textposition='outside')
    fig.update_layout(globalTemplate)
    fig.update_layout(
        title_x=0.5,
        height=Graphcs.pxGraficos
    )
    
    return fig

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

    produtos_populares_df = df_plot[df_plot['VendaMensalNum'] > 0].nlargest(n, 'VendaMensalNum')
    
    if produtos_populares_df.empty:
        return criar_figura_vazia(f"Venda vs. Estoque dos Top {n} Produtos (Sem produtos com vendas)")

    produtos_populares_df = produtos_populares_df.sort_values(by='VendaMensalNum', ascending=False)
    
    # Aplicar abreviação se solicitado seguindo padrão do projeto
    if abreviar_nomes:
        x_axis_values = produtos_populares_df[EstoqueColumns.PRODUTO].apply(
            lambda x: conversores.abreviar(x, 15)
        )
    else:
        x_axis_values = produtos_populares_df[EstoqueColumns.PRODUTO]

    # Usar cores do projeto
    cor_estoque = Graphcs.defaultColor
    cor_vendas = '#DC3545'

    trace_estoque = go.Bar(
        name='Estoque',
        x=x_axis_values,
        y=produtos_populares_df['EstoqueNum'],
        marker_color=cor_estoque
    )
    
    trace_vendas = go.Bar(
        name='Vendas no Mês',
        x=x_axis_values,
        y=produtos_populares_df['VendaMensalNum'],
        marker_color=cor_vendas
    )

    fig = go.Figure(data=[trace_estoque, trace_vendas])

    fig.update_layout(globalTemplate)
    fig.update_layout(
        barmode='group',
        title_text=f'Estoque vs. Venda Mensal (Top {produtos_populares_df.shape[0]} Produtos Populares)',
        title_x=0.5,
        xaxis_title=None,
        yaxis_title="Quantidade",
        showlegend=True,
        height=Graphcs.pxGraficos
    )

    return fig

def criar_grafico_treemap_estoque_grupo(df_filtrado):
    """Cria treemap de estoque por grupo seguindo padrão do projeto."""
    titulo_grafico = "Estoque por Grupo (Treemap)"
    nova_altura_grafico = 450

    if (df_filtrado.empty or 
        EstoqueColumns.GRUPO not in df_filtrado.columns or 
        EstoqueColumns.ESTOQUE not in df_filtrado.columns):
        return criar_figura_vazia(f"{titulo_grafico} - Sem dados", nova_altura_grafico)

    df_filtrado = df_filtrado.copy()
    df_filtrado[EstoqueColumns.ESTOQUE] = pd.to_numeric(
        df_filtrado[EstoqueColumns.ESTOQUE], errors='coerce'
    ).fillna(0)
    df_para_treemap = df_filtrado[df_filtrado[EstoqueColumns.ESTOQUE] > 0].copy()

    if df_para_treemap.empty:
        return criar_figura_vazia(f"{titulo_grafico} - Sem dados positivos", nova_altura_grafico)

    df_para_treemap['NomeGrupo'] = df_para_treemap[EstoqueColumns.GRUPO].str.replace(
        r'^\d+\s*', '', regex=True
    )

    fig = px.treemap(
        df_para_treemap, 
        path=[px.Constant("Todos os Grupos"), 'NomeGrupo'], 
        values=EstoqueColumns.ESTOQUE, 
        title=titulo_grafico,
        color=EstoqueColumns.ESTOQUE,
        color_continuous_scale=Colors.ORANGE_COLORS,
        custom_data=['NomeGrupo', EstoqueColumns.ESTOQUE]
    )
    
    fig.update_traces(
        textinfo='label + percent root',
        hovertemplate='<b>%{customdata[0]}</b><br>Estoque: %{customdata[1]:,.0f}<extra></extra>',
        textposition='middle center',
        textfont=dict(family="Arial Black, sans-serif", size=11, color="black"),
        marker_line_width=1,
        marker_line_color='rgba(255,255,255,0.5)'
    )
    
    fig.update_layout(
        height=nova_altura_grafico,
        paper_bgcolor=styleColors.back_pri_color,
        plot_bgcolor=styleColors.back_pri_color,
        font_color=styleColors.text_color,
        title_font_size=18,
        title_x=0.5
    )
    
    return fig

def criar_grafico_produtos_sem_venda_grupo(df):
    """Cria treemap dos produtos sem venda agrupados por grupo seguindo padrão do projeto."""
    titulo_grafico = "Produtos Sem Venda por Grupo"
    nova_altura_grafico = 450

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

    # Usar a quantidade de produtos sem venda como valor do treemap
    fig = px.treemap(
        df_agrupado, 
        path=[px.Constant("Todos os Grupos"), 'NomeGrupo'], 
        values='QtdProdutosSemVenda', 
        title=titulo_grafico,
        color='EstoqueParado',
        color_continuous_scale=px.colors.sequential.Reds,
        custom_data=['NomeGrupo', 'QtdProdutosSemVenda', 'EstoqueParado']
    )
    
    fig.update_traces(
        textinfo='label + value',
        hovertemplate='<b>%{customdata[0]}</b><br>Produtos sem venda: %{customdata[1]}<br>Estoque parado: %{customdata[2]:,.0f}<extra></extra>',
        textposition='middle center',
        textfont=dict(family="Arial Black, sans-serif", size=11, color="black"),
        marker_line_width=1,
        marker_line_color='rgba(255,255,255,0.5)'
    )
    
    fig.update_layout(
        height=nova_altura_grafico,
        paper_bgcolor=styleColors.back_pri_color,
        plot_bgcolor=styleColors.back_pri_color,
        font_color=styleColors.text_color,
        title_font_size=18,
        title_x=0.5
    )
    
    return fig