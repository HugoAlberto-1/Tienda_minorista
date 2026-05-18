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
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # CSS personalizado para mejor apariencia
    st.markdown("""
        <style>
        /* Fondo general */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Tarjetas de los botones */
        .card-button {
            background: white;
            border-radius: 15px;
            padding: 25px 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        
        .card-button:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }
        
        /* Títulos */
        .main-title {
            text-align: center;
            color: white;
            font-size: 3em;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        .subtitle {
            text-align: center;
            color: rgba(255,255,255,0.95);
            font-size: 1.2em;
            margin-bottom: 40px;
        }
        
        .welcome-text {
            text-align: center;
            color: white;
            font-size: 1.4em;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        /* Botones personalizados */
        .stButton > button {
            border-radius: 10px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: scale(1.02);
        }
        
        /* Sección de macro módulos */
        .macro-section {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .macro-title {
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
            text-align: center;
        }
        
        /* Indicador de módulo activo */
        .active-module {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)


def mostrar_tarjeta(icono, titulo, descripcion, key):
    """Función para crear tarjetas modernas"""
    return st.markdown(f"""
        <div style="
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            height: 100%;
        ">
            <div style="font-size: 3em; margin-bottom: 10px;">{icono}</div>
            <div style="font-size: 1.2em; font-weight: bold; margin-bottom: 10px;">{titulo}</div>
            <div style="color: #666; font-size: 0.9em;">{descripcion}</div>
        </div>
    """, unsafe_allow_html=True)


def menu_principal():
    configurar_pagina()
    
    # Contenedor principal con fondo degradado
    with st.container():
        # Título principal
        st.markdown('<div class="main-title">📦 Sistema de Inventario</div>', unsafe_allow_html=True)
        
        # Mensaje de bienvenida personalizado
        nombre_empleado = st.session_state.get("nombre_empleado", "Usuario")
        st.markdown(f'<div class="welcome-text">✨ ¡Bienvenida, {nombre_empleado}! ✨</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Gestiona tu negocio de manera eficiente</div>', unsafe_allow_html=True)

        if "macro_modulo" not in st.session_state:
            st.session_state["macro_modulo"] = None

        # Mostrar solo los macro módulos
        if st.session_state["macro_modulo"] is None:
            st.markdown("### 🎯 ¿Qué deseas hacer?")
            
            # Tarjetas principales con 2 columnas y luego 2 filas
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                # Tarjeta de Registro
                with st.container():
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    border-radius: 20px; padding: 30px; text-align: center; cursor: pointer;">
                            <div style="font-size: 4em;">✏️</div>
                            <div style="font-size: 1.5em; font-weight: bold; color: white; margin: 15px 0;">
                                Ingresa nueva información
                            </div>
                            <div style="color: rgba(255,255,255,0.9);">
                                Registra productos, empleados y categorías
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📝 Ingresa nueva información", key="btn_registro", use_container_width=True):
                        st.session_state["macro_modulo"] = "registro"
                        st.rerun()
            
            with col2:
                # Tarjeta de Transacciones
                with st.container():
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                    border-radius: 20px; padding: 30px; text-align: center;">
                            <div style="font-size: 4em;">💸</div>
                            <div style="font-size: 1.5em; font-weight: bold; color: white; margin: 15px 0;">
                                Compra y vende productos
                            </div>
                            <div style="color: rgba(255,255,255,0.9);">
                                Registra tus compras y ventas diarias
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🛒 Compra y vende productos", key="btn_transacciones", use_container_width=True):
                        st.session_state["macro_modulo"] = "transacciones"
                        st.rerun()
            
            # Segunda fila
            col3, col4 = st.columns(2, gap="large")
            
            with col3:
                # Tarjeta de Inventario
                with st.container():
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                                    border-radius: 20px; padding: 30px; text-align: center;">
                            <div style="font-size: 4em;">📋</div>
                            <div style="font-size: 1.5em; font-weight: bold; color: white; margin: 15px 0;">
                                Consulta tu inventario
                            </div>
                            <div style="color: rgba(255,255,255,0.9);">
                                Visualiza el stock actual de productos
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📊 Ver inventario", key="btn_inventario", use_container_width=True):
                        st.session_state.module = "Inventario"
                        st.rerun()
            
            with col4:
                # Tarjeta de Reportes
                with st.container():
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                                    border-radius: 20px; padding: 30px; text-align: center;">
                            <div style="font-size: 4em;">📊</div>
                            <div style="font-size: 1.5em; font-weight: bold; color: white; margin: 15px 0;">
                                Consulta tus reportes
                            </div>
                            <div style="color: rgba(255,255,255,0.9);">
                                Analiza ventas y productos más vendidos
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📈 Ver reportes", key="btn_reportes", use_container_width=True):
                        st.session_state["macro_modulo"] = "reportes"
                        st.rerun()

        # Submenús según macro módulo
        elif st.session_state["macro_modulo"] == "registro":
            with st.container():
                st.markdown('<div class="macro-section">', unsafe_allow_html=True)
                st.markdown('<div class="macro-title">✏️ Registra información</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("📦 Nuevo Producto", use_container_width=True):
                        st.session_state.module = "Producto"
                        st.rerun()
                    st.caption("Registra productos en el sistema")
                
                with col2:
                    if st.button("✏️ Editar Producto", use_container_width=True):
                        st.session_state.module = "Editar"
                        st.rerun()
                    st.caption("Modifica información de productos")
                
                with col3:
                    if st.button("👩‍💼 Nueva Empleada", use_container_width=True):
                        st.session_state.module = "Empleado"
                        st.rerun()
                    st.caption("Registra nuevas empleadas")
                
                with col4:
                    if st.button("📁 Gestionar Categorías", use_container_width=True):
                        st.session_state.module = "Categoria"
                        st.rerun()
                    st.caption("Administra categorías de productos")
                
                st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state["macro_modulo"] == "transacciones":
            with st.container():
                st.markdown('<div class="macro-section">', unsafe_allow_html=True)
                st.markdown('<div class="macro-title">💸 Haz una compra o una venta</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2, gap="large")
                
                with col1:
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                    border-radius: 15px; padding: 30px; text-align: center;">
                            <div style="font-size: 3em;">🛒</div>
                            <div style="font-size: 1.3em; font-weight: bold; color: white; margin: 10px 0;">
                                Realizar Venta
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Iniciar Venta", key="venta_btn", use_container_width=True):
                        st.session_state.module = "Ventas"
                        st.rerun()
                
                with col2:
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                                    border-radius: 15px; padding: 30px; text-align: center;">
                            <div style="font-size: 3em;">📥</div>
                            <div style="font-size: 1.3em; font-weight: bold; color: white; margin: 10px 0;">
                                Realizar Compra
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Iniciar Compra", key="compra_btn", use_container_width=True):
                        st.session_state.module = "Compras"
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state["macro_modulo"] == "reportes":
            with st.container():
                st.markdown('<div class="macro-section">', unsafe_allow_html=True)
                st.markdown('<div class="macro-title">📊 Consulta tus reportes</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2, gap="large")
                
                with col1:
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                                    border-radius: 15px; padding: 30px; text-align: center;">
                            <div style="font-size: 3em;">📈</div>
                            <div style="font-size: 1.3em; font-weight: bold; color: white; margin: 10px 0;">
                                Reporte de Ventas
                            </div>
                            <div style="color: white;">Análisis detallado de ventas</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Ver Reporte", key="reporte_ventas_btn", use_container_width=True):
                        st.session_state.module = "Reportes_Ventas"
                        st.rerun()
                
                with col2:
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                                    border-radius: 15px; padding: 30px; text-align: center;">
                            <div style="font-size: 3em;">🏆</div>
                            <div style="font-size: 1.3em; font-weight: bold; color: white; margin: 10px 0;">
                                Top 30 más vendidos
                            </div>
                            <div style="color: white;">Productos más populares</div>
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

        # Botón cerrar sesión (al final, más discreto)
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚪 Cerrar sesión", use_container_width=True):
                for key in ['logueado', 'usuario', 'module', 'nombre_empleado', 'macro_modulo']: 
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("✅ Sesión cerrada correctamente.")
                st.rerun()


# ─────────────────────────────────────────────
# 🔄 ROUTER DE MÓDULOS
# ─────────────────────────────────────────────
def cargar_modulo():
    if "module" in st.session_state:
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
