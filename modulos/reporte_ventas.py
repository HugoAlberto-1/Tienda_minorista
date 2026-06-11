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
        </style>
    """, unsafe_allow_html=True)


def reporte_ventas():
    configurar_estilo()
    
    st.markdown('<div class="report-title">📊 Reporte de Ventas</div>', unsafe_allow_html=True)
    st.markdown('<div class="report-subtitle">Análisis de ventas mensuales</div>', unsafe_allow_html=True)

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

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # ============================================================
        # PRIMERO: Obtener el TOTAL GENERAL desde la base de datos
        # ============================================================
        if id_tienda_usar is None:
            query_total = """
                SELECT COALESCE(SUM(pv.Cantidad_vendida * pv.Precio_Venta), 0) as TotalGeneral
                FROM Venta v
                JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
            """
            cursor.execute(query_total, (fecha_inicio, fecha_fin))
        else:
            query_total = """
                SELECT COALESCE(SUM(pv.Cantidad_vendida * pv.Precio_Venta), 0) as TotalGeneral
                FROM Venta v
                JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
                  AND v.id_tienda = %s
            """
            cursor.execute(query_total, (fecha_inicio, fecha_fin, id_tienda_usar))
        
        total_row = cursor.fetchone()
        gran_total = float(total_row[0]) if total_row else 0
        gran_total = round(gran_total, 2)

        # ============================================================
        # CONSULTA PRINCIPAL - Ventas agrupadas
        # ============================================================
        
        if id_tienda_usar is None:
            # TODAS LAS TIENDAS - Ventas por tienda
            query = """
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
            cursor.execute(query, (fecha_inicio, fecha_fin))
            rows = cursor.fetchall()
            
            if rows:
                df = pd.DataFrame(rows, columns=["Tienda", "Total_Ventas"])
                df["Total_Ventas"] = df["Total_Ventas"].astype(float)
                
                st.markdown("### 📊 Ventas por Tienda")
                fig = px.bar(
                    df,
                    x="Tienda",
                    y="Total_Ventas",
                    title="Total de Ventas por Tienda",
                    color="Total_Ventas",
                    color_continuous_scale="Blues",
                    text=df["Total_Ventas"].apply(lambda x: f"${x:,.2f}")
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    xaxis_title="Tienda",
                    yaxis_title="Total de Ventas ($)",
                    height=500,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Datos para exportar (detalle)
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
                    ORDER BY v.Fecha DESC
                """
                cursor.execute(query_detalle, (fecha_inicio, fecha_fin))
                rows_detalle = cursor.fetchall()
                if rows_detalle:
                    df_detalle = pd.DataFrame(rows_detalle, columns=["Nombre", "Cantidad Vendida", "unidad", "Precio Venta", "Fecha Venta", "Tienda"])
                else:
                    df_detalle = pd.DataFrame()
            else:
                st.warning("No hay datos en el período seleccionado.")
                return
                
        else:
            # TIENDA ESPECÍFICA - Ventas por mes
            st.markdown(f"### 📊 Análisis de Ventas Mensuales - {filtro_tienda}")
            
            # Consulta para ventas mensuales
            query = """
                SELECT 
                    CONCAT(
                        CASE MONTH(v.Fecha)
                            WHEN 1 THEN 'Ene' WHEN 2 THEN 'Feb' WHEN 3 THEN 'Mar'
                            WHEN 4 THEN 'Abr' WHEN 5 THEN 'May' WHEN 6 THEN 'Jun'
                            WHEN 7 THEN 'Jul' WHEN 8 THEN 'Ago' WHEN 9 THEN 'Sep'
                            WHEN 10 THEN 'Oct' WHEN 11 THEN 'Nov' WHEN 12 THEN 'Dic'
                        END,
                        ' ', YEAR(v.Fecha)
                    ) as Nombre_Mes,
                    COALESCE(SUM(pv.Cantidad_vendida * pv.Precio_Venta), 0) as Total_Ventas
                FROM Venta v
                JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                WHERE DATE(v.Fecha) BETWEEN %s AND %s
                  AND v.id_tienda = %s
                GROUP BY YEAR(v.Fecha), MONTH(v.Fecha)
                ORDER BY YEAR(v.Fecha) ASC, MONTH(v.Fecha) ASC
            """
            cursor.execute(query, (fecha_inicio, fecha_fin, id_tienda_usar))
            rows = cursor.fetchall()
            
            if rows:
                df = pd.DataFrame(rows, columns=["Nombre_Mes", "Total_Ventas"])
                df["Total_Ventas"] = df["Total_Ventas"].astype(float)
                
                # Gráfico de barras
                fig = px.bar(
                    df,
                    x="Nombre_Mes",
                    y="Total_Ventas",
                    title="Total de Ventas por Mes",
                    color="Total_Ventas",
                    color_continuous_scale="Blues",
                    text=df["Total_Ventas"].apply(lambda x: f"${x:,.2f}")
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    xaxis_title="Mes",
                    yaxis_title="Total de Ventas ($)",
                    height=500,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Datos para exportar (detalle)
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
                    ORDER BY v.Fecha DESC
                """
                cursor.execute(query_detalle, (fecha_inicio, fecha_fin, id_tienda_usar))
                rows_detalle = cursor.fetchall()
                if rows_detalle:
                    df_detalle = pd.DataFrame(rows_detalle, columns=["Nombre", "Cantidad Vendida", "unidad", "Precio Venta", "Fecha Venta"])
                else:
                    df_detalle = pd.DataFrame()
            else:
                st.warning("No hay datos de ventas en el período seleccionado para esta tienda.")
                return

        # ============================================================
        # TOTAL GENERAL Y EXPORTACIÓN
        # ============================================================
        
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
        st.markdown("### 📁 Exportar datos")
        
        if not df_detalle.empty:
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                # Hoja 1: Detalle de ventas
                df_excel = df_detalle.copy()
                if "Fecha Venta" in df_excel.columns:
                    df_excel["Fecha Venta"] = pd.to_datetime(df_excel["Fecha Venta"]).dt.strftime("%Y-%m-%d")
                df_excel.to_excel(writer, index=False, sheet_name="Detalle_Ventas")
                
                # Hoja 2: Resumen por mes (si es tienda específica)
                if id_tienda_usar is not None and 'df' in locals() and not df.empty:
                    df_resumen = df[["Nombre_Mes", "Total_Ventas"]].copy()
                    df_resumen["Total_Ventas"] = df_resumen["Total_Ventas"].round(2)
                    df_resumen.to_excel(writer, index=False, sheet_name="Resumen_Mensual")
                
                # Hoja 3: Totales
                df_totales = pd.DataFrame({
                    "Concepto": ["TOTAL GENERAL DE VENTAS"],
                    "Monto": [gran_total]
                })
                df_totales.to_excel(writer, index=False, sheet_name="Totales")
            
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
