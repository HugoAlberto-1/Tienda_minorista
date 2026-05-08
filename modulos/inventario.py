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
        return cantidad  # Para productos por unidad


# 🔹 Resaltar stock bajo
def resaltar_stock_bajo(fila):
    if "Stock Libras" in fila.index:
        color = 'background-color: #ffcccc' if fila["Stock Libras"] < 10 else ''
        return ['' if col != "Stock Libras" else color for col in fila.index]

    if "Stock Unidades" in fila.index:
        color = 'background-color: #ffcccc' if fila["Stock Unidades"] < 5 else ''
        return ['' if col != "Stock Unidades" else color for col in fila.index]

    return ['' for _ in fila.index]


def modulo_inventario():
    st.title("📦 Inventario Actual")

    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión.")
        st.stop()

    id_tienda = st.session_state["id_tienda"]

    # 🔥 NUEVO FILTRO
    filtro_tipo = st.selectbox(
        "🔎 Ver productos:",
        ("Todos", "Perecederos", "No perecederos"),
        index=0
    )

    opcion_orden = st.selectbox(
        "📑 Ordenar inventario por:",
        ("Nombre (A-Z)", "Nombre (Z-A)",
         "Stock (Ascendente)", "Stock (Descendente)",
         "Más vendidos", "Menos vendidos"),
        index=0
    )

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Cod_barra, Nombre, IFNULL(Tipo_producto,'N/A')
            FROM Producto
            WHERE id_tienda = %s
        """, (id_tienda,))
        productos = cursor.fetchall()

        inventario_detalle = []

        for cod_barra, nombre, tipo_producto in productos:

            # Aplicar filtro
            if filtro_tipo == "Perecederos" and tipo_producto.lower() != "perecedero":
                continue
            if filtro_tipo == "No perecederos" and tipo_producto.lower() == "perecedero":
                continue

            # 🔹 Compras
            cursor.execute("""
                SELECT cantidad_comprada, unidad
                FROM ProductoxCompra
                WHERE Cod_barra = %s AND id_tienda = %s
            """, (cod_barra, id_tienda))

            compras = cursor.fetchall()

            # 🔹 Ventas
            cursor.execute("""
                SELECT Cantidad_vendida, unidad
                FROM ProductoxVenta
                WHERE Cod_barra = %s AND id_tienda = %s
            """, (cod_barra, id_tienda))

            ventas = cursor.fetchall()

            # -----------------------
            # 🟢 PRODUCTOS PERECEDEROS
            # -----------------------
            if tipo_producto.lower() == "perecedero":

                total_comprado_lb = sum(
                    convertir_a_libras(c[0], c[1]) for c in compras
                )

                total_vendido_lb = sum(
                    convertir_a_libras(v[0], v[1]) for v in ventas
                )

                stock_libras = total_comprado_lb - total_vendido_lb

                inventario_detalle.append({
                    "Nombre": nombre,
                    "Tipo": tipo_producto,
                    "Stock Libras": stock_libras,
                    "Stock Quintal": stock_libras / 100,
                    "Stock Arroba": stock_libras / 25,
                    "_Total_vendidos": int(total_vendido_lb)
                })

            # -----------------------
            # 🔵 PRODUCTOS NO PERECEDEROS
            # -----------------------
            else:

                total_comprado = sum(c[0] for c in compras)
                total_vendido = sum(v[0] for v in ventas)

                stock_unidades = total_comprado - total_vendido

                inventario_detalle.append({
                    "Nombre": nombre,
                    "Tipo": tipo_producto,
                    "Stock Unidades": stock_unidades,
                    "_Total_vendidos": int(total_vendido)
                })

        if not inventario_detalle:
            st.info("ℹ️ No hay productos para este filtro.")
            return

        df = pd.DataFrame(inventario_detalle)

        df_agrupado = df.groupby(df["Nombre"].str.lower(), as_index=False).agg("sum")
        df_agrupado["Nombre"] = df.groupby(df["Nombre"].str.lower())["Nombre"].first().values
        df_agrupado["Tipo"] = df.groupby(df["Nombre"].str.lower())["Tipo"].first().values

        # 🔹 Ordenación
        if opcion_orden == "Nombre (A-Z)":
            df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower())
        elif opcion_orden == "Nombre (Z-A)":
            df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=False)
        elif "Stock Libras" in df_agrupado.columns:
            df_agrupado = df_agrupado.sort_values("Stock Libras", ascending=(opcion_orden=="Stock (Ascendente)"))
        elif "Stock Unidades" in df_agrupado.columns:
            df_agrupado = df_agrupado.sort_values("Stock Unidades", ascending=(opcion_orden=="Stock (Ascendente)"))

        df_agrupado = df_agrupado.drop(columns=["_Total_vendidos"])

        styled_df = df_agrupado.style.apply(resaltar_stock_bajo, axis=1).format("{:.2f}")

        st.subheader("📋 Inventario")
        st.dataframe(styled_df, use_container_width=True)

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
