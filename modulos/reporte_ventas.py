import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
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
        /* Fondo general */
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        /* Títulos */
        .report-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        /* Subtítulos */
        .report-subtitle {{
            text-align: center;
            color: {COLOR_SECONDARY};
            font-size: 1.1em;
            margin-bottom: 20px;
        }}
        
        /* Info box */
        .info-box {{
            background: {COLOR_HOVER};
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid {COLOR_PRIMARY};
            margin: 15px 0;
            color: {COLOR_TEXT_DARK};
        }}
        
        /* Botones */
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
        
        /* Botones de descarga */
        .stDownloadButton button {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
        }}
        
        .stDownloadButton button:hover {{
            background-color: {COLOR_SECONDARY} !important;
            transform: translateY(-1px) !important;
        }}
        
        /* Botón volver */
        .volver-btn button {{
            background-color: #6c757d !important;
            color: white !important;
        }}
        
        .volver-btn button:hover {{
            background-color: #5a6268 !important;
        }}
        
        /* Labels */
        .stTextInput > label, .stSelectbox > label, .stDateInput label {{
            color: {COLOR_TEXT} !important;
            font-weight: 500 !important;
        }}
        
        /* Fecha inputs */
        .stDateInput input {{
            color: #333333 !important;
            background-color: white !important;
        }}
        
        /* Selectores */
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
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: {COLOR_PRIMARY} !important;
        }}
        </style>
    """, unsafe_allow_html=True)


def reporte_ventas():
    configurar_estilo()
    
    st.markdown('<div class="report-title">📊 Reporte de Ventas por Producto</div>', unsafe_allow_html=True)
    st.markdown('<div class="report-subtitle">Análisis detallado de ventas</div>', unsafe_allow_html=True)

    # 🔐 Obtener información de la tienda desde la sesión
    rol_usuario = st.session_state.get("nivel_usuario", "")
    nombre_tienda = st.session_state.get("nombre_tienda", "Tienda Minorista")
    id_tienda_sesion = st.session_state.get("id_tienda", None)

    # ============================================================
    # ADMINISTRADOR: puede seleccionar una tienda específica
    # ============================================================
    if rol_usuario == "Administrador":
        st.markdown('<div class="info-box">👑 <strong>Administrador</strong> - Puedes filtrar por tienda</div>', unsafe_allow_html=True)
        
        # Obtener lista de tiendas
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

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # ============================================================
        # CONSULTAS SEGÚN EL TIPO DE FILTRO
        # ============================================================
        if rol_usuario == "Administrador" and id_tienda_usar is None:
            # ============================================================
            # OPCIÓN 1: TODAS LAS TIENDAS - Ventas por tienda
            # ============================================================
            query_por_tienda = """
                SELECT 
                    COALESCE(t.nombre, 'Sin tienda') as Tienda,
                    COALESCE(SUM(pv.Cantidad_vendida * pv.Precio_Venta), 0) as Total_Ventas
                FROM Venta v
                JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                LEFT JOIN tienda t ON v.id_tienda = t.id_tienda
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
                GROUP BY t.nombre
                ORDER BY Total_Ventas DESC
            """
            cursor.execute(query_por_tienda, (fecha_inicio, fecha_fin))
            rows_por_tienda = cursor.fetchall()
            
            if rows_por_tienda:
                df_por_tienda = pd.DataFrame(rows_por_tienda, columns=["Tienda", "Total_Ventas"])
                df_por_tienda["Total_Ventas"] = df_por_tienda["Total_Ventas"].astype(float)
                gran_total = float(df_por_tienda["Total_Ventas"].sum())
                gran_total = round(gran_total, 2)
            else:
                df_por_tienda = pd.DataFrame()
                gran_total = 0
            
            # Datos detallados para exportar
            query_detalle = """
                SELECT
                    p.Nombre,
                    pv.Cantidad_vendida,
                    pv.unidad,
                    pv.Precio_Venta,
                    v.Fecha,
                    COALESCE(t.nombre, 'Sin tienda') as Tienda
                FROM Venta v
                JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                JOIN Producto p ON p.Cod_barra = pv.Cod_barra
                LEFT JOIN tienda t ON v.id_tienda = t.id_tienda
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
                ORDER BY v.Fecha DESC, p.Nombre ASC
            """
            cursor.execute(query_detalle, (fecha_inicio, fecha_fin))
            rows_detalle = cursor.fetchall()
            if rows_detalle:
                columns_detalle = ["Nombre", "Cantidad Vendida", "unidad", "Precio Venta", "Fecha Venta", "Tienda"]
                df_detalle = pd.DataFrame(rows_detalle, columns=columns_detalle)
            else:
                df_detalle = pd.DataFrame()
                
        else:
            # ============================================================
            # OPCIÓN 2: TIENDA ESPECÍFICA - Ventas por mes (TODOS LOS MESES)
            # ============================================================
            if rol_usuario == "Administrador":
                st.markdown(f"### 📊 Análisis de Ventas Mensuales - {filtro_tienda}")
            else:
                st.markdown(f"### 📊 Análisis de Ventas Mensuales - {nombre_tienda}")
            
            # Consulta para ventas mensuales (agrupadas por mes)
            query_mensual = """
                SELECT 
                    DATE_FORMAT(v.Fecha, '%%Y-%%m') as Mes,
                    DATE_FORMAT(v.Fecha, '%%b %%Y') as Nombre_Mes,
                    COALESCE(SUM(pv.Cantidad_vendida * pv.Precio_Venta), 0) as Total_Ventas,
                    COUNT(DISTINCT v.ID_Venta) as Numero_Ventas
                FROM Venta v
                JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
                  AND v.id_tienda = %s
                GROUP BY DATE_FORMAT(v.Fecha, '%%Y-%%m'), DATE_FORMAT(v.Fecha, '%%b %%Y')
                ORDER BY Mes ASC
            """
            cursor.execute(query_mensual, (fecha_inicio, fecha_fin, id_tienda_usar))
            rows_mensual = cursor.fetchall()
            
            # Crear DataFrame con los resultados de ventas
            if rows_mensual:
                df_ventas = pd.DataFrame(rows_mensual, columns=["Mes", "Nombre_Mes", "Total_Ventas", "Numero_Ventas"])
                df_ventas["Total_Ventas"] = df_ventas["Total_Ventas"].astype(float)
                df_ventas["Numero_Ventas"] = df_ventas["Numero_Ventas"].astype(int)
            else:
                df_ventas = pd.DataFrame(columns=["Mes", "Nombre_Mes", "Total_Ventas", "Numero_Ventas"])
            
            # Generar todos los meses entre fecha_inicio y fecha_fin
            meses = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='MS')
            df_meses = pd.DataFrame({
                'Mes': [m.strftime('%Y-%m') for m in meses],
                'Nombre_Mes': [m.strftime('%b %Y') for m in meses]
            })
            
            # Combinar todos los meses con los datos de ventas (left join)
            df_completo = df_meses.merge(df_ventas, on="Mes", how="left")
            df_completo["Total_Ventas"] = df_completo["Total_Ventas"].fillna(0)
            df_completo["Numero_Ventas"] = df_completo["Numero_Ventas"].fillna(0)
            # Usar el nombre del mes de df_meses si no hay datos
            df_completo["Nombre_Mes"] = df_completo["Nombre_Mes_x"]
            df_completo = df_completo[["Mes", "Nombre_Mes", "Total_Ventas", "Numero_Ventas"]]
            
            # Calcular gran total
            gran_total = float(df_completo["Total_Ventas"].sum())
            gran_total = round(gran_total, 2)
            
            # Datos detallados para exportar
            query_detalle = """
                SELECT
                    p.Nombre,
                    pv.Cantidad_vendida,
                    pv.unidad,
                    pv.Precio_Venta,
                    v.Fecha
                FROM Venta v
                JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                JOIN Producto p ON p.Cod_barra = pv.Cod_barra
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
                  AND v.id_tienda = %s
                ORDER BY v.Fecha DESC, p.Nombre ASC
            """
            cursor.execute(query_detalle, (fecha_inicio, fecha_fin, id_tienda_usar))
            rows_detalle = cursor.fetchall()
            if rows_detalle:
                columns_detalle = ["Nombre", "Cantidad Vendida", "unidad", "Precio Venta", "Fecha Venta"]
                df_detalle = pd.DataFrame(rows_detalle, columns=columns_detalle)
            else:
                df_detalle = pd.DataFrame()

        # ============================================================
        # MOSTRAR RESULTADOS SEGÚN EL TIPO
        # ============================================================
        
        if (rol_usuario == "Administrador" and id_tienda_usar is None and df_por_tienda.empty) or \
           (rol_usuario != "Administrador" and df_completo.empty) or \
           (rol_usuario == "Administrador" and id_tienda_usar is not None and df_completo.empty):
            st.markdown('<div style="background-color: #fff3cd; color: #856404; padding: 12px; border-radius: 8px; border-left: 4px solid #ffc107;">⚠️ No se encontraron ventas en el rango seleccionado.</div>', unsafe_allow_html=True)
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown('<div class="volver-btn">', unsafe_allow_html=True)
                if st.button("🔙 Volver al Menú Principal", use_container_width=True):
                    st.session_state["module"] = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            return
        
        if rol_usuario == "Administrador" and id_tienda_usar is None:
            # ============================================================
            # TODAS LAS TIENDAS - Gráfico de ventas por tienda
            # ============================================================
            st.markdown("### 📊 Ventas por Tienda")
            
            # Crear gráfico de barras
            fig = px.bar(
                df_por_tienda,
                x="Tienda",
                y="Total_Ventas",
                title="Total de Ventas por Tienda",
                color="Total_Ventas",
                color_continuous_scale="Blues",
                text=df_por_tienda["Total_Ventas"].apply(lambda x: f"${x:,.2f}")
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_title="Tienda",
                yaxis_title="Total de Ventas ($)",
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            # ============================================================
            # TIENDA ESPECÍFICA - Gráfico de ventas por mes (TODOS LOS MESES)
            # ============================================================
            st.markdown("### 📈 Ventas Mensuales")
            
            # Gráfico de barras de ventas por mes
            fig_mensual = px.bar(
                df_completo,
                x="Nombre_Mes",
                y="Total_Ventas",
                title="Total de Ventas por Mes",
                color="Total_Ventas",
                color_continuous_scale="Blues",
                text=df_completo["Total_Ventas"].apply(lambda x: f"${x:,.2f}" if x > 0 else "")
            )
            fig_mensual.update_traces(textposition='outside')
            fig_mensual.update_layout(
                xaxis_title="Mes",
                yaxis_title="Total de Ventas ($)",
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig_mensual, use_container_width=True)

        # ============================================================
        # TOTAL GENERAL Y EXPORTACIÓN
        # ============================================================
        
        # Mostrar GRAN TOTAL
        st.markdown("---")
        st.markdown("## 💰 TOTAL GENERAL DE VENTAS")
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
                Ingresos totales del período
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Exportar a Excel
        st.markdown("### 📁 Exportar datos")
        
        if not df_detalle.empty:
            df_excel = df_detalle.copy()
            if "Fecha Venta" in df_excel.columns:
                df_excel["Fecha Venta"] = pd.to_datetime(df_excel["Fecha Venta"]).dt.strftime("%Y-%m-%d")
            if "Total" not in df_excel.columns and "Precio Venta" in df_excel.columns and "Cantidad Vendida" in df_excel.columns:
                df_excel["Total"] = df_excel["Cantidad Vendida"] * df_excel["Precio Venta"]
                df_excel["Total"] = df_excel["Total"].round(2)
            
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                df_excel.to_excel(writer, index=False, sheet_name="ReporteVentas")
            
            st.download_button(
                label="⬇️ Descargar Excel",
                data=excel_buffer.getvalue(),
                file_name=f"reporte_ventas_{fecha_inicio}_{fecha_fin}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.info("No hay datos para exportar")

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


def modulo_reporte_ventas():
    reporte_ventas()
