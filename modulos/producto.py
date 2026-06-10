import streamlit as st
from config.conexion import obtener_conexion

def configurar_estilo():
    """Configuración de estilos CSS para el módulo de producto - MODO CLARO"""
    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
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
        .module-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        /* Subtítulos */
        .module-subtitle {{
            text-align: center;
            color: {COLOR_SECONDARY};
            font-size: 1.1em;
            margin-bottom: 30px;
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
        
        /* Botón guardar */
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
        
        /* Success y error messages */
        .stAlert {{
            border-radius: 8px;
        }}
        </style>
    """, unsafe_allow_html=True)


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


def modulo_producto():
    configurar_estilo()
    
    st.markdown('<div class="module-title">📦 Registro de Productos</div>', unsafe_allow_html=True)

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

    # ✅ Cargar categorías desde la base de datos
    categorias = obtener_categorias_db(id_tienda)
    
    if not categorias:
        st.warning("⚠️ No hay categorías disponibles. Ve a 'Gestión de Categorías' y crea una primero.")
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⬅ Volver al menú principal", use_container_width=True):
                st.session_state["module"] = None
                st.rerun()
        return

    # Reset seguro del formulario
    if st.session_state.get("reiniciar_formulario"):
        st.session_state.pop("cod_barra_input", None)
        st.session_state.pop("nombre_producto_input", None)
        st.session_state.pop("categoria_input", None)
        st.session_state.pop("reiniciar_formulario", None)
        st.rerun()

    if st.session_state.get("producto_guardado"):
        st.success("✅ Producto guardado correctamente.")
        st.session_state.pop("producto_guardado", None)

    st.markdown('<div class="module-subtitle">➕ Agregar nuevo producto</div>', unsafe_allow_html=True)

    Cod_barra = st.text_input(
        "📦 Código de barras",
        value=st.session_state.get("cod_barra_input", ""),
        key="cod_barra_input",
        placeholder="Ej: 123456789"
    )

    Nombre = st.text_input(
        "🏷️ Nombre del producto",
        value=st.session_state.get("nombre_producto_input", ""),
        key="nombre_producto_input",
        placeholder="Ej: Arroz blanco"
    )

    # 🔽 SELECTOR DE CATEGORÍA (cargado desde la BD)
    categoria = st.selectbox(
        "📁 Categoría del producto:",
        categorias,
        index=0,
        key="categoria_input",
        help="Selecciona la categoría a la que pertenece este producto"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Guardar producto", use_container_width=True, type="primary"):
            if not Cod_barra.strip() or not Nombre.strip() or not categoria:
                st.warning("⚠️ Por favor, completa todos los campos.")
            else:
                conn = obtener_conexion()
                if not conn:
                    st.error("❌ No se pudo conectar a la base de datos.")
                    st.stop()

                cursor = conn.cursor()
                try:
                    # Verificar duplicado por tienda usando el índice único
                    cursor.execute(
                        "SELECT COUNT(*) FROM Producto WHERE Cod_barra = %s AND id_tienda = %s",
                        (Cod_barra.strip(), id_tienda)
                    )
                    existe = cursor.fetchone()[0]

                    if existe > 0:
                        st.error(f"❌ Ya existe un producto con el código de barras '{Cod_barra}' en esta tienda.")
                    else:
                        # Insertar producto (id_producto se genera automáticamente)
                        cursor.execute(
                            """
                            INSERT INTO Producto (Cod_barra, Nombre, categoria, id_tienda)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (Cod_barra.strip(), Nombre.strip(), categoria, id_tienda)
                        )
                        conn.commit()

                        st.session_state["producto_guardado"] = True
                        st.session_state["reiniciar_formulario"] = True
                        st.success(f"✅ Producto '{Nombre}' guardado correctamente en categoría '{categoria}'")
                        st.rerun()

                except Exception as e:
                    conn.rollback()
                    # Verificar si es error de duplicado (por si acaso)
                    if "Duplicate entry" in str(e):
                        st.error(f"❌ El código de barras '{Cod_barra}' ya existe en esta tienda.")
                    else:
                        st.error(f"❌ Error al guardar el producto: {e}")

                finally:
                    cursor.close()
                    conn.close()

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⬅ Volver al menú principal", use_container_width=True):
            st.session_state["module"] = None
            st.rerun()
