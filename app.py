import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'modulos'))

import streamlit as st
from login import login, verificar_usuario

from modulos.compras import modulo_compras
from modulos.ventas import modulo_ventas
from modulos.producto import modulo_producto
from modulos.editar_producto import modulo_editar_producto
from modulos.dashboard import dashboard
from modulos.empleado import modulo_empleado
from modulos.inventario import modulo_inventario
from modulos.reporte_ventas import reporte_ventas
from modulos.categoria import modulo_categoria
from modulos.gestion_admin import modulo_gestion_admin
from modulos.productos_mas_menos_vendidos import modulo_productos_mas_menos_vendidos
from modulos.reporte_compras import modulo_reporte_compras

# ============================================================
# 🆕 NUEVO MÓDULO: COMPARATIVA DE COSTOS
# ============================================================
from modulos.comparativa_inv import modulo_comparativa_inv


def configurar_pagina():
    """Configuración de la página con CSS personalizado"""

    st.set_page_config(
        page_title="Sistema de Inventario",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # ============================================================
    # 🎨 PALETA DE COLORES
    # ============================================================

    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_ACCENT = "#3a7ca5"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_LIGHT = "#666666"
    COLOR_HOVER = "#e8f0fe"

    # ============================================================
    # 🎨 CSS PERSONALIZADO
    # ============================================================

    st.markdown(
        f"""
        <style>

        /* ============================================================
           FONDO GENERAL
           ============================================================ */

        .stApp {{
            background-color: {COLOR_BG};
        }}


        /* ============================================================
           TÍTULOS
           ============================================================ */

        .main-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 20px;
        }}


        .subtitle {{
            text-align: center;
            color: {COLOR_SECONDARY};
            font-size: 1.1em;
            margin-bottom: 30px;
        }}


        .welcome-text {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 1.2em;
            margin: 20px 0;
            padding: 12px;
            background: {COLOR_HOVER};
            border-radius: 8px;
            border-left: 4px solid {COLOR_PRIMARY};
        }}


        /* ============================================================
           TARJETAS PEQUEÑAS
           ============================================================ */

        .card {{
            background: {COLOR_CARD};
            border-radius: 12px;
            padding: 20px 15px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
            height: 100%;
        }}


        .card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
            border-color: {COLOR_ACCENT};
        }}


        .card-icon {{
            font-size: 2.2em;
            margin-bottom: 10px;
        }}


        .card-title {{
            font-size: 1.1em;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            margin-bottom: 8px;
        }}


        .card-desc {{
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.8em;
            line-height: 1.3;
        }}


        /* ============================================================
           TARJETAS GRANDES - MACRO MÓDULOS
           ============================================================ */

        .macro-card {{
            background: {COLOR_CARD};
            border-radius: 12px;
            padding: 25px 20px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
            cursor: pointer;
            min-height: 150px;
        }}


        .macro-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
            border-color: {COLOR_PRIMARY};
        }}


        .macro-icon {{
            font-size: 2.5em;
            margin-bottom: 12px;
        }}


        .macro-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            margin-bottom: 8px;
        }}


        .macro-desc {{
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.85em;
        }}


        /* ============================================================
           SECCIÓN DE SUBMENÚ
           ============================================================ */

        .macro-section {{
            background: {COLOR_CARD};
            border-radius: 12px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
        }}


        .section-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 2px solid {COLOR_ACCENT};
            padding-bottom: 10px;
            display: inline-block;
            width: auto;
        }}


        /* ============================================================
           BOTONES
           ============================================================ */

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


        /* ============================================================
           TÍTULOS DE SECCIÓN
           ============================================================ */

        .section-header {{
            text-align: center;
            margin-bottom: 25px;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 🏠 MENÚ PRINCIPAL
# ============================================================

def menu_principal():

    configurar_pagina()

    with st.container():

        # ============================================================
        # 🔐 OBTENER INFORMACIÓN DEL USUARIO
        # ============================================================

        rol_usuario = st.session_state.get(
            "nivel_usuario",
            ""
        )

        nombre_tienda = st.session_state.get(
            "nombre_tienda",
            "Tienda Minorista"
        )

        nombre_empleado = st.session_state.get(
            "nombre_empleado",
            "Usuario"
        )


        # ============================================================
        # 🏪 TÍTULO PRINCIPAL
        # ============================================================

        st.markdown(
            f"""
            <div class="main-title">
                🛒 {nombre_tienda}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ============================================================
        # 👋 MENSAJE DE BIENVENIDA
        # ============================================================

        st.markdown(
            f"""
            <div class="welcome-text">
                ✨ Bienvenida, {nombre_empleado} ✨
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="subtitle">
                Gestiona tu negocio de manera eficiente
            </div>
            """,
            unsafe_allow_html=True
        )


        # ============================================================
        # 🔐 CREAR MACRO MÓDULO SI NO EXISTE
        # ============================================================

        if "macro_modulo" not in st.session_state:

            st.session_state["macro_modulo"] = None


        # ============================================================
        # 👑 MENÚ PARA ADMINISTRADOR
        # ============================================================

        if rol_usuario == "Administrador":

            # ========================================================
            # 🏠 MENÚ PRINCIPAL DEL ADMINISTRADOR
            # ========================================================

            if st.session_state["macro_modulo"] is None:

                st.info(
                    "👑 Panel de Administrador"
                )


                # ====================================================
                # PRIMERA FILA
                #
                # 📦 Inventario Global
                # 💰 Comparativa de Costos
                # ====================================================

                col1, col2 = st.columns(
                    2,
                    gap="large"
                )


                # ====================================================
                # 📦 INVENTARIO GLOBAL
                # ====================================================

                with col1:

                    st.markdown(
                        """
                        <div class="macro-card">

                            <div class="macro-icon">
                                📦
                            </div>

                            <div class="macro-title">
                                Inventario Global
                            </div>

                            <div class="macro-desc">
                                Ver inventario de todas las tiendas
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "📊 Ver inventario",
                        key="btn_inventario_admin",
                        use_container_width=True
                    ):

                        st.session_state.module = "Inventario"

                        st.rerun()


                # ====================================================
                # 💰 COMPARATIVA DE COSTOS
                # ====================================================

                with col2:

                    st.markdown(
                        """
                        <div class="macro-card">

                            <div class="macro-icon">
                                💰
                            </div>

                            <div class="macro-title">
                                Comparativa de Costos
                            </div>

                            <div class="macro-desc">
                                Comparar precios unitarios entre tiendas
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "💲 Ver comparativa",
                        key="btn_comparativa_inv_admin",
                        use_container_width=True
                    ):

                        st.session_state.module = "ComparativaInv"

                        st.rerun()


                # Separación visual entre filas
                st.markdown("<br>", unsafe_allow_html=True)


                # ====================================================
                # SEGUNDA FILA
                #
                # 👑 Administración
                # 📊 Reportes Globales
                # ====================================================

                col3, col4 = st.columns(
                    2,
                    gap="large"
                )


                # ====================================================
                # 👑 ADMINISTRACIÓN
                # ====================================================

                with col3:

                    st.markdown(
                        """
                        <div class="macro-card">

                            <div class="macro-icon">
                                👑
                            </div>

                            <div class="macro-title">
                                Administración
                            </div>

                            <div class="macro-desc">
                                Gestionar tiendas y usuarios
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "⚙️ Gestionar",
                        key="btn_gestion_admin",
                        use_container_width=True
                    ):

                        st.session_state.module = "GestionAdmin"

                        st.rerun()


                # ====================================================
                # 📊 REPORTES GLOBALES
                # ====================================================

                with col4:

                    st.markdown(
                        """
                        <div class="macro-card">

                            <div class="macro-icon">
                                📊
                            </div>

                            <div class="macro-title">
                                Reportes Globales
                            </div>

                            <div class="macro-desc">
                                Reportes de ventas de todas las tiendas
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "📈 Ver reportes",
                        key="btn_reportes_admin",
                        use_container_width=True
                    ):

                        st.session_state[
                            "macro_modulo"
                        ] = "reportes"

                        st.rerun()


            # ========================================================
            # 📊 SUBMENÚ DE REPORTES DEL ADMINISTRADOR
            # ========================================================

            elif st.session_state["macro_modulo"] == "reportes":

                with st.container():

                    st.markdown(
                        """
                        <div style="text-align: center;">
                            <span class="section-title">
                                📊 Consulta tus reportes
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    # =================================================
                    # TRES COLUMNAS PARA LOS REPORTES
                    # =================================================

                    col1, col2, col3 = st.columns(
                        3,
                        gap="large"
                    )


                    # =================================================
                    # 📈 REPORTE DE VENTAS
                    # =================================================

                    with col1:

                        st.markdown(
                            """
                            <div class="card" style="padding: 30px;">

                                <div class="card-icon">
                                    📈
                                </div>

                                <div class="card-title">
                                    Reporte de Ventas
                                </div>

                                <div class="card-desc">
                                    Análisis detallado de ventas
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Ver Reporte",
                            key="reporte_ventas_btn",
                            use_container_width=True
                        ):

                            st.session_state.module = "Reportes_Ventas"

                            st.rerun()


                    # =================================================
                    # 📥 REPORTE DE COMPRAS
                    # =================================================

                    with col2:

                        st.markdown(
                            """
                            <div class="card" style="padding: 30px;">

                                <div class="card-icon">
                                    📥
                                </div>

                                <div class="card-title">
                                    Reporte de Compras
                                </div>

                                <div class="card-desc">
                                    Análisis detallado de compras
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Ver Reporte de Compras",
                            key="reporte_compras_btn",
                            use_container_width=True
                        ):

                            st.session_state.module = "Reportes_Compras"

                            st.rerun()


                    # =================================================
                    # 🏆 PRODUCTOS MÁS Y MENOS VENDIDOS
                    # =================================================

                    with col3:

                        st.markdown(
                            """
                            <div class="card" style="padding: 30px;">

                                <div class="card-icon">
                                    🏆
                                </div>

                                <div class="card-title">
                                    Productos más y menos vendidos
                                </div>

                                <div class="card-desc">
                                    Productos más populares
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Ver Ranking",
                            key="top_30_btn",
                            use_container_width=True
                        ):

                            st.session_state.module = "productomasvendido"

                            st.rerun()


                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )


        # ============================================================
        # 👩‍💼 MENÚ PARA VENDEDOR
        # ============================================================

        else:

            # ========================================================
            # MENÚ PRINCIPAL DEL VENDEDOR
            # ========================================================

            if st.session_state["macro_modulo"] is None:

                # ====================================================
                # PRIMERA FILA
                # ====================================================

                col1, col2 = st.columns(
                    2,
                    gap="large"
                )


                # ====================================================
                # ✏️ INGRESAR INFORMACIÓN
                # ====================================================

                with col1:

                    st.markdown(
                        """
                        <div class="macro-card">

                            <div class="macro-icon">
                                ✏️
                            </div>

                            <div class="macro-title">
                                Ingresa nueva información
                            </div>

                            <div class="macro-desc">
                                Registra productos, empleados y categorías
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "📝 Ingresar información",
                        key="btn_registro",
                        use_container_width=True
                    ):

                        st.session_state[
                            "macro_modulo"
                        ] = "registro"

                        st.rerun()


                # ====================================================
                # 💸 TRANSACCIONES
                # ====================================================

                with col2:

                    st.markdown(
                        """
                        <div class="macro-card">

                            <div class="macro-icon">
                                💸
                            </div>

                            <div class="macro-title">
                                Compra y vende productos
                            </div>

                            <div class="macro-desc">
                                Registra tus compras y ventas diarias
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "🛒 Comprar/Vender",
                        key="btn_transacciones",
                        use_container_width=True
                    ):

                        st.session_state[
                            "macro_modulo"
                        ] = "transacciones"

                        st.rerun()


                # ====================================================
                # SEGUNDA FILA
                # ====================================================

                col3, col4 = st.columns(
                    2,
                    gap="large"
                )


                # ====================================================
                # 📋 INVENTARIO
                # ====================================================

                with col3:

                    st.markdown(
                        """
                        <div class="macro-card">

                            <div class="macro-icon">
                                📋
                            </div>

                            <div class="macro-title">
                                Consulta tu inventario
                            </div>

                            <div class="macro-desc">
                                Visualiza el stock actual de productos
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "📊 Ver inventario",
                        key="btn_inventario",
                        use_container_width=True
                    ):

                        st.session_state.module = "Inventario"

                        st.rerun()


                # ====================================================
                # 📊 REPORTES
                # ====================================================

                with col4:

                    st.markdown(
                        """
                        <div class="macro-card">

                            <div class="macro-icon">
                                📊
                            </div>

                            <div class="macro-title">
                                Consulta tus reportes
                            </div>

                            <div class="macro-desc">
                                Analiza ventas y productos más vendidos
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "📈 Ver reportes",
                        key="btn_reportes",
                        use_container_width=True
                    ):

                        st.session_state[
                            "macro_modulo"
                        ] = "reportes"

                        st.rerun()


            # ========================================================
            # ✏️ SUBMENÚ REGISTRO
            # ========================================================

            elif st.session_state["macro_modulo"] == "registro":

                with st.container():

                    st.markdown(
                        """
                        <div style="text-align: center;">
                            <span class="section-title">
                                ✏️ Registra información
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    col1, col2, col3, col4 = st.columns(4)


                    # =================================================
                    # 📦 NUEVO PRODUCTO
                    # =================================================

                    with col1:

                        st.markdown(
                            """
                            <div class="card">

                                <div class="card-icon">
                                    📦
                                </div>

                                <div class="card-title">
                                    Nuevo Producto
                                </div>

                                <div class="card-desc">
                                    Registra productos en el sistema
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Agregar",
                            key="btn_producto",
                            use_container_width=True
                        ):

                            st.session_state.module = "Producto"

                            st.rerun()


                    # =================================================
                    # ✏️ EDITAR PRODUCTO
                    # =================================================

                    with col2:

                        st.markdown(
                            """
                            <div class="card">

                                <div class="card-icon">
                                    ✏️
                                </div>

                                <div class="card-title">
                                    Editar Producto
                                </div>

                                <div class="card-desc">
                                    Modifica información de productos
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Editar",
                            key="btn_editar",
                            use_container_width=True
                        ):

                            st.session_state.module = "Editar"

                            st.rerun()


                    # =================================================
                    # 👩‍💼 NUEVA SOCIA
                    # =================================================

                    with col3:

                        st.markdown(
                            """
                            <div class="card">

                                <div class="card-icon">
                                    👩‍💼
                                </div>

                                <div class="card-title">
                                    Nueva Socia
                                </div>

                                <div class="card-desc">
                                    Registra nuevas usuarias
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Registrar",
                            key="btn_empleado",
                            use_container_width=True
                        ):

                            st.session_state.module = "Empleado"

                            st.rerun()


                    # =================================================
                    # 📁 CATEGORÍAS
                    # =================================================

                    with col4:

                        st.markdown(
                            """
                            <div class="card">

                                <div class="card-icon">
                                    📁
                                </div>

                                <div class="card-title">
                                    Gestionar Categorías
                                </div>

                                <div class="card-desc">
                                    Administra categorías de productos
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Gestionar",
                            key="btn_categoria",
                            use_container_width=True
                        ):

                            st.session_state.module = "Categoria"

                            st.rerun()


                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )


            # ========================================================
            # 💸 SUBMENÚ TRANSACCIONES
            # ========================================================

            elif st.session_state["macro_modulo"] == "transacciones":

                with st.container():

                    st.markdown(
                        """
                        <div style="text-align: center;">
                            <span class="section-title">
                                💸 Haz una compra o una venta
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    col1, col2 = st.columns(
                        2,
                        gap="large"
                    )


                    # =================================================
                    # 🛒 REALIZAR VENTA
                    # =================================================

                    with col1:

                        st.markdown(
                            """
                            <div class="card" style="padding: 30px;">

                                <div class="card-icon">
                                    🛒
                                </div>

                                <div class="card-title">
                                    Realizar Venta
                                </div>

                                <div class="card-desc">
                                    Registra una nueva venta de productos
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Iniciar Venta",
                            key="venta_btn",
                            use_container_width=True
                        ):

                            st.session_state.module = "Ventas"

                            st.rerun()


                    # =================================================
                    # 📥 REALIZAR COMPRA
                    # =================================================

                    with col2:

                        st.markdown(
                            """
                            <div class="card" style="padding: 30px;">

                                <div class="card-icon">
                                    📥
                                </div>

                                <div class="card-title">
                                    Realizar Compra
                                </div>

                                <div class="card-desc">
                                    Registra una nueva compra de productos
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Iniciar Compra",
                            key="compra_btn",
                            use_container_width=True
                        ):

                            st.session_state.module = "Compras"

                            st.rerun()


                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )


            # ========================================================
            # 📊 SUBMENÚ REPORTES DEL VENDEDOR
            # ========================================================

            elif st.session_state["macro_modulo"] == "reportes":

                with st.container():

                    st.markdown(
                        """
                        <div style="text-align: center;">
                            <span class="section-title">
                                📊 Consulta tus reportes
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    # =================================================
                    # TRES COLUMNAS
                    # =================================================

                    col1, col2, col3 = st.columns(
                        3,
                        gap="large"
                    )


                    # =================================================
                    # 📈 REPORTE VENTAS
                    # =================================================

                    with col1:

                        st.markdown(
                            """
                            <div class="card" style="padding: 30px;">

                                <div class="card-icon">
                                    📈
                                </div>

                                <div class="card-title">
                                    Reporte de Ventas
                                </div>

                                <div class="card-desc">
                                    Análisis detallado de ventas
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Ver Reporte",
                            key="reporte_ventas_btn_vendedor",
                            use_container_width=True
                        ):

                            st.session_state.module = "Reportes_Ventas"

                            st.rerun()


                    # =================================================
                    # 📥 REPORTE COMPRAS
                    # =================================================

                    with col2:

                        st.markdown(
                            """
                            <div class="card" style="padding: 30px;">

                                <div class="card-icon">
                                    📥
                                </div>

                                <div class="card-title">
                                    Reporte de Compras
                                </div>

                                <div class="card-desc">
                                    Análisis detallado de compras
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Ver Reporte de Compras",
                            key="reporte_compras_btn_vendedor",
                            use_container_width=True
                        ):

                            st.session_state.module = "Reportes_Compras"

                            st.rerun()


                    # =================================================
                    # 🏆 PRODUCTOS MÁS / MENOS VENDIDOS
                    # =================================================

                    with col3:

                        st.markdown(
                            """
                            <div class="card" style="padding: 30px;">

                                <div class="card-icon">
                                    🏆
                                </div>

                                <div class="card-title">
                                    Productos más y menos vendidos
                                </div>

                                <div class="card-desc">
                                    Productos más populares
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Ver Ranking",
                            key="top_30_btn_vendedor",
                            use_container_width=True
                        ):

                            st.session_state.module = "productomasvendido"

                            st.rerun()


                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )


        # ============================================================
        # 🔙 BOTÓN PARA VOLVER ATRÁS EN SUBMENÚ
        # ============================================================

        if st.session_state["macro_modulo"]:

            st.markdown("---")

            if st.button(
                "🔙 Volver al menú principal",
                use_container_width=True
            ):

                st.session_state[
                    "macro_modulo"
                ] = None

                st.rerun()


        # ============================================================
        # 🚪 CERRAR SESIÓN
        # ============================================================

        st.markdown("---")

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col2:

            if st.button(
                "🚪 Cerrar sesión",
                use_container_width=True
            ):

                for key in [
                    "logueado",
                    "usuario",
                    "module",
                    "nombre_empleado",
                    "macro_modulo",
                    "nombre_tienda",
                    "nivel_usuario",
                    "id_empleado",
                    "id_tienda"
                ]:

                    if key in st.session_state:

                        del st.session_state[key]

                st.success(
                    "✅ Sesión cerrada correctamente."
                )

                st.rerun()


# ─────────────────────────────────────────────
# 🔄 ROUTER DE MÓDULOS CON VERIFICACIÓN DE ROL
# ─────────────────────────────────────────────

def cargar_modulo():

    # ============================================================
    # 🔐 DATOS DE SESIÓN
    # ============================================================

    rol = st.session_state.get(
        "nivel_usuario",
        ""
    )

    modulo_solicitado = st.session_state.get(
        "module",
        ""
    )


    # ============================================================
    # 👑 MÓDULOS PERMITIDOS PARA ADMINISTRADOR
    # ============================================================

    modulos_permitidos_admin = [

        "Inventario",

        # 🆕 NUEVO MÓDULO
        "ComparativaInv",

        "Reportes_Ventas",

        "productomasvendido",

        "GestionAdmin",

        "Reportes_Compras"
    ]


    # ============================================================
    # 🏠 SI NO HAY MÓDULO → MENÚ PRINCIPAL
    # ============================================================

    if (
        modulo_solicitado == ""
        or modulo_solicitado is None
    ):

        menu_principal()

        return


    # ============================================================
    # ⛔ VERIFICACIÓN DE ACCESO PARA ADMINISTRADOR
    # ============================================================

    if (
        rol == "Administrador"
        and modulo_solicitado
        not in modulos_permitidos_admin
    ):

        st.warning(
            "⚠️ No tienes acceso a este módulo como Administrador."
        )

        st.session_state[
            "macro_modulo"
        ] = None

        if "module" in st.session_state:

            del st.session_state[
                "module"
            ]

        st.rerun()

        return


    # ============================================================
    # 🔀 ROUTER DE MÓDULOS
    # ============================================================

    if st.session_state.module == "Ventas":

        modulo_ventas()


    elif st.session_state.module == "Compras":

        modulo_compras()


    elif st.session_state.module == "Producto":

        modulo_producto()


    elif st.session_state.module == "Editar":

        modulo_editar_producto()


    elif st.session_state.module == "Dashboard":

        dashboard()


    elif st.session_state.module == "Empleado":

        modulo_empleado()


    elif st.session_state.module == "Inventario":

        modulo_inventario()


    # ============================================================
    # 🆕 COMPARATIVA DE COSTOS
    # ============================================================

    elif st.session_state.module == "ComparativaInv":

        modulo_comparativa_inv()


    elif st.session_state.module == "Reportes_Ventas":

        reporte_ventas()


    elif st.session_state.module == "Categoria":

        modulo_categoria()


    elif st.session_state.module == "GestionAdmin":

        modulo_gestion_admin()


    elif st.session_state.module == "productomasvendido":

        modulo_productos_mas_menos_vendidos()


    elif st.session_state.module == "Reportes_Compras":

        modulo_reporte_compras()


    else:

        menu_principal()


# ─────────────────────────────────────────────
# 🟢 MAIN APP
# ─────────────────────────────────────────────

def app():

    if (
        "logueado" not in st.session_state
        or not st.session_state["logueado"]
    ):

        login()

    else:

        cargar_modulo()


if __name__ == "__main__":

    app()
