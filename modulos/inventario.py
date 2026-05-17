import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime, timedelta

# Lista de categorías
CATEGORIAS = [
    "Aceites, grasas y mantecas",
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

    # 🔹 Filtro por tipo de producto (ahora con categorías)
    col1, col2 = st.columns([1, 2])
    with col1:
        # Opciones de filtro: Todas las categorías + "Todos"
        opciones_filtro = ["Todos"] + CATEGORIAS
        filtro_categoria = st.selectbox(
            "🔍 Filtrar por categoría:",
            opciones_filtro,
            index=0
        )
        
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

        # 🔹 Obtener productos de la tienda (incluyendo categoría)
        cursor.execute("""
            SELECT Cod_barra, Nombre, IFNULL(Tipo_producto,'N/A'), IFNULL(Categoria,'N/A')
            FROM Producto
            WHERE id_tienda = %s
        """, (id_tienda,))
        productos = cursor.fetchall()

        if not productos:
            st.info("ℹ️ No hay productos registrados para esta tienda.")
            return

        inventario_detalle = []

        for cod_barra, nombre, tipo_producto, categoria in productos:

            # 🔹 Aplicar filtro por tipo (todos, perecedero o no perecedero)
            if filtro_tipo == "Perecedero" and tipo_producto != "Perecedero":
                continue
            elif filtro_tipo == "No perecedero" and tipo_producto != "No perecedero":
                continue
            
            # 🔹 Aplicar filtro por categoría
            if filtro_categoria != "Todos" and categoria != filtro_categoria:
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

            # Determinar qué tipo de stock mostrar basado en el tipo de producto real
            # Para productos perecederos mostrar en libras, para no perecederos en unidades
            if tipo_producto == "No perecedero":
                inventario_detalle.append({
                    "Nombre": nombre,
                    "Tipo": tipo_producto,
                    "Categoría": categoria,
                    "Stock Unidades": stock_unidades,
                    "_Total_vendidos": int(total_vendido_unidades)
                })
            else:  # Para "Perecedero" o "N/A"
                inventario_detalle.append({
                    "Nombre": nombre,
                    "Tipo": tipo_producto,
                    "Categoría": categoria,
                    "Stock Libras": stock_libras,
                    "Stock Quintal": convertir_a_quintal(stock_libras),
                    "Stock Arroba": convertir_a_arroba(stock_libras),
                    "_Total_vendidos": int(total_vendido_lb)
                })

        # 🔹 Crear DataFrame
        df = pd.DataFrame(inventario_detalle)

        if df.empty:
            st.warning(f"⚠️ No hay productos que coincidan con los filtros seleccionados.")
            return

        # 🔹 Determinar si hay mezcla de tipos de productos
        tiene_perecederos = any(df["Tipo"] == "Perecedero")
        tiene_no_perecederos = any(df["Tipo"] == "No perecedero")
        
        # 🔹 Agrupar por nombre y categoría
        if tiene_no_perecederos and not tiene_perecederos:
            # Solo no perecederos
            df_agrupado = df.groupby(df["Nombre"].str.lower(), as_index=False).agg({
                "Nombre": "first",
                "Tipo": "first",
                "Categoría": "first",
                "Stock Unidades": "sum",
                "_Total_vendidos": "sum"
            })
            columna_stock = "Stock Unidades"
        elif tiene_perecederos and not tiene_no_perecederos:
            # Solo perecederos
            df_agrupado = df.groupby(df["Nombre"].str.lower(), as_index=False).agg({
                "Nombre": "first",
                "Tipo": "first",
                "Categoría": "first",
                "Stock Libras": "sum",
                "Stock Quintal": "sum",
                "Stock Arroba": "sum",
                "_Total_vendidos": "sum"
            })
            columna_stock = "Stock Libras"
        else:
            # Hay mezcla, mostrar ambas columnas
            # Para perecederos
            df_perecederos = df[df["Tipo"] == "Perecedero"].groupby(df["Nombre"].str.lower(), as_index=False).agg({
                "Nombre": "first",
                "Tipo": "first",
                "Categoría": "first",
                "Stock Libras": "sum",
                "Stock Quintal": "sum",
                "Stock Arroba": "sum",
                "_Total_vendidos": "sum"
            })
            
            # Para no perecederos
            df_no_perecederos = df[df["Tipo"] == "No perecedero"].groupby(df["Nombre"].str.lower(), as_index=False).agg({
                "Nombre": "first",
                "Tipo": "first",
                "Categoría": "first",
                "Stock Unidades": "sum",
                "_Total_vendidos": "sum"
            })
            
            # Unir ambos dataframes (columnas diferentes)
            df_agrupado = pd.concat([df_perecederos, df_no_perecederos], ignore_index=True, sort=False)
            columna_stock = None  # Indicador de mezcla

        # 🔹 Ordenación
        if columna_stock is not None:  # Caso normal (un solo tipo)
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
        else:  # Caso con mezcla, solo ordenar por nombre o ventas
            if opcion_orden in ["Nombre (A-Z)", "Nombre (Z-A)"]:
                ascending = opcion_orden == "Nombre (A-Z)"
                df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=ascending)
            elif opcion_orden in ["Más vendidos", "Menos vendidos"]:
                ascending = opcion_orden == "Menos vendidos"
                df_agrupado = df_agrupado.sort_values("_Total_vendidos", ascending=ascending)

        df_agrupado = df_agrupado.drop(columns=["_Total_vendidos"])

        # 🔹 Aplicar estilo según las columnas disponibles
        # Definir formato condicional
        def apply_styling(df_estilizado):
            styled = df_estilizado.style
            for col in df_estilizado.columns:
                if col == "Stock Unidades":
                    styled = styled.format({col: "{:.0f}"})
                elif col in ["Stock Libras", "Stock Quintal", "Stock Arroba"]:
                    styled = styled.format({col: "{:.2f}"})
            
            # Aplicar resaltado según la columna de stock disponible
            if "Stock Unidades" in df_estilizado.columns:
                styled = styled.apply(lambda row: [
                    'background-color: #ffcccc' if row["Stock Unidades"] < 10 and col == "Stock Unidades" else ''
                    for col in row.index
                ], axis=1)
            if "Stock Libras" in df_estilizado.columns:
                styled = styled.apply(lambda row: [
                    'background-color: #ffcccc' if row["Stock Libras"] < 10 and col == "Stock Libras" else ''
                    for col in row.index
                ], axis=1)
            return styled

        # 🔹 Mostrar información del filtro activo
        if filtro_categoria != "Todos":
            st.subheader(f"📋 Inventario por categoría: {filtro_categoria}")
        elif filtro_tipo != "Todos":
            st.subheader(f"📋 Inventario de productos {filtro_tipo.lower()}s")
        else:
            st.subheader("📋 Inventario completo")
        
        styled_df = apply_styling(df_agrupado)
        st.dataframe(styled_df, use_container_width=True)

        # 🔹 Productos próximos a vencer (solo si hay perecederos en el filtro)
        if filtro_tipo in ["Todos", "Perecedero"]:
            hoy = datetime.now().date()
            prox_mes = (datetime.now() + timedelta(days=30)).date()

            cursor.execute("""
                SELECT pc.Cod_barra, p.Nombre, pc.unidad, pc.fecha_vencimiento, IFNULL(p.Categoria, 'N/A')
                FROM ProductoxCompra pc
                JOIN Producto p ON pc.Cod_barra = p.Cod_barra
                WHERE pc.fecha_vencimiento BETWEEN %s AND %s
                  AND pc.id_tienda = %s
                  AND p.id_tienda = %s
                  AND p.Tipo_producto = 'Perecedero'
                ORDER BY pc.fecha_vencimiento ASC
            """, (hoy, prox_mes, id_tienda, id_tienda))

            proximos = cursor.fetchall()

            if proximos:
                df_v = pd.DataFrame(
                    proximos,
                    columns=["Código de barras", "Nombre", "Unidad", "Fecha vencimiento", "Categoría"]
                )
                df_v["Fecha vencimiento"] = pd.to_datetime(df_v["Fecha vencimiento"]).dt.date
                
                # Aplicar filtro de categoría también a productos próximos a vencer
                if filtro_categoria != "Todos":
                    df_v = df_v[df_v["Categoría"] == filtro_categoria]

                if not df_v.empty:
                    st.subheader("⏳ Productos próximos a vencer (30 días)")
                    st.dataframe(df_v.drop(columns=["Categoría"]), use_container_width=True)
                else:
                    st.info("✅ No hay productos perecederos próximos a vencer en esta categoría.")
            else:
                if filtro_tipo == "Perecedero":
                    st.info("✅ No hay productos perecederos próximos a vencer.")

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
