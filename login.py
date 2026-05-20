import streamlit as st
from config.conexion import obtener_conexion

def configurar_pagina_login():
    """Configuración de la página con CSS personalizado para el login estilo Riot Games"""
    st.set_page_config(
        page_title="Sistema de Inventario - Login",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Paleta de colores
    COLOR_PRIMARY = "#1e3a5f"      # Azul oscuro principal
    COLOR_SECONDARY = "#2c5f8a"    # Azul medio
    COLOR_BG = "#0a0e27"           # Fondo oscuro elegante
    COLOR_CARD = "#111827"          # Fondo de la tarjeta
    COLOR_TEXT = "#f3f4f6"          # Texto claro
    COLOR_TEXT_MUTED = "#9ca3af"    # Texto gris
    COLOR_BORDER = "#374151"        # Bordes
    
    # CSS personalizado para el login estilo Riot Games
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
            background: linear-gradient(135deg, {COLOR_BG} 0%, {COLOR_CARD} 100%);
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
            color: {COLOR_TEXT};
            text-align: center;
            margin-bottom: 30px;
            letter-spacing: 2px;
        }}
        
        .system-name {{
            font-size: 0.9em;
            color: {COLOR_TEXT_MUTED};
            text-align: center;
            margin-bottom: 40px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Campos de entrada */
        .input-label {{
            font-size: 0.75em;
            font-weight: 600;
            color: {COLOR_TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            display: block;
        }}
        
        /* Columna derecha - Imagen decorativa */
        .login-image {{
            flex: 1;
            background: linear-gradient(135deg, {COLOR_PRIMARY}, {COLOR_SECONDARY});
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
        }}
        
        .image-content {{
            text-align: center;
            color: white;
            padding: 40px;
            z-index: 2;
        }}
        
        .image-icon {{
            font-size: 8em;
            margin-bottom: 30px;
            animation: float 3s ease-in-out infinite;
        }}
        
        .image-title {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        
        .image-subtitle {{
            font-size: 1em;
            opacity: 0.9;
            margin-bottom: 30px;
        }}
        
        .feature-list {{
            text-align: left;
            margin-top: 30px;
        }}
        
        .feature-item {{
            margin: 15px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .feature-icon {{
            font-size: 1.2em;
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
            background: rgba(255,255,255,0.05);
            border-radius: 50%;
            bottom: -100px;
            right: -100px;
        }}
        
        .bg-decoration-2 {{
            position: absolute;
            width: 200px;
            height: 200px;
            background: rgba(255,255,255,0.03);
            border-radius: 50%;
            top: -50px;
            left: -50px;
        }}
        
        /* Botón de login */
        .login-btn {{
            width: 100%;
            padding: 12px;
            margin-top: 20px;
            background: {COLOR_PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .login-btn:hover {{
            background: {COLOR_SECONDARY};
            transform: translateY(-2px);
        }}
        
        /* Footer */
        .login-footer {{
            text-align: center;
            margin-top: 40px;
            font-size: 0.7em;
            color: {COLOR_TEXT_MUTED};
        }}
        
        /* Checkbox personalizado */
        .checkbox-container {{
            display: flex;
            align-items: center;
            margin: 15px 0;
            gap: 8px;
        }}
        
        .checkbox-container label {{
            color: {COLOR_TEXT_MUTED};
            font-size: 0.8em;
        }}
        
        /* Links */
        .forgot-link {{
            text-align: right;
            margin-top: 10px;
        }}
        
        .forgot-link a {{
            color: {COLOR_TEXT_MUTED};
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
            color: {COLOR_TEXT_MUTED};
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
        st.markdown('<div class="form-wrapper">', unsafe_allow_html=True)
        
        # Logo y título
        st.markdown('<div class="logo">📦</div>', unsafe_allow_html=True)
        st.markdown('<div class="company-name">TIENDA CERRO DE DIOS</div>', unsafe_allow_html=True)
        st.markdown('<div class="system-name">Sistema de Inventario</div>', unsafe_allow_html=True)
        
        # Campos de entrada con estilo personalizado
        st.markdown('<label class="input-label">USUARIO</label>', unsafe_allow_html=True)
        usuario = st.text_input("", key="usuario_input", placeholder="Ingresa tu usuario", label_visibility="collapsed")
        
        st.markdown('<label class="input-label">CONTRASEÑA</label>', unsafe_allow_html=True)
        contrasena = st.text_input("", type="password", key="contrasena_input", placeholder="Ingresa tu contraseña", label_visibility="collapsed")
        
        # Checkbox Stay signed in
        col1, col2 = st.columns([1, 1])
        with col1:
            stay_signed = st.checkbox("Mantener sesión iniciada", key="stay_signed")
        with col2:
            st.markdown('<div class="forgot-link"><a href="#">¿OLVIDASTE TU CONTRASEÑA?</a></div>', unsafe_allow_html=True)
        
        # Botón de login personalizado
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
                <div style="margin-top: 10px;">Este sistema está protegido por autenticación de usuarios</div>
                <div>© 2024 - Sistema de Gestión de Inventario</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
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
                        <span>Control de inventario en tiempo real</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">💰</span>
                        <span>Registro de compras y ventas</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">📊</span>
                        <span>Reportes y análisis de datos</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">🔐</span>
                        <span>Seguridad y respaldo de información</span>
                    </div>
                </div>
            </div>
            <div class="bg-decoration"></div>
            <div class="bg-decoration-2"></div>
        """, unsafe_allow_html=True)
