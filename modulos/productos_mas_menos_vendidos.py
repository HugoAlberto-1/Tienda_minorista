import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

def configurar_estilo():
    """Configuración de estilos CSS para el módulo"""
    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_HOVER = "#e8f0fe"
    COLOR_BORDER = "#e0e0e0"
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        .stApp, .stApp p, .stApp div, .stApp span, .stApp label, .stMarkdown {{
            color: {COLOR_TEXT} !important;
        }}
        
        .main-title {{
            text-align: center;
            color: {COLOR_PRIMARY} !important;
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .subtitle {{
            text-align: center;
            color: {COLOR_SECONDARY} !important;
            font-size: 1.1em;
            margin-bottom: 20px;
        }}
        
        .info-box {{
            background: {COLOR_HOVER};
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid {COLOR_PRIMARY};
            margin: 15px 0;
            color: {COLOR_TEXT} !important;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, {COLOR_CARD} 0%, {COLOR_HOVER} 100%);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, {COLOR_SECONDARY} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, {COLOR_SECONDARY} 100%);
            color: white !important;
            border-radius: 8px;
            border: none;
            padding: 10px;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {COLOR_PRIMARY} !important;
        }}
        
        .stDataFrame {{
            background-color: {COLOR_CARD} !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }}
        
        [data-testid="stDataFrame"] th {{
            background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, {COLOR_SECONDARY} 100%) !important;
            color: white !important;
            font-weight: 600 !important;
        }}
        
        [data-testid="stDataFrame"] td {{
            color: {COLOR_TEXT} !important;
            background-color: {COLOR_CARD} !important;
        }}
        
        [data-testid="stDataFrame"] tr:hover td {{
            background-color: {COLOR_HOVER} !important;
        }}
        </style>
    """, unsafe_allow_html=True)


def obtener_datos_ventas(id_tienda, fecha_inicio, fecha_fin, es_admin=False):
    """Obtiene todos los productos con sus cantidades vendidas"""
    conn = obtener_conexion()
    if not conn:
        return pd.DataFrame()
    
    cursor = conn.cursor()
    
    try:
        if es_admin:
            query = """
                SELECT 
                    p.Nombre as Producto,
                    p.Cod_barra as Codigo,
                    p.categoria as Categoria,
                    COALESCE(SUM(pv.Cantidad_vendida), 0) as Cantidad_Vendida,
                    COALESCE(SUM(pv.Cantidad_vendida * pv.Precio_Venta), 0) as Total_Vendido,
                    COUNT(DISTINCT pv.ID_Venta) as Numero_Ventas,
                    pv.unidad as Unidad
                FROM Producto p
                LEFT JOIN ProductoxVenta pv ON p.Cod_barra = pv.Cod_barra
                LEFT JOIN Venta v ON pv.ID_Venta = v.ID_Venta AND DATE(v.Fecha) BETWEEN %s AND %s
                GROUP BY p.Cod_barra, p.Nombre, p.categoria, pv.unidad
                ORDER BY Cantidad_Vendida DESC
            """
            cursor.execute(query, (fecha_inicio, fecha_fin))
        else:
            query = """
                SELECT 
                    p.Nombre as Producto,
                    p.Cod_barra as Codigo,
                    p.categoria as Categoria,
                    COALESCE(SUM(pv.Cantidad_vendida), 0) as Cantidad_Vendida,
                    COALESCE(SUM(pv.Cantidad_vendida * pv.Precio_Venta), 0) as Total_Vendido,
                    COUNT(DISTINCT pv.ID_Venta) as Numero_Ventas,
                    pv.unidad as Unidad
                FROM Producto p
                LEFT JOIN ProductoxVenta pv ON p.Cod_barra = pv.Cod_barra
                LEFT JOIN Venta v ON pv.ID_Venta = v.ID_Venta AND DATE(v.Fecha) BETWEEN %s AND %s AND v.id_tienda = %s
                WHERE p.id_tienda = %s
                GROUP BY p.Cod_barra, p.Nombre, p.categoria, pv.unidad
                ORDER BY Cantidad_Vendida DESC
            """
            cursor.execute(query, (fecha_inicio, fecha_fin, id_tienda, id_tienda))
        
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if resultados:
            df = pd.DataFrame(resultados, columns=["Producto", "Codigo", "Categoria", "Cantidad_Vendida", "Total_Vendido", "Numero_Ventas", "Unidad"])
            # Formatear cantidad con unidad
            df["Cantidad con Unidad"] = df.apply(
                lambda x: f"{x['Cantidad_Vendida']:.2f} {x['Unidad']}" if x['Unidad'] and x['Cantidad_Vendida'] > 0 else f"{x['Cantidad_Vendida']:.2f}", 
                axis=1
            )
            # Redondear Total_Vendido
            df["Total_Vendido"] = df["Total_Vendido"].round(2)
            return df
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        cursor.close()
        conn.close()
        return pd.DataFrame()


def obtener_resumen_ventas(id_tienda, fecha_inicio, fecha_fin, es_admin=False):
    """Obtiene resumen general de ventas"""
    conn = obtener_conexion()
    if not conn:
        return None, None, None
    
    cursor = conn.cursor()
    
    try:
        if es_admin:
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT v.ID_Venta) as total_ventas,
                    COALESCE(SUM(pv.Cantidad_vendida), 0) as total_productos,
                    COALESCE(SUM(pv.Cantidad_vendida * pv.Precio_Venta), 0) as total_ingresos
                FROM Venta v
                LEFT JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
            """, (fecha_inicio, fecha_fin))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT v.ID_Venta) as total_ventas,
                    COALESCE(SUM(pv.Cantidad_vendida), 0) as total_productos,
                    COALESCE(SUM(pv.Cantidad_vendida * pv.Precio_Venta), 0) as total_ingresos
                FROM Venta v
                LEFT JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
                  AND v.id_tienda = %s
            """, (fecha_inicio, fecha_fin, id_tienda))
        
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return resultado
        
    except Exception as e:
        st.error(f"Error al obtener resumen: {e}")
        cursor.close()
        conn.close()
        return None, None, None


def graficar_productos(df, titulo, color_gradiente):
    """Crea gráfico de barras atractivo con gradiente y tooltips mejorados"""
    if df.empty:
        return None
    
    # Limitar a top 15 para mejor visualización
    df_plot = df.head(15).copy()
    
    # Crear colores gradiente
    colors = [color_gradiente] * len(df_plot)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_plot["Producto"],
        y=df_plot["Cantidad_Vendida"],
        text=df_plot["Cantidad con Unidad"],
        textposition='outside',
        textfont=dict(size=10, color="#333333"),
        marker=dict(
            color=df_plot["Cantidad_Vendida"],
            colorscale=[[0, color_gradiente], [1, color_gradiente.replace("1e3a5f", "2c5f8a")]],
            showscale=False,
            line=dict(width=1, color='white')
        ),
        hovertemplate='<b>%{x}</b><br>' +
                      'Cantidad Vendida: %{y:.2f}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>",
            font=dict(size=18, color="#1e3a5f"),
            x=0.5
        ),
        xaxis=dict(
            title="Producto",
            titlefont=dict(size=12, color="#666666"),
            tickangle=-45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title="Cantidad Vendida",
            titlefont=dict(size=12, color="#666666"),
            gridcolor='#e0e0e0',
            gridwidth=0.5
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        margin=dict(t=50, b=100, l=50, r=30),
        bargap=0.3,
        bargroupgap=0.1
    )
    
    # Agregar línea de tendencia suave
    if len(df_plot) > 2:
        fig.add_trace(go.Scatter(
            x=df_plot["Producto"],
            y=df_plot["Cantidad_Vendida"].rolling(window=3, min_periods=1).mean(),
            mode='lines+markers',
            name='Tendencia',
            line=dict(color='#ff6b6b', width=2, dash='dot'),
            marker=dict(size=6, color='#ff6b6b'),
            hovertemplate='Tendencia: %{y:.2f}<extra></extra>'
        ))
    
    return fig


def graficar_torta_categorias(df, titulo):
    """Crea gráfico de torta para distribución por categoría"""
    if df.empty:
        return None
    
    # Agrupar por categoría
    df_categoria = df.groupby("Categoria")["Cantidad_Vendida"].sum().reset_index()
    df_categoria = df_categoria[df_categoria["Cantidad_Vendida"] > 0]
    
    if df_categoria.empty:
        return None
    
    # Colores profesionales
    colores = ['#1e3a5f', '#2c5f8a', '#3a7ca5', '#4a9ac0', '#5ab8db', '#6ad6f6', '#7af4ff']
    
    fig = go.Figure(data=[go.Pie(
        labels=df_categoria["Categoria"],
        values=df_categoria["Cantidad_Vendida"],
        hole=0.4,
        marker=dict(colors=colores, line=dict(color='white', width=2)),
        textinfo='label+percent',
        textposition='auto',
        hovertemplate='<b>%{label}</b><br>' +
                      'Cantidad: %{value:.2f}<br>' +
                      'Porcentaje: %{percent}<br>' +
                      '<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>",
            font=dict(size=16, color="#1e3a5f"),
            x=0.5
        ),
        height=450,
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=10)
        )
    )
    
    return fig


def modulo_productos_mas_menos_vendidos():
    configurar_estilo()
    
    st.markdown('<div class="main-title">📊 Productos Más y Menos Vendidos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Análisis completo de ventas por producto</div>', unsafe_allow_html=True)
    
    # Obtener información de la sesión
    rol_usuario = st.session_state.get("nivel_usuario", "")
    nombre_tienda = st.session_state.get("nombre_tienda", "Tienda Minorista")
    id_tienda = st.session_state.get("id_tienda", None)
    
    # Selector de tienda para administrador
    if rol_usuario == "Administrador":
        st.markdown('<div class="info-box">👑 Administrador - Puedes seleccionar cualquier tienda</div>', unsafe_allow_html=True)
        
        conn = obtener_conexion()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_tienda, nombre FROM tienda WHERE activo = 1 ORDER BY nombre")
            tiendas = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if tiendas:
                opciones = {t["nombre"]: t["id_tienda"] for t in tiendas}
                tienda_seleccionada = st.selectbox("🏪 Seleccionar tienda", ["Todas las tiendas"] + list(opciones.keys()))
                
                if tienda_seleccionada == "Todas las tiendas":
                    id_tienda_usar = None
                    es_admin = True
                else:
                    id_tienda_usar = opciones[tienda_seleccionada]
                    es_admin = False
                    nombre_tienda = tienda_seleccionada
            else:
                st.warning("No hay tiendas activas.")
                return
        else:
            st.error("Error de conexión.")
            return
    else:
        id_tienda_usar = id_tienda
        es_admin = False
        st.markdown(f'<div class="info-box">🏪 Tienda: <strong>{nombre_tienda}</strong></div>', unsafe_allow_html=True)
    
    # Filtros de fecha
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_inicio = st.date_input(
            "📅 Fecha inicio",
            value=datetime.today().replace(day=1),
            key="inicio"
        )
    with col2:
        fecha_fin = st.date_input(
            "📅 Fecha fin",
            value=datetime.today(),
            key="fin"
        )
    
    if fecha_inicio > fecha_fin:
        st.error("❌ La fecha de inicio no puede ser mayor que la fecha de fin.")
        return
    
    # Obtener resumen de ventas
    with st.spinner("Cargando datos..."):
        total_ventas, total_productos, total_ingresos = obtener_resumen_ventas(id_tienda_usar, fecha_inicio, fecha_fin, es_admin)
        df_completo = obtener_datos_ventas(id_tienda_usar, fecha_inicio, fecha_fin, es_admin)
    
    # Mostrar resumen en métricas
    st.markdown("### 📈 Resumen del Período")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div>💰 Total Ingresos</div>
                <div class="metric-value">${total_ingresos:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div>📦 Productos Vendidos</div>
                <div class="metric-value">{total_productos:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div>🛒 Transacciones</div>
                <div class="metric-value">{total_ventas:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if df_completo.empty:
        st.warning("⚠️ No hay datos de ventas en el período seleccionado.")
    else:
        # Separar productos con ventas y sin ventas
        df_con_ventas = df_completo[df_completo["Cantidad_Vendida"] > 0].copy()
        df_sin_ventas = df_completo[df_completo["Cantidad_Vendida"] == 0].copy()
        
        # Ordenar más vendidos (mayor a menor)
        df_mas_vendidos = df_con_ventas.sort_values("Cantidad_Vendida", ascending=False)
        
        # Ordenar menos vendidos (menor a mayor, solo los que tienen ventas > 0)
        df_menos_vendidos = df_con_ventas.sort_values("Cantidad_Vendida", ascending=True)
        
        # ============================================================
        # GRÁFICO DE TORTA POR CATEGORÍA
        # ============================================================
        if not df_con_ventas.empty:
            fig_torta = graficar_torta_categorias(df_con_ventas, "Distribución de Ventas por Categoría")
            if fig_torta:
                st.plotly_chart(fig_torta, use_container_width=True)
                st.markdown("---")
        
        # ============================================================
        # GRÁFICO Y TABLA DE MÁS VENDIDOS
        # ============================================================
        st.markdown("## 🏆 Productos Más Vendidos")
        
        if not df_mas_vendidos.empty:
            fig_mas = graficar_productos(df_mas_vendidos, "Top Productos Más Vendidos", "#2ecc71")
            if fig_mas:
                st.plotly_chart(fig_mas, use_container_width=True)
            
            # Tabla completa de más vendidos
            st.dataframe(
                df_mas_vendidos[["Producto", "Categoria", "Cantidad con Unidad", "Total_Vendido", "Numero_Ventas"]],
                use_container_width=True
            )
        else:
            st.info("No hay productos con ventas en el período seleccionado.")
        
        st.markdown("---")
        
        # ============================================================
        # GRÁFICO Y TABLA DE MENOS VENDIDOS
        # ============================================================
        st.markdown("## 📉 Productos Menos Vendidos")
        
        if not df_menos_vendidos.empty:
            fig_menos = graficar_productos(df_menos_vendidos, "Productos Menos Vendidos", "#e74c3c")
            if fig_menos:
                st.plotly_chart(fig_menos, use_container_width=True)
            
            # Tabla completa de menos vendidos
            st.dataframe(
                df_menos_vendidos[["Producto", "Categoria", "Cantidad con Unidad", "Total_Vendido", "Numero_Ventas"]],
                use_container_width=True
            )
        else:
            st.info("No hay productos con ventas en el período seleccionado.")
        
        # ============================================================
        # PRODUCTOS SIN VENTAS
        # ============================================================
        if not df_sin_ventas.empty:
            st.markdown("---")
            st.markdown("## 🚫 Productos Sin Ventas")
            st.info(f"Hay {len(df_sin_ventas)} productos que no tuvieron ventas en el período seleccionado.")
            
            with st.expander("📋 Ver productos sin ventas"):
                st.dataframe(
                    df_sin_ventas[["Producto", "Categoria"]],
                    use_container_width=True
                )
    
    # Botón para volver
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Volver al menú principal", use_container_width=True):
            st.session_state["module"] = None
            st.rerun()
