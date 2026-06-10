import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime

def configurar_estilo():
    """Configuración de estilos CSS para el módulo"""
    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_HOVER = "#e8f0fe"
    
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
            background: {COLOR_CARD};
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: {COLOR_PRIMARY} !important;
        }}
        
        .top-card {{
            background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, {COLOR_SECONDARY} 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            height: 100%;
        }}
        
        .top-card:hover {{
            transform: translateY(-5px);
        }}
        
        .top-card .position {{
            font-size: 2em;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        }}
        
        .top-card .product-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        }}
        
        .top-card .quantity {{
            font-size: 1.5em;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 5px;
        }}
        
        .top-card .unit {{
            font-size: 0.9em;
            color: rgba(255,255,255,0.8);
        }}
        
        .top-card .total {{
            font-size: 1.1em;
            font-weight: bold;
            color: #ffd700;
            margin-top: 10px;
        }}
        
        .bottom-card {{
            background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            height: 100%;
        }}
        
        .bottom-card:hover {{
            transform: translateY(-5px);
        }}
        
        .bottom-card .position {{
            font-size: 2em;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        }}
        
        .bottom-card .product-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        }}
        
        .bottom-card .quantity {{
            font-size: 1.5em;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 5px;
        }}
        
        .bottom-card .unit {{
            font-size: 0.9em;
            color: rgba(255,255,255,0.8);
        }}
        
        .bottom-card .total {{
            font-size: 1.1em;
            font-weight: bold;
            color: #ffd700;
            margin-top: 10px;
        }}
        
        .stButton > button {{
            background-color: {COLOR_PRIMARY};
            color: white !important;
            border-radius: 8px;
            border: none;
            padding: 10px;
        }}
        
        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY};
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {COLOR_PRIMARY} !important;
        }}
        
        .stDataFrame {{
            background-color: {COLOR_CARD} !important;
            border-radius: 10px !important;
        }}
        
        [data-testid="stDataFrame"] th {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
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
    """Obtiene todos los productos con sus ingresos totales (sin importar unidad)"""
    conn = obtener_conexion()
    if not conn:
        return pd.DataFrame()
    
    cursor = conn.cursor()
    
    try:
        if es_admin:
            query = """
                SELECT 
                    p.id_producto,
                    p.Nombre as Producto,
                    p.categoria as Categoria,
                    SUM(pv.Cantidad_vendida) as Cantidad_Total,
                    SUM(pv.Cantidad_vendida * pv.Precio_Venta) as Total_Ingresos
                FROM Producto p
                JOIN ProductoxVenta pv ON p.Cod_barra = pv.Cod_barra AND p.id_tienda = pv.id_tienda
                JOIN Venta v ON pv.Id_venta = v.Id_venta
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
                GROUP BY p.id_producto, p.Nombre, p.categoria
                ORDER BY Total_Ingresos DESC
            """
            cursor.execute(query, (fecha_inicio, fecha_fin))
        else:
            query = """
                SELECT 
                    p.id_producto,
                    p.Nombre as Producto,
                    p.categoria as Categoria,
                    SUM(pv.Cantidad_vendida) as Cantidad_Total,
                    SUM(pv.Cantidad_vendida * pv.Precio_Venta) as Total_Ingresos
                FROM Producto p
                JOIN ProductoxVenta pv ON p.Cod_barra = pv.Cod_barra AND p.id_tienda = pv.id_tienda
                JOIN Venta v ON pv.Id_venta = v.Id_venta
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
                  AND v.id_tienda = %s
                GROUP BY p.id_producto, p.Nombre, p.categoria
                ORDER BY Total_Ingresos DESC
            """
            cursor.execute(query, (fecha_inicio, fecha_fin, id_tienda))
        
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not resultados:
            return pd.DataFrame()
        
        df = pd.DataFrame(resultados, columns=["id_producto", "Producto", "Categoria", "Cantidad_Total", "Total_Ingresos"])
        
        if not df.empty:
            # Redondear valores
            df["Total_Ingresos"] = df["Total_Ingresos"].round(2)
            df["Cantidad_Total"] = df["Cantidad_Total"].round(2)
            df["Cantidad con Unidad"] = df["Cantidad_Total"].apply(lambda x: f"{x:.2f} unidades (convertidas)")
        
        return df
        
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        if cursor:
            cursor.close()
        if conn:
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


def mostrar_top_card_ingresos(producto, ingresos, posicion, color="blue"):
    """Muestra una tarjeta con la información del producto basada en ingresos"""
    if color == "blue":
        card_class = "top-card"
    else:
        card_class = "bottom-card"
    
    if posicion == 1:
        medalla = "🥇"
    elif posicion == 2:
        medalla = "🥈"
    elif posicion == 3:
        medalla = "🥉"
    else:
        medalla = f"#{posicion}"
    
    st.markdown(f"""
        <div class="{card_class}">
            <div class="position">{medalla}</div>
            <div class="product-name">{producto}</div>
            <div class="quantity">${ingresos:,.2f}</div>
            <div class="unit">en ingresos</div>
        </div>
    """, unsafe_allow_html=True)


def modulo_productos_mas_menos_vendidos():
    configurar_estilo()
    
    st.markdown('<div class="main-title">📊 Productos que Más y Menos Ingresos Generan</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Análisis de ingresos por producto</div>', unsafe_allow_html=True)
    
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
        fecha_inicio = st.date_input("📅 Fecha inicio", value=datetime.today().replace(day=1))
    with col2:
        fecha_fin = st.date_input("📅 Fecha fin", value=datetime.today())
    
    if fecha_inicio > fecha_fin:
        st.error("❌ La fecha de inicio no puede ser mayor que la fecha de fin.")
        return
    
    # Obtener datos
    with st.spinner("Cargando datos..."):
        total_ventas, total_productos, total_ingresos = obtener_resumen_ventas(id_tienda_usar, fecha_inicio, fecha_fin, es_admin)
        df_completo = obtener_datos_ventas(id_tienda_usar, fecha_inicio, fecha_fin, es_admin)
    
    # Mostrar resumen
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
        # Ordenar por ingresos (mayor a menor)
        df_mayores_ingresos = df_completo.sort_values("Total_Ingresos", ascending=False)
        # Ordenar por ingresos (menor a mayor)
        df_menores_ingresos = df_completo[df_completo["Total_Ingresos"] > 0].sort_values("Total_Ingresos", ascending=True)
        
        # ============================================================
        # TOP 3 PRODUCTOS QUE MÁS INGRESOS GENERAN - TARJETAS
        # ============================================================
        st.markdown("## 🏆 Top 3 Productos que Más Ingresos Generan")
        
        if len(df_mayores_ingresos) >= 3:
            top3_mas = df_mayores_ingresos.head(3)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                row = top3_mas.iloc[0]
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=1,
                    color="blue"
                )
            with col2:
                row = top3_mas.iloc[1]
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=2,
                    color="blue"
                )
            with col3:
                row = top3_mas.iloc[2]
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=3,
                    color="blue"
                )
        elif len(df_mayores_ingresos) == 2:
            st.info("Solo hay 2 productos con ingresos en el período.")
            col1, col2 = st.columns(2)
            with col1:
                row = df_mayores_ingresos.iloc[0]
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=1,
                    color="blue"
                )
            with col2:
                row = df_mayores_ingresos.iloc[1]
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=2,
                    color="blue"
                )
        elif len(df_mayores_ingresos) == 1:
            st.info("Solo hay 1 producto con ingresos en el período.")
            row = df_mayores_ingresos.iloc[0]
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=1,
                    color="blue"
                )
        else:
            st.info("No hay productos con ingresos en el período seleccionado.")
        
        st.markdown("---")
        
        # ============================================================
        # TABLA DE PRODUCTOS QUE MÁS INGRESOS GENERAN (COMPLETA)
        # ============================================================
        st.markdown("### 📋 Lista completa de productos por ingresos generados")
        st.dataframe(
            df_mayores_ingresos[["Producto", "Categoria", "Cantidad_Total", "Total_Ingresos"]],
            use_container_width=True
        )
        
        st.markdown("---")
        
        # ============================================================
        # TOP 3 PRODUCTOS QUE MENOS INGRESOS GENERAN - TARJETAS
        # ============================================================
        st.markdown("## 📉 Top 3 Productos que Menos Ingresos Generan")
        
        if len(df_menores_ingresos) >= 3:
            top3_menos = df_menores_ingresos.head(3)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                row = top3_menos.iloc[0]
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=1,
                    color="red"
                )
            with col2:
                row = top3_menos.iloc[1]
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=2,
                    color="red"
                )
            with col3:
                row = top3_menos.iloc[2]
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=3,
                    color="red"
                )
        elif len(df_menores_ingresos) == 2:
            st.info("Solo hay 2 productos con ingresos en el período.")
            col1, col2 = st.columns(2)
            with col1:
                row = df_menores_ingresos.iloc[0]
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=1,
                    color="red"
                )
            with col2:
                row = df_menores_ingresos.iloc[1]
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=2,
                    color="red"
                )
        elif len(df_menores_ingresos) == 1:
            st.info("Solo hay 1 producto con ingresos en el período.")
            row = df_menores_ingresos.iloc[0]
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                mostrar_top_card_ingresos(
                    producto=row["Producto"],
                    ingresos=row["Total_Ingresos"],
                    posicion=1,
                    color="red"
                )
        else:
            st.info("No hay productos con ingresos en el período seleccionado.")
        
        st.markdown("---")
        
        # ============================================================
        # TABLA DE PRODUCTOS QUE MENOS INGRESOS GENERAN (COMPLETA)
        # ============================================================
        st.markdown("### 📋 Lista completa de productos por menores ingresos")
        if not df_menores_ingresos.empty:
            st.dataframe(
                df_menores_ingresos[["Producto", "Categoria", "Cantidad_Total", "Total_Ingresos"]],
                use_container_width=True
            )
        else:
            st.info("No hay productos con ingresos en el período seleccionado.")
        
        # ============================================================
        # PRODUCTOS SIN INGRESOS (QUE NO SE VENDIERON)
        # ============================================================
        productos_con_ingresos = set(df_completo["Producto"].tolist())
        
        # Obtener todos los productos
        conn = obtener_conexion()
        if conn:
            cursor = conn.cursor()
            if es_admin:
                cursor.execute("SELECT Nombre, categoria FROM Producto")
            else:
                cursor.execute("SELECT Nombre, categoria FROM Producto WHERE id_tienda = %s", (id_tienda_usar,))
            todos_productos = cursor.fetchall()
            cursor.close()
            conn.close()
            
            productos_sin_ingresos = [p for p in todos_productos if p[0] not in productos_con_ingresos]
            
            if productos_sin_ingresos:
                st.markdown("---")
                st.markdown(f"## 🚫 Productos Sin Ingresos (No se vendieron) ({len(productos_sin_ingresos)})")
                df_sin_ingresos = pd.DataFrame(productos_sin_ingresos, columns=["Producto", "Categoria"])
                with st.expander("📋 Ver productos sin ingresos"):
                    st.dataframe(df_sin_ingresos, use_container_width=True)
    
    # Botón para volver
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Volver al menú principal", use_container_width=True):
            st.session_state["module"] = None
            st.rerun()
