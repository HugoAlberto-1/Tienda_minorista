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
    
    # CSS personalizado para el login - SIN SCROLL
    st.markdown(f"""
        <style>
        /* ========== BLOQUEAR SCROLL COMPLETAMENTE ========== */
        html, body {{
            overflow: hidden !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        .stApp {{
            overflow: hidden !important;
            height: 100vh !important;
            background-color: {COLOR_BG};
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        .stAppViewContainer {{
            overflow: hidden !important;
            height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        .main {{
            overflow: hidden !important;
            height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        /* CORRECCIÓN: Forzar paddings a 0 en el contenedor general de Streamlit */
        .block-container {{
            overflow: hidden !important;
            height: 100vh !important;
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            margin: 0 !important;
            max-width: 100% !important;
        }}

        /* CORRECCIÓN: Eliminar márgenes por defecto en el primer elemento interno */
        .block-container > div:first-child {{
            margin-top: 0 !important;
            padding-top: 0 !important;
        }}
        
        /* Ocultar scrollbars */
        ::-webkit-scrollbar {{
            display: none !important;
        }}
        
        * {{
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }}
        
        /* Ocultar header */
        header {{
            display: none !important;
        }}
        
        .stDeployButton {{
            display: none !important;
        }}
        
        /* Eliminar cualquier padding/margin del contenedor principal */
        .stApp > div {{
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        /* Contenedor de las columnas - ocupa toda la pantalla */
        .row-widget.stColumns {{
            display: flex !important;
            height: 100vh !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
        }}
        
        /* Columna izquierda - Formulario */
        div[data-testid="column"]:first-child {{
            flex: 0.8;
            background-color: {COLOR_CARD};
            padding: 0px !important;
            margin: 0 !important;
            height: 100vh !important;
            overflow: hidden !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }}
        
        /* Columna derecha - Imagen SIN NINGÚN ESPACIO */
        div[data-testid="column"]:last-child {{
            flex: 1.2;
            padding: 0 !important;
            margin: 0 !important;
            height: 100vh !important;
            overflow: hidden !important;
            position: relative;
        }}
        
        /* Eliminar cualquier contenedor interno que pueda agregar padding */
        div[data-testid="column"]:last-child > div {{
            padding: 0 !important;
            margin: 0 !important;
            height: 100% !important;
        }}
        
        /* Contenedor de la imagen - OCUPA TODA LA ALTURA */
        .image-container {{
            width: 100%;
            height: 100vh;
            overflow: hidden;
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            margin: 0;
            padding: 0;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100vh;
            object-fit: cover;
            object-position: center;
            display: block;
            margin: 0;
            padding: 0;
        }}
        
        /* Estilos del formulario */
        .form-content {{
            width: 100%;
            max-width: 340px;
            margin: 20 auto;
        }}
        
        .logo {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-align: center;
        }}
        
        .company-name {{
            font-size: 1.2em;
            font-weight: 700;
            color: {COLOR_PRIMARY};
            text-align: center;
            margin-bottom: 5px;
            letter-spacing: 1px;
        }}
        
        .system-name {{
            font-size: 0.75em;
            color: {COLOR_TEXT_LIGHT};
            text-align: center;
            margin-bottom: 25px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .input-label {{
            font-size: 0.7em;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
            margin-top: 8px;
            display: block;
        }}
        
        .stTextInput > div > div > input {{
            border-radius: 6px;
            border: 1px solid {COLOR_BORDER};
            padding: 8px 12px;
            font-size: 0.85em;
            background-color: {COLOR_CARD};
            color: {COLOR_TEXT};
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLOR_PRIMARY};
            box-shadow: 0 0 0 2px rgba(30,58,95,0.1);
        }}
        
        .stButton > button {{
            width: 100%;
            padding: 8px;
            margin-top: 15px;
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.85em;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY};
            transform: translateY(-1px);
        }}
        
        .stCheckbox {{
            margin-top: 10px;
        }}
        
        .stCheckbox label {{
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.75em;
        }}
        
        .forgot-link {{
            text-align: right;
            margin-top: 10px;
        }}
        
        .forgot-link a {{
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.7em;
            text-decoration: none;
        }}
        
        .forgot-link a:hover {{
            color: {COLOR_PRIMARY};
        }}
        
        .login-footer {{
            text-align: center;
            margin-top: 25px;
            font-size: 0.6em;
            color: {COLOR_TEXT_LIGHT};
            line-height: 1.4;
        }}
        
        /* Asegurar que los mensajes no causen scroll */
        .stAlert {{
            margin-top: 8px;
            margin-bottom: 0;
            padding: 6px;
            font-size: 0.75em;
        }}
        
        /* Eliminar márgenes extra */
        .element-container {{
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        .stMarkdown {{
            margin: 0 !important;
            padding: 0 !important;
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
    
    # CORRECCIÓN: Se cambia el parámetro gap a "none" para evitar desfases de layout externos
    col_form, col_image = st.columns([0.8, 1.2], gap="none")
    
    # ========== COLUMNA IZQUIERDA - FORMULARIO ==========
    with col_form:
        # Logo y título
        st.markdown('<div class="logo">📦</div>', unsafe_allow_html=True)
        st.markdown('<div class="company-name">TIENDA CERRO DE DIOS</div>', unsafe_allow_html=True)
        st.markdown('<div class="system-name">SISTEMA DE INVENTARIO</div>', unsafe_allow_html=True)
        
        # Campos de entrada
        st.markdown('<label class="input-label">USUARIO</label>', unsafe_allow_html=True)
        usuario = st.text_input("", key="usuario_input", placeholder="Ingresa tu usuario", label_visibility="collapsed")
        
        st.markdown('<label class="input-label">CONTRASEÑA</label>', unsafe_allow_html=True)
        contrasena = st.text_input("", type="password", key="contrasena_input", placeholder="Ingresa tu contraseña", label_visibility="collapsed")
        
        # Checkbox y forgot password
        col1, col2 = st.columns([1, 1])
        with col1:
            stay_signed = st.checkbox("Mantener sesión")
        with col2:
            st.markdown('<div class="forgot-link"><a href="#">¿Olvidaste tu contraseña?</a></div>', unsafe_allow_html=True)
        
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
        st.markdown("""
            <div class="login-footer">
                <div>v1.0.0</div>
                <div>Sistema de Gestión de Inventario</div>
                <div>© 2024 - Tienda Cerro de Dios</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== COLUMNA DERECHA - IMAGEN ALTA RESOLUCIÓN ==========
    with col_image:
        imagen_url = "https://images.pexels.com/photos/3183197/pexels-photo-3183197.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&fit=crop"
        
        st.markdown(f"""
            <div class="image-container">
                <img src="{imagen_url}" alt="Tienda de abarrotes">
            </div>
        """, unsafe_allow_html=True)


# Ejecutar la función login
if __name__ == "__main__":
    login()
