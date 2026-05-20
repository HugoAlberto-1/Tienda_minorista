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
    
    # CSS personalizado para el login
    st.markdown(f"""
        <style>
        /* Eliminar todos los márgenes y paddings por defecto */
        .main, .stApp, .stApp > div {{
            margin: 0;
            padding: 0;
        }}
        
        .main .block-container {{
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            width: 100% !important;
        }}
        
        /* Ocultar header */
        header {{
            display: none;
        }}
        
        /* Contenedor principal en dos columnas usando flex */
        .split-layout {{
            display: flex;
            width: 100%;
            height: 100vh;
            flex-direction: row;
        }}
        
        /* Columna izquierda - Formulario (1/3) */
        .split-left {{
            flex: 1;
            background: {COLOR_CARD};
            display: flex;
            justify-content: center;
            align-items: center;
            overflow-y: auto;
        }}
        
        /* Columna derecha - Imagen (2/3) */
        .split-right {{
            flex: 2;
            background: {COLOR_SECONDARY};
            overflow: hidden;
        }}
        
        .split-right img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
            display: block;
        }}
        
        /* Formulario interno */
        .form-wrapper {{
            width: 100%;
            max-width: 380px;
            padding: 20px;
        }}
        
        /* Logo y título */
        .logo {{
            font-size: 3em;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .company-name {{
            font-size: 1.5em;
            font-weight: 700;
            color: {COLOR_PRIMARY};
            text-align: center;
            margin-bottom: 10px;
            letter-spacing: 2px;
        }}
        
        .system-name {{
            font-size: 0.9em;
            color: {COLOR_TEXT_LIGHT};
            text-align: center;
            margin-bottom: 40px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Campos de entrada */
        .input-label {{
            font-size: 0.75em;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            display: block;
        }}
        
        .stTextInput > div > div > input {{
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
            padding: 10px 15px;
            font-size: 0.95em;
            background-color: {COLOR_CARD};
            color: {COLOR_TEXT};
            width: 100%;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLOR_PRIMARY};
            box-shadow: 0 0 0 2px rgba(30,58,95,0.1);
        }}
        
        /* Botón de login */
        .stButton > button {{
            width: 100%;
            padding: 12px;
            margin-top: 20px;
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY};
            transform: translateY(-2px);
        }}
        
        /* Checkbox y forgot */
        .row-flex {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
        }}
        
        .forgot-link a {{
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.75em;
            text-decoration: none;
        }}
        
        .forgot-link a:hover {{
            color: {COLOR_PRIMARY};
        }}
        
        /* Footer */
        .login-footer {{
            text-align: center;
            margin-top: 40px;
            font-size: 0.7em;
            color: {COLOR_TEXT_LIGHT};
        }}
        
        /* Ocultar elementos de Streamlit que puedan interferir */
        .stAppHeader {{
            display: none;
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
    
    # Usar HTML puro para el layout de dos columnas
    st.markdown("""
        <div class="split-layout">
            <div class="split-left">
                <div class="form-wrapper">
    """, unsafe_allow_html=True)
    
    # Contenido del formulario
    st.markdown('<div class="logo">📦</div>', unsafe_allow_html=True)
    st.markdown('<div class="company-name">TIENDA CERRO DE DIOS</div>', unsafe_allow_html=True)
    st.markdown('<div class="system-name">Sistema de Inventario</div>', unsafe_allow_html=True)
    
    # Campos de entrada
    st.markdown('<label class="input-label">USUARIO</label>', unsafe_allow_html=True)
    usuario = st.text_input("", key="usuario_input", placeholder="Ingresa tu usuario", label_visibility="collapsed")
    
    st.markdown('<label class="input-label">CONTRASEÑA</label>', unsafe_allow_html=True)
    contrasena = st.text_input("", type="password", key="contrasena_input", placeholder="Ingresa tu contraseña", label_visibility="collapsed")
    
    # Checkbox y forgot password
    st.markdown("""
        <div class="row-flex">
            <div>
                <input type="checkbox" id="stay_signed">
                <label for="stay_signed" style="color: #666; font-size: 0.8em;">Mantener sesión iniciada</label>
            </div>
            <div class="forgot-link">
                <a href="#">¿Olvidaste tu contraseña?</a>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Botón de login
    if st.button("INICIAR SESIÓN", key="login_button", use_container_width=True):
        if not usuario or not contrasena:
            st.error("❌ Por favor, completa todos los campos.")
        else:
            resultado = verificar_usuario(usuario.strip(), contrasena.strip())
            
            if resultado:
                id_empleado, nombre_empleado, id_tienda, nivel_usuario = resultado
                
                if id_tienda is None:
                    st.error("⚠️ Este usuario no tiene una tienda asignada. Contacta al administrador.")
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
    
    # Footer
    st.markdown(f"""
        <div class="login-footer">
            <div>v1.0.0</div>
            <div style="margin-top: 10px;">Sistema de Gestión de Inventario</div>
            <div>© 2024 - Tienda Cerro de Dios</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
            </div>
        </div>
        <div class="split-right">
            <img src="https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=2070&auto=format&fit=crop" alt="Imagen de fondo">
        </div>
    </div>
    """, unsafe_allow_html=True)
