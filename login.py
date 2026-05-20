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
        }}
        
        .stAppViewContainer {{
            overflow: hidden !important;
            height: 100vh !important;
        }}
        
        .main {{
            overflow: hidden !important;
            height: 100vh !important;
        }}
        
        .block-container {{
            overflow: hidden !important;
            height: 100vh !important;
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
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
            flex: 1;
            background-color: {COLOR_CARD};
            padding: 20px !important;
            margin: 0 !important;
            height: 100vh !important;
            overflow: hidden !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }}
        
        /* Columna derecha - Imagen */
        div[data-testid="column"]:last-child {{
            flex: 1.2;
            padding: 0 !important;
            margin: 0 !important;
            height: 100vh !important;
            overflow: hidden !important;
            position: relative;
        }}
        
        /* Contenedor de la imagen */
        .image-container {{
            width: 100%;
            height: 100vh;
            overflow: hidden;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
        }}
        
        /* Estilos del formulario */
        .form-content {{
            width: 100%;
            max-width: 400px;
            margin: 0 auto;
        }}
        
        .logo {{
            font-size: 3em;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .company-name {{
            font-size: 1.4em;
            font-weight: 700;
            color: {COLOR_PRIMARY};
            text-align: center;
            margin-bottom: 5px;
            letter-spacing: 1px;
        }}
        
        .system-name {{
            font-size: 0.85em;
            color: {COLOR_TEXT_LIGHT};
            text-align: center;
            margin-bottom: 30px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .input-label {{
            font-size: 0.75em;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
            margin-top: 10px;
            display: block;
        }}
        
        .stTextInput > div > div > input {{
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
            padding: 10px 12px;
            font-size: 0.9em;
            background-color: {COLOR_CARD};
            color: {COLOR_TEXT};
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLOR_PRIMARY};
            box-shadow: 0 0 0 2px rgba(30,58,95,0.1);
        }}
        
        .stButton > button {{
            width: 100%;
            padding: 10px;
            margin-top: 20px;
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY};
            transform: translateY(-1px);
        }}
        
        .stCheckbox {{
            margin-top: 12px;
        }}
        
        .stCheckbox label {{
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.8em;
        }}
        
        .forgot-link {{
            text-align: right;
            margin-top: 12px;
        }}
        
        .forgot-link a {{
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.75em;
            text-decoration: none;
        }}
        
        .forgot-link a:hover {{
            color: {COLOR_PRIMARY};
        }}
        
        .login-footer {{
            text-align: center;
            margin-top: 30px;
            font-size: 0.65em;
            color: {COLOR_TEXT_LIGHT};
            line-height: 1.5;
        }}
        
        /* Asegurar que los mensajes no causen scroll */
        .stAlert {{
            margin-top: 10px;
            margin-bottom: 0;
            padding: 8px;
            font-size: 0.8em;
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
    
    # Crear las dos columnas
    col_form, col_image = st.columns([1, 1.2], gap="small")
    
    # ========== COLUMNA IZQUIERDA - FORMULARIO ==========
    with col_form:
        st.markdown('<div class="form-content">', unsafe_allow_html=True)
        
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
    
    # ========== COLUMNA DERECHA - IMAGEN ==========
    with col_image:
        # Cambia esta URL por tu imagen
        imagen_url = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=2070&auto=format&fit=crop"
        
        # Si quieres usar imagen local:
        # import base64
        # from PIL import Image
        # from io import BytesIO
        # 
        # img = Image.open("tu-imagen.jpg")
        # # Redimensionar si es necesario
        # img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
        # buffered = BytesIO()
        # img.save(buffered, format="JPEG", quality=95)
        # img_base64 = base64.b64encode(buffered.getvalue()).decode()
        # imagen_url = f"data:image/jpeg;base64,{img_base64}"
        
        st.markdown(f"""
            <div class="image-container">
                <img src="{imagen_url}" alt="Imagen de fondo">
            </div>
        """, unsafe_allow_html=True)


# Ejecutar la función login
if __name__ == "__main__":
    login()
