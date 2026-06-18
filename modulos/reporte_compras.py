import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

def configurar_estilo():
    """Configuración de estilos CSS para el módulo - Mismo estilo que inventario"""
    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_DARK = "#1a1a1a"
    COLOR_HOVER = "#e8f0fe"
    COLOR_BORDER = "#e0e0e0"
    COLOR_BUTTON = "#1e3a5f"
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        .report-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .report-subtitle {{
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
            color: {COLOR_TEXT_DARK};
        }}
        
        .stButton > button {{
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
        }}
        
        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY};
            transform: translateY(-1px);
        }}
        
        .volver-btn button {{
            background-color: #6c757d !important;
            color: white !important;
        }}
        
        .volver-btn button:hover {{
            background-color: #5a6268 !important;
        }}
        
        .stTextInput > label, .stSelectbox > label, .stDateInput label {{
            color: {COLOR_TEXT} !important;
            font-weight: 500 !important;
        }}
        
        .stDateInput input {{
            color: #333333 !important;
            background-color: white !important;
        }}
        
        .stSelectbox > div > div {{
            background-color: {COLOR_BUTTON};
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
        }}
        
        .stSelectbox > div > div > div {{
            color: white !important;
        }}
        
        .stSelectbox svg {{
            fill: white !important;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {COLOR_PRIMARY} !important;
        }}
        
        /* Dataframe */
        .stDataFrame {{
            background-color: {COLOR_CARD} !important;
        }}
        
        [data-testid="stDataFrame"] {{
            background-color: {COLOR_CARD} !important;
            border-radius: 12px !important;
            border: 1px solid {COLOR_BORDER} !important;
        }}
        
        [data-testid="stDataFrame"] table {{
            background-color: {COLOR_CARD} !important;
        }}
        
        [data-testid="stDataFrame"] th {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
            font-weight: 600 !important;
            text-align: center !important;
            padding: 12px 8px !important;
        }}
        
        [data-testid="stDataFrame"] td {{
            color: {COLOR_TEXT} !important;
            text-align: center !important;
            padding: 10px 8px !important;
            background-color: {COLOR_CARD} !important;
            border-bottom: 1px solid {COLOR_BORDER} !important;
        }}
        
        [data-testid="stDataFrame"] tr:nth-child(even) td {{
            background-color: #f8f9fa !important;
        }}
        
        [data-testid="stDataFrame"] tr:hover td {{
            background-color: {COLOR_HOVER} !important;
        }}
        
        [data-testid="stDataFrame"] td div {{
            color: {COLOR_TEXT} !important;
        }}
        </style>
    """, unsafe_allow_html=True)


def reporte_compras():
    configurar_estilo()
    
    st.markdown('<div class="report-title">📊 Reporte de Compras</div>', unsafe_allow_html=True)
    st.markdown('<div class="report-subtitle">Análisis de compras mensuales</div>', unsafe_allow_html=True)

    rol_usuario = st.session_state.get("nivel_usuario", "")
    nombre_tienda = st.session_state.get("nombre_tienda", "Tienda Minorista")
    id_tienda_sesion = st.session_state.get("id_tienda", None)

    # ADMINISTRADOR: puede seleccionar tienda
    if rol_usuario == "Administrador":
        st.markdown('<div class="info-box">👑 <strong>Administrador</strong> - Puedes filtrar por tienda</div>', unsafe_allow_html=True)
        
        conn = obtener_conexion()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_tienda, nombre FROM tienda WHERE activo = 1 ORDER BY nombre")
            tiendas = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if tiendas:
                opciones_tienda = {t["nombre"]: t["id_tienda"] for t in tiendas}
                tienda_seleccionada = st.selectbox(
                    "🏪 Filtrar por tienda:",
                    ["Todas las tiendas"] + list(opciones_tienda.keys())
                )
                
                if tienda_seleccionada == "Todas las tiendas":
                    id_tienda_usar = None
                    filtro_tienda = "Todas las tiendas"
                else:
                    id_tienda_usar = opciones_tienda[tienda_seleccionada]
                    filtro_tienda = tienda_seleccionada
            else:
                st.warning("No hay tiendas activas.")
                return
        else:
            st.error("Error de conexión.")
            return
    else:
        id_tienda_usar = id_tienda_sesion
        filtro_tienda = nombre_tienda
        st.markdown(f'<div class="info-box">🏪 <strong>Tienda:</strong> {nombre_tienda}</div>', unsafe_allow_html=True)

    # Filtros de fecha
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("📅 Fecha inicio", value=datetime.today().replace(day=1))
    with col2:
        fecha_fin = st.date_input("📅 Fecha fin", value=datetime.today())

    if fecha_inicio > fecha_fin:
        st.error("❌ La fecha de inicio no puede ser mayor que la fecha de fin.")
        return

    # ============================================================
    # FILTRO POR TIPO DE COMPRA
    # ============================================================
    try:
        conn_test = obtener_conexion()
        cursor_test = conn_test.cursor()
        cursor_test.execute("SHOW COLUMNS FROM Compra LIKE 'Tipo_Compra'")
        columna_existe = cursor_test.fetchone() is not None
        cursor_test.close()
        conn_test.close()
        
        if columna_existe:
            tipo_compra_filtro = st.selectbox(
                "📋 Filtrar por tipo de compra:",
                ["Todos", "Propia", "Global"]
            )
        else:
            tipo_compra_filtro = "Todos"
            st.info("ℹ️ La columna 'Tipo_Compra' no existe en la tabla Compra. Mostrando todas las compras.")
    except:
        tipo_compra_filtro = "Todos"

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # ============================================================
        # Obtener el TOTAL GENERAL desde la base de datos
        # ============================================================
        if id_tienda_usar is None:
            if tipo_compra_filtro == "Todos" or not columna_existe:
                query_total = """
                    SELECT COALESCE(SUM(pc.cantidad_comprada * pc.Precio_Compra), 0) as TotalGeneral
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                """
                cursor.execute(query_total, (fecha_inicio, fecha_fin))
            else:
                query_total = """
                    SELECT COALESCE(SUM(pc.cantidad_comprada * pc.Precio_Compra), 0) as TotalGeneral
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                      AND c.Tipo_Compra = %s
                """
                cursor.execute(query_total, (fecha_inicio, fecha_fin, tipo_compra_filtro))
        else:
            if tipo_compra_filtro == "Todos" or not columna_existe:
                query_total = """
                    SELECT COALESCE(SUM(pc.cantidad_comprada * pc.Precio_Compra), 0) as TotalGeneral
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                      AND pc.id_tienda = %s
                """
                cursor.execute(query_total, (fecha_inicio, fecha_fin, id_tienda_usar))
            else:
                query_total = """
                    SELECT COALESCE(SUM(pc.cantidad_comprada * pc.Precio_Compra), 0) as TotalGeneral
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                      AND pc.id_tienda = %s
                      AND c.Tipo_Compra = %s
                """
                cursor.execute(query_total, (fecha_inicio, fecha_fin, id_tienda_usar, tipo_compra_filtro))
        
        total_row = cursor.fetchone()
        gran_total = float(total_row[0]) if total_row else 0
        gran_total = round(gran_total, 2)

        # ============================================================
        # CONSULTA PARA DETALLE DE COMPRAS (TABLA)
        # ============================================================
        if id_tienda_usar is None:
            if tipo_compra_filtro == "Todos" or not columna_existe:
                query_detalle = """
                    SELECT 
                        c.Id_compra,
                        c.Fecha,
                        pc.cod_barra,
                        p.Nombre as Producto,
                        pc.cantidad_comprada,
                        pc.unidad,
                        pc.Precio_Compra,
                        (pc.cantidad_comprada * pc.Precio_Compra) as Total,
                        COALESCE(t.nombre, 'Sin tienda') as Tienda
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    JOIN Producto p ON pc.cod_barra = p.Cod_barra AND p.id_tienda = pc.id_tienda
                    LEFT JOIN tienda t ON pc.id_tienda = t.id_tienda
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                    ORDER BY c.Fecha DESC
                """
                cursor.execute(query_detalle, (fecha_inicio, fecha_fin))
            else:
                query_detalle = """
                    SELECT 
                        c.Id_compra,
                        c.Fecha,
                        pc.cod_barra,
                        p.Nombre as Producto,
                        pc.cantidad_comprada,
                        pc.unidad,
                        pc.Precio_Compra,
                        (pc.cantidad_comprada * pc.Precio_Compra) as Total,
                        COALESCE(t.nombre, 'Sin tienda') as Tienda,
                        c.Tipo_Compra
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    JOIN Producto p ON pc.cod_barra = p.Cod_barra AND p.id_tienda = pc.id_tienda
                    LEFT JOIN tienda t ON pc.id_tienda = t.id_tienda
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                      AND c.Tipo_Compra = %s
                    ORDER BY c.Fecha DESC
                """
                cursor.execute(query_detalle, (fecha_inicio, fecha_fin, tipo_compra_filtro))
        else:
            if tipo_compra_filtro == "Todos" or not columna_existe:
                query_detalle = """
                    SELECT 
                        c.Id_compra,
                        c.Fecha,
                        pc.cod_barra,
                        p.Nombre as Producto,
                        pc.cantidad_comprada,
                        pc.unidad,
                        pc.Precio_Compra,
                        (pc.cantidad_comprada * pc.Precio_Compra) as Total
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    JOIN Producto p ON pc.cod_barra = p.Cod_barra AND p.id_tienda = pc.id_tienda
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                      AND pc.id_tienda = %s
                    ORDER BY c.Fecha DESC
                """
                cursor.execute(query_detalle, (fecha_inicio, fecha_fin, id_tienda_usar))
            else:
                query_detalle = """
                    SELECT 
                        c.Id_compra,
                        c.Fecha,
                        pc.cod_barra,
                        p.Nombre as Producto,
                        pc.cantidad_comprada,
                        pc.unidad,
                        pc.Precio_Compra,
                        (pc.cantidad_comprada * pc.Precio_Compra) as Total,
                        c.Tipo_Compra
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    JOIN Producto p ON pc.cod_barra = p.Cod_barra AND p.id_tienda = pc.id_tienda
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                      AND pc.id_tienda = %s
                      AND c.Tipo_Compra = %s
                    ORDER BY c.Fecha DESC
                """
                cursor.execute(query_detalle, (fecha_inicio, fecha_fin, id_tienda_usar, tipo_compra_filtro))
        
        rows_detalle = cursor.fetchall()
        
        if rows_detalle:
            # Determinar columnas según el número de campos
            if len(rows_detalle[0]) == 9:
                df_detalle = pd.DataFrame(rows_detalle, columns=["ID Compra", "Fecha", "Código", "Producto", "Cantidad", "Unidad", "Precio Unitario", "Total", "Tienda"])
            else:
                df_detalle = pd.DataFrame(rows_detalle, columns=["ID Compra", "Fecha", "Código", "Producto", "Cantidad", "Unidad", "Precio Unitario", "Total", "Tienda", "Tipo Compra"])
            
            # Formatear fechas
            df_detalle["Fecha"] = pd.to_datetime(df_detalle["Fecha"]).dt.strftime("%Y-%m-%d")
            
            # Formatear valores monetarios
            df_detalle["Precio Unitario"] = df_detalle["Precio Unitario"].apply(lambda x: f"${x:.2f}")
            df_detalle["Total"] = df_detalle["Total"].apply(lambda x: f"${x:.2f}")
        else:
            df_detalle = pd.DataFrame()

        # ============================================================
        # CONSULTA PRINCIPAL - Compras agrupadas (GRÁFICO)
        # ============================================================
        
        if id_tienda_usar is None:
            if tipo_compra_filtro == "Todos" or not columna_existe:
                query = """
                    SELECT 
                        COALESCE(t.nombre, 'Sin tienda') as Tienda,
                        COALESCE(SUM(pc.cantidad_comprada * pc.Precio_Compra), 0) as Total_Compras
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    LEFT JOIN tienda t ON pc.id_tienda = t.id_tienda
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                    GROUP BY t.nombre
                    ORDER BY Total_Compras DESC
                """
                cursor.execute(query, (fecha_inicio, fecha_fin))
                rows = cursor.fetchall()
                tiene_tipo = False
            else:
                query = """
                    SELECT 
                        COALESCE(t.nombre, 'Sin tienda') as Tienda,
                        COALESCE(SUM(pc.cantidad_comprada * pc.Precio_Compra), 0) as Total_Compras,
                        c.Tipo_Compra
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    LEFT JOIN tienda t ON pc.id_tienda = t.id_tienda
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                      AND c.Tipo_Compra = %s
                    GROUP BY t.nombre, c.Tipo_Compra
                    ORDER BY Total_Compras DESC
                """
                cursor.execute(query, (fecha_inicio, fecha_fin, tipo_compra_filtro))
                rows = cursor.fetchall()
                tiene_tipo = True
            
            if rows:
                if tiene_tipo:
                    df = pd.DataFrame(rows, columns=["Tienda", "Total_Compras", "Tipo_Compra"])
                    df["Total_Compras"] = df["Total_Compras"].astype(float)
                    
                    st.markdown("### 📊 Compras por Tienda")
                    fig = px.bar(
                        df,
                        x="Tienda",
                        y="Total_Compras",
                        title="Total de Compras por Tienda",
                        color="Tipo_Compra",
                        color_discrete_map={"Propia": "#2ecc71", "Global": "#3498db"},
                        text=df["Total_Compras"].apply(lambda x: f"${x:,.2f}")
                    )
                else:
                    df = pd.DataFrame(rows, columns=["Tienda", "Total_Compras"])
                    df["Total_Compras"] = df["Total_Compras"].astype(float)
                    
                    st.markdown("### 📊 Compras por Tienda")
                    fig = px.bar(
                        df,
                        x="Tienda",
                        y="Total_Compras",
                        title="Total de Compras por Tienda",
                        color="Total_Compras",
                        color_continuous_scale="Blues",
                        text=df["Total_Compras"].apply(lambda x: f"${x:,.2f}")
                    )
                
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    xaxis_title="Tienda",
                    yaxis_title="Total de Compras ($)",
                    height=500,
                )
                st.plotly_chart(fig, use_container_width=True)
                
        else:
            if tipo_compra_filtro == "Todos" or not columna_existe:
                query = """
                    SELECT 
                        CONCAT(
                            CASE MONTH(c.Fecha)
                                WHEN 1 THEN 'Ene' WHEN 2 THEN 'Feb' WHEN 3 THEN 'Mar'
                                WHEN 4 THEN 'Abr' WHEN 5 THEN 'May' WHEN 6 THEN 'Jun'
                                WHEN 7 THEN 'Jul' WHEN 8 THEN 'Ago' WHEN 9 THEN 'Sep'
                                WHEN 10 THEN 'Oct' WHEN 11 THEN 'Nov' WHEN 12 THEN 'Dic'
                            END,
                            ' ', YEAR(c.Fecha)
                        ) as Nombre_Mes,
                        COALESCE(SUM(pc.cantidad_comprada * pc.Precio_Compra), 0) as Total_Compras
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                      AND pc.id_tienda = %s
                    GROUP BY YEAR(c.Fecha), MONTH(c.Fecha)
                    ORDER BY YEAR(c.Fecha) ASC, MONTH(c.Fecha) ASC
                """
                cursor.execute(query, (fecha_inicio, fecha_fin, id_tienda_usar))
                rows = cursor.fetchall()
                tiene_tipo = False
            else:
                query = """
                    SELECT 
                        CONCAT(
                            CASE MONTH(c.Fecha)
                                WHEN 1 THEN 'Ene' WHEN 2 THEN 'Feb' WHEN 3 THEN 'Mar'
                                WHEN 4 THEN 'Abr' WHEN 5 THEN 'May' WHEN 6 THEN 'Jun'
                                WHEN 7 THEN 'Jul' WHEN 8 THEN 'Ago' WHEN 9 THEN 'Sep'
                                WHEN 10 THEN 'Oct' WHEN 11 THEN 'Nov' WHEN 12 THEN 'Dic'
                            END,
                            ' ', YEAR(c.Fecha)
                        ) as Nombre_Mes,
                        COALESCE(SUM(pc.cantidad_comprada * pc.Precio_Compra), 0) as Total_Compras,
                        c.Tipo_Compra
                    FROM ProductoxCompra pc
                    JOIN Compra c ON pc.Id_compra = c.Id_compra
                    WHERE DATE(c.Fecha) BETWEEN %s AND %s
                      AND pc.id_tienda = %s
                      AND c.Tipo_Compra = %s
                    GROUP BY YEAR(c.Fecha), MONTH(c.Fecha), c.Tipo_Compra
                    ORDER BY YEAR(c.Fecha) ASC, MONTH(c.Fecha) ASC
                """
                cursor.execute(query, (fecha_inicio, fecha_fin, id_tienda_usar, tipo_compra_filtro))
                rows = cursor.fetchall()
                tiene_tipo = True
            
            if rows:
                if tiene_tipo:
                    df = pd.DataFrame(rows, columns=["Nombre_Mes", "Total_Compras", "Tipo_Compra"])
                    df["Total_Compras"] = df["Total_Compras"].astype(float)
                    
                    st.markdown(f"### 📊 Análisis de Compras Mensuales - {filtro_tienda}")
                    fig = px.bar(
                        df,
                        x="Nombre_Mes",
                        y="Total_Compras",
                        title="Total de Compras por Mes",
                        color="Tipo_Compra",
                        color_discrete_map={"Propia": "#2ecc71", "Global": "#3498db"},
                        text=df["Total_Compras"].apply(lambda x: f"${x:,.2f}"),
                        barmode="group"
                    )
                else:
                    df = pd.DataFrame(rows, columns=["Nombre_Mes", "Total_Compras"])
                    df["Total_Compras"] = df["Total_Compras"].astype(float)
                    
                    st.markdown(f"### 📊 Análisis de Compras Mensuales - {filtro_tienda}")
                    fig = px.bar(
                        df,
                        x="Nombre_Mes",
                        y="Total_Compras",
                        title="Total de Compras por Mes",
                        color="Total_Compras",
                        color_continuous_scale="Blues",
                        text=df["Total_Compras"].apply(lambda x: f"${x:,.2f}")
                    )
                
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    xaxis_title="Mes",
                    yaxis_title="Total de Compras ($)",
                    height=500,
                )
                st.plotly_chart(fig, use_container_width=True)

        # ============================================================
        # TABLA DE DETALLE DE COMPRAS
        # ============================================================
        if not df_detalle.empty:
            st.markdown("---")
            st.markdown("### 📋 Detalle de Compras")
            st.dataframe(df_detalle, use_container_width=True)

        # ============================================================
        # TOTAL GENERAL
        # ============================================================
        
        st.markdown("---")
        st.markdown("## 💰 TOTAL GENERAL DE COMPRAS")
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #1e3a5f 0%, #2c5f8a 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        '>
            <div style='
                font-size: 2.5em;
                font-weight: bold;
                color: #ffd700;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                letter-spacing: 2px;
            '>
                ${gran_total:,.2f}
            </div>
            <div style='
                font-size: 0.9em;
                color: rgba(255,255,255,0.8);
                margin-top: 8px;
            '>
                Total de compras del período
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Botón para volver
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="volver-btn">', unsafe_allow_html=True)
            if st.button("🔙 Volver al Menú Principal", use_container_width=True):
                st.session_state["module"] = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al generar el reporte: {e}")

    finally:
        if "cursor" in locals():
            cursor.close()
        if "con" in locals():
            con.close()


def modulo_reporte_compras():
    reporte_compras()
