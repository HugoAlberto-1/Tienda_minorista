import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime, timedelta


# 🔹 Conversión a unidad base (LIBRAS)
def convertir_a_libras(cantidad, unidad):
    if not unidad:
        return 0

    unidad = unidad.lower()

    if unidad in ["quintal", "qq"]:
        return cantidad * 100
    elif unidad in ["arroba"]:
        return cantidad * 25
    elif unidad in ["libra", "libras", "lb"]:
        return cantidad
    else:
        return cantidad


# 🔹 Conversión a unidades para perecederos
def convertir_a_quintal(cantidad_libras):
    return cantidad_libras / 100

def convertir_a_arroba(cantidad_libras):
    return cantidad_libras / 25


# 🔹 Resaltar stock bajo (menos de 10 libras para perecederos / menos de 10 unidades para no perecederos)
def resaltar_stock_bajo_perecederos(fila):
    color = 'background-color: #ffcccc' if fila["Stock Libras"] < 10 else ''
    return ['' if col != "Stock Libras" else color for col in fila.index]

def resaltar_stock_bajo_no_perecederos(fila):
    color = 'background-color: #ffcccc' if fila["Stock Unidades"] < 10 else ''
    return ['' if col != "Stock Unidades" else color for col in fila.index]


def modulo_inventario():
    st.title("📦 Inventario Actual")

    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.stop()

    id_tienda = st.session_state["id_tienda"]

    # 🔹 Filtro por tipo de producto
    col1, col2 = st.columns([1, 2])
    with col1:
        filtro_tipo = st.selectbox(
            "🔍 Filtrar por tipo de producto:",
            ("Todos", "Perecedero", "No perecedero"),
            index=0
        )

    opcion_orden = st.selectbox(
        "📑 Ordenar inventario por:",
        ("Nombre (A-Z)", "Nombre (Z-A)",
         "Stock (Ascendente)", "Stock (Descendente)",
         "Más vendidos", "Menos vendidos"),
        index=0
    )

    conn = None
    cursor = None

    try:
        conn = obtener_conexion()
        if not conn:
            st.error("❌ No se pudo conectar a la base de datos.")
            st.stop()

        cursor = conn.cursor()

        # 🔹 Obtener productos de la tienda
        cursor.execute("""
            SELECT Cod_barra, Nombre, IFNULL(Tipo_producto,'N/A')
            FROM Producto
            WHERE id_tienda = %s
        """, (id_tienda,))
        productos = cursor.fetchall()

        if not productos:
            st.info("ℹ️ No hay productos registrados para esta tienda.")
            return

        inventario_detalle = []

        for cod_barra, nombre, tipo_producto in productos:

            # 🔹 Aplicar filtro por tipo
            if filtro_tipo == "Perecedero" and tipo_producto != "Perecedero":
                continue
            elif filtro_tipo == "No perecedero" and tipo_producto != "No perecedero":
                continue

            # 🔹 Compras
            cursor.execute("""
                SELECT cantidad_comprada, unidad
                FROM ProductoxCompra
                WHERE Cod_barra = %s AND id_tienda = %s
            """, (cod_barra, id_tienda))

            compras = cursor.fetchall()

            # Para perecederos (en libras)
            total_comprado_lb = sum(
                convertir_a_libras(c[0], c[1]) for c in compras
            )

            # Para no perecederos (en unidades)
            total_comprado_unidades = sum(c[0] for c in compras)

            # 🔹 Ventas
            cursor.execute("""
                SELECT Cantidad_vendida, unidad
                FROM ProductoxVenta
                WHERE Cod_barra = %s AND id_tienda = %s
            """, (cod_barra, id_tienda))

            ventas = cursor.fetchall()

            # Para perecederos (en libras)
            total_vendido_lb = sum(
                convertir_a_libras(v[0], v[1]) for v in ventas
            )

            # Para no perecederos (en unidades)
            total_vendido_unidades = sum(v[0] for v in ventas)

            stock_libras = total_comprado_lb - total_vendido_lb
            stock_unidades = total_comprado_unidades - total_vendido_unidades

            # 🔹 Construir diccionario según el tipo de filtro
            if filtro_tipo == "No perecedero":
                inventario_detalle.append({
                    "Nombre": nombre,
                    "Tipo": tipo_producto,
                    "Stock Unidades": stock_unidades,
                    "_Total_vendidos": int(total_vendido_unidades)
                })
            else:  # Para "Todos" o "Perecedero"
                inventario_detalle.append({
                    "Nombre": nombre,
                    "Tipo": tipo_producto,
                    "Stock Libras": stock_libras,
                    "Stock Quintal": convertir_a_quintal(stock_libras),
                    "Stock Arroba": convertir_a_arroba(stock_libras),
                    "_Total_vendidos": int(total_vendido_lb) if tipo_producto == "Perecedero" else int(total_vendido_unidades)
                })

        # 🔹 Crear DataFrame
        df = pd.DataFrame(inventario_detalle)

        if df.empty:
            st.warning(f"⚠️ No hay productos del tipo '{filtro_tipo}' para mostrar.")
            return

        # 🔹 Agrupar por nombre
        if filtro_tipo == "No perecedero":
            df_agrupado = df.groupby(df["Nombre"].str.lower(), as_index=False).agg({
                "Nombre": "first",
                "Tipo": "first",
                "Stock Unidades": "sum",
                "_Total_vendidos": "sum"
            })
        else:
            df_agrupado = df.groupby(df["Nombre"].str.lower(), as_index=False).agg({
                "Nombre": "first",
                "Tipo": "first",
                "Stock Libras": "sum",
                "Stock Quintal": "sum",
                "Stock Arroba": "sum",
                "_Total_vendidos": "sum"
            })

        # 🔹 Ordenación
        columna_stock = "Stock Libras" if filtro_tipo != "No perecedero" else "Stock Unidades"
        
        if opcion_orden == "Nombre (A-Z)":
            df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=True)
        elif opcion_orden == "Nombre (Z-A)":
            df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=False)
        elif opcion_orden == "Stock (Ascendente)":
            df_agrupado = df_agrupado.sort_values(columna_stock, ascending=True)
        elif opcion_orden == "Stock (Descendente)":
            df_agrupado = df_agrupado.sort_values(columna_stock, ascending=False)
        elif opcion_orden == "Más vendidos":
            df_agrupado = df_agrupado.sort_values("_Total_vendidos", ascending=False)
        else:
            df_agrupado = df_agrupado.sort_values("_Total_vendidos", ascending=True)

        df_agrupado = df_agrupado.drop(columns=["_Total_vendidos"])

        # 🔹 Aplicar estilo según el tipo de filtro
        if filtro_tipo == "No perecedero":
            styled_df = df_agrupado.style.apply(resaltar_stock_bajo_no_perecederos, axis=1).format({
                "Stock Unidades": "{:.0f}"
            })
        else:
            styled_df = df_agrupado.style.apply(resaltar_stock_bajo_perecederos, axis=1).format({
                "Stock Libras": "{:.2f}",
                "Stock Quintal": "{:.2f}",
                "Stock Arroba": "{:.2f}"
            })

        # 🔹 Mostrar información del filtro activo y las columnas
        if filtro_tipo == "Todos":
            st.subheader("📋 Inventario completo - Unidades mixtas")
            st.info("ℹ️ Mostrando productos perecederos en Libras/Quintal/Arroba y no perecederos en Unidades")
        elif filtro_tipo == "Perecedero":
            st.subheader("📋 Inventario de productos perecederos (Libras, Quintal, Arroba)")
        else:
            st.subheader("📋 Inventario de productos no perecederos (Unidades)")
        
        st.dataframe(styled_df, use_container_width=True)

        # 🔹 Productos próximos a vencer (solo para perecederos o todos)
        if filtro_tipo != "No perecedero":
            hoy = datetime.now().date()
            prox_mes = (datetime.now() + timedelta(days=30)).date()

            cursor.execute("""
                SELECT pc.Cod_barra, p.Nombre, pc.unidad, pc.fecha_vencimiento
                FROM ProductoxCompra pc
                JOIN Producto p ON pc.Cod_barra = p.Cod_barra
                WHERE pc.fecha_vencimiento BETWEEN %s AND %s
                  AND pc.id_tienda = %s
                  AND p.id_tienda = %s
                ORDER BY pc.fecha_vencimiento ASC
            """, (hoy, prox_mes, id_tienda, id_tienda))

            proximos = cursor.fetchall()

            if proximos:
                df_v = pd.DataFrame(
                    proximos,
                    columns=["Código de barras", "Nombre", "Unidad", "Fecha vencimiento"]
                )
                df_v["Fecha vencimiento"] = pd.to_datetime(df_v["Fecha vencimiento"]).dt.date

                st.subheader("⏳ Productos próximos a vencer (30 días)")
                st.dataframe(df_v, use_container_width=True)
            else:
                if filtro_tipo == "Perecedero":
                    st.info("✅ No hay productos perecederos próximos a vencer.")
                else:
                    st.info("✅ No hay productos próximos a vencer.")
        else:
            st.info("📌 Los productos no perecederos no tienen fecha de vencimiento.")

    except Exception as e:
        st.error(f"❌ Error al cargar inventario: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    st.markdown("---")
    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
