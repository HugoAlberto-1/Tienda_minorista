import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def configurar_estilo_top():
    """Configuración de estilos CSS para el módulo de top productos"""
    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_HOVER = "#e8f0fe"
    COLOR_BORDER = "#e0e0e0"
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        .top-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .top-subtitle {{
            text-align: center;
            color: {COLOR_SECONDARY};
            font-size: 1.1em;
            margin-bottom: 20px;
        }}
        
        .info-box {{
            background: {COLOR_HOVER};
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid {COLOR_PRIMARY};
            margin: 15px 0;
        }}
        
        .metric-card {{
            background: {COLOR_CARD};
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: {COLOR_PRIMARY};
        }}
        
        .stButton > button {{
            background-color: {COLOR_PRIMARY};
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px;
        }}
        
        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY};
        }}
        </style>
    """, unsafe_allow_html=True)


def obtener_productos_mas_vendidos(id_tienda, fecha_inicio, fecha_fin, limite=30, es_admin=False):
    """Obtiene los productos más vendidos en el período"""
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
                    SUM(pv.Cantidad_vendida) as Cantidad_Vendida,
                    SUM(pv.Cantidad_vendida * pv.Precio_Venta) as Total_Vendido,
                    COUNT(DISTINCT v.ID_Venta) as Numero_Ventas,
                    pv.unidad as Unidad
                FROM ProductoxVenta pv
                JOIN Venta v ON pv.ID_Venta = v.ID_Venta
                JOIN Producto p ON pv.Cod_barra = p.Cod_barra
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
                GROUP BY p.Cod_barra, p.Nombre, p.categoria, pv.unidad
                ORDER BY Cantidad_Vendida DESC
                LIMIT %s
            """
            cursor.execute(query, (fecha_inicio, fecha_fin, limite))
        else:
            query = """
                SELECT 
                    p.Nombre as Producto,
                    p.Cod_barra as Codigo,
                    p.categoria as Categoria,
                    SUM(pv.Cantidad_vendida) as Cantidad_Vendida,
                    SUM(pv.Cantidad_vendida * pv.Precio_Venta) as Total_Vendido,
                    COUNT(DISTINCT v.ID_Venta) as Numero_Ventas,
                    pv.unidad as Unidad
                FROM ProductoxVenta pv
                JOIN Venta v ON pv.ID_Venta = v.ID_Venta
                JOIN Producto p ON pv.Cod_barra = p.Cod_barra
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
                  AND v.id_tienda = %s
                GROUP BY p.Cod_barra, p.Nombre, p.categoria, pv.unidad
                ORDER BY Cantidad_Vendida DESC
                LIMIT %s
            """
            cursor.execute(query, (fecha_inicio, fecha_fin, id_tienda, limite))
        
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if resultados:
            df = pd.DataFrame(resultados, columns=["Producto", "Codigo", "Categoria", "Cantidad_Vendida", "Total_Vendido", "Numero_Ventas", "Unidad"])
            # Formatear cantidad con unidad
            df["Cantidad con Unidad"] = df.apply(lambda x: f"{x['Cantidad_Vendida']:.2f} {x['Unidad']}" if x['Unidad'] else f"{x['Cantidad_Vendida']:.2f}", axis=1)
            return df
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error al obtener productos más vendidos: {e}")
        cursor.close()
        conn.close()
        return pd.DataFrame()


def obtener_productos_menos_vendidos(id_tienda, fecha_inicio, fecha_fin, limite=30, es_admin=False):
    """Obtiene los productos menos vendidos en el período"""
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
                HAVING Cantidad_Vendida > 0
                ORDER BY Cantidad_Vendida ASC
                LIMIT %s
            """
            cursor.execute(query, (fecha_inicio, fecha_fin, limite))
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
                HAVING Cantidad_Vendida > 0
                ORDER BY Cantidad_Vendida ASC
                LIMIT %s
            """
            cursor.execute(query, (fecha_inicio, fecha_fin, id_tienda, id_tienda, limite))
        
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if resultados:
            df = pd.DataFrame(resultados, columns=["Producto", "Codigo", "Categoria", "Cantidad_Vendida", "Total_Vendido", "Numero_Ventas", "Unidad"])
            # Formatear cantidad con unidad
            df["Cantidad con Unidad"] = df.apply(lambda x: f"{x['Cantidad_Vendida']:.2f} {x['Unidad']}" if x['Unidad'] and x['Cantidad_Vendida'] > 0 else f"{x['Cantidad_Vendida']:.2f}", axis=1)
            return df
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error al obtener productos menos vendidos: {e}")
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
                    SUM(pv.Cantidad_vendida) as total_productos,
                    SUM(pv.Cantidad_vendida * pv.Precio_Venta) as total_ingresos
                FROM Venta v
                JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
            """, (fecha_inicio, fecha_fin))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT v.ID_Venta) as total_ventas,
                    SUM(pv.Cantidad_vendida) as total_productos,
                    SUM(pv.Cantidad_vendida * pv.Precio_Venta) as total_ingresos
                FROM Venta v
                JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
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


def graficar_top_productos(df, titulo, color):
    """Crea gráfico de barras para top productos"""
    if df.empty:
        return None
    
    fig = px.bar(
        df.head(15),
        x="Producto",
        y="Cantidad_Vendida",
        title=titulo,
        color_discrete_sequence=[color],
        text="Cantidad_Vendida"
    )
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(
        xaxis_title="Producto",
        yaxis_title="Cantidad Vendida",
        xaxis_tickangle=-45,
        height=500,
        showlegend=False
    )
    return fig


def modulo_top_30():
    configurar_estilo_top()
    
    st.markdown('<div class="top-title">🏆 Top 30 Productos</div>', unsafe_allow_html=True)
    st.markdown('<div class="top-subtitle">Productos más y menos vendidos</div>', unsafe_allow_html=True)
    
    # Obtener información de la sesión
    rol_usuario = st.session_state.get("nivel_usuario", "")
    nombre_tienda = st.session_state.get("nombre_tienda", "Tienda Minorista")
    id_tienda = st.session_state.get("id_tienda", None)
    
    # Mostrar información de la tienda
    if rol_usuario == "Administrador":
        st.markdown('<div class="info-box">👑 Administrador - Reporte de todas las tiendas</div>', unsafe_allow_html=True)
        
        # Selector de tienda para admin
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
            key="inicio_top30"
        )
    with col2:
        fecha_fin = st.date_input(
            "📅 Fecha fin",
            value=datetime.today(),
            key="fin_top30"
        )
    
    if fecha_inicio > fecha_fin:
        st.error("❌ La fecha de inicio no puede ser mayor que la fecha de fin.")
        return
    
    # Obtener resumen de ventas
    total_ventas, total_productos, total_ingresos = obtener_resumen_ventas(id_tienda_usar, fecha_inicio, fecha_fin, es_admin)
    
    if total_ventas and total_ventas > 0:
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
    
    # Obtener datos
    with st.spinner("Cargando datos..."):
        df_mas = obtener_productos_mas_vendidos(id_tienda_usar, fecha_inicio, fecha_fin, 30, es_admin)
        df_menos = obtener_productos_menos_vendidos(id_tienda_usar, fecha_inicio, fecha_fin, 30, es_admin)
    
    # Mostrar resultados en dos columnas
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 🏆 TOP 30 MÁS VENDIDOS")
        if not df_mas.empty:
            fig_mas = graficar_top_productos(df_mas, "Top 30 Productos Más Vendidos", "#2ecc71")
            if fig_mas:
                st.plotly_chart(fig_mas, use_container_width=True)
            
            # Tabla
            st.dataframe(
                df_mas[["Producto", "Categoria", "Cantidad con Unidad", "Total_Vendido", "Numero_Ventas"]].head(30),
                use_container_width=True
            )
        else:
            st.info("No hay datos de productos más vendidos en el período seleccionado.")
    
    with col2:
        st.markdown("### 📉 TOP 30 MENOS VENDIDOS")
        if not df_menos.empty:
            fig_menos = graficar_top_productos(df_menos, "Top 30 Productos Menos Vendidos", "#e74c3c")
            if fig_menos:
                st.plotly_chart(fig_menos, use_container_width=True)
            
            # Tabla
            st.dataframe(
                df_menos[["Producto", "Categoria", "Cantidad con Unidad", "Total_Vendido", "Numero_Ventas"]].head(30),
                use_container_width=True
            )
        else:
            st.info("No hay datos de productos menos vendidos en el período seleccionado.")
    
    # Botón para volver
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Volver al menú principal", use_container_width=True):
            st.session_state["module"] = None
            st.rerun()


# Esta es la función que se llamará desde app.py
def modulo_top_30_mas_vendidos():
    """Función principal que se llama desde app.py - Mantiene el nombre original"""
    modulo_top_30()
