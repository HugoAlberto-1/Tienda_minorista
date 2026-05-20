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
    COLOR_ACCENT = "#3a7ca5"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_LIGHT = "#666666"
    COLOR_BORDER = "#e0e0e0"
    
    # CSS personalizado para el login
    st.markdown(f"""
        <style>
        /* Solución para bloquear scroll */
        header, footer, .stDeployButton, [data-testid="stToolbar"] {{
            display: none !important;
        }}
        
        html, body {{
            overflow: hidden !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            position: fixed !important;
            width: 100% !important;
        }}
        
        .stApp {{
            overflow: hidden !important;
            height: 100vh !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            background-color: {COLOR_BG};
        }}
        
        .main > div {{
            overflow: hidden !important;
            height: 100vh !important;
        }}
        
        .block-container {{
            overflow: hidden !important;
            padding: 0 !important;
            max-width: 100% !important;
            margin: 0 !important;
        }}
        
        /* Forzar que las columnas no generen scroll */
        .row-widget.stColumns {{
            height: 100vh !important;
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        /* Ajustar cada columna */
        div[data-testid="column"] {{
            overflow-y: auto !important;
            height: 100vh !important;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }}
        
        div[data-testid="column"]::-webkit-scrollbar {{
            display: none !important;
        }}
        
        /* Contenedor del formulario con padding izquierdo */
        .form-container {{
            padding-left: 100px !important;
            padding-right: 50px !important;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100vh;
        }}
        
        /* Ajustar el contenido dentro del formulario */
        .form-content {{
            width: 100%;
            max-width: 450px;
        }}
        
        /* Ocultar elementos no deseados */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Logo y título */
        .logo {{
            font-size: 3em;
            margin-bottom: 20px;
            text-align: left;
        }}
        
        .company-name {{
            font-size: 1.5em;
            font-weight: 700;
            color: {COLOR_PRIMARY};
            text-align: left;
            margin-bottom: 10px;
            letter-spacing: 2px;
        }}
        
        .system-name {{
            font-size: 0.9em;
            color: {COLOR_TEXT_LIGHT};
            text-align: left;
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
            text-align: left;
        }}
        
        .stTextInput > div > div > input {{
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
            padding: 10px 15px;
            font-size: 0.95em;
            background-color: {COLOR_CARD};
            color: {COLOR_TEXT};
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
        
        /* Footer */
        .login-footer {{
            text-align: left;
            margin-top: 40px;
            font-size: 0.7em;
            color: {COLOR_TEXT_LIGHT};
        }}
        
        /* Columna derecha - Imagen decorativa */
        .image-content {{
            text-align: center;
            padding: 40px;
            z-index: 2;
            width: 100%;
        }}
        
        .image-icon {{
            font-size: 5em;
            margin-bottom: 20px;
            animation: float 3s ease-in-out infinite;
        }}
        
        .image-title {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: {COLOR_PRIMARY};
        }}
        
        .image-subtitle {{
            font-size: 1em;
            margin-bottom: 40px;
            color: {COLOR_PRIMARY};
        }}
        
        .feature-list {{
            margin-top: 20px;
            width: 100%;
        }}
        
        .feature-item {{
            margin: 20px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            width: 100%;
            max-width: 320px;
        }}
        
        .feature-icon {{
            font-size: 1.3em;
            min-width: 35px;
            text-align: center;
        }}
        
        .feature-text {{
            font-size: 0.95em;
            text-align: left;
            color: {COLOR_PRIMARY};
        }}
        
        /* Animación flotante */
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-20px); }}
        }}
        
        /* Decoración de fondo */
        .bg-decoration {{
            position: absolute;
            width: 300px;
            height: 300px;
            background: rgba(30,58,95,0.05);
            border-radius: 50%;
            bottom: -100px;
            right: -100px;
        }}
        
        .bg-decoration-2 {{
            position: absolute;
            width: 200px;
            height: 200px;
            background: rgba(30,58,95,0.03);
            border-radius: 50%;
            top: -50px;
            left: -50px;
        }}
        
        /* Ajustes responsivos */
        @media (max-width: 768px) {{
            .form-container {{
                padding-left: 20px !important;
                padding-right: 20px !important;
            }}
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
    
    # Usar columnas de Streamlit para el diseño de dos columnas
    col_form, col_image = st.columns([1, 1], gap="large")
    
    # Columna izquierda - Formulario con contenedor para padding
    with col_form:
        # Contenedor con padding izquierdo
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-content">', unsafe_allow_html=True)
        
        # Logo y título
        st.markdown('<div class="logo">📦</div>', unsafe_allow_html=True)
        st.markdown('<div class="company-name">TIENDA CERRO DE DIOS</div>', unsafe_allow_html=True)
        st.markdown('<div class="system-name">Sistema de Inventario</div>', unsafe_allow_html=True)
        
        # Campos de entrada
        st.markdown('<label class="input-label">USUARIO</label>', unsafe_allow_html=True)
        usuario = st.text_input("", key="usuario_input", placeholder="Ingresa tu usuario", label_visibility="collapsed")
        
        st.markdown('<label class="input-label">CONTRASEÑA</label>', unsafe_allow_html=True)
        contrasena = st.text_input("", type="password", key="contrasena_input", placeholder="Ingresa tu contraseña", label_visibility="collapsed")
        
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
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Columna derecha - Imagen decorativa
    with col_image:
        st.markdown("""
            <div class="image-content">
                <div class="image-icon">🏪</div>
                <div class="image-title">Bienvenido</div>
                <div class="image-subtitle">Gestiona tu negocio de manera eficiente</div>
                <div class="feature-list">
                    <div class="feature-item">
                        <span class="feature-icon">✅</span>
                        <span class="feature-text">Control de inventario en tiempo real</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">💰</span>
                        <span class="feature-text">Registro de compras y ventas</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">📊</span>
                        <span class="feature-text">Reportes y análisis de datos</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">🔐</span>
                        <span class="feature-text">Seguridad y respaldo de información</span>
                    </div>
                </div>
            </div>
            <div class="bg-decoration"></div>
            <div class="bg-decoration-2"></div>
        """, unsafe_allow_html=True)


# Ejecutar la función login
if __name__ == "__main__":
    login()
