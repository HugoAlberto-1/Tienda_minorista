import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

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
        
        /* Metric cards */
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
        
        /* Botón volver - Color gris con texto blanco */
        .volver-btn button {{
            background-color: #6c757d !important;
            background: #6c757d !important;
            color: white !important;
        }}
        
        .volver-btn button:hover {{
            background-color: #5a6268 !important;
            background: #5a6268 !important;
            color: white !important;
            transform: translateY(-2px);
        }}
        
        /* Labels */
        .stTextInput > label, .stSelectbox > label {{
            color: {COLOR_TEXT_DARK} !important;
            font-weight: 500 !important;
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
        
        /* Fecha inputs - labels en color oscuro */
        .stDateInput label {{
            color: #333333 !important;
            font-weight: 500 !important;
        }}
        
        /* Fecha inputs - texto dentro del input */
        .stDateInput input {{
            color: #333333 !important;
            background-color: white !important;
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
        
        /* Alertas */
        .stAlert {{
            background-color: {COLOR_CARD} !important;
            border: 1px solid {COLOR_BORDER} !important;
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
                # Agregar opción "Todas las tiendas"
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
        # Vendedor: solo su tienda
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

        # 🔧 Consulta según el rol del usuario y el filtro de tienda
        if rol_usuario == "Administrador":
            if id_tienda_usar is None:
                # Todas las tiendas
                query = """
                    SELECT
                        p.Nombre,
                        pv.Cantidad_vendida,
                        pv.unidad,
                        pv.Precio_Venta,
                        v.Fecha,
                        t.nombre as Tienda
                    FROM Venta v
                    JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                    JOIN Producto p ON p.Cod_barra = pv.Cod_barra
                    LEFT JOIN tienda t ON v.id_tienda = t.id_tienda
                    WHERE DATE(v.Fecha) BETWEEN %s AND %s
                    ORDER BY v.Fecha DESC, p.Nombre ASC
                """
                cursor.execute(query, (fecha_inicio, fecha_fin))
            else:
                # Tienda específica
                query = """
                    SELECT
                        p.Nombre,
                        pv.Cantidad_vendida,
                        pv.unidad,
                        pv.Precio_Venta,
                        v.Fecha,
                        t.nombre as Tienda
                    FROM Venta v
                    JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
                    JOIN Producto p ON p.Cod_barra = pv.Cod_barra
                    LEFT JOIN tienda t ON v.id_tienda = t.id_tienda
                    WHERE DATE(v.Fecha) BETWEEN %s AND %s
                      AND v.id_tienda = %s
                    ORDER BY v.Fecha DESC, p.Nombre ASC
                """
                cursor.execute(query, (fecha_inicio, fecha_fin, id_tienda_usar))
            
            rows = cursor.fetchall()
            if rows:
                columns = ["Nombre", "Cantidad Vendida", "unidad", "Precio Venta", "Fecha Venta", "Tienda"]
            else:
                columns = []
        else:
            # Vendedor
            query = """
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
            cursor.execute(query, (fecha_inicio, fecha_fin, id_tienda_usar))
            rows = cursor.fetchall()
            columns = ["Nombre", "Cantidad Vendida", "unidad", "Precio Venta", "Fecha Venta"]

        if not rows:
            # Mensaje de advertencia con color oscuro
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

        # ---- DataFrame ----
        df = pd.DataFrame(rows, columns=columns)

        df["Cantidad Vendida"] = pd.to_numeric(df["Cantidad Vendida"], errors="coerce").fillna(0)
        df["Precio Venta"] = pd.to_numeric(df["Precio Venta"], errors="coerce").fillna(0)
        df["Fecha Venta"] = pd.to_datetime(df["Fecha Venta"], errors="coerce")
        
        # Formatear unidad
        df["unidad"] = df["unidad"].fillna("").astype(str)

        # ➤ CALCULAR TOTAL
        df["Total"] = (df["Cantidad Vendida"] * df["Precio Venta"]).round(2)

        # ➤ CALCULAR GRAN TOTAL
        gran_total = df["Total"].sum().round(2)

        # Mostrar tabla
        st.markdown("---")
        st.markdown("### 🗂 Detalles de Ventas")
        
        # Formatear para mostrar
        df_mostrar = df.copy()
        df_mostrar["Cantidad Vendida"] = df_mostrar.apply(
            lambda x: f"{x['Cantidad Vendida']:.2f} {x['unidad']}" if x['unidad'] else f"{x['Cantidad Vendida']:.2f}", axis=1
        )
        df_mostrar["Precio Venta"] = df_mostrar["Precio Venta"].apply(lambda x: f"${x:.2f}")
        df_mostrar["Total"] = df_mostrar["Total"].apply(lambda x: f"${x:.2f}")
        df_mostrar["Fecha Venta"] = df_mostrar["Fecha Venta"].dt.strftime("%Y-%m-%d")
        
        # Seleccionar columnas a mostrar
        if rol_usuario == "Administrador":
            df_mostrar = df_mostrar[["Nombre", "Cantidad Vendida", "Precio Venta", "Total", "Fecha Venta", "Tienda"]]
        else:
            df_mostrar = df_mostrar[["Nombre", "Cantidad Vendida", "Precio Venta", "Total", "Fecha Venta"]]
        
        st.dataframe(df_mostrar, use_container_width=True)

        # ➤ Mostrar GRAN TOTAL debajo - Con recuadro
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

        # ➤ Exportar a Excel
        st.markdown("### 📁 Exportar ventas filtradas")

        col1, col2 = st.columns(2)

        with col1:
            # Para Excel, exportar con unidad separada
            df_excel = df.copy()
            df_excel["Fecha Venta"] = df_excel["Fecha Venta"].dt.strftime("%Y-%m-%d")
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

        # ➤ Exportar PDF
        with col2:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)

                # Título
                pdf.set_font("Arial", "B", 16)
                pdf.cell(190, 10, txt="Reporte de Ventas", ln=True, align="C")
                pdf.ln(5)
                
                # Nombre de la tienda o filtro
                pdf.set_font("Arial", "I", 10)
                if rol_usuario == "Administrador":
                    pdf.cell(190, 8, txt=f"Reporte - {filtro_tienda}", ln=True, align="C")
                else:
                    pdf.cell(190, 8, txt=f"Tienda: {nombre_tienda}", ln=True, align="C")
                
                pdf.cell(190, 8, txt=f"Periodo: {fecha_inicio} al {fecha_fin}", ln=True, align="C")
                pdf.ln(5)

                # Definir columnas
                if rol_usuario == "Administrador":
                    headers = ["Producto", "Cantidad (Unidad)", "Precio", "Total", "Fecha", "Tienda"]
                    widths = [55, 25, 20, 20, 30, 40]
                else:
                    headers = ["Producto", "Cantidad (Unidad)", "Precio", "Total", "Fecha"]
                    widths = [70, 30, 25, 25, 40]

                pdf.set_font("Arial", "B", 9)
                for w, h in zip(widths, headers):
                    pdf.cell(w, 8, h, 1, 0, "C")
                pdf.ln(8)

                pdf.set_font("Arial", size=8)
                for _, row in df.iterrows():
                    fecha_str = row["Fecha Venta"].strftime("%Y-%m-%d") if pd.notna(row["Fecha Venta"]) else ""
                    cantidad_con_unidad = f"{row['Cantidad Vendida']:.2f} {row['unidad']}" if row['unidad'] else f"{row['Cantidad Vendida']:.2f}"
                    
                    pdf.cell(widths[0], 8, str(row["Nombre"])[:30], 1)
                    pdf.cell(widths[1], 8, cantidad_con_unidad[:25], 1, 0, "R")
                    pdf.cell(widths[2], 8, f"${row['Precio Venta']:.2f}", 1, 0, "R")
                    pdf.cell(widths[3], 8, f"${row['Total']:.2f}", 1, 0, "R")
                    pdf.cell(widths[4], 8, fecha_str, 1, 0, "C")
                    
                    if rol_usuario == "Administrador":
                        pdf.cell(widths[5], 8, str(row["Tienda"])[:25], 1, 0, "C")
                    
                    pdf.ln(6)

                # Total general
                pdf.set_font("Arial", "B", 12)
                pdf.ln(5)
                pdf.cell(190, 10, f"TOTAL GENERAL: ${gran_total:,.2f}", 0, 1, "R")

                pdf_output = pdf.output(dest="S")
                if isinstance(pdf_output, str):
                    pdf_bytes = pdf_output.encode("latin-1")
                else:
                    pdf_bytes = bytes(pdf_output)

                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"reporte_ventas_{fecha_inicio}_{fecha_fin}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error al generar PDF: {e}")

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
