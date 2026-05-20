import streamlit as st
from config.conexion import obtener_conexion

def configurar_pagina_login():
    """Configuración de la página con CSS personalizado para el login"""
    st.set_page_config(
        page_title="Sistema de Inventario - Login",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Paleta de colores corporativos
    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_LIGHT = "#666666"
    COLOR_BORDER = "#e0e0e0"
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        header {{
            display: none;
        }}
        
        /* Campos de entrada */
        .stTextInput > div > div > input {{
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
            padding: 10px 15px;
            background-color: {COLOR_CARD};
            color: {COLOR_TEXT};
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLOR_PRIMARY};
            box-shadow: 0 0 0 2px rgba(30,58,95,0.1);
        }}
        
        /* Botón */
        .stButton > button {{
            width: 100%;
            padding: 12px;
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY};
        }}
        
        /* Checkbox */
        .stCheckbox label {{
            color: {COLOR_TEXT_LIGHT};
        }}
        </style>
    """, unsafe_allow_html=True)


def verificar_usuario(usuario, contrasena):
    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()
        query = """
            SELECT Id_empleado, nombre, id_tienda, Nivel_usuario
            FROM Empleado
            WHERE Usuario = %s AND contrasena = %s
            LIMIT 1
        """
        cursor.execute(query, (usuario, contrasena))
        resultado = cursor.fetchone()
        return resultado
    finally:
        con.close()


def login():
    configurar_pagina_login()
    
    # Dos columnas
    col_form, col_image = st.columns([1, 1], gap="large")
    
    # Columna izquierda - Formulario
    with col_form:
        st.markdown('<h1 style="text-align: center; color: #1e3a5f;">📦 TIENDA CERRO DE DIOS</h1>', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center; color: #2c5f8a; margin-bottom: 40px;">SISTEMA DE INVENTARIO</h3>', unsafe_allow_html=True)
        
        st.markdown('<label style="font-weight: 600; color: #1e3a5f;">USUARIO</label>', unsafe_allow_html=True)
        usuario = st.text_input("", key="usuario_input", placeholder="Ingresa tu usuario", label_visibility="collapsed")
        
        st.markdown('<label style="font-weight: 600; color: #1e3a5f;">CONTRASEÑA</label>', unsafe_allow_html=True)
        contrasena = st.text_input("", type="password", key="contrasena_input", placeholder="Ingresa tu contraseña", label_visibility="collapsed")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            stay_signed = st.checkbox("Mantener sesión iniciada")
        with col2:
            st.markdown('<p style="text-align: right; margin-top: 10px;"><a href="#" style="color: #666; text-decoration: none;">¿Olvidaste tu contraseña?</a></p>', unsafe_allow_html=True)
        
        if st.button("INICIAR SESIÓN", key="login_button", use_container_width=True):
            if not usuario or not contrasena:
                st.error("❌ Por favor, completa todos los campos.")
            else:
                resultado = verificar_usuario(usuario.strip(), contrasena.strip())
                
                if resultado:
                    id_empleado, nombre_empleado, id_tienda, nivel_usuario = resultado
                    
                    if id_tienda is None:
                        st.error("⚠️ Este usuario no tiene una tienda asignada.")
                        return
                    
                    st.session_state["logueado"] = True
                    st.session_state["usuario"] = usuario.strip()
                    st.session_state["nombre_empleado"] = nombre_empleado
                    st.session_state["id_empleado"] = id_empleado
                    st.session_state["id_tienda"] = int(id_tienda)
                    st.session_state["nivel_usuario"] = nivel_usuario
                    
                    st.success(f"✔️ ¡Bienvenido, {nombre_empleado}!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown('<p style="text-align: center; margin-top: 40px; font-size: 0.7em; color: #999;">v1.0.0</p>', unsafe_allow_html=True)
    
    # Columna derecha - Información con texto visible
    with col_image:
        # Usar un contenedor con color sólido para asegurar visibilidad
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1e3a5f, #2c5f8a); 
                        border-radius: 20px; 
                        padding: 50px 30px; 
                        height: 100%;
                        min-height: 500px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <div style="font-size: 4em;">🏪</div>
                    <h2 style="color: white; margin-top: 20px;">Bienvenido</h2>
                    <p style="color: rgba(255,255,255,0.9);">Gestiona tu negocio de manera eficiente</p>
                </div>
                
                <div style="margin-top: 20px;">
                    <div style="display: flex; align-items: center; margin-bottom: 20px; justify-content: center;">
                        <span style="font-size: 1.3em; margin-right: 12px;">✅</span>
                        <span style="color: white; font-size: 0.95em;">Control de inventario en tiempo real</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 20px; justify-content: center;">
                        <span style="font-size: 1.3em; margin-right: 12px;">💰</span>
                        <span style="color: white; font-size: 0.95em;">Registro de compras y ventas</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 20px; justify-content: center;">
                        <span style="font-size: 1.3em; margin-right: 12px;">📊</span>
                        <span style="color: white; font-size: 0.95em;">Reportes y análisis de datos</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 20px; justify-content: center;">
                        <span style="font-size: 1.3em; margin-right: 12px;">🔐</span>
                        <span style="color: white; font-size: 0.95em;">Seguridad y respaldo de información</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
