import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime, timedelta

# ✅ Función para obtener categorías desde la base de datos
def obtener_categorias_db(id_tienda):
    """Obtiene las categorías activas desde la base de datos"""
    conn = obtener_conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT nombre FROM Categoria WHERE id_tienda = %s AND activo = 1 ORDER BY nombre",
            (id_tienda,)
        )
        resultados = cursor.fetchall()
        return [row[0] for row in resultados]
    except Exception as e:
        st.error(f"Error al cargar categorías: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

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
        return 0

def convertir_a_quintal(cantidad_libras):
    return cantidad_libras / 100

def convertir_a_arroba(cantidad_libras):
    return cantidad_libras / 25

def configurar_estilo():
    """Configuración de estilos CSS para el módulo de inventario"""
    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_ACCENT = "#3a7ca5"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_DARK = "#1a1a1a"
    COLOR_TEXT_LIGHT = "#666666"
    COLOR_HOVER = "#e8f0fe"
    COLOR_BORDER = "#e0e0e0"
    COLOR_BUTTON = "#1e3a5f"
    COLOR_TABLE_HEADER = "#1e3a5f"
    COLOR_TABLE_ROW_ODD = "#ffffff"
    COLOR_TABLE_ROW_EVEN = "#f8f9fa"
    
    st.markdown(f"""
        <style>
        /* Fondo general */
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        /* Títulos */
        .inventory-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        /* Subtítulos */
        .inventory-subtitle {{
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
        
        /* Labels */
        .stTextInput > label, .stSelectbox > label, .stDateInput > label {{
            color: {COLOR_TEXT_DARK} !important;
            font-weight: 500 !important;
        }}
        
        /* Inputs y selectores */
        .stTextInput > div > div > input {{
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
            background-color: {COLOR_BUTTON};
            color: white !important;
            padding: 10px 15px;
        }}
        
        .stTextInput > div > div > input::placeholder {{
            color: rgba(255,255,255,0.7) !important;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLOR_PRIMARY};
            box-shadow: 0 0 0 2px rgba(30,58,95,0.1);
        }}
        
        /* Selectbox */
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
        
        /* Botón volver */
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
        
        /* ============================================ */
        /* ESTILOS FORZADOS PARA LA TABLA (DATAFRAME) */
        /* ============================================ */
        
        /* Contenedor de la tabla */
        [data-testid="stDataFrame"] {{
            background-color: {COLOR_CARD} !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid {COLOR_BORDER} !important;
        }}
        
        /* Tabla completa */
        [data-testid="stDataFrame"] table {{
            width: 100% !important;
            border-collapse: collapse !important;
            background-color: {COLOR_CARD} !important;
        }}
        
        /* Encabezados de la tabla */
        [data-testid="stDataFrame"] th {{
            background-color: {COLOR_TABLE_HEADER} !important;
            color: white !important;
            font-weight: 600 !important;
            text-align: center !important;
            padding: 12px 8px !important;
            border: none !important;
            font-size: 0.9em !important;
        }}
        
        /* Celdas de la tabla */
        [data-testid="stDataFrame"] td {{
            color: {COLOR_TEXT} !important;
            text-align: center !important;
            padding: 10px 8px !important;
            border-bottom: 1px solid {COLOR_BORDER} !important;
            background-color: {COLOR_CARD} !important;
        }}
        
        /* Filas pares */
        [data-testid="stDataFrame"] tr:nth-child(even) td {{
            background-color: {COLOR_TABLE_ROW_EVEN} !important;
        }}
        
        /* Filas impares */
        [data-testid="stDataFrame"] tr:nth-child(odd) td {{
            background-color: {COLOR_TABLE_ROW_ODD} !important;
        }}
        
        /* Hover sobre filas */
        [data-testid="stDataFrame"] tr:hover td {{
            background-color: {COLOR_HOVER} !important;
        }}
        
        /* Scrollbar */
        [data-testid="stDataFrame"] .dataframe {{
            scrollbar-width: thin;
        }}
        </style>
    """, unsafe_allow_html=True)


def aplicar_estilo_tabla(df):
    """Aplica estilo CSS directamente al DataFrame"""
    # Estilo para el encabezado
    styled = df.style.set_table_styles([
        {'selector': 'thead tr th', 'props': [
            ('background-color', '#1e3a5f'),
            ('color', 'white'),
            ('font-weight', '600'),
            ('text-align', 'center'),
            ('padding', '12px 8px'),
            ('font-size', '0.9em')
        ]},
        {'selector': 'tbody tr td', 'props': [
            ('text-align', 'center'),
            ('padding', '10px 8px'),
            ('color', '#333333'),
            ('border-bottom', '1px solid #e0e0e0')
        ]},
        {'selector': 'tbody tr:nth-child(even)', 'props': [
            ('background-color', '#f8f9fa')
        ]},
        {'selector': 'tbody tr:nth-child(odd)', 'props': [
            ('background-color', '#ffffff')
        ]},
        {'selector': 'tbody tr:hover', 'props': [
            ('background-color', '#e8f0fe')
        ]}
    ])
    
    # Formato numérico
    for col in df.columns:
        if col in ["Stock Quintal", "Stock Arroba", "Stock Libras"]:
            styled = styled.format({col: "{:.2f}"})
        elif col == "Stock Unidades":
            styled = styled.format({col: "{:.0f}"})
    
    return styled


def modulo_inventario():
    configurar_estilo()
    
    st.markdown('<div class="inventory-title">📦 Inventario Actual</div>', unsafe_allow_html=True)

    if not st.session_state.get("logueado"):
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.markdown("---")
        if st.button("⬅ Volver al menú principal"):
            st.session_state["module"] = None
            st.rerun()
        return

    rol = st.session_state.get("nivel_usuario", "")
    id_tienda_sesion = st.session_state.get("id_tienda")
    nombre_tienda = st.session_state.get("nombre_tienda", "Mi Tienda")

    # ============================================================
    # 👑 ADMINISTRADOR: puede seleccionar cualquier tienda
    # ============================================================
    if rol == "Administrador":
        st.markdown(f'<div class="inventory-subtitle">👑 Inventario global - Administrador</div>', unsafe_allow_html=True)

        conn = obtener_conexion()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_tienda, nombre
                FROM tienda
                WHERE activo = 1
                ORDER BY nombre
            """)
            tiendas = cursor.fetchall()
            cursor.close()
            conn.close()

            if not tiendas:
                st.warning("No hay tiendas activas.")
                return

            opciones = {t["nombre"]: t["id_tienda"] for t in tiendas}
            tienda_nombre = st.selectbox("🏪 Seleccionar tienda", list(opciones.keys()))
            id_tienda = opciones[tienda_nombre]
            nombre_tienda = tienda_nombre

            st.markdown(f'<div class="info-box">📌 Mostrando inventario de: <strong>{tienda_nombre}</strong></div>', unsafe_allow_html=True)
        else:
            st.error("❌ No se pudo conectar a la base de datos.")
            return
    else:
        # Vendedor: solo su tienda
        id_tienda = id_tienda_sesion
        if not id_tienda:
            st.error("❌ No tienes una tienda asignada.")
            return
        
        st.markdown(f'<div class="info-box">🏪 Tienda: <strong>{nombre_tienda}</strong></div>', unsafe_allow_html=True)

    # ============================================================
    # Filtros de búsqueda
    # ============================================================
    
    # ✅ Cargar categorías desde la base de datos
    categorias_db = obtener_categorias_db(id_tienda)

    # 🔹 Buscador de productos por nombre
    buscador = st.text_input(
        "🔎 Buscar producto por nombre:",
        placeholder="Escribe el nombre del producto...",
        help="Puedes buscar cualquier producto por su nombre sin importar la categoría"
    )

    # 🔹 Filtro por categoría
    if categorias_db:
        filtro_categoria = st.selectbox(
            "🔍 Filtrar por categoría:",
            ["Todas las categorías"] + categorias_db,
            index=0
        )
    else:
        st.warning("⚠️ No hay categorías disponibles. Ve a 'Gestión de Categorías' y crea una primero.")
        filtro_categoria = "Todas las categorías"

    conn = None
    cursor = None
    mostrar_contenido = True
    mensaje_info = None

    try:
        conn = obtener_conexion()
        if not conn:
            st.error("❌ No se pudo conectar a la base de datos.")
            mostrar_contenido = False
        else:
            cursor = conn.cursor()

            # Construir consulta SQL
            if filtro_categoria == "Todas las categorías":
                if buscador:
                    cursor.execute("""
                        SELECT Cod_barra, Nombre, categoria
                        FROM Producto
                        WHERE id_tienda = %s 
                          AND LOWER(Nombre) LIKE LOWER(%s)
                        ORDER BY Nombre ASC
                    """, (id_tienda, f"%{buscador}%"))
                else:
                    cursor.execute("""
                        SELECT Cod_barra, Nombre, categoria
                        FROM Producto
                        WHERE id_tienda = %s
                        ORDER BY Nombre ASC
                    """, (id_tienda,))
            else:
                if buscador:
                    cursor.execute("""
                        SELECT Cod_barra, Nombre, categoria
                        FROM Producto
                        WHERE id_tienda = %s 
                          AND categoria = %s 
                          AND LOWER(Nombre) LIKE LOWER(%s)
                        ORDER BY Nombre ASC
                    """, (id_tienda, filtro_categoria, f"%{buscador}%"))
                else:
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
                    # Compras
                    cursor.execute("""
                        SELECT cantidad_comprada, unidad, fecha_vencimiento
                        FROM ProductoxCompra
                        WHERE Cod_barra = %s AND id_tienda = %s
                    """, (cod_barra, id_tienda))

                    compras = cursor.fetchall()

                    # Determinar unidad principal para carnes y congelados
                    unidad_principal = None
                    if categoria == "Carnes y congelados" and compras:
                        hay_compras_libras = any(c[1] and c[1].lower() in ["libra", "libras", "lb"] for c in compras)
                        hay_compras_unidades = any(c[1] and c[1].lower() in ["unidad", "unidades", "pieza", "piezas"] for c in compras)
                        
                        if hay_compras_libras:
                            unidad_principal = "libras"
                        elif hay_compras_unidades:
                            unidad_principal = "unidades"

                    # Fecha de vencimiento más reciente
                    fecha_vencimiento = None
                    for compra in compras:
                        if compra[2]:
                            if fecha_vencimiento is None or compra[2] < fecha_vencimiento:
                                fecha_vencimiento = compra[2]

                    total_comprado_lb = sum(convertir_a_libras(c[0], c[1]) for c in compras)
                    total_comprado_unidades = sum(c[0] for c in compras if c[1] and c[1].lower() not in ["libra", "libras", "lb", "quintal", "qq", "arroba"])

                    # Ventas
                    cursor.execute("""
                        SELECT Cantidad_vendida, unidad
                        FROM ProductoxVenta
                        WHERE Cod_barra = %s AND id_tienda = %s
                    """, (cod_barra, id_tienda))

                    ventas = cursor.fetchall()

                    total_vendido_lb = sum(convertir_a_libras(v[0], v[1]) for v in ventas)
                    total_vendido_unidades = sum(v[0] for v in ventas if v[1] and v[1].lower() not in ["libra", "libras", "lb", "quintal", "qq", "arroba"])

                    stock_libras = total_comprado_lb - total_vendido_lb
                    stock_unidades = total_comprado_unidades - total_vendido_unidades

                    # Agregar según categoría
                    if categoria == "Granos y productos a granel":
                        inventario_detalle.append({
                            "Código": cod_barra,
                            "Nombre": nombre,
                            "Categoría": categoria,
                            "Stock Quintal": convertir_a_quintal(stock_libras),
                            "Stock Arroba": convertir_a_arroba(stock_libras),
                            "Stock Libras": stock_libras,
                            "Fecha Vencimiento": fecha_vencimiento
                        })
                    elif categoria == "Carnes y congelados":
                        if unidad_principal == "libras":
                            inventario_detalle.append({
                                "Código": cod_barra,
                                "Nombre": nombre,
                                "Categoría": categoria,
                                "Stock Libras": stock_libras,
                                "Stock Unidades": None,
                                "Fecha Vencimiento": fecha_vencimiento
                            })
                        else:
                            inventario_detalle.append({
                                "Código": cod_barra,
                                "Nombre": nombre,
                                "Categoría": categoria,
                                "Stock Libras": None,
                                "Stock Unidades": stock_unidades,
                                "Fecha Vencimiento": fecha_vencimiento
                            })
                    else:
                        inventario_detalle.append({
                            "Código": cod_barra,
                            "Nombre": nombre,
                            "Categoría": categoria,
                            "Stock Unidades": stock_unidades,
                            "Fecha Vencimiento": fecha_vencimiento
                        })

                df = pd.DataFrame(inventario_detalle)

                if df.empty:
                    st.warning(f"⚠️ No hay productos para mostrar.")
                    mostrar_contenido = False
                else:
                    # Agrupar por tipo de categoría
                    df_granos = df[df["Categoría"] == "Granos y productos a granel"] if not df[df["Categoría"] == "Granos y productos a granel"].empty else None
                    df_carnes = df[df["Categoría"] == "Carnes y congelados"] if not df[df["Categoría"] == "Carnes y congelados"].empty else None
                    df_otros = df[~df["Categoría"].isin(["Granos y productos a granel", "Carnes y congelados"])] if not df[~df["Categoría"].isin(["Granos y productos a granel", "Carnes y congelados"])].empty else None
                    
                    frames = []
                    
                    if df_granos is not None:
                        df_granos_agg = df_granos.groupby(df_granos["Código"], as_index=False).agg({
                            "Código": "first",
                            "Nombre": "first",
                            "Categoría": "first",
                            "Stock Quintal": "sum",
                            "Stock Arroba": "sum",
                            "Stock Libras": "sum",
                            "Fecha Vencimiento": lambda x: min(x.dropna()) if not x.dropna().empty else None
                        })
                        frames.append(df_granos_agg)
                    
                    if df_carnes is not None:
                        agg_dict = {
                            "Código": "first",
                            "Nombre": "first",
                            "Categoría": "first",
                            "Fecha Vencimiento": lambda x: min(x.dropna()) if not x.dropna().empty else None
                        }
                        if "Stock Libras" in df_carnes.columns:
                            agg_dict["Stock Libras"] = "sum"
                        if "Stock Unidades" in df_carnes.columns:
                            agg_dict["Stock Unidades"] = "sum"
                        df_carnes_agg = df_carnes.groupby(df_carnes["Código"], as_index=False).agg(agg_dict)
                        frames.append(df_carnes_agg)
                    
                    if df_otros is not None:
                        df_otros_agg = df_otros.groupby(df_otros["Código"], as_index=False).agg({
                            "Código": "first",
                            "Nombre": "first",
                            "Categoría": "first",
                            "Stock Unidades": "sum",
                            "Fecha Vencimiento": lambda x: min(x.dropna()) if not x.dropna().empty else None
                        })
                        frames.append(df_otros_agg)
                    
                    if frames:
                        df_agrupado = pd.concat(frames, ignore_index=True, sort=False)
                        df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=True)
                        
                        columnas = ["Código"] + [col for col in df_agrupado.columns if col not in ["Código", "Fecha Vencimiento"]] + ["Fecha Vencimiento"]
                        df_agrupado = df_agrupado[columnas]
                        
                        # Formatear valores
                        for col in df_agrupado.columns:
                            if col in ["Stock Quintal", "Stock Arroba", "Stock Libras"]:
                                df_agrupado[col] = df_agrupado[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) and x != 0 else "—" if pd.isna(x) or x == 0 else "—")
                            elif col == "Stock Unidades":
                                df_agrupado[col] = df_agrupado[col].apply(lambda x: f"{int(x)}" if pd.notna(x) and x > 0 else "—" if pd.isna(x) or x == 0 else "—")
                            elif col == "Fecha Vencimiento":
                                df_agrupado[col] = df_agrupado[col].apply(lambda x: x.strftime("%Y-%m-%d") if pd.notna(x) else "—")
                        
                        # Rellenar NaN con "—"
                        df_agrupado = df_agrupado.fillna("—")
                        
                        # Aplicar estilo a la tabla
                        styled_df = aplicar_estilo_tabla(df_agrupado)
                        
                        if buscador:
                            st.markdown(f'<div class="inventory-subtitle">📋 Resultados de búsqueda: "{buscador}"</div>', unsafe_allow_html=True)
                            st.info(f"✅ Se encontraron {len(df_agrupado)} productos")
                            if filtro_categoria != "Todas las categorías":
                                st.caption(f"Filtrando por categoría: {filtro_categoria}")
                        else:
                            if filtro_categoria == "Todas las categorías":
                                st.markdown('<div class="inventory-subtitle">📋 Inventario completo - Todas las categorías</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="inventory-subtitle">📋 Inventario por categoría: {filtro_categoria}</div>', unsafe_allow_html=True)
                        
                        # Mostrar dataframe con estilos
                        st.dataframe(styled_df, use_container_width=True)

                    # Productos próximos a vencer
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

                            st.markdown('<div class="inventory-subtitle">⏳ Productos próximos a vencer (30 días)</div>', unsafe_allow_html=True)
                            st.dataframe(df_v, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al cargar inventario: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    if mensaje_info:
        st.info(mensaje_info)
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⬅ Volver al menú principal", use_container_width=True, type="secondary"):
            st.session_state["module"] = None
            st.rerun()
