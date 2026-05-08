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


# 🔹 Convertir desde libras a unidad seleccionada
def convertir_desde_libras(stock_lb, unidad_destino):
    if unidad_destino == "Libras":
        return stock_lb
    elif unidad_destino == "Quintal":
        return stock_lb / 100
    elif unidad_destino == "Arroba":
        return stock_lb / 25


# 🔹 Resaltar stock bajo (menos de 10 libras reales)
def resaltar_stock_bajo(fila):
    stock_real_lb = fila["_stock_lb"]
    color = 'background-color: #ffcccc' if stock_real_lb < 10 else ''
    return [color if col == "Stock" else '' for col in fila.index]


def modulo_inventario():
    st.title("📦 Inventario Actual")

    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.stop()

    id_tienda = st.session_state["id_tienda"]

    # 🔥 Selector de unidad dinámica
    unidad_visualizacion = st.selectbox(
        "📏 Ver inventario en:",
        ("Libras", "Quintal", "Arroba"),
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
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Cod_barra, Nombre, IFNULL(Tipo_producto,'N/A')
            FROM Producto
            WHERE id_tienda = %s
        """, (id_tienda,))
        productos = cursor.fetchall()

        if not productos:
            st.info("ℹ️ No hay productos registrados.")
            return

        inventario_detalle = []

        for cod_barra, nombre, tipo_producto in productos:

            # 🔹 Compras
            cursor.execute("""
                SELECT cantidad_comprada, unidad
                FROM ProductoxCompra
                WHERE Cod_barra = %s AND id_tienda = %s
            """, (cod_barra, id_tienda))

            compras = cursor.fetchall()
            total_comprado_lb = sum(
                convertir_a_libras(c[0], c[1]) for c in compras
            )

            # 🔹 Ventas
            cursor.execute("""
                SELECT Cantidad_vendida, unidad
                FROM ProductoxVenta
                WHERE Cod_barra = %s AND id_tienda = %s
            """, (cod_barra, id_tienda))

            ventas = cursor.fetchall()
            total_vendido_lb = sum(
                convertir_a_libras(v[0], v[1]) for v in ventas
            )

            stock_lb = total_comprado_lb - total_vendido_lb

            inventario_detalle.append({
                "Nombre": nombre,
                "Tipo": tipo_producto,
                "Stock": convertir_desde_libras(stock_lb, unidad_visualizacion),
                "_stock_lb": stock_lb,
                "_Total_vendidos": int(total_vendido_lb)
            })

        df = pd.DataFrame(inventario_detalle)

        df_agrupado = df.groupby(df["Nombre"].str.lower(), as_index=False).agg({
            "Nombre": "first",
            "Tipo": "first",
            "Stock": "sum",
            "_stock_lb": "sum",
            "_Total_vendidos": "sum"
        })

        # 🔹 Ordenación
        if opcion_orden == "Nombre (A-Z)":
            df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=True)
        elif opcion_orden == "Nombre (Z-A)":
            df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=False)
        elif opcion_orden == "Stock (Ascendente)":
            df_agrupado = df_agrupado.sort_values("Stock", ascending=True)
        elif opcion_orden == "Stock (Descendente)":
            df_agrupado = df_agrupado.sort_values("Stock", ascending=False)
        elif opcion_orden == "Más vendidos":
            df_agrupado = df_agrupado.sort_values("_Total_vendidos", ascending=False)
        else:
            df_agrupado = df_agrupado.sort_values("_Total_vendidos", ascending=True)

        df_agrupado = df_agrupado.drop(columns=["_Total_vendidos"])

        styled_df = df_agrupado.style.apply(resaltar_stock_bajo, axis=1).format({
            "Stock": "{:.2f}"
        })

        st.subheader(f"📋 Inventario en {unidad_visualizacion}")
        st.dataframe(styled_df, use_container_width=True)

        # 🔹 Productos próximos a vencer
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
            st.info("✅ No hay productos próximos a vencer.")

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
