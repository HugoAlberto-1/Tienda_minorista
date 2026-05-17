import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime, timedelta

# Lista de categorías
CATEGORIAS = [
    "Abarrotes",
    "Granos y productos a granel",
    "Sopas, pastas y consomés",
    "Condimentos y salsas",
    "Bebidas",
    "Lácteos y derivados",
    "Snacks y boquitas",
    "Dulces y chocolates",
    "Panadería y repostería",
    "Ingredientes para hornear",
    "Carnes y congelados",
    "Enlatados y conservas",
    "Desechables y empaques",
    "Limpieza del hogar",
    "Higiene personal",
    "Cuidado del bebé",
    "Medicamentos y botiquín",
    "Papelería y útiles escolares",
    "Juguetes y regalos",
    "Accesorios personales y belleza",
    "Hogar y utensilios",
    "Ferretería básica y eléctricos",
    "Mascotas",
    "Productos naturales y especias",
    "Productos de temporada y fiesta"
]

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


def modulo_inventario():
    st.title("📦 Inventario Actual")

    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.stop()

    id_tienda = st.session_state["id_tienda"]

    # 🔹 Filtro por categoría (sin opción "Todos")
    filtro_categoria = st.selectbox(
        "🔍 Filtrar por categoría:",
        CATEGORIAS,
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

        # 🔹 Obtener productos de la tienda filtrados por categoría
        cursor.execute("""
            SELECT Cod_barra, Nombre, IFNULL(tipo,'N/A')
            FROM Producto
            WHERE id_tienda = %s AND tipo = %s
        """, (id_tienda, filtro_categoria))
        
        productos = cursor.fetchall()

        if not productos:
            st.info(f"ℹ️ No hay productos registrados en la categoría '{filtro_categoria}' para esta tienda.")
            return

        inventario_detalle = []

        for cod_barra, nombre, categoria in productos:

            # 🔹 Compras
            cursor.execute("""
                SELECT cantidad_comprada, unidad
                FROM ProductoxCompra
                WHERE Cod_barra = %s AND id_tienda = %s
            """, (cod_barra, id_tienda))

            compras = cursor.fetchall()

            # Total comprado en libras
            total_comprado_lb = sum(
                convertir_a_libras(c[0], c[1]) for c in compras
            )

            # Total comprado en unidades
            total_comprado_unidades = sum(c[0] for c in compras)

            # 🔹 Ventas
            cursor.execute("""
                SELECT Cantidad_vendida, unidad
                FROM ProductoxVenta
                WHERE Cod_barra = %s AND id_tienda = %s
            """, (cod_barra, id_tienda))

            ventas = cursor.fetchall()

            # Total vendido en libras
            total_vendido_lb = sum(
                convertir_a_libras(v[0], v[1]) for v in ventas
            )

            # Total vendido en unidades
            total_vendido_unidades = sum(v[0] for v in ventas)

            stock_libras = total_comprado_lb - total_vendido_lb
            stock_unidades = total_comprado_unidades - total_vendido_unidades

            # Agregar ambos tipos de stock
            inventario_detalle.append({
                "Nombre": nombre,
                "Categoría": categoria,
                "Stock Libras": stock_libras,
                "Stock Quintal": convertir_a_quintal(stock_libras),
                "Stock Arroba": convertir_a_arroba(stock_libras),
                "Stock Unidades": stock_unidades,
                "_Total_vendidos_libras": int(total_vendido_lb),
                "_Total_vendidos_unidades": int(total_vendido_unidades)
            })

        # 🔹 Crear DataFrame
        df = pd.DataFrame(inventario_detalle)

        if df.empty:
            st.warning(f"⚠️ No hay productos en la categoría '{filtro_categoria}' para mostrar.")
            return

        # 🔹 Agrupar por nombre
        df_agrupado = df.groupby(df["Nombre"].str.lower(), as_index=False).agg({
            "Nombre": "first",
            "Categoría": "first",
            "Stock Libras": "sum",
            "Stock Quintal": "sum",
            "Stock Arroba": "sum",
            "Stock Unidades": "sum",
            "_Total_vendidos_libras": "sum",
            "_Total_vendidos_unidades": "sum"
        })

        # 🔹 Ordenación
        if opcion_orden == "Nombre (A-Z)":
            df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=True)
        elif opcion_orden == "Nombre (Z-A)":
            df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=False)
        elif opcion_orden == "Stock (Ascendente)":
            # Por defecto ordenar por Stock Libras
            df_agrupado = df_agrupado.sort_values("Stock Libras", ascending=True)
        elif opcion_orden == "Stock (Descendente)":
            df_agrupado = df_agrupado.sort_values("Stock Libras", ascending=False)
        elif opcion_orden == "Más vendidos":
            # Ordenar por el total de ventas (usando libras como referencia principal)
            df_agrupado = df_agrupado.sort_values("_Total_vendidos_libras", ascending=False)
        else:  # "Menos vendidos"
            df_agrupado = df_agrupado.sort_values("_Total_vendidos_libras", ascending=True)

        # Eliminar columnas auxiliares
        df_agrupado = df_agrupado.drop(columns=["_Total_vendidos_libras", "_Total_vendidos_unidades"])

        # 🔹 Aplicar formato y estilo
        def resaltar_stock_bajo(row):
            # Resaltar si stock en libras es menor a 10 O stock en unidades es menor a 10
            estilo = []
            for col in row.index:
                if col == "Stock Libras" and row["Stock Libras"] < 10:
                    estilo.append('background-color: #ffcccc')
                elif col == "Stock Unidades" and row["Stock Unidades"] < 10:
                    estilo.append('background-color: #ffcccc')
                else:
                    estilo.append('')
            return estilo

        styled_df = df_agrupado.style.apply(resaltar_stock_bajo, axis=1).format({
            "Stock Libras": "{:.2f}",
            "Stock Quintal": "{:.2f}",
            "Stock Arroba": "{:.2f}",
            "Stock Unidades": "{:.0f}"
        })

        # 🔹 Mostrar información del filtro activo
        st.subheader(f"📋 Inventario por categoría: {filtro_categoria}")
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
              AND p.tipo = %s
            ORDER BY pc.fecha_vencimiento ASC
        """, (hoy, prox_mes, id_tienda, id_tienda, filtro_categoria))

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
            st.info("✅ No hay productos próximos a vencer en esta categoría.")

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
