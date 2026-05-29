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


def configurar_pagina():
    """Configuración de la página con CSS personalizado"""
    st.set_page_config(
        page_title="Sistema de Inventario",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Paleta de colores corporativos (azul corporativo)
    COLOR_PRIMARY = "#1e3a5f"      # Azul oscuro principal
    COLOR_SECONDARY = "#2c5f8a"    # Azul medio
    COLOR_ACCENT = "#3a7ca5"       # Azul claro
    COLOR_BG = "#f5f7fa"           # Fondo gris muy claro
    COLOR_CARD = "#ffffff"          # Blanco para tarjetas
    COLOR_TEXT = "#333333"          # Texto oscuro
    COLOR_TEXT_LIGHT = "#666666"    # Texto gris
    COLOR_HOVER = "#e8f0fe"         # Hover suave
    
    # CSS personalizado
    st.markdown(f"""
        <style>
        /* Fondo general */
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        /* Títulos */
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
        
        /* Tarjetas */
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
        
        /* Tarjetas grandes para macro-módulos */
        .macro-card {{
            background: {COLOR_CARD};
            border-radius: 12px;
            padding: 25px 20px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
            cursor: pointer;
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
        
        /* Sección de submenú */
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
        
        /* Botones */
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
        
        /* Títulos de sección */
        .section-header {{
            text-align: center;
            margin-bottom: 25px;
        }}
        </style>
    """, unsafe_allow_html=True)


def menu_principal():
    configurar_pagina()
    
    with st.container():
        # 🔐 OBTENER EL ROL DEL USUARIO
        rol_usuario = st.session_state.get("nivel_usuario", "")
        nombre_tienda = st.session_state.get("nombre_tienda", "Tienda Minorista")
        nombre_empleado = st.session_state.get("nombre_empleado", "Usuario")
        
        # Título principal con el nombre de la tienda
        st.markdown(f'<div class="main-title">🛒 {nombre_tienda}</div>', unsafe_allow_html=True)
        
        # Mensaje de bienvenida con el rol incluido
        st.markdown(f'<div class="welcome-text">✨ Bienvenida, {nombre_empleado} ✨<br><small style="font-size:0.8rem;">Rol: {rol_usuario}</small></div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Gestiona tu negocio de manera eficiente</div>', unsafe_allow_html=True)

        if "macro_modulo" not in st.session_state:
            st.session_state["macro_modulo"] = None

        # ============================================================
        # 👑 MENÚ PARA ADMINISTRADOR (SOLO INVENTARIO Y REPORTES)
        # ============================================================
        if rol_usuario == "Administrador":
            
            if st.session_state["macro_modulo"] is None:
                # Mostrar solo dos opciones: Inventario y Reportes
                col1, col2 = st.columns(2, gap="large")
                
                with col1:
                    st.markdown(f"""
                        <div class="macro-card">
                            <div class="macro-icon">📋</div>
                            <div class="macro-title">Consulta tu inventario</div>
                            <div class="macro-desc">Visualiza el stock actual de productos</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("📊 Ver inventario", key="btn_inventario_admin", use_container_width=True):
                        st.session_state.module = "Inventario"
                        st.rerun()
                
                with col2:
                    st.markdown(f"""
                        <div class="macro-card">
                            <div class="macro-icon">📊</div>
                            <div class="macro-title">Consulta tus reportes</div>
                            <div class="macro-desc">Analiza ventas y productos más vendidos</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("📈 Ver reportes", key="btn_reportes_admin", use_container_width=True):
                        st.session_state["macro_modulo"] = "reportes"
                        st.rerun()
            
            elif st.session_state["macro_modulo"] == "reportes":
                with st.container():
                    st.markdown(f'<div style="text-align: center;"><span class="section-title">📊 Consulta tus reportes</span></div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2, gap="large")
                    
                    with col1:
                        st.markdown(f"""
                            <div class="card" style="padding: 30px;">
                                <div class="card-icon">📈</div>
                                <div class="card-title">Reporte de Ventas</div>
                                <div class="card-desc">Análisis detallado de ventas</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Ver Reporte", key="reporte_ventas_btn", use_container_width=True):
                            st.session_state.module = "Reportes_Ventas"
                            st.rerun()
                    
                    with col2:
                        st.markdown(f"""
                            <div class="card" style="padding: 30px;">
                                <div class="card-icon">🏆</div>
                                <div class="card-title">Top 30 más vendidos</div>
                                <div class="card-desc">Productos más populares</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Ver Ranking", key="top_30_btn", use_container_width=True):
                            st.session_state.module = "productomasvendido"
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)

        # ============================================================
        # 👩‍💼 MENÚ PARA VENDEDOR (TODOS LOS MÓDULOS ORIGINALES)
        # ============================================================
        else:  # Vendedor o cualquier otro rol no administrador
            
            # Mostrar solo los macro módulos originales
            if st.session_state["macro_modulo"] is None:
                col1, col2 = st.columns(2, gap="large")
                
                with col1:
                    # Tarjeta de Registro
                    st.markdown(f"""
                        <div class="macro-card">
                            <div class="macro-icon">✏️</div>
                            <div class="macro-title">Ingresa nueva información</div>
                            <div class="macro-desc">Registra productos, empleados y categorías</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("📝 Ingresar información", key="btn_registro", use_container_width=True):
                        st.session_state["macro_modulo"] = "registro"
                        st.rerun()
                
                with col2:
                    # Tarjeta de Transacciones
                    st.markdown(f"""
                        <div class="macro-card">
                            <div class="macro-icon">💸</div>
                            <div class="macro-title">Compra y vende productos</div>
                            <div class="macro-desc">Registra tus compras y ventas diarias</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("🛒 Comprar/Vender", key="btn_transacciones", use_container_width=True):
                        st.session_state["macro_modulo"] = "transacciones"
                        st.rerun()
                
                # Segunda fila
                col3, col4 = st.columns(2, gap="large")
                
                with col3:
                    # Tarjeta de Inventario
                    st.markdown(f"""
                        <div class="macro-card">
                            <div class="macro-icon">📋</div>
                            <div class="macro-title">Consulta tu inventario</div>
                            <div class="macro-desc">Visualiza el stock actual de productos</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("📊 Ver inventario", key="btn_inventario", use_container_width=True):
                        st.session_state.module = "Inventario"
                        st.rerun()
                
                with col4:
                    # Tarjeta de Reportes
                    st.markdown(f"""
                        <div class="macro-card">
                            <div class="macro-icon">📊</div>
                            <div class="macro-title">Consulta tus reportes</div>
                            <div class="macro-desc">Analiza ventas y productos más vendidos</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("📈 Ver reportes", key="btn_reportes", use_container_width=True):
                        st.session_state["macro_modulo"] = "reportes"
                        st.rerun()

            # Submenús según macro módulo (solo para vendedor)
            elif st.session_state["macro_modulo"] == "registro":
                with st.container():
                    st.markdown(f'<div style="text-align: center;"><span class="section-title">✏️ Registra información</span></div>', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                            <div class="card">
                                <div class="card-icon">📦</div>
                                <div class="card-title">Nuevo Producto</div>
                                <div class="card-desc">Registra productos en el sistema</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Agregar", key="btn_producto", use_container_width=True):
                            st.session_state.module = "Producto"
                            st.rerun()
                    
                    with col2:
                        st.markdown(f"""
                            <div class="card">
                                <div class="card-icon">✏️</div>
                                <div class="card-title">Editar Producto</div>
                                <div class="card-desc">Modifica información de productos</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Editar", key="btn_editar", use_container_width=True):
                            st.session_state.module = "Editar"
                            st.rerun()
                    
                    with col3:
                        st.markdown(f"""
                            <div class="card">
                                <div class="card-icon">👩‍💼</div>
                                <div class="card-title">Nueva Socia</div>
                                <div class="card-desc">Registra nuevas usuarias</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Registrar", key="btn_empleado", use_container_width=True):
                            st.session_state.module = "Empleado"
                            st.rerun()
                    
                    with col4:
                        st.markdown(f"""
                            <div class="card">
                                <div class="card-icon">📁</div>
                                <div class="card-title">Gestionar Categorías</div>
                                <div class="card-desc">Administra categorías de productos</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Gestionar", key="btn_categoria", use_container_width=True):
                            st.session_state.module = "Categoria"
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)

            elif st.session_state["macro_modulo"] == "transacciones":
                with st.container():
                    st.markdown(f'<div style="text-align: center;"><span class="section-title">💸 Haz una compra o una venta</span></div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2, gap="large")
                    
                    with col1:
                        st.markdown(f"""
                            <div class="card" style="padding: 30px;">
                                <div class="card-icon">🛒</div>
                                <div class="card-title">Realizar Venta</div>
                                <div class="card-desc">Registra una nueva venta de productos</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Iniciar Venta", key="venta_btn", use_container_width=True):
                            st.session_state.module = "Ventas"
                            st.rerun()
                    
                    with col2:
                        st.markdown(f"""
                            <div class="card" style="padding: 30px;">
                                <div class="card-icon">📥</div>
                                <div class="card-title">Realizar Compra</div>
                                <div class="card-desc">Registra una nueva compra de productos</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Iniciar Compra", key="compra_btn", use_container_width=True):
                            st.session_state.module = "Compras"
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)

            elif st.session_state["macro_modulo"] == "reportes":
                with st.container():
                    st.markdown(f'<div style="text-align: center;"><span class="section-title">📊 Consulta tus reportes</span></div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2, gap="large")
                    
                    with col1:
                        st.markdown(f"""
                            <div class="card" style="padding: 30px;">
                                <div class="card-icon">📈</div>
                                <div class="card-title">Reporte de Ventas</div>
                                <div class="card-desc">Análisis detallado de ventas</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Ver Reporte", key="reporte_ventas_btn", use_container_width=True):
                            st.session_state.module = "Reportes_Ventas"
                            st.rerun()
                    
                    with col2:
                        st.markdown(f"""
                            <div class="card" style="padding: 30px;">
                                <div class="card-icon">🏆</div>
                                <div class="card-title">Top 30 más vendidos</div>
                                <div class="card-desc">Productos más populares</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Ver Ranking", key="top_30_btn", use_container_width=True):
                            st.session_state.module = "productomasvendido"
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)

        # Botón para volver atrás en submenú
        if st.session_state["macro_modulo"]:
            st.markdown("---")
            if st.button("🔙 Volver al menú principal", use_container_width=True):
                st.session_state["macro_modulo"] = None
                st.rerun()

        # Botón cerrar sesión
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚪 Cerrar sesión", use_container_width=True):
                for key in ['logueado', 'usuario', 'module', 'nombre_empleado', 'macro_modulo', 'nombre_tienda', 'nivel_usuario', 'id_empleado', 'id_tienda']: 
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("✅ Sesión cerrada correctamente.")
                st.rerun()


# ─────────────────────────────────────────────
# 🔄 ROUTER DE MÓDULOS CON VERIFICACIÓN DE ROL (CORREGIDO)
# ─────────────────────────────────────────────
def cargar_modulo():
    # 🔐 Verificar si el usuario tiene acceso al módulo solicitado
    rol = st.session_state.get("nivel_usuario", "")
    modulo_solicitado = st.session_state.get("module", "")
    
    # Módulos permitidos para Administrador
    modulos_permitidos_admin = ["Inventario", "Reportes_Ventas", "productomasvendido"]
    
    # 🔥 CORRECCIÓN: Si no hay módulo seleccionado, mostrar menú principal
    if modulo_solicitado == "" or modulo_solicitado is None:
        menu_principal()
        return
    
    # Si es Administrador y el módulo no está permitido, mostrar error y volver
    if rol == "Administrador" and modulo_solicitado not in modulos_permitidos_admin:
        st.warning("⚠️ No tienes acceso a este módulo como Administrador.")
        st.session_state["macro_modulo"] = None
        if "module" in st.session_state:
            del st.session_state["module"]
        st.rerun()
        return
    
    # Cargar el módulo correspondiente
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
    elif st.session_state.module == "Reportes_Ventas":
        reporte_ventas()
    elif st.session_state.module == "Categoria":
        modulo_categoria()
    else:
        menu_principal()


# ─────────────────────────────────────────────
# 🟢 MAIN APP
# ─────────────────────────────────────────────
def app():
    if "logueado" not in st.session_state or not st.session_state["logueado"]:
        login()
    else:
        cargar_modulo()


if __name__ == "__main__":
    app()
