import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

def reporte_ventas():
    st.header("📊 Reporte de Ventas por Producto")

    # 🔐 Obtener información de la tienda desde la sesión
    rol_usuario = st.session_state.get("nivel_usuario", "")
    nombre_tienda = st.session_state.get("nombre_tienda", "Tienda Minorista")
    id_tienda = st.session_state.get("id_tienda", None)

    # Mostrar nombre de la tienda en la interfaz
    if rol_usuario == "Administrador":
        st.info(f"👑 **Administrador** - Reporte de todas las tiendas")
    else:
        st.info(f"🏪 **Tienda:** {nombre_tienda}")

    # Filtros de fecha
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1))
    with col2:
        fecha_fin = st.date_input("Hasta", value=datetime.today())

    if fecha_inicio > fecha_fin:
        st.warning("⚠️ La fecha de inicio no puede ser mayor que la de fin.")
        return

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # 🔧 Consulta según el rol del usuario (incluyendo la unidad)
        if rol_usuario == "Administrador":
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
            rows = cursor.fetchall()
            
            if rows:
                columns = ["Nombre", "Cantidad Vendida", "unidad", "Precio Venta", "Fecha Venta", "Tienda"]
            else:
                columns = []
        else:
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
            cursor.execute(query, (fecha_inicio, fecha_fin, id_tienda))
            rows = cursor.fetchall()
            columns = ["Nombre", "Cantidad Vendida", "unidad", "Precio Venta", "Fecha Venta"]

        if not rows:
            st.warning("⚠️ No se encontraron ventas en el rango seleccionado.")
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔙 Volver al Menú Principal", use_container_width=True):
                    st.session_state["module"] = None
                    st.rerun()
            return

        # ---- DataFrame ----
        df = pd.DataFrame(rows, columns=columns)

        df["Cantidad Vendida"] = pd.to_numeric(df["Cantidad Vendida"], errors="coerce").fillna(0)
        df["Precio Venta"] = pd.to_numeric(df["Precio Venta"], errors="coerce").fillna(0)
        df["Fecha Venta"] = pd.to_datetime(df["Fecha Venta"], errors="coerce")
        
        # Formatear unidad (minúscula)
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

        # ➤ Mostrar GRAN TOTAL debajo
        st.markdown("---")
        st.markdown("## 💰 TOTAL GENERAL DE VENTAS")
        st.markdown(f"""
        <div style='font-size:30px; font-weight:bold; color:green; text-align:center;'>
            ${gran_total:,.2f}
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
                
                # Nombre de la tienda
                pdf.set_font("Arial", "I", 10)
                if rol_usuario == "Administrador":
                    pdf.cell(190, 8, txt="Reporte Global - Todas las tiendas", ln=True, align="C")
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
            if st.button("🔙 Volver al Menú Principal", use_container_width=True, type="secondary"):
                st.session_state["module"] = None
                st.rerun()

    except Exception as e:
        st.error(f"❌ Error al generar el reporte: {e}")

    finally:
        if "cursor" in locals():
            cursor.close()
        if "con" in locals():
            con.close()


def modulo_reporte_ventas():
    reporte_ventas()
