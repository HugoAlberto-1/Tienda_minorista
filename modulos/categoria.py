import streamlit as st
from config.conexion import obtener_conexion

def configurar_estilo():
    """Configuración de estilos CSS para el módulo de categorías - MODO CLARO"""
    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_DARK = "#1a1a1a"
    COLOR_TEXT_LIGHT = "#ffffff"
    COLOR_HOVER = "#e8f0fe"
    COLOR_BORDER = "#e0e0e0"
    COLOR_BUTTON = "#1e3a5f"
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        .module-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .module-subtitle {{
            text-align: center;
            color: {COLOR_SECONDARY};
            font-size: 1.1em;
            margin-bottom: 30px;
        }}
        
        .info-box {{
            background: {COLOR_HOVER};
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid {COLOR_PRIMARY};
            margin: 15px 0;
            color: {COLOR_TEXT_DARK};
        }}
        
        .stTextInput > label, .stSelectbox > label, .stTextArea > label {{
            color: {COLOR_TEXT_DARK} !important;
            font-weight: 500 !important;
        }}
        
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
        
        .stTextArea > div > textarea {{
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
            background-color: {COLOR_BUTTON};
            color: white !important;
            padding: 10px 15px;
        }}
        
        .stTextArea > div > textarea::placeholder {{
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
        
        .stAlert {{
            border-radius: 8px;
        }}
        
        /* Estilos para tarjetas de categorías - Mismo estilo que el subtítulo */
        .category-card {{
            background: {COLOR_CARD};
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid {COLOR_BORDER};
            transition: all 0.3s ease;
        }}
        
        .category-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
            border-color: {COLOR_ACCENT};
        }}
        
        .category-name {{
            font-size: 1.2em;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid {COLOR_ACCENT};
            display: inline-block;
        }}
        
        .category-detail {{
            color: {COLOR_TEXT};
            margin: 8px 0;
            font-size: 0.9em;
        }}
        
        .category-detail strong {{
            color: {COLOR_PRIMARY};
            font-weight: 600;
        }}
        
        hr {{
            border-color: {COLOR_BORDER};
        }}
        
        /* Estilos para tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: {COLOR_CARD};
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            font-weight: 500;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
        }}
        
        .stTabs [aria-selected="false"] {{
            background-color: {COLOR_BORDER};
            color: {COLOR_TEXT_DARK};
        }}
        </style>
    """, unsafe_allow_html=True)


# ==================== FUNCIONES DE BASE DE DATOS ====================

def obtener_categorias(id_tienda):
    """Obtiene todas las categorías activas de una tienda"""
    conn = obtener_conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT id_categoria, nombre, descripcion, fecha_creacion 
               FROM Categoria 
               WHERE id_tienda = %s AND activo = 1 
               ORDER BY nombre""",
            (id_tienda,)
        )
        categorias = cursor.fetchall()
        return categorias
    except Exception as e:
        st.error(f"Error al obtener categorías: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def obtener_categorias_solo_nombres(id_tienda):
    """Obtiene solo los nombres de las categorías (para los selectbox)"""
    conn = obtener_conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT nombre 
               FROM Categoria 
               WHERE id_tienda = %s AND activo = 1 
               ORDER BY nombre""",
            (id_tienda,)
        )
        resultados = cursor.fetchall()
        return [row[0] for row in resultados]
    except Exception as e:
        st.error(f"Error al obtener nombres de categorías: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def crear_categoria(id_tienda, nombre, descripcion):
    """Crea una nueva categoría"""
    conn = obtener_conexion()
    if not conn:
        return False, "No se pudo conectar a la base de datos"
    cursor = conn.cursor()
    try:
        # Verificar si ya existe una categoría con el mismo nombre
        cursor.execute(
            "SELECT COUNT(*) FROM Categoria WHERE nombre = %s AND id_tienda = %s AND activo = 1",
            (nombre, id_tienda)
        )
        existe = cursor.fetchone()[0]
        
        if existe > 0:
            return False, f"Ya existe una categoría activa con el nombre '{nombre}'"
        
        cursor.execute(
            """INSERT INTO Categoria (nombre, descripcion, id_tienda, fecha_creacion, activo) 
               VALUES (%s, %s, %s, CURRENT_DATE, 1)""",
            (nombre, descripcion, id_tienda)
        )
        conn.commit()
        return True, f"Categoría '{nombre}' creada exitosamente"
    except Exception as e:
        conn.rollback()
        return False, f"Error al crear la categoría: {e}"
    finally:
        cursor.close()
        conn.close()


def actualizar_categoria(id_categoria, nombre, descripcion, id_tienda):
    """Actualiza una categoría existente"""
    conn = obtener_conexion()
    if not conn:
        return False, "No se pudo conectar a la base de datos"
    cursor = conn.cursor()
    try:
        # Verificar si ya existe otra categoría con el mismo nombre
        cursor.execute(
            """SELECT COUNT(*) FROM Categoria 
               WHERE nombre = %s AND id_tienda = %s AND id_categoria != %s AND activo = 1""",
            (nombre, id_tienda, id_categoria)
        )
        existe = cursor.fetchone()[0]
        
        if existe > 0:
            return False, f"Ya existe otra categoría activa con el nombre '{nombre}'"
        
        cursor.execute(
            """UPDATE Categoria 
               SET nombre = %s, descripcion = %s 
               WHERE id_categoria = %s AND id_tienda = %s""",
            (nombre, descripcion, id_categoria, id_tienda)
        )
        conn.commit()
        return True, f"Categoría '{nombre}' actualizada exitosamente"
    except Exception as e:
        conn.rollback()
        return False, f"Error al actualizar la categoría: {e}"
    finally:
        cursor.close()
        conn.close()


def eliminar_categoria(id_categoria, id_tienda):
    """Elimina (soft delete) una categoría"""
    conn = obtener_conexion()
    if not conn:
        return False, "No se pudo conectar a la base de datos"
    cursor = conn.cursor()
    try:
        # Verificar si hay productos usando esta categoría
        cursor.execute(
            """SELECT COUNT(*) FROM Producto 
               WHERE categoria = (SELECT nombre FROM Categoria WHERE id_categoria = %s) 
               AND id_tienda = %s""",
            (id_categoria, id_tienda)
        )
        productos_asociados = cursor.fetchone()[0]
        
        if productos_asociados > 0:
            return False, f"No se puede eliminar la categoría porque tiene {productos_asociados} producto(s) asociado(s). Primero reasigna esos productos."
        
        cursor.execute(
            "UPDATE Categoria SET activo = 0 WHERE id_categoria = %s AND id_tienda = %s",
            (id_categoria, id_tienda)
        )
        conn.commit()
        return True, "Categoría eliminada exitosamente"
    except Exception as e:
        conn.rollback()
        return False, f"Error al eliminar la categoría: {e}"
    finally:
        cursor.close()
        conn.close()


# ==================== INTERFAZ DE USUARIO ====================

def modulo_categoria():
    configurar_estilo()
    
    st.markdown('<div class="module-title">📁 Gestión de Categorías</div>', unsafe_allow_html=True)
    
    # Validación de sesión
    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.markdown("---")
        if st.button("⬅ Volver al menú principal"):
            st.session_state["module"] = None
            st.rerun()
        return
    
    id_tienda = st.session_state["id_tienda"]
    nombre_tienda = st.session_state.get("nombre_tienda", "Mi Tienda")
    
    # Mostrar tienda actual
    st.markdown(f'<div class="info-box">🏪 Tienda: <strong>{nombre_tienda}</strong></div>', unsafe_allow_html=True)
    
    # Pestañas para las diferentes acciones
    tab1, tab2, tab3 = st.tabs(["📋 Lista de categorías", "➕ Crear nueva categoría", "✏️ Editar/Eliminar"])
    
    with tab1:
        mostrar_lista_categorias(id_tienda)
    
    with tab2:
        mostrar_formulario_crear(id_tienda)
    
    with tab3:
        mostrar_formulario_editar_eliminar(id_tienda)
    
    # Botón para volver al menú principal
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⬅ Volver al menú principal", use_container_width=True):
            st.session_state["module"] = None
            st.rerun()


def mostrar_lista_categorias(id_tienda):
    """Muestra la lista de categorías activas con tarjetas estilo subtítulo"""
    st.markdown('<div class="module-subtitle">📋 Categorías registradas</div>', unsafe_allow_html=True)
    
    categorias = obtener_categorias(id_tienda)
    
    if not categorias:
        st.info("ℹ️ No hay categorías registradas. Crea una en la pestaña 'Crear nueva categoría'.")
    else:
        st.write(f"**Total de categorías:** {len(categorias)}")
        st.markdown("---")
        
        # Mostrar categorías en formato de tarjetas
        for cat in categorias:
            id_cat, nombre, descripcion, fecha = cat
            st.markdown(f"""
                <div class="category-card">
                    <div class="category-name">📁 {nombre}</div>
                    <div class="category-detail"><strong>ID:</strong> {id_cat}</div>
                    <div class="category-detail"><strong>Descripción:</strong> {descripcion if descripcion else 'Sin descripción'}</div>
                    <div class="category-detail"><strong>Fecha de creación:</strong> {fecha}</div>
                </div>
            """, unsafe_allow_html=True)


def mostrar_formulario_crear(id_tienda):
    """Formulario para crear nueva categoría"""
    st.markdown('<div class="module-subtitle">➕ Crear nueva categoría</div>', unsafe_allow_html=True)
    
    with st.form("form_crear_categoria"):
        nombre = st.text_input(
            "📝 Nombre de la categoría", 
            placeholder="Ej: Bebidas, Lácteos, Carnes, etc.",
            help="El nombre debe ser único para esta tienda"
        )
        descripcion = st.text_area(
            "📄 Descripción (opcional)", 
            placeholder="Describe qué productos pertenecen a esta categoría...",
            help="Una breve descripción de la categoría"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("✅ Crear categoría", type="primary", use_container_width=True)
        
        if submitted:
            if not nombre.strip():
                st.error("❌ El nombre de la categoría es obligatorio.")
            else:
                exito, mensaje = crear_categoria(id_tienda, nombre.strip(), descripcion.strip() if descripcion else None)
                if exito:
                    st.success(mensaje)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(mensaje)


def mostrar_formulario_editar_eliminar(id_tienda):
    """Formulario para editar o eliminar categorías existentes"""
    st.markdown('<div class="module-subtitle">✏️ Editar o eliminar categoría</div>', unsafe_allow_html=True)
    
    categorias = obtener_categorias(id_tienda)
    
    if not categorias:
        st.info("ℹ️ No hay categorías para editar o eliminar.")
        return
    
    # Crear opciones para el selectbox
    opciones = {f"{cat[1]}": cat[0] for cat in categorias}
    
    categoria_seleccionada_nombre = st.selectbox(
        "🔍 Selecciona una categoría",
        list(opciones.keys()),
        key="select_categoria_editar"
    )
    
    if categoria_seleccionada_nombre:
        id_categoria = opciones[categoria_seleccionada_nombre]
        # Buscar la categoría seleccionada
        cat_seleccionada = next((cat for cat in categorias if cat[0] == id_categoria), None)
        
        if cat_seleccionada:
            with st.form("form_editar_categoria"):
                nuevo_nombre = st.text_input("📝 Nombre", value=cat_seleccionada[1])
                nueva_descripcion = st.text_area("📄 Descripción", value=cat_seleccionada[2] if cat_seleccionada[2] else "")
                
                st.info("ℹ️ **Nota:** Si cambias el nombre de la categoría, deberás actualizar manualmente los productos existentes.")
                
                col1, col2 = st.columns(2, gap="large")
                with col1:
                    if st.form_submit_button("💾 Guardar cambios", type="primary", use_container_width=True):
                        if not nuevo_nombre.strip():
                            st.error("❌ El nombre es obligatorio.")
                        else:
                            exito, mensaje = actualizar_categoria(
                                id_categoria, 
                                nuevo_nombre.strip(), 
                                nueva_descripcion.strip() if nueva_descripcion else None, 
                                id_tienda
                            )
                            if exito:
                                st.success(mensaje)
                                st.rerun()
                            else:
                                st.error(mensaje)
                
                with col2:
                    if st.form_submit_button("🗑️ Eliminar categoría", use_container_width=True):
                        exito, mensaje = eliminar_categoria(id_categoria, id_tienda)
                        if exito:
                            st.success(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)
