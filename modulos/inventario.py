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


# 🔹 Conversión a unidades para granos
def convertir_a_quintal(cantidad_libras):
    return cantidad_libras / 100

def convertir_a_arroba(cantidad_libras):
    return cantidad_libras / 25


def modulo_inventario():
    st.title("📦 Inventario Actual")

    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        # Botón de volver al final también en caso de error
        st.markdown("---")
        if st.button("⬅ Volver al menú principal"):
            st.session_state.module = None
            st.rerun()
        return

    id_tienda = st.session_state["id_tienda"]

    # 🔹 Buscador de productos por nombre (PRIMERO)
    buscador = st.text_input(
        "🔎 Buscar producto por nombre:",
        placeholder="Escribe el nombre del producto...",
        help="Puedes buscar cualquier producto por su nombre sin importar la categoría"
    )

    # 🔹 Filtro por categoría (DESPUÉS del buscador)
    filtro_categoria = st.selectbox(
        "🔍 Filtrar por categoría:",
        ["Todas las categorías"] + CATEGORIAS,
        index=0
    )

    conn = None
    cursor = None
    
    # Variable para controlar si se debe mostrar el contenido
    mostrar_contenido = True
    mensaje_info = None

    try:
        conn = obtener_conexion()
        if not conn:
            st.error("❌ No se pudo conectar a la base de datos.")
            mostrar_contenido = False
        else:
            cursor = conn.cursor()

            # 🔹 Construir consulta SQL según los filtros
            if filtro_categoria == "Todas las categorías":
                if buscador:
                    # Buscar en todas las categorías
                    cursor.execute("""
                        SELECT Cod_barra, Nombre, categoria
                        FROM Producto
                        WHERE id_tienda = %s 
                          AND LOWER(Nombre) LIKE LOWER(%s)
                        ORDER BY Nombre ASC
                    """, (id_tienda, f"%{buscador}%"))
                else:
                    # Mostrar todos los productos sin filtro de categoría
                    cursor.execute("""
                        SELECT Cod_barra, Nombre, categoria
                        FROM Producto
                        WHERE id_tienda = %s
                        ORDER BY Nombre ASC
                    """, (id_tienda,))
            else:
                if buscador:
                    # Buscar en una categoría específica
                    cursor.execute("""
                        SELECT Cod_barra, Nombre, categoria
                        FROM Producto
                        WHERE id_tienda = %s 
                          AND categoria = %s 
                          AND LOWER(Nombre) LIKE LOWER(%s)
                        ORDER BY Nombre ASC
                    """, (id_tienda, filtro_categoria, f"%{buscador}%"))
                else:
                    # Mostrar todos los productos de una categoría específica
                    cursor.execute("""
                        SELECT Cod_barra, Nombre, categoria
                        FROM Producto
                        WHERE id_tienda = %s AND categoria = %s
                        ORDER BY Nombre ASC
                    """, (id_tienda, filtro_categoria))
            
            productos = cursor.fetchall()

            if not productos:
                if buscador:
                    if filtro_categoria == "Todas las categorías":
                        mensaje_info = f"ℹ️ No se encontraron productos con '{buscador}' en ninguna categoría."
                    else:
                        mensaje_info = f"ℹ️ No se encontraron productos con '{buscador}' en la categoría '{filtro_categoria}'."
                else:
                    if filtro_categoria == "Todas las categorías":
                        mensaje_info = f"ℹ️ No hay productos registrados en ninguna categoría."
                    else:
                        mensaje_info = f"ℹ️ No hay productos registrados en la categoría '{filtro_categoria}' para esta tienda."
                mostrar_contenido = False
            else:
                inventario_detalle = []

                for cod_barra, nombre, categoria in productos:
                    # 🔹 Compras
                    cursor.execute("""
                        SELECT cantidad_comprada, unidad
                        FROM ProductoxCompra
                        WHERE Cod_barra = %s AND id_tienda = %s
                    """, (cod_barra, id_tienda))

                    compras = cursor.fetchall()

                    # Para carnes y congelados, determinar la unidad principal de compra
                    unidad_principal = None
                    if categoria == "Carnes y congelados" and compras:
                        # Obtener la unidad más usada en compras
                        unidades_compra = {}
                        for compra in compras:
                            unidad = compra[1] if compra[1] else "unidad"
                            if unidad.lower() in ["libra", "libras", "lb"]:
                                unidad_principal = "libras"
                            elif unidad.lower() in ["unidad", "unidades", "pieza", "piezas"]:
                                unidad_principal = "unidades"
                        
                        # Si no se pudo determinar, revisar la primera compra
                        if not unidad_principal and compras:
                            primera_unidad = compras[0][1] if compras[0][1] else "unidad"
                            if primera_unidad.lower() in ["libra", "libras", "lb"]:
                                unidad_principal = "libras"
                            else:
                                unidad_principal = "unidades"

                    # Total comprado en libras
                    total_comprado_lb = sum(
                        convertir_a_libras(c[0], c[1]) for c in compras
                    )

                    # Total comprado en unidades
                    total_comprado_unidades = sum(c[0] for c in compras if c[1] and c[1].lower() not in ["libra", "libras", "lb", "quintal", "qq", "arroba"])

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
                    total_vendido_unidades = sum(v[0] for v in ventas if v[1] and v[1].lower() not in ["libra", "libras", "lb", "quintal", "qq", "arroba"])

                    stock_libras = total_comprado_lb - total_vendido_lb
                    stock_unidades = total_comprado_unidades - total_vendido_unidades

                    # Agregar según la categoría
                    if categoria == "Granos y productos a granel":
                        inventario_detalle.append({
                            "Nombre": nombre,
                            "Categoría": categoria,
                            "Stock Quintal": convertir_a_quintal(stock_libras),
                            "Stock Arroba": convertir_a_arroba(stock_libras),
                            "Stock Libras": stock_libras,
                            "_Total_vendidos_libras": int(total_vendido_lb)
                        })
                    elif categoria == "Carnes y congelados":
                        # Determinar qué columna mostrar según la unidad principal
                        if unidad_principal == "libras":
                            inventario_detalle.append({
                                "Nombre": nombre,
                                "Categoría": categoria,
                                "Stock Libras": stock_libras,
                                "Stock Unidades": None,  # Mostrar como guión
                                "_Total_vendidos_libras": int(total_vendido_lb)
                            })
                        else:
                            inventario_detalle.append({
                                "Nombre": nombre,
                                "Categoría": categoria,
                                "Stock Libras": None,  # Mostrar como guión
                                "Stock Unidades": stock_unidades,
                                "_Total_vendidos_unidades": int(total_vendido_unidades)
                            })
                    else:
                        # Otras categorías solo usan unidades
                        inventario_detalle.append({
                            "Nombre": nombre,
                            "Categoría": categoria,
                            "Stock Unidades": stock_unidades,
                            "_Total_vendidos_unidades": int(total_vendido_unidades)
                        })

                # 🔹 Crear DataFrame
                df = pd.DataFrame(inventario_detalle)

                if df.empty:
                    st.warning(f"⚠️ No hay productos para mostrar.")
                    mostrar_contenido = False
                else:
                    # Agrupar por nombre y categoría
                    df_agrupado = None
                    
                    # Separar por tipo de categoría para agrupar correctamente
                    df_granos = df[df["Categoría"] == "Granos y productos a granel"] if not df[df["Categoría"] == "Granos y productos a granel"].empty else None
                    df_carnes = df[df["Categoría"] == "Carnes y congelados"] if not df[df["Categoría"] == "Carnes y congelados"].empty else None
                    df_otros = df[~df["Categoría"].isin(["Granos y productos a granel", "Carnes y congelados"])] if not df[~df["Categoría"].isin(["Granos y productos a granel", "Carnes y congelados"])].empty else None
                    
                    frames = []
                    
                    # Procesar granos
                    if df_granos is not None:
                        df_granos_agg = df_granos.groupby(df_granos["Nombre"].str.lower(), as_index=False).agg({
                            "Nombre": "first",
                            "Categoría": "first",
                            "Stock Quintal": "sum",
                            "Stock Arroba": "sum",
                            "Stock Libras": "sum",
                            "_Total_vendidos_libras": "sum"
                        })
                        df_granos_agg = df_granos_agg.drop(columns=["_Total_vendidos_libras"])
                        frames.append(df_granos_agg)
                    
                    # Procesar carnes
                    if df_carnes is not None:
                        df_carnes_agg = df_carnes.groupby(df_carnes["Nombre"].str.lower(), as_index=False).agg({
                            "Nombre": "first",
                            "Categoría": "first",
                            "Stock Libras": "sum",
                            "Stock Unidades": "sum",
                            "_Total_vendidos_libras": "sum",
                            "_Total_vendidos_unidades": "sum"
                        })
                        df_carnes_agg = df_carnes_agg.drop(columns=["_Total_vendidos_libras", "_Total_vendidos_unidades"])
                        frames.append(df_carnes_agg)
                    
                    # Procesar otros
                    if df_otros is not None:
                        df_otros_agg = df_otros.groupby(df_otros["Nombre"].str.lower(), as_index=False).agg({
                            "Nombre": "first",
                            "Categoría": "first",
                            "Stock Unidades": "sum",
                            "_Total_vendidos_unidades": "sum"
                        })
                        df_otros_agg = df_otros_agg.drop(columns=["_Total_vendidos_unidades"])
                        frames.append(df_otros_agg)
                    
                    # Combinar todos los dataframes
                    if frames:
                        df_agrupado = pd.concat(frames, ignore_index=True, sort=False)
                        # Ordenar alfabéticamente por nombre
                        df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=True)
                        
                        # Función para formatear valores
                        def format_value(val, col_name):
                            if pd.isna(val) or val is None:
                                return "—"
                            if col_name in ["Stock Quintal", "Stock Arroba", "Stock Libras"]:
                                if isinstance(val, (int, float)):
                                    return f"{val:.2f}"
                                return str(val)
                            elif col_name == "Stock Unidades":
                                if isinstance(val, (int, float)):
                                    return f"{int(val)}"
                                return str(val)
                            return str(val)
                        
                        # Crear una copia del dataframe para mostrar
                        df_mostrar = df_agrupado.copy()
                        
                        # Aplicar formato a cada columna
                        for col in df_mostrar.columns:
                            if col in ["Stock Quintal", "Stock Arroba", "Stock Libras", "Stock Unidades"]:
                                df_mostrar[col] = df_mostrar[col].apply(lambda x: format_value(x, col))
                        
                        # 🔹 Mostrar información del filtro activo
                        if buscador:
                            st.subheader(f"📋 Resultados de búsqueda: '{buscador}'")
                            if len(df_agrupado) == 1:
                                st.info(f"✅ Se encontró {len(df_agrupado)} producto")
                            else:
                                st.info(f"✅ Se encontraron {len(df_agrupado)} productos")
                            
                            if filtro_categoria != "Todas las categorías":
                                st.caption(f"Filtrando por categoría: {filtro_categoria}")
                        else:
                            if filtro_categoria == "Todas las categorías":
                                st.subheader(f"📋 Inventario completo - Todas las categorías")
                            else:
                                st.subheader(f"📋 Inventario por categoría: {filtro_categoria}")
                        
                        st.dataframe(df_mostrar, use_container_width=True)
                    else:
                        st.warning("⚠️ No hay datos para mostrar.")

                    # 🔹 Productos próximos a vencer (omitir para granos)
                    if filtro_categoria != "Granos y productos a granel":
                        hoy = datetime.now().date()
                        prox_mes = (datetime.now() + timedelta(days=30)).date()

                        if filtro_categoria == "Todas las categorías":
                            if buscador:
                                cursor.execute("""
                                    SELECT pc.Cod_barra, p.Nombre, pc.unidad, pc.fecha_vencimiento, p.categoria
                                    FROM ProductoxCompra pc
                                    JOIN Producto p ON pc.Cod_barra = p.Cod_barra
                                    WHERE pc.fecha_vencimiento BETWEEN %s AND %s
                                      AND pc.id_tienda = %s
                                      AND p.id_tienda = %s
                                      AND p.categoria != 'Granos y productos a granel'
                                      AND LOWER(p.Nombre) LIKE LOWER(%s)
                                    ORDER BY pc.fecha_vencimiento ASC
                                """, (hoy, prox_mes, id_tienda, id_tienda, f"%{buscador}%"))
                            else:
                                cursor.execute("""
                                    SELECT pc.Cod_barra, p.Nombre, pc.unidad, pc.fecha_vencimiento, p.categoria
                                    FROM ProductoxCompra pc
                                    JOIN Producto p ON pc.Cod_barra = p.Cod_barra
                                    WHERE pc.fecha_vencimiento BETWEEN %s AND %s
                                      AND pc.id_tienda = %s
                                      AND p.id_tienda = %s
                                      AND p.categoria != 'Granos y productos a granel'
                                    ORDER BY pc.fecha_vencimiento ASC
                                """, (hoy, prox_mes, id_tienda, id_tienda))
                        else:
                            if filtro_categoria != "Granos y productos a granel":
                                if buscador:
                                    cursor.execute("""
                                        SELECT pc.Cod_barra, p.Nombre, pc.unidad, pc.fecha_vencimiento
                                        FROM ProductoxCompra pc
                                        JOIN Producto p ON pc.Cod_barra = p.Cod_barra
                                        WHERE pc.fecha_vencimiento BETWEEN %s AND %s
                                          AND pc.id_tienda = %s
                                          AND p.id_tienda = %s
                                          AND p.categoria = %s
                                          AND LOWER(p.Nombre) LIKE LOWER(%s)
                                        ORDER BY pc.fecha_vencimiento ASC
                                    """, (hoy, prox_mes, id_tienda, id_tienda, filtro_categoria, f"%{buscador}%"))
                                else:
                                    cursor.execute("""
                                        SELECT pc.Cod_barra, p.Nombre, pc.unidad, pc.fecha_vencimiento
                                        FROM ProductoxCompra pc
                                        JOIN Producto p ON pc.Cod_barra = p.Cod_barra
                                        WHERE pc.fecha_vencimiento BETWEEN %s AND %s
                                          AND pc.id_tienda = %s
                                          AND p.id_tienda = %s
                                          AND p.categoria = %s
                                        ORDER BY pc.fecha_vencimiento ASC
                                    """, (hoy, prox_mes, id_tienda, id_tienda, filtro_categoria))

                        proximos = cursor.fetchall() if 'cursor' in locals() else []
                        
                        if proximos:
                            if filtro_categoria == "Todas las categorías":
                                df_v = pd.DataFrame(
                                    proximos,
                                    columns=["Código de barras", "Nombre", "Unidad", "Fecha vencimiento", "Categoría"]
                                )
                            else:
                                df_v = pd.DataFrame(
                                    proximos,
                                    columns=["Código de barras", "Nombre", "Unidad", "Fecha vencimiento"]
                                )
                            df_v["Fecha vencimiento"] = pd.to_datetime(df_v["Fecha vencimiento"]).dt.date

                            st.subheader("⏳ Productos próximos a vencer (30 días)")
                            st.dataframe(df_v, use_container_width=True)
                        else:
                            if not buscador and filtro_categoria != "Granos y productos a granel" and filtro_categoria != "Todas las categorías":
                                st.info("✅ No hay productos próximos a vencer en esta categoría.")

    except Exception as e:
        st.error(f"❌ Error al cargar inventario: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    # 🔹 MOSTRAR MENSAJE INFORMATIVO SI NO HAY PRODUCTOS
    if mensaje_info:
        st.info(mensaje_info)
    
    # 🔹 BOTÓN PARA VOLVER AL MENÚ PRINCIPAL - AL FINAL DE TODO
    st.markdown("---")
    
    # Usamos columnas para centrar el botón visualmente
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⬅ Volver al menú principal", use_container_width=True, type="secondary"):
            st.session_state.module = None
            st.rerun()
