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
    """Configuración de estilos CSS para el módulo de inventario - MODO CLARO"""
    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_ACCENT = "#3a7ca5"
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
        .stTextInput > label, .stSelectbox > label {{
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
        
        /* Estilos para tabla en modo claro */
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
        
        /* Estilos para métricas estilo tarjeta */
        .metric-card {{
            background: {COLOR_CARD};
            border-radius: 12px;
            padding: 20px 15px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid {COLOR_BORDER};
            transition: all 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
            border-color: {COLOR_ACCENT};
        }}
        
        .metric-icon {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .metric-label {{
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        
        .metric-value {{
            color: {COLOR_PRIMARY};
            font-size: 1.8em;
            font-weight: bold;
        }}
        </style>
    """, unsafe_allow_html=True)


def obtener_productos_proximos_vencer(id_tienda, dias, filtro_categoria="Todas las categorías"):
    """Obtiene los productos próximos a vencer en un período específico"""
    conn = obtener_conexion()
    if not conn:
        return []
    
    cursor = conn.cursor()
    hoy = datetime.now().date()
    fecha_limite = hoy + timedelta(days=dias)
    
    try:
        if filtro_categoria == "Todas las categorías":
            cursor.execute("""
                SELECT DISTINCT
                    pc.Cod_barra, 
                    p.Nombre, 
                    pc.unidad, 
                    pc.fecha_vencimiento, 
                    p.categoria,
                    pc.cantidad_comprada
                FROM ProductoxCompra pc
                JOIN Producto p ON pc.Cod_barra = p.Cod_barra AND pc.id_tienda = p.id_tienda
                WHERE pc.fecha_vencimiento BETWEEN %s AND %s
                  AND pc.id_tienda = %s
                  AND p.categoria != 'Granos y productos a granel'
                ORDER BY pc.fecha_vencimiento ASC
            """, (hoy, fecha_limite, id_tienda))
        else:
            cursor.execute("""
                SELECT DISTINCT
                    pc.Cod_barra, 
                    p.Nombre, 
                    pc.unidad, 
                    pc.fecha_vencimiento, 
                    p.categoria,
                    pc.cantidad_comprada
                FROM ProductoxCompra pc
                JOIN Producto p ON pc.Cod_barra = p.Cod_barra AND pc.id_tienda = p.id_tienda
                WHERE pc.fecha_vencimiento BETWEEN %s AND %s
                  AND pc.id_tienda = %s
                  AND p.categoria = %s
                ORDER BY pc.fecha_vencimiento ASC
            """, (hoy, fecha_limite, id_tienda, filtro_categoria))
        
        productos = cursor.fetchall()
        return productos
    except Exception as e:
        st.error(f"Error al obtener productos próximos a vencer: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def mostrar_productos_proximos_vencer(id_tienda, filtro_categoria="Todas las categorías"):
    """Muestra un selector de período y los productos próximos a vencer"""
    
    st.markdown("---")
    st.markdown('<div class="inventory-subtitle">⏳ Productos próximos a vencer</div>', unsafe_allow_html=True)
    
    # Selector de período - LISTA DESPLEGABLE
    periodo = st.selectbox(
        "Seleccione el período:",
        ["7 días", "15 días", "30 días", "60 días"],
        index=1
    )
    
    # Mapeo de período a días
    dias_map = {
        "7 días": 7,
        "15 días": 15,
        "30 días": 30,
        "60 días": 60
    }
    dias = dias_map[periodo]
    
    # Obtener productos próximos a vencer
    productos = obtener_productos_proximos_vencer(id_tienda, dias, filtro_categoria)
    
    if not productos:
        st.info(f"✅ No hay productos próximos a vencer en los próximos {dias} días.")
        return
    
    # Crear DataFrame
    data = []
    for prod in productos:
        cod_barra, nombre, unidad, fecha_vencimiento, categoria, cantidad = prod
        dias_restantes = (fecha_vencimiento - datetime.now().date()).days
        
        # Determinar estado
        if dias_restantes < 0:
            estado = "VENCIDO"
        elif dias_restantes <= 7:
            estado = "Urgente (≤7 días)"
        elif dias_restantes <= 15:
            estado = "Próximo (≤15 días)"
        else:
            estado = "Vigente"
        
        data.append({
            "Código": cod_barra,
            "Producto": nombre,
            "Categoría": categoria,
            "Unidad": unidad,
            "Cantidad": cantidad,
            "Fecha Vencimiento": fecha_vencimiento.strftime("%Y-%m-%d"),
            "Días Restantes": dias_restantes,
            "Estado": estado
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values("Fecha Vencimiento", ascending=True)
    
    # Mostrar resumen con métricas estilo tarjeta
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📦</div>
                <div class="metric-label">TOTAL DE PRODUCTOS</div>
                <div class="metric-value">{len(df)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        urgentes = len(df[df["Estado"] == "Urgente (≤7 días)"])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">⚠️</div>
                <div class="metric-label">PRODUCTOS URGENTES</div>
                <div class="metric-value">{urgentes}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        vencidos = len(df[df["Estado"] == "VENCIDO"])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">❌</div>
                <div class="metric-label">PRODUCTOS VENCIDOS</div>
                <div class="metric-value">{vencidos}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Función para colorear las filas según el estado
    def color_rows(row):
        if row["Estado"] == "VENCIDO":
            return ['background-color: #f8d7da'] * len(row)
        elif row["Estado"] == "Urgente (≤7 días)":
            return ['background-color: #fff3cd'] * len(row)
        return [''] * len(row)
    
    # Aplicar estilo
    styled_df = df.style.apply(color_rows, axis=1)
    
    st.dataframe(styled_df, use_container_width=True)
    
    # Botón para volver al inventario completo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📋 Ver inventario completo", use_container_width=True):
            st.rerun()


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

    # Variable para controlar si mostrar productos próximos a vencer
    if "mostrar_vencimiento" not in st.session_state:
        st.session_state["mostrar_vencimiento"] = False

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

    # Botón para alternar entre inventario y productos próximos a vencer
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state["mostrar_vencimiento"]:
            if st.button("⏳ Ver productos próximos a vencer", use_container_width=True):
                st.session_state["mostrar_vencimiento"] = True
                st.rerun()
        else:
            if st.button("📋 Volver al inventario", use_container_width=True):
                st.session_state["mostrar_vencimiento"] = False
                st.rerun()

    if st.session_state["mostrar_vencimiento"]:
        # Mostrar productos próximos a vencer
        categorias_db = obtener_categorias_db(id_tienda)
        if categorias_db:
            filtro_categoria = st.selectbox(
                "🔍 Filtrar por categoría:",
                ["Todas las categorías"] + categorias_db,
                index=0,
                key="filtro_vencimiento"
            )
        else:
            filtro_categoria = "Todas las categorías"
        mostrar_productos_proximos_vencer(id_tienda, filtro_categoria)
    else:
        # ============================================================
        # Filtros de búsqueda para inventario normal
        # ============================================================
        
        categorias_db = obtener_categorias_db(id_tienda)

        buscador = st.text_input(
            "🔎 Buscar producto por nombre:",
            placeholder="Escribe el nombre del producto...",
            help="Puedes buscar cualquier producto por su nombre sin importar la categoría"
        )

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
        mensaje_info = None

        try:
            conn = obtener_conexion()
            if not conn:
                st.error("❌ No se pudo conectar a la base de datos.")
                return
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
                        
                        fecha_str = fecha_vencimiento.strftime("%Y-%m-%d") if fecha_vencimiento else "—"

                        # Agregar según categoría
                        if categoria == "Granos y productos a granel":
                            inventario_detalle.append({
                                "Código": cod_barra,
                                "Nombre": nombre,
                                "Categoría": categoria,
                                "Stock (Quintales)": round(convertir_a_quintal(stock_libras), 2),
                                "Stock (Arrobas)": round(convertir_a_arroba(stock_libras), 2),
                                "Stock (Libras)": round(stock_libras, 2),
                                "Stock (Unidades)": "—",
                                "Fecha Vencimiento": fecha_str
                            })
                        elif categoria == "Carnes y congelados":
                            if unidad_principal == "libras":
                                inventario_detalle.append({
                                    "Código": cod_barra,
                                    "Nombre": nombre,
                                    "Categoría": categoria,
                                    "Stock (Libras)": round(stock_libras, 2),
                                    "Stock (Unidades)": "—",
                                    "Stock (Quintales)": "—",
                                    "Stock (Arrobas)": "—",
                                    "Fecha Vencimiento": fecha_str
                                })
                            else:
                                inventario_detalle.append({
                                    "Código": cod_barra,
                                    "Nombre": nombre,
                                    "Categoría": categoria,
                                    "Stock (Unidades)": int(stock_unidades) if stock_unidades > 0 else 0,
                                    "Stock (Libras)": "—",
                                    "Stock (Quintales)": "—",
                                    "Stock (Arrobas)": "—",
                                    "Fecha Vencimiento": fecha_str
                                })
                        else:
                            inventario_detalle.append({
                                "Código": cod_barra,
                                "Nombre": nombre,
                                "Categoría": categoria,
                                "Stock (Unidades)": int(stock_unidades) if stock_unidades > 0 else 0,
                                "Stock (Libras)": "—",
                                "Stock (Quintales)": "—",
                                "Stock (Arrobas)": "—",
                                "Fecha Vencimiento": fecha_str
                            })

                    df = pd.DataFrame(inventario_detalle)

                    if df.empty:
                        st.warning(f"⚠️ No hay productos para mostrar.")
                    else:
                        # Definir orden de columnas
                        columnas_orden = ["Código", "Nombre", "Categoría", "Stock (Quintales)", "Stock (Arrobas)", "Stock (Libras)", "Stock (Unidades)", "Fecha Vencimiento"]
                        df = df[columnas_orden]
                        
                        # Ordenar por nombre
                        df = df.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=True)
                        
                        if buscador:
                            st.markdown(f'<div class="inventory-subtitle">📋 Resultados de búsqueda: "{buscador}"</div>', unsafe_allow_html=True)
                            st.info(f"✅ Se encontraron {len(df)} productos")
                            if filtro_categoria != "Todas las categorías":
                                st.caption(f"Filtrando por categoría: {filtro_categoria}")
                        else:
                            if filtro_categoria == "Todas las categorías":
                                st.markdown('<div class="inventory-subtitle">📋 Inventario completo - Todas las categorías</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="inventory-subtitle">📋 Inventario por categoría: {filtro_categoria}</div>', unsafe_allow_html=True)
                        
                        # Mostrar dataframe con estilo claro
                        st.dataframe(df, use_container_width=True)

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
