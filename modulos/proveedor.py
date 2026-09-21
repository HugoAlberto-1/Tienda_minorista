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
    """, unsafe_allow_html=True)


# ==========================================================
# VALIDACIONES
# ==========================================================
def validar_dui(dui):
    """
    Valida DUI salvadoreño.
    Acepta:
    01234567-8
    012345678

    Lo devuelve con formato:
    01234567-8
    """

    dui_limpio = dui.strip().replace("-", "").replace(" ", "")

    if not dui_limpio.isdigit():
        return None, "El DUI debe contener únicamente números."

    if len(dui_limpio) != 9:
        return None, f"El DUI debe tener 9 dígitos. Ingresaste {len(dui_limpio)}."

    dui_formateado = f"{dui_limpio[:8]}-{dui_limpio[8]}"

    return dui_formateado, None


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
        return None, "El contacto debe contener únicamente números."

    if len(telefono_limpio) != 8:
        return None, "El número de contacto debe contener 8 dígitos."

    telefono_formateado = (
        f"{telefono_limpio[:4]}-{telefono_limpio[4:]}"
    )

    return telefono_formateado, None


# ==========================================================
# MÓDULO PROVEEDOR
# ==========================================================
def modulo_proveedor():

    configurar_estilo()

    st.markdown(
        '<div class="module-title">🚚 Registrar Proveedor</div>',
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
            "❌ No has iniciado sesión. Inicia sesión primero."
        )

        st.markdown("---")

        if st.button("⬅ Volver al menú principal"):
            st.session_state.module = None
            st.rerun()

        return


    # ======================================================
    # DATOS DE LA TIENDA DEL USUARIO
    # ======================================================

    id_tienda = st.session_state["id_tienda"]

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
            <strong>{nombre_tienda}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ======================================================
    # LIMPIAR CAMPOS DESPUÉS DE GUARDAR
    # ======================================================

    if st.session_state.get("reiniciar_proveedor"):

        campos = [
            "proveedor_nombre_input",
            "proveedor_dui_input",
            "proveedor_direccion_input",
            "proveedor_contacto_input",
            "proveedor_lead_time_input"
        ]

        for campo in campos:
            st.session_state.pop(campo, None)

        st.session_state.pop(
            "reiniciar_proveedor",
            None
        )

        st.rerun()


    # ======================================================
    # MENSAJE DE ÉXITO
    # ======================================================

    if st.session_state.get("proveedor_guardado"):

        st.success(
            "✅ Proveedor guardado correctamente."
        )

        st.session_state.pop(
            "proveedor_guardado",
            None
        )


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


        DUI = st.text_input(
            "🆔 DUI",
            key="proveedor_dui_input",
            placeholder="Ej: 01234567-8",
            help="Puedes ingresar el DUI con o sin guión."
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
            help="Puedes ingresar el teléfono con o sin guión."
        )


        Lead_time = st.number_input(
            "⏱️ Tiempo de entrega (días)",
            min_value=1,
            step=1,
            value=1,
            key="proveedor_lead_time_input",
            help="Número aproximado de días que tarda el proveedor en entregar."
        )


    # ======================================================
    # BOTÓN GUARDAR
    # ======================================================

    st.markdown("<br>", unsafe_allow_html=True)

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

            if (
                not Nombre.strip()
                or not DUI.strip()
                or not Direccion.strip()
                or not Contacto.strip()
            ):

                st.warning(
                    "⚠️ Por favor, completa todos los campos."
                )

            else:

                # ==========================================
                # VALIDAR DUI
                # ==========================================

                dui_validado, error_dui = validar_dui(DUI)

                if error_dui:

                    st.error(
                        f"❌ {error_dui}"
                    )

                else:

                    # ======================================
                    # VALIDAR CONTACTO
                    # ======================================

                    contacto_validado, error_contacto = (
                        validar_telefono(Contacto)
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
                            # NORMALIZAR DUI PARA BÚSQUEDA
                            # ==============================

                            dui_sin_guion = (
                                dui_validado.replace("-", "")
                            )


                            # ==============================
                            # VERIFICAR DUPLICADO
                            # SOLO DENTRO DE LA MISMA TIENDA
                            # ==============================

                            cursor.execute(
                                """
                                SELECT COUNT(*)
                                FROM Proveedor
                                WHERE
                                    REPLACE(DUI, '-', '') = %s
                                    AND id_tienda = %s
                                """,
                                (
                                    dui_sin_guion,
                                    id_tienda
                                )
                            )


                            existe = cursor.fetchone()[0]


                            if existe:

                                st.error(
                                    "❌ Ya existe un proveedor "
                                    "con este DUI en esta tienda."
                                )

                            else:

                                # ==========================
                                # INSERTAR PROVEEDOR
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
                                        dui_validado,
                                        Direccion.strip(),
                                        contacto_validado,
                                        int(Lead_time),
                                        id_tienda
                                    )
                                )


                                conn.commit()


                                # ==========================
                                # ACTIVAR MENSAJE DE ÉXITO
                                # Y LIMPIAR FORMULARIO
                                # ==========================

                                st.session_state[
                                    "proveedor_guardado"
                                ] = True

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
