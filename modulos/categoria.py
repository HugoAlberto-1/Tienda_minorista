import streamlit as st
from config.conexion import obtener_conexion


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Las categorías son globales.
# Como actualmente la tabla Categoria exige id_tienda
# y todas tus categorías están asociadas a la tienda 2,
# las nuevas categorías se guardarán con id_tienda = 2.
ID_TIENDA_CATALOGO_CATEGORIAS = 2


# ============================================================
# ESTILOS
# ============================================================

def configurar_estilo():
    """Configuración de estilos CSS para el módulo de categorías - MODO CLARO"""

    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_ACCENT = "#3a7ca5"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_DARK = "#1a1a1a"
    COLOR_TEXT_LIGHT = "#ffffff"
    COLOR_HOVER = "#e8f0fe"
    COLOR_BORDER = "#e0e0e0"
    COLOR_BUTTON = "#1e3a5f"

    st.markdown(
        f"""
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

        .total-categorias {{
            color: {COLOR_TEXT_DARK} !important;
            font-weight: 500 !important;
            font-size: 1em !important;
        }}

        .stTextInput > label,
        .stSelectbox > label,
        .stTextArea > label {{
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

        /* ============================================ */
        /* SELECTBOX - FONDO AZUL Y TEXTO BLANCO */
        /* ============================================ */

        .stSelectbox [data-baseweb="select"] > div {{
            background-color: {COLOR_BUTTON} !important;
            border-radius: 8px !important;
            border: 1px solid {COLOR_BORDER} !important;
            color: white !important;
        }}

        .stSelectbox [data-baseweb="select"] div {{
            color: white !important;
            -webkit-text-fill-color: white !important;
        }}

        .stSelectbox [data-baseweb="select"] span {{
            color: white !important;
            -webkit-text-fill-color: white !important;
        }}

        .stSelectbox [data-baseweb="select"] svg {{
            fill: white !important;
            color: white !important;
        }}

        /* ============================================ */
        /* BOTONES */
        /* ============================================ */

        .stButton > button {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }}

        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY} !important;
            transform: translateY(-1px) !important;
            color: white !important;
        }}

        .stForm button[type="submit"] {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.3s ease !important;
        }}

        .stForm button[type="submit"]:hover {{
            background-color: {COLOR_SECONDARY} !important;
            transform: translateY(-1px) !important;
            color: white !important;
        }}

        button {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
        }}

        button:hover {{
            background-color: {COLOR_SECONDARY} !important;
        }}

        /* ============================================ */
        /* EXPANDER */
        /* ============================================ */

        .streamlit-expanderHeader {{
            background-color: {COLOR_PRIMARY} !important;
            border-radius: 8px !important;
            border: 1px solid {COLOR_BORDER};
        }}

        .streamlit-expanderHeader p {{
            color: {COLOR_TEXT_LIGHT} !important;
            font-weight: 600 !important;
            font-size: 1em !important;
        }}

        .streamlit-expanderHeader span {{
            color: {COLOR_TEXT_LIGHT} !important;
        }}

        details summary {{
            background-color: {COLOR_PRIMARY} !important;
            color: {COLOR_TEXT_LIGHT} !important;
        }}

        details summary p {{
            color: {COLOR_TEXT_LIGHT} !important;
        }}

        .streamlit-expanderContent {{
            background-color: {COLOR_CARD} !important;
            border-radius: 8px !important;
            border: 1px solid {COLOR_BORDER} !important;
            border-top: none !important;
            padding: 10px !important;
        }}

        hr {{
            border-color: {COLOR_BORDER};
        }}

        /* ============================================ */
        /* TABS */
        /* ============================================ */

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
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================

def obtener_categorias(id_tienda=None):
    """
    Obtiene TODAS las categorías activas.

    id_tienda se conserva como parámetro únicamente para
    mantener compatibilidad con el resto del sistema,
    pero ya NO se utiliza como filtro.
    """

    conn = obtener_conexion()

    if not conn:
        return []

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                id_categoria,
                nombre,
                descripcion,
                fecha_creacion
            FROM Categoria
            WHERE activo = 1
            ORDER BY nombre
            """
        )

        categorias = cursor.fetchall()

        return categorias

    except Exception as e:

        st.error(
            f"Error al obtener categorías: {e}"
        )

        return []

    finally:

        cursor.close()
        conn.close()


def obtener_categorias_solo_nombres(id_tienda=None):
    """
    Obtiene los nombres de TODAS las categorías activas.

    Sirve para los selectbox de productos, inventario,
    edición de productos, etc.
    """

    conn = obtener_conexion()

    if not conn:
        return []

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT DISTINCT nombre
            FROM Categoria
            WHERE activo = 1
            ORDER BY nombre
            """
        )

        resultados = cursor.fetchall()

        return [
            row[0]
            for row in resultados
        ]

    except Exception as e:

        st.error(
            f"Error al obtener nombres de categorías: {e}"
        )

        return []

    finally:

        cursor.close()
        conn.close()


def crear_categoria(id_tienda, nombre, descripcion):
    """
    Crea una categoría GLOBAL.

    Aunque cualquier tienda pueda crearla,
    se almacena bajo el ID 2 porque actualmente
    la estructura de Categoria requiere id_tienda.
    """

    conn = obtener_conexion()

    if not conn:

        return (
            False,
            "No se pudo conectar a la base de datos"
        )

    cursor = conn.cursor()

    try:

        # ========================================================
        # VERIFICAR SI LA CATEGORÍA YA EXISTE GLOBALMENTE
        # ========================================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM Categoria
            WHERE nombre = %s
            AND activo = 1
            """,
            (
                nombre,
            )
        )

        existe = cursor.fetchone()[0]

        if existe > 0:

            return (
                False,
                f"Ya existe una categoría activa "
                f"con el nombre '{nombre}'"
            )

        # ========================================================
        # CREAR CATEGORÍA EN EL CATÁLOGO GLOBAL
        # ========================================================

        cursor.execute(
            """
            INSERT INTO Categoria
            (
                nombre,
                descripcion,
                id_tienda,
                fecha_creacion,
                activo
            )
            VALUES
            (
                %s,
                %s,
                %s,
                CURRENT_DATE,
                1
            )
            """,
            (
                nombre,
                descripcion,
                ID_TIENDA_CATALOGO_CATEGORIAS
            )
        )

        conn.commit()

        return (
            True,
            f"Categoría '{nombre}' creada exitosamente"
        )

    except Exception as e:

        conn.rollback()

        return (
            False,
            f"Error al crear la categoría: {e}"
        )

    finally:

        cursor.close()
        conn.close()


def actualizar_categoria(
    id_categoria,
    nombre,
    descripcion,
    id_tienda=None
):
    """
    Actualiza una categoría GLOBAL.
    """

    conn = obtener_conexion()

    if not conn:

        return (
            False,
            "No se pudo conectar a la base de datos"
        )

    cursor = conn.cursor()

    try:

        # ========================================================
        # OBTENER NOMBRE ACTUAL
        # ========================================================

        cursor.execute(
            """
            SELECT nombre
            FROM Categoria
            WHERE id_categoria = %s
            AND activo = 1
            """,
            (
                id_categoria,
            )
        )

        resultado = cursor.fetchone()

        if not resultado:

            return (
                False,
                "La categoría seleccionada no existe."
            )

        nombre_anterior = resultado[0]

        # ========================================================
        # VERIFICAR DUPLICADOS GLOBALMENTE
        # ========================================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM Categoria
            WHERE nombre = %s
            AND id_categoria != %s
            AND activo = 1
            """,
            (
                nombre,
                id_categoria
            )
        )

        existe = cursor.fetchone()[0]

        if existe > 0:

            return (
                False,
                f"Ya existe otra categoría activa "
                f"con el nombre '{nombre}'"
            )

        # ========================================================
        # ACTUALIZAR CATEGORÍA
        # ========================================================

        cursor.execute(
            """
            UPDATE Categoria
            SET
                nombre = %s,
                descripcion = %s
            WHERE id_categoria = %s
            """,
            (
                nombre,
                descripcion,
                id_categoria
            )
        )

        # ========================================================
        # ACTUALIZAR PRODUCTOS DE TODAS LAS TIENDAS
        # ========================================================
        #
        # Como Producto guarda el nombre de la categoría
        # y no id_categoria, si cambia el nombre debemos
        # actualizarlo en todas las tiendas.
        # ========================================================

        if nombre_anterior != nombre:

            cursor.execute(
                """
                UPDATE Producto
                SET categoria = %s
                WHERE categoria = %s
                """,
                (
                    nombre,
                    nombre_anterior
                )
            )

        conn.commit()

        return (
            True,
            f"Categoría '{nombre}' actualizada exitosamente"
        )

    except Exception as e:

        conn.rollback()

        return (
            False,
            f"Error al actualizar la categoría: {e}"
        )

    finally:

        cursor.close()
        conn.close()


def eliminar_categoria(
    id_categoria,
    id_tienda=None
):
    """
    Elimina lógicamente una categoría GLOBAL.

    Antes de eliminar verifica si cualquier producto
    de cualquier tienda utiliza la categoría.
    """

    conn = obtener_conexion()

    if not conn:

        return (
            False,
            "No se pudo conectar a la base de datos"
        )

    cursor = conn.cursor()

    try:

        # ========================================================
        # OBTENER NOMBRE DE CATEGORÍA
        # ========================================================

        cursor.execute(
            """
            SELECT nombre
            FROM Categoria
            WHERE id_categoria = %s
            AND activo = 1
            """,
            (
                id_categoria,
            )
        )

        resultado = cursor.fetchone()

        if not resultado:

            return (
                False,
                "La categoría seleccionada no existe."
            )

        nombre_categoria = resultado[0]

        # ========================================================
        # VERIFICAR PRODUCTOS DE TODAS LAS TIENDAS
        # ========================================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM Producto
            WHERE categoria = %s
            """,
            (
                nombre_categoria,
            )
        )

        productos_asociados = (
            cursor.fetchone()[0]
        )

        if productos_asociados > 0:

            return (
                False,
                f"No se puede eliminar la categoría "
                f"porque tiene {productos_asociados} "
                f"producto(s) asociado(s) en el sistema. "
                f"Primero reasigna esos productos."
            )

        # ========================================================
        # SOFT DELETE GLOBAL
        # ========================================================

        cursor.execute(
            """
            UPDATE Categoria
            SET activo = 0
            WHERE id_categoria = %s
            """,
            (
                id_categoria,
            )
        )

        conn.commit()

        return (
            True,
            "Categoría eliminada exitosamente"
        )

    except Exception as e:

        conn.rollback()

        return (
            False,
            f"Error al eliminar la categoría: {e}"
        )

    finally:

        cursor.close()
        conn.close()


# ============================================================
# INTERFAZ DE USUARIO
# ============================================================

def modulo_categoria():

    configurar_estilo()

    st.markdown(
        '<div class="module-title">'
        '📁 Gestión de Categorías'
        '</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # VALIDACIÓN DE SESIÓN
    # ========================================================

    if (
        not st.session_state.get("logueado")
        or "id_tienda" not in st.session_state
    ):

        st.error(
            "❌ No has iniciado sesión. "
            "Inicia sesión primero."
        )

        st.markdown("---")

        if st.button(
            "⬅ Volver al menú principal"
        ):

            st.session_state["module"] = None
            st.rerun()

        return

    # ========================================================
    # INFORMACIÓN DE LA TIENDA
    # ========================================================

    id_tienda = st.session_state["id_tienda"]

    nombre_tienda = st.session_state.get(
        "nombre_tienda",
        "Mi Tienda"
    )

    st.markdown(
        f"""
        <div class="info-box">
            🏪 Tienda actual:
            <strong>{nombre_tienda}</strong>
            <br>
            🌐 Las categorías mostradas son globales
            y están disponibles para todas las tiendas.
        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # PESTAÑAS
    # ========================================================

    tab1, tab2, tab3 = st.tabs(
        [
            "📋 Lista de categorías",
            "➕ Crear nueva categoría",
            "✏️ Editar/Eliminar"
        ]
    )

    with tab1:

        mostrar_lista_categorias(
            id_tienda
        )

    with tab2:

        mostrar_formulario_crear(
            id_tienda
        )

    with tab3:

        mostrar_formulario_editar_eliminar(
            id_tienda
        )

    # ========================================================
    # VOLVER
    # ========================================================

    st.markdown("---")

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:

        if st.button(
            "⬅ Volver al menú principal",
            use_container_width=True
        ):

            st.session_state["module"] = None
            st.rerun()


# ============================================================
# LISTAR CATEGORÍAS
# ============================================================

def mostrar_lista_categorias(id_tienda=None):

    st.markdown(
        '<div class="module-subtitle">'
        '📋 Categorías disponibles para todas las tiendas'
        '</div>',
        unsafe_allow_html=True
    )

    categorias = obtener_categorias(
        id_tienda
    )

    if not categorias:

        st.info(
            "ℹ️ No hay categorías registradas. "
            "Crea una en la pestaña "
            "'Crear nueva categoría'."
        )

    else:

        st.markdown(
            f"""
            <p class="total-categorias">
                <strong>Total de categorías:</strong>
                {len(categorias)}
            </p>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        for cat in categorias:

            (
                id_cat,
                nombre,
                descripcion,
                fecha
            ) = cat

            with st.expander(
                f"📁 {nombre}"
            ):

                st.markdown(
                    f"""
                    <p style="color: #1a1a1a;">
                        <strong>ID:</strong>
                        {id_cat}
                    </p>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <p style="color: #1a1a1a;">
                        <strong>Descripción:</strong>
                        {
                            descripcion
                            if descripcion
                            else "Sin descripción"
                        }
                    </p>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <p style="color: #1a1a1a;">
                        <strong>Fecha de creación:</strong>
                        {fecha}
                    </p>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# CREAR CATEGORÍA
# ============================================================

def mostrar_formulario_crear(id_tienda=None):

    st.markdown(
        '<div class="module-subtitle">'
        '➕ Crear nueva categoría global'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "🌐 La categoría que crees estará disponible "
        "para todas las tiendas."
    )

    with st.form(
        "form_crear_categoria"
    ):

        nombre = st.text_input(
            "📝 Nombre de la categoría",
            placeholder=(
                "Ej: Bebidas, Lácteos, Carnes, etc."
            ),
            help=(
                "El nombre debe ser único "
                "en todo el sistema"
            )
        )

        descripcion = st.text_area(
            "📄 Descripción (opcional)",
            placeholder=(
                "Describe qué productos pertenecen "
                "a esta categoría..."
            ),
            help=(
                "Una breve descripción "
                "de la categoría"
            )
        )

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col2:

            submitted = (
                st.form_submit_button(
                    "✅ Crear categoría",
                    type="primary",
                    use_container_width=True
                )
            )

        if submitted:

            if not nombre.strip():

                st.error(
                    "❌ El nombre de la categoría "
                    "es obligatorio."
                )

            else:

                exito, mensaje = crear_categoria(
                    id_tienda,
                    nombre.strip(),
                    (
                        descripcion.strip()
                        if descripcion
                        else None
                    )
                )

                if exito:

                    st.success(
                        mensaje
                    )

                    st.balloons()

                    st.rerun()

                else:

                    st.error(
                        mensaje
                    )


# ============================================================
# EDITAR / ELIMINAR
# ============================================================

def mostrar_formulario_editar_eliminar(
    id_tienda=None
):

    st.markdown(
        '<div class="module-subtitle">'
        '✏️ Editar o eliminar categoría global'
        '</div>',
        unsafe_allow_html=True
    )

    st.warning(
        "⚠️ Los cambios realizados en una categoría "
        "afectarán a todas las tiendas."
    )

    categorias = obtener_categorias(
        id_tienda
    )

    if not categorias:

        st.info(
            "ℹ️ No hay categorías "
            "para editar o eliminar."
        )

        return

    # ========================================================
    # OPCIONES
    # ========================================================

    opciones = {
        f"{cat[1]}": cat[0]
        for cat in categorias
    }

    categoria_seleccionada_nombre = (
        st.selectbox(
            "🔍 Selecciona una categoría",
            list(opciones.keys()),
            key="select_categoria_editar"
        )
    )

    if categoria_seleccionada_nombre:

        id_categoria = opciones[
            categoria_seleccionada_nombre
        ]

        cat_seleccionada = next(
            (
                cat
                for cat in categorias
                if cat[0] == id_categoria
            ),
            None
        )

        if cat_seleccionada:

            with st.form(
                "form_editar_categoria"
            ):

                nuevo_nombre = (
                    st.text_input(
                        "📝 Nombre",
                        value=cat_seleccionada[1]
                    )
                )

                nueva_descripcion = (
                    st.text_area(
                        "📄 Descripción",
                        value=(
                            cat_seleccionada[2]
                            if cat_seleccionada[2]
                            else ""
                        )
                    )
                )

                st.info(
                    "ℹ️ Si cambias el nombre de la categoría, "
                    "los productos asociados en todas las tiendas "
                    "también serán actualizados automáticamente."
                )

                col1, col2 = st.columns(
                    2,
                    gap="large"
                )

                # ================================================
                # GUARDAR
                # ================================================

                with col1:

                    if st.form_submit_button(
                        "💾 Guardar cambios",
                        type="primary",
                        use_container_width=True
                    ):

                        if not nuevo_nombre.strip():

                            st.error(
                                "❌ El nombre "
                                "es obligatorio."
                            )

                        else:

                            exito, mensaje = (
                                actualizar_categoria(
                                    id_categoria,
                                    nuevo_nombre.strip(),
                                    (
                                        nueva_descripcion.strip()
                                        if nueva_descripcion
                                        else None
                                    ),
                                    id_tienda
                                )
                            )

                            if exito:

                                st.success(
                                    mensaje
                                )

                                st.rerun()

                            else:

                                st.error(
                                    mensaje
                                )

                # ================================================
                # ELIMINAR
                # ================================================

                with col2:

                    if st.form_submit_button(
                        "🗑️ Eliminar categoría",
                        use_container_width=True
                    ):

                        exito, mensaje = (
                            eliminar_categoria(
                                id_categoria,
                                id_tienda
                            )
                        )

                        if exito:

                            st.success(
                                mensaje
                            )

                            st.rerun()

                        else:

                            st.error(
                                mensaje
                            )
