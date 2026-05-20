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
    COLOR_TEXT_LIGHT = "#666666"
    COLOR_BORDER = "#e0e0e0"
    
    # CSS personalizado para eliminar TODOS los espacios
    st.markdown(f"""
        <style>
        /* Eliminar todo el padding y margin por defecto */
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        /* Ocultar header y elementos de Streamlit */
        header, .stDeployButton, .stStatusWidget, .stAppViewContainer > div:first-child {{
            display: none !important;
        }}
        
        /* Eliminar padding del main container */
        .main .block-container {{
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            width: 100% !important;
        }}
        
        /* Forzar que el contenedor principal ocupe toda la pantalla */
        .stAppViewContainer, .stAppViewContainer > div, .stAppViewContainer > div > div {{
            width: 100% !important;
            height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        /* Contenedor de las columnas - ocupa toda la pantalla */
        .row-widget.stColumns {{
            display: flex !important;
            height: 100vh !important;
            width: 100vw !important;
            margin: 0 !important;
            padding: 0 !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
        }}
        
        /* Columnas sin padding ni margin */
        div[data-testid="column"] {{
            padding: 0 !important;
            margin: 0 !important;
            height: 100vh !important;
        }}
        
        /* Columna izquierda - Formulario centrado */
        div[data-testid="column"]:first-child {{
            flex: 1;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            background: {COLOR_CARD};
            overflow-y: auto;
            padding: 20px !important;
        }}
        
        /* Columna derecha - Imagen sin espacios */
        div[data-testid="column"]:last-child {{
            flex: 2;
            padding: 0 !important;
            margin: 0 !important;
            position: relative;
            overflow: hidden;
        }}
        
        /* Contenedor interno del formulario */
        .form-wrapper {{
            width: 100%;
            max-width: 400px;
            margin: 0 auto;
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
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLOR_PRIMARY};
            box-shadow: 0 0 0 2px rgba(30,58,95,0.1);
        }}
        
        /* Contenedor de la imagen - SIN NINGÚN ESPACIO */
        .login-image {{
            width: 100%;
            height: 100vh;
            position: relative;
            overflow: hidden;
        }}
        
        .login-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
            display: block;
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
        
        /* Checkbox */
        .stCheckbox {{
            margin-top: 15px;
        }}
        
        .stCheckbox label {{
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.8em;
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
        
        /* Eliminar espacios de elementos de Streamlit */
        .element-container, .stMarkdown, .stVerticalBlock, .stHorizontalBlock {{
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        /* Ocultar scrollbar si aparece (opcional) */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 4px;
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
    
    # Crear columnas sin gap y sin espacios
    # Usamos un contenedor vacío para eliminar espacios adicionales
    col_form, col_image = st.columns([1, 2], gap="small")
    
    # Columna izquierda - Formulario
    with col_form:
        # Contenedor para centrar el formulario
        st.markdown('<div style="width: 100%; display: flex; justify-content: center;">', unsafe_allow_html=True)
        st.markdown('<div style="width: 100%; max-width: 400px;">', unsafe_allow_html=True)
        
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
            stay_signed = st.checkbox("Mantener sesión iniciada")
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
        st.markdown(f"""
            <div class="login-footer">
                <div>v1.0.0</div>
                <div style="margin-top: 10px;">Sistema de Gestión de Inventario</div>
                <div>© 2024 - Tienda Cerro de Dios</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Columna derecha - Imagen que ocupa TODA la columna sin espacios
    with col_image:
        # Usar imagen local (recomendado) o URL
        # Opción 1: Imagen desde URL
        imagen_url = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=2070&auto=format&fit=crop"
        
        # Opción 2: Imagen local (descomenta estas líneas)
        # from PIL import Image
        # import base64
        # from io import BytesIO
        # 
        # img = Image.open("imagenes/tu-imagen.jpg")
        # buffered = BytesIO()
        # img.save(buffered, format="JPEG", quality=95)
        # img_base64 = base64.b64encode(buffered.getvalue()).decode()
        # imagen_url = f"data:image/jpeg;base64,{img_base64}"
        
        st.markdown(f"""
            <div class="login-image">
                <img src="{imagen_url}" alt="Imagen de fondo">
            </div>
        """, unsafe_allow_html=True)

# Para ejecutar la función login cuando se llama al script
if __name__ == "__main__":
    login()
