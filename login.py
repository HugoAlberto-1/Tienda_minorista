import streamlit as st
from config.conexion import obtener_conexion

def configurar_pagina_login():
    """Configuración de la página con CSS personalizado para el login"""
    st.set_page_config(
        page_title="Sistema de Inventario - Login",
        page_icon="🛒​",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Paleta de colores corporativos (mismo que el menú principal)
    COLOR_PRIMARY = "#1e3a5f"      # Azul oscuro principal
    COLOR_SECONDARY = "#2c5f8a"    # Azul medio
    COLOR_ACCENT = "#3a7ca5"       # Azul claro
    COLOR_BG = "#f5f7fa"           # Fondo gris muy claro
    COLOR_CARD = "#ffffff"          # Blanco para tarjetas
    COLOR_TEXT = "#333333"          # Texto oscuro
    COLOR_TEXT_LIGHT = "#666666"    # Texto gris
    COLOR_BORDER = "#e0e0e0"        # Bordes
    
    # CSS personalizado para el login
    st.markdown(f"""
        <style>
        /* Fondo general */
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        /* Ocultar elementos no deseados */
        header {{
            display: none;
        }}
        
        /* Contenedor principal - dos columnas */
        .login-container {{
            display: flex;
            min-height: 100vh;
            width: 100%;
        }}
        
        /* Columna izquierda - Formulario */
        .login-form {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px;
            background: {COLOR_CARD};
        }}
        
        .form-wrapper {{
            width: 100%;
            max-width: 400px;
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
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLOR_PRIMARY};
            box-shadow: 0 0 0 2px rgba(30,58,95,0.1);
        }}
        
        /* Columna derecha - Imagen decorativa */
        .login-image {{
            flex: 1;
            background: linear-gradient(135deg, {COLOR_BG}, {COLOR_CARD});
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
            border-radius: 30px 0 0 30px;
            margin: 20px 0;
            border: 1px solid {COLOR_BORDER};
        }}
        
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
        
        /* Lista de características - CENTRADA CON EL MISMO COLOR DE USUARIO/CONTRASEÑA */
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
            text-align: center;
            margin-top: 40px;
            font-size: 0.7em;
            color: {COLOR_TEXT_LIGHT};
        }}
        
        /* Links */
        .forgot-link {{
            text-align: right;
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
        
        /* Versión */
        .version {{
            text-align: center;
            margin-top: 20px;
            font-size: 0.7em;
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
    
    # Usar columnas de Streamlit para el diseño de dos columnas
    col_form, col_image = st.columns([1, 1], gap="large")
    
    # Columna izquierda - Formulario
    with col_form:
        # Logo y título
        st.markdown('<div class="logo">📦</div>', unsafe_allow_html=True)
        st.markdown('<div class="company-name">TIENDAS MINORISTAS</div>', unsafe_allow_html=True)
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
                <div>© 2024 - Tiendas Minoristas</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Columna derecha - Imagen decorativa con características centradas
    with col_image:
        st.markdown("""
            <div class="image-content">
                <div class="image-icon">🏪</div>
                <div class="image-title">Bienvenida</div>
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
