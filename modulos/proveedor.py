import streamlit as st
from config.conexion import obtener_conexion


# ==========================================================
# CONFIGURACIÓN DE ESTILO
# ==========================================================

def configurar_estilo():
    """Configuración de estilos CSS para el módulo de proveedor"""

    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_BG = "#f5f7fa"
    COLOR_TEXT_DARK = "#1a1a1a"
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

        .stTextInput > label,
        .stNumberInput > label {{
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

        hr {{
            border-color: {COLOR_BORDER};
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# VALIDACIONES
# ==========================================================

def validar_dui_nit(dui_nit):
    """
    Valida DUI o NIT.

    El campo es opcional.

    Si se ingresa:
    - Puede contener guiones y espacios.
    - Después de limpiarlo debe contener únicamente números.
    - NO se limita a 9 dígitos.
    - Se guarda sin guiones ni espacios.

    Ejemplos válidos:
    01234567-8
    012345678
    0614-290123-102-3
    06142901231023

    Si está vacío:
    devuelve None para almacenar NULL en la BD.
    """

    # Campo opcional
    if not dui_nit or not dui_nit.strip():
        return None, None

    # Eliminar espacios y guiones
    dui_nit_limpio = (
        dui_nit.strip()
        .replace("-", "")
        .replace(" ", "")
    )

    # Validar que solo queden números
    if not dui_nit_limpio.isdigit():

        return (
            None,
            "El DUI/NIT debe contener únicamente números, "
            "aunque puedes escribirlo con guiones o espacios."
        )

    # No existe restricción de 9 dígitos
    return dui_nit_limpio, None


def validar_telefono(telefono):
    """
    Valida teléfono.

    Acepta:
    7777-8888
    77778888

    Lo devuelve:
    7777-8888
    """

    telefono_limpio = (
        telefono.strip()
        .replace("-", "")
        .replace(" ", "")
    )

    if not telefono_limpio.isdigit():

        return (
            None,
            "El contacto debe contener únicamente números."
        )

    if len(telefono_limpio) != 8:

        return (
            None,
            "El número de contacto debe contener 8 dígitos."
        )

    telefono_formateado = (
        f"{telefono_limpio[:4]}-"
        f"{telefono_limpio[4:]}"
    )

    return telefono_formateado, None


# ==========================================================
# MÓDULO PROVEEDOR
# ==========================================================

def modulo_proveedor():

    configurar_estilo()

    st.markdown(
    f'<div class="info-box">🏪 Tienda: <strong>{nombre_tienda}</strong></div>',
    unsafe_allow_html=True
)

    # ======================================================
    # VALIDAR SESIÓN
    # ======================================================

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

            st.session_state.module = None

            st.rerun()

        return


    # ======================================================
    # DATOS DE LA TIENDA DEL USUARIO
    # ======================================================

    id_tienda = st.session_state[
        "id_tienda"
    ]

    nombre_tienda = st.session_state.get(
        "nombre_tienda",
        "Mi Tienda"
    )


    # ======================================================
    # MOSTRAR TIENDA
    # ======================================================

    st.markdown(
        f"""
        <div class="info-box">

            🏪 Tienda:

            <strong>
                {nombre_tienda}
            </strong>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ======================================================
    # LIMPIAR CAMPOS DESPUÉS DE GUARDAR
    # ======================================================

    if st.session_state.get(
        "reiniciar_proveedor"
    ):

        campos = [
            "proveedor_nombre_input",
            "proveedor_dui_input",
            "proveedor_direccion_input",
            "proveedor_contacto_input",
            "proveedor_lead_time_input"
        ]

        for campo in campos:

            st.session_state.pop(
                campo,
                None
            )

        st.session_state.pop(
            "reiniciar_proveedor",
            None
        )

        st.rerun()


    # ======================================================
    # MENSAJE DE ÉXITO
    # ======================================================

    if st.session_state.get(
        "proveedor_guardado"
    ):

        st.success(
            "✅ Proveedor guardado correctamente."
        )

        st.session_state.pop(
            "proveedor_guardado",
            None
        )


    # ======================================================
    # SUBTÍTULO
    # ======================================================

    st.markdown(
        '<div class="module-subtitle">'
        '➕ Agregar nuevo proveedor'
        '</div>',
        unsafe_allow_html=True
    )


    # ======================================================
    # FORMULARIO
    # ======================================================

    col1, col2 = st.columns(
        2,
        gap="large"
    )


    # ======================================================
    # COLUMNA IZQUIERDA
    # ======================================================

    with col1:

        Nombre = st.text_input(
            "🏢 Nombre del proveedor",
            key="proveedor_nombre_input",
            placeholder="Ej: Distribuidora Martínez"
        )


        # ==================================================
        # DUI / NIT OPCIONAL
        # ==================================================

        DUI_NIT = st.text_input(
            "🆔 DUI/NIT (opcional)",
            key="proveedor_dui_input",
            placeholder=(
                "Ej: 01234567-8 "
                "o 0614-290123-102-3"
            ),
            help=(
                "Campo opcional. Puedes ingresar DUI o NIT "
                "con o sin guiones. Puede contener más de "
                "9 dígitos."
            )
        )


        Direccion = st.text_input(
            "📍 Dirección",
            key="proveedor_direccion_input",
            placeholder="Ej: San Salvador"
        )


    # ======================================================
    # COLUMNA DERECHA
    # ======================================================

    with col2:

        Contacto = st.text_input(
            "📞 Contacto",
            key="proveedor_contacto_input",
            placeholder="Ej: 7777-8888",
            help=(
                "Puedes ingresar el teléfono "
                "con o sin guión."
            )
        )


        Lead_time = st.number_input(
            "⏱️ Tiempo de entrega (días)",
            min_value=1,
            step=1,
            value=1,
            key="proveedor_lead_time_input",
            help=(
                "Número aproximado de días que "
                "tarda el proveedor en entregar."
            )
        )


    # ======================================================
    # BOTÓN GUARDAR
    # ======================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:

        if st.button(
            "💾 Guardar proveedor",
            use_container_width=True,
            type="primary"
        ):

            # ==============================================
            # VALIDAR CAMPOS OBLIGATORIOS
            # ==============================================
            #
            # IMPORTANTE:
            # DUI/NIT NO se encuentra aquí porque
            # ahora es opcional.
            # ==============================================

            if (
                not Nombre.strip()
                or not Direccion.strip()
                or not Contacto.strip()
            ):

                st.warning(
                    "⚠️ Por favor, completa los campos "
                    "obligatorios: nombre, dirección "
                    "y contacto."
                )

            else:

                # ==========================================
                # VALIDAR DUI/NIT
                # ==========================================
                #
                # Si está vacío:
                # dui_nit_validado = None
                #
                # Si tiene contenido:
                # se valida.
                # ==========================================

                (
                    dui_nit_validado,
                    error_dui_nit
                ) = validar_dui_nit(
                    DUI_NIT
                )


                if error_dui_nit:

                    st.error(
                        f"❌ {error_dui_nit}"
                    )

                else:

                    # ======================================
                    # VALIDAR CONTACTO
                    # ======================================

                    (
                        contacto_validado,
                        error_contacto
                    ) = validar_telefono(
                        Contacto
                    )


                    if error_contacto:

                        st.error(
                            f"❌ {error_contacto}"
                        )

                    else:

                        # ==================================
                        # CONEXIÓN A BD
                        # ==================================

                        conn = obtener_conexion()

                        if not conn:

                            st.error(
                                "❌ No se pudo conectar "
                                "a la base de datos."
                            )

                            st.stop()


                        cursor = conn.cursor()


                        try:

                            # ==============================
                            # VERIFICAR DUI/NIT DUPLICADO
                            # ==============================
                            #
                            # SOLO se verifica si el usuario
                            # escribió un DUI/NIT.
                            #
                            # Si está vacío se omite
                            # completamente esta validación.
                            # ==============================

                            existe = 0


                            if dui_nit_validado:

                                cursor.execute(
                                    """
                                    SELECT COUNT(*)

                                    FROM Proveedor

                                    WHERE

                                        REPLACE(
                                            REPLACE(
                                                DUI,
                                                '-',
                                                ''
                                            ),
                                            ' ',
                                            ''
                                        ) = %s

                                        AND id_tienda = %s
                                    """,
                                    (
                                        dui_nit_validado,
                                        id_tienda
                                    )
                                )


                                existe = (
                                    cursor.fetchone()[0]
                                )


                            # ==============================
                            # DUPLICADO ENCONTRADO
                            # ==============================

                            if existe:

                                st.error(
                                    "❌ Ya existe un proveedor "
                                    "con este DUI/NIT "
                                    "en esta tienda."
                                )

                            else:

                                # ==========================
                                # INSERTAR PROVEEDOR
                                # ==========================
                                #
                                # Aunque en pantalla diga
                                # DUI/NIT, siempre se almacena
                                # en la columna DUI.
                                #
                                # Si no se escribió:
                                # dui_nit_validado = None
                                # y MySQL recibirá NULL.
                                # ==========================

                                cursor.execute(
                                    """
                                    INSERT INTO Proveedor
                                    (
                                        Nombre,
                                        DUI,
                                        Direccion,
                                        Contacto,
                                        lead_time,
                                        id_tienda
                                    )

                                    VALUES
                                    (
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s
                                    )
                                    """,
                                    (
                                        Nombre.strip(),

                                        # DUI o NIT
                                        # Siempre va al campo DUI
                                        dui_nit_validado,

                                        Direccion.strip(),

                                        contacto_validado,

                                        int(
                                            Lead_time
                                        ),

                                        id_tienda
                                    )
                                )


                                conn.commit()


                                # ==========================
                                # MENSAJE DE ÉXITO
                                # ==========================

                                st.session_state[
                                    "proveedor_guardado"
                                ] = True


                                # ==========================
                                # LIMPIAR FORMULARIO
                                # ==========================

                                st.session_state[
                                    "reiniciar_proveedor"
                                ] = True


                                st.rerun()


                        except Exception as e:

                            conn.rollback()

                            st.error(
                                f"❌ Error al guardar "
                                f"el proveedor: {e}"
                            )


                        finally:

                            cursor.close()

                            conn.close()


    # ======================================================
    # BOTÓN VOLVER
    # ======================================================

    st.markdown("---")

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:

        if st.button(
            "⬅ Volver al menú principal",
            use_container_width=True
        ):

            st.session_state.module = None

            st.rerun()
