import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "modulos"))

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
from modulos.comparativa_inv import modulo_comparativa_precios
from modulos.pronosticos import modulo_pronosticos


# ============================================================
# 🎨 CONFIGURACIÓN GENERAL DE LA PÁGINA
# ============================================================

def configurar_pagina():

    st.set_page_config(
        page_title="Sistema de Inventario",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_ACCENT = "#3a7ca5"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT_LIGHT = "#666666"
    COLOR_HOVER = "#e8f0fe"

    st.markdown(
        f"""
        <style>

        .stApp {{
            background-color: {COLOR_BG};
        }}

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

        .macro-card {{
            background: {COLOR_CARD};
            border-radius: 12px;
            padding: 25px 20px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
            min-height: 145px;
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

        .card {{
            background: {COLOR_CARD};
            border-radius: 12px;
            padding: 20px 15px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
            min-height: 160px;
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

        .section-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 2px solid {COLOR_ACCENT};
            padding-bottom: 10px;
            display: inline-block;
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

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 🧩 FUNCIONES AUXILIARES PARA TARJETAS
# ============================================================

def mostrar_macro_tarjeta(icono, titulo, descripcion):
    """
    Muestra una tarjeta grande del menú principal.

    El HTML se construye en una sola línea para evitar
    que Streamlit lo interprete como bloque de código.
    """

    html = (
        '<div class="macro-card">'
        f'<div class="macro-icon">{icono}</div>'
        f'<div class="macro-title">{titulo}</div>'
        f'<div class="macro-desc">{descripcion}</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def mostrar_tarjeta(icono, titulo, descripcion):
    """
    Muestra una tarjeta de los submenús.
    """

    html = (
        '<div class="card">'
        f'<div class="card-icon">{icono}</div>'
        f'<div class="card-title">{titulo}</div>'
        f'<div class="card-desc">{descripcion}</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def mostrar_titulo_seccion(texto):
    """
    Título centrado para los submenús.
    """

    html = (
        '<div style="text-align:center;">'
        f'<span class="section-title">{texto}</span>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ============================================================
# 🏠 MENÚ PRINCIPAL
# ============================================================

def menu_principal():

    configurar_pagina()

    with st.container():

        # ============================================================
        # DATOS DEL USUARIO
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
        # ENCABEZADO
        # ============================================================

        st.markdown(
            f'<div class="main-title">🛒 {nombre_tienda}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="welcome-text">✨ Bienvenida, {nombre_empleado} ✨</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">Gestiona tu negocio de manera eficiente</div>',
            unsafe_allow_html=True
        )


        # ============================================================
        # INICIALIZAR MACRO MÓDULO
        # ============================================================

        if "macro_modulo" not in st.session_state:
            st.session_state["macro_modulo"] = None


        # ============================================================
        # 👑 MENÚ ADMINISTRADOR
        # ============================================================

        if rol_usuario == "Administrador":

            # ========================================================
            # PANEL PRINCIPAL ADMIN
            # ========================================================

            if st.session_state["macro_modulo"] is None:

                st.info("👑 Panel de Administrador")


                # ====================================================
                # PRIMERA FILA
                # Inventario + Comparativa
                # ====================================================

                col1, col2, col_pron = st.columns(
                    3,
                    gap="large"
                )


                # ----------------------------------------------------
                # INVENTARIO GLOBAL
                # ----------------------------------------------------

                with col1:

                    mostrar_macro_tarjeta(
                        "📦",
                        "Inventario Global",
                        "Ver inventario de todas las tiendas"
                    )

                    if st.button(
                        "📊 Ver inventario",
                        key="btn_inventario_admin",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Inventario"
                        st.rerun()


                # ----------------------------------------------------
                # COMPARATIVA DE COSTOS
                # ----------------------------------------------------

                with col2:

                    mostrar_macro_tarjeta(
                        "💰",
                        "Comparativa de Costos",
                        "Comparar precios unitarios entre tiendas"
                    )

                    if st.button(
                        "💲 Ver comparativa",
                        key="btn_comparativa_inv_admin",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "ComparativaInv"
                        st.rerun()


                # ----------------------------------------------------
                # PRONÓSTICOS Y PUNTO DE REORDEN
                # ----------------------------------------------------

                with col_pron:

                    mostrar_macro_tarjeta(
                        "📈",
                        "Pronósticos y Reorden",
                        "Rotación, cobertura, alertas y compras sugeridas"
                    )

                    if st.button(
                        "📦 Ver pronósticos",
                        key="btn_pronosticos_admin",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Pronosticos"
                        st.rerun()


                # Separación entre filas
                st.markdown("<br>", unsafe_allow_html=True)


                # ====================================================
                # SEGUNDA FILA
                # Administración + Reportes
                # ====================================================

                col3, col4, col5 = st.columns(
                    3,
                    gap="large"
                )


                # ----------------------------------------------------
                # ADMINISTRACIÓN
                # ----------------------------------------------------

                with col3:

                    mostrar_macro_tarjeta(
                        "👑",
                        "Administración",
                        "Gestionar tiendas y usuarios"
                    )

                    if st.button(
                        "⚙️ Gestionar",
                        key="btn_gestion_admin",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "GestionAdmin"
                        st.rerun()


                # ----------------------------------------------------
                # REPORTES GLOBALES
                # ----------------------------------------------------

                with col4:

                    mostrar_macro_tarjeta(
                        "📊",
                        "Reportes Globales",
                        "Reportes de ventas de todas las tiendas"
                    )

                    if st.button(
                        "📈 Ver reportes",
                        key="btn_reportes_admin",
                        use_container_width=True
                    ):

                        st.session_state["macro_modulo"] = "reportes"
                        st.rerun()

            
            # ========================================================
            # REPORTES ADMINISTRADOR
            # ========================================================

            elif st.session_state["macro_modulo"] == "reportes":

                mostrar_titulo_seccion(
                    "📊 Consulta tus reportes"
                )

                col1, col2, col3 = st.columns(
                    3,
                    gap="large"
                )


                # ----------------------------------------------------
                # REPORTE VENTAS
                # ----------------------------------------------------

                with col1:

                    mostrar_tarjeta(
                        "📈",
                        "Reporte de Ventas",
                        "Análisis detallado de ventas"
                    )

                    if st.button(
                        "Ver Reporte",
                        key="reporte_ventas_btn",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Reportes_Ventas"
                        st.rerun()


                # ----------------------------------------------------
                # REPORTE COMPRAS
                # ----------------------------------------------------

                with col2:

                    mostrar_tarjeta(
                        "📥",
                        "Reporte de Compras",
                        "Análisis detallado de compras"
                    )

                    if st.button(
                        "Ver Reporte de Compras",
                        key="reporte_compras_btn",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Reportes_Compras"
                        st.rerun()


                # ----------------------------------------------------
                # PRODUCTOS MÁS / MENOS VENDIDOS
                # ----------------------------------------------------

                with col3:

                    mostrar_tarjeta(
                        "🏆",
                        "Productos más y menos vendidos",
                        "Productos más populares"
                    )

                    if st.button(
                        "Ver Ranking",
                        key="top_30_btn",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "productomasvendido"
                        st.rerun()

            elif st.session_state["macro_modulo"] == "transacciones":
        
                mostrar_titulo_seccion(
                            "💸 Haz una compra o una venta"
                        )
        
                    col1, col2 = st.columns(
                            2,
                            gap="large"
                        )
        
        
                        # ----------------------------------------------------
                        # VENTA
                        # ----------------------------------------------------
        
                 with col1:
        
                    mostrar_tarjeta(
                                "🛒",
                                "Realizar Venta",
                                "Registra una nueva venta de productos"
                            )
        
                            if st.button(
                                "Iniciar Venta",
                                key="venta_btn",
                                use_container_width=True
                            ):
        
                                st.session_state["module"] = "Ventas"
                                st.rerun()
        
        
                        # ----------------------------------------------------
                        # COMPRA
                        # ----------------------------------------------------
        
                 with col2:
        
                      mostrar_tarjeta(
                                "📥",
                                "Realizar Compra",
                                "Registra una nueva compra de productos"
                            )
        
                            if st.button(
                                "Iniciar Compra",
                                key="compra_btn",
                                use_container_width=True
                            ):
        
                                st.session_state["module"] = "Compras"
                                st.rerun()

        # ============================================================
        # 👩‍💼 MENÚ VENDEDOR
        # ============================================================

        else:

            # ========================================================
            # PANEL PRINCIPAL VENDEDOR
            # ========================================================

            if st.session_state["macro_modulo"] is None:

                # ====================================================
                # PRIMERA FILA
                # ====================================================

                col1, col2 = st.columns(
                    2,
                    gap="large"
                )


                # ----------------------------------------------------
                # INGRESAR INFORMACIÓN
                # ----------------------------------------------------

                with col1:

                    mostrar_macro_tarjeta(
                        "✏️",
                        "Ingresa nueva información",
                        "Registra productos, empleados y categorías"
                    )

                    if st.button(
                        "📝 Ingresar información",
                        key="btn_registro",
                        use_container_width=True
                    ):

                        st.session_state["macro_modulo"] = "registro"
                        st.rerun()


                # ----------------------------------------------------
                # TRANSACCIONES
                # ----------------------------------------------------

                with col2:

                    mostrar_macro_tarjeta(
                        "💸",
                        "Compra y vende productos",
                        "Registra tus compras y ventas diarias"
                    )

                    if st.button(
                        "🛒 Comprar/Vender",
                        key="btn_transacciones",
                        use_container_width=True
                    ):

                        st.session_state["macro_modulo"] = "transacciones"
                        st.rerun()


                # ====================================================
                # SEGUNDA FILA
                # ====================================================

                col3, col4 = st.columns(
                    2,
                    gap="large"
                )


                # ----------------------------------------------------
                # INVENTARIO
                # ----------------------------------------------------

                with col3:

                    mostrar_macro_tarjeta(
                        "📋",
                        "Consulta tu inventario",
                        "Visualiza el stock actual de productos"
                    )

                    if st.button(
                        "📊 Ver inventario",
                        key="btn_inventario",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Inventario"
                        st.rerun()


                # ----------------------------------------------------
                # REPORTES
                # ----------------------------------------------------

                with col4:

                    mostrar_macro_tarjeta(
                        "📊",
                        "Consulta tus reportes",
                        "Analiza ventas y productos más vendidos"
                    )

                    if st.button(
                        "📈 Ver reportes",
                        key="btn_reportes",
                        use_container_width=True
                    ):

                        st.session_state["macro_modulo"] = "reportes"
                        st.rerun()


                # ----------------------------------------------------
                # PRONÓSTICOS Y PUNTO DE REORDEN
                # ----------------------------------------------------

                with col5:

                    mostrar_macro_tarjeta(
                        "📈",
                        "Pronósticos y Reorden",
                        "Rotación, cobertura, alertas y compras sugeridas"
                    )

                    if st.button(
                        "📦 Ver pronósticos",
                        key="btn_pronosticos_vendedor",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Pronosticos"
                        st.rerun()


            # ========================================================
            # SUBMENÚ REGISTRO
            # ========================================================

            elif st.session_state["macro_modulo"] == "registro":

                mostrar_titulo_seccion(
                    "✏️ Registra información"
                )

                col1, col2, col3, col4 = st.columns(4)


                # ----------------------------------------------------
                # PRODUCTO
                # ----------------------------------------------------

                with col1:

                    mostrar_tarjeta(
                        "📦",
                        "Nuevo Producto",
                        "Registra productos en el sistema"
                    )

                    if st.button(
                        "Agregar",
                        key="btn_producto",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Producto"
                        st.rerun()


                # ----------------------------------------------------
                # EDITAR PRODUCTO
                # ----------------------------------------------------

                with col2:

                    mostrar_tarjeta(
                        "✏️",
                        "Editar Producto",
                        "Modifica información de productos"
                    )

                    if st.button(
                        "Editar",
                        key="btn_editar",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Editar"
                        st.rerun()


                # ----------------------------------------------------
                # EMPLEADO
                # ----------------------------------------------------

                with col3:

                    mostrar_tarjeta(
                        "👩‍💼",
                        "Nueva Socia",
                        "Registra nuevas usuarias"
                    )

                    if st.button(
                        "Registrar",
                        key="btn_empleado",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Empleado"
                        st.rerun()


                # ----------------------------------------------------
                # CATEGORÍAS
                # ----------------------------------------------------

                with col4:

                    mostrar_tarjeta(
                        "📁",
                        "Gestionar Categorías",
                        "Administra categorías de productos"
                    )

                    if st.button(
                        "Gestionar",
                        key="btn_categoria",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Categoria"
                        st.rerun()


            # ========================================================
            # SUBMENÚ TRANSACCIONES
            # ========================================================

            elif st.session_state["macro_modulo"] == "transacciones":

                mostrar_titulo_seccion(
                    "💸 Haz una compra o una venta"
                )

                col1, col2 = st.columns(
                    2,
                    gap="large"
                )


                # ----------------------------------------------------
                # VENTA
                # ----------------------------------------------------

                with col1:

                    mostrar_tarjeta(
                        "🛒",
                        "Realizar Venta",
                        "Registra una nueva venta de productos"
                    )

                    if st.button(
                        "Iniciar Venta",
                        key="venta_btn",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Ventas"
                        st.rerun()


                # ----------------------------------------------------
                # COMPRA
                # ----------------------------------------------------

                with col2:

                    mostrar_tarjeta(
                        "📥",
                        "Realizar Compra",
                        "Registra una nueva compra de productos"
                    )

                    if st.button(
                        "Iniciar Compra",
                        key="compra_btn",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Compras"
                        st.rerun()


            # ========================================================
            # SUBMENÚ REPORTES
            # ========================================================

            elif st.session_state["macro_modulo"] == "reportes":

                mostrar_titulo_seccion(
                    "📊 Consulta tus reportes"
                )

                col1, col2, col3 = st.columns(
                    3,
                    gap="large"
                )


                # ----------------------------------------------------
                # REPORTE VENTAS
                # ----------------------------------------------------

                with col1:

                    mostrar_tarjeta(
                        "📈",
                        "Reporte de Ventas",
                        "Análisis detallado de ventas"
                    )

                    if st.button(
                        "Ver Reporte",
                        key="reporte_ventas_btn_vendedor",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Reportes_Ventas"
                        st.rerun()


                # ----------------------------------------------------
                # REPORTE COMPRAS
                # ----------------------------------------------------

                with col2:

                    mostrar_tarjeta(
                        "📥",
                        "Reporte de Compras",
                        "Análisis detallado de compras"
                    )

                    if st.button(
                        "Ver Reporte de Compras",
                        key="reporte_compras_btn_vendedor",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "Reportes_Compras"
                        st.rerun()


                # ----------------------------------------------------
                # RANKING
                # ----------------------------------------------------

                with col3:

                    mostrar_tarjeta(
                        "🏆",
                        "Productos más y menos vendidos",
                        "Productos más populares"
                    )

                    if st.button(
                        "Ver Ranking",
                        key="top_30_btn_vendedor",
                        use_container_width=True
                    ):

                        st.session_state["module"] = "productomasvendido"
                        st.rerun()


        # ============================================================
        # 🔙 BOTÓN VOLVER DE LOS SUBMENÚS
        # ============================================================

        if st.session_state["macro_modulo"]:

            st.markdown("---")

            if st.button(
                "🔙 Volver al menú principal",
                use_container_width=True
            ):

                st.session_state["macro_modulo"] = None
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

                claves_sesion = [
                    "logueado",
                    "usuario",
                    "module",
                    "nombre_empleado",
                    "macro_modulo",
                    "nombre_tienda",
                    "nivel_usuario",
                    "id_empleado",
                    "id_tienda"
                ]

                for key in claves_sesion:

                    if key in st.session_state:
                        del st.session_state[key]

                st.success(
                    "✅ Sesión cerrada correctamente."
                )

                st.rerun()


# ============================================================
# 🔄 ROUTER DE MÓDULOS
# ============================================================

def cargar_modulo():

    rol = st.session_state.get(
        "nivel_usuario",
        ""
    )

    modulo_solicitado = st.session_state.get(
        "module",
        ""
    )


    # ============================================================
    # MÓDULOS PERMITIDOS PARA ADMINISTRADOR
    # ============================================================

    modulos_permitidos_admin = [
        "Inventario",
        "ComparativaInv",
        "Reportes_Ventas",
        "productomasvendido",
        "GestionAdmin",
        "Reportes_Compras",
        "Pronosticos",
        "Compras",
        "Ventas"
    ]


    # ============================================================
    # SI NO HAY MÓDULO → MENÚ PRINCIPAL
    # ============================================================

    if modulo_solicitado == "" or modulo_solicitado is None:

        menu_principal()
        return


    # ============================================================
    # SEGURIDAD ADMINISTRADOR
    # ============================================================

    if (
        rol == "Administrador"
        and modulo_solicitado not in modulos_permitidos_admin
    ):

        st.warning(
            "⚠️ No tienes acceso a este módulo como Administrador."
        )

        st.session_state["macro_modulo"] = None

        if "module" in st.session_state:
            del st.session_state["module"]

        st.rerun()
        return


    # ============================================================
    # ROUTER
    # ============================================================

    if modulo_solicitado == "Ventas":

        modulo_ventas()


    elif modulo_solicitado == "Compras":

        modulo_compras()


    elif modulo_solicitado == "Producto":

        modulo_producto()


    elif modulo_solicitado == "Editar":

        modulo_editar_producto()


    elif modulo_solicitado == "Dashboard":

        dashboard()


    elif modulo_solicitado == "Empleado":

        modulo_empleado()


    elif modulo_solicitado == "Inventario":

        modulo_inventario()


    elif modulo_solicitado == "ComparativaInv":

        modulo_comparativa_precios()


    elif modulo_solicitado == "Reportes_Ventas":

        reporte_ventas()


    elif modulo_solicitado == "Categoria":

        modulo_categoria()


    elif modulo_solicitado == "GestionAdmin":

        modulo_gestion_admin()


    elif modulo_solicitado == "productomasvendido":

        modulo_productos_mas_menos_vendidos()


    elif modulo_solicitado == "Reportes_Compras":

        modulo_reporte_compras()


    elif modulo_solicitado == "Pronosticos":

        modulo_pronosticos()


    else:

        st.session_state["module"] = None
        menu_principal()


# ============================================================
# 🟢 MAIN APP
# ============================================================

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
