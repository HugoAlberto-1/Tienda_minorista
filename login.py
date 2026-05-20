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
    
    # CSS más suave pero efectivo
    st.markdown(f"""
        <style>
        /* Ocultar solo el header y sidebar */
        header {{
            display: none !important;
        }}
        
        .stDeployButton {{
            display: none !important;
        }}
        
        /* Eliminar padding del main container pero mantenerlo visible */
        .main .block-container {{
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }}
        
        /* Hacer que las columnas ocupen toda la altura */
        .stColumns {{
            gap: 0rem !important;
        }}
        
        /* Columna izquierda - formulario */
        div[data-testid="column"]:first-child {{
            background-color: {COLOR_CARD};
            padding: 2rem !important;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        /* Columna derecha - imagen */
        div[data-testid="column"]:last-child {{
            padding: 0 !important;
            margin: 0 !important;
            min-height: 100vh;
            position: relative;
        }}
        
        /* Contenedor de la imagen */
        .image-container {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
        }}
        
        /* Estilos del formulario */
        .logo {{
            font-size: 3.5em;
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
            font-size: 0.85em;
            color: {COLOR_TEXT_LIGHT};
            text-align: center;
            margin-bottom: 40px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .input-label {{
            font-size: 0.7em;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
            display: block;
        }}
        
        .stTextInput > div > div > input {{
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
            padding: 10px 12px;
            font-size: 0.9em;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLOR_PRIMARY};
            box-shadow: 0 0 0 2px rgba(30,58,95,0.1);
        }}
        
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
        
        .stCheckbox {{
            margin-top: 15px;
        }}
        
        .stCheckbox label {{
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.8em;
        }}
        
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
        
        .login-footer {{
            text-align: center;
            margin-top: 50px;
            font-size: 0.7em;
            color: {COLOR_TEXT_LIGHT};
        }}
        
        /* Asegurar que el formulario sea visible */
        .form-content {{
            width: 100%;
            max-width: 400px;
            margin: 0 auto;
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
    col_form, col_image = st.columns([1, 1.5], gap="small")
    
    # Columna izquierda - Formulario
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
                <div style="margin-top: 5px;">Sistema de Gestión de Inventario</div>
                <div>© 2024 - Tienda Cerro de Dios</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Columna derecha - Imagen
    with col_image:
        # URL de la imagen (puedes cambiarla)
        imagen_url = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=2070&auto=format&fit=crop"
        
        # Si quieres usar imagen local, descomenta esto:
        # import base64
        # from PIL import Image
        # from io import BytesIO
        # 
        # img = Image.open("ruta/a/tu/imagen.jpg")
        # buffered = BytesIO()
        # img.save(buffered, format="JPEG")
        # img_base64 = base64.b64encode(buffered.getvalue()).decode()
        # imagen_url = f"data:image/jpeg;base64,{img_base64}"
        
        st.markdown(f"""
            <div style="position: relative; width: 100%; height: 100vh; overflow: hidden;">
                <img src="{imagen_url}" style="width: 100%; height: 100%; object-fit: cover; object-position: center;">
            </div>
        """, unsafe_allow_html=True)


# Ejecutar la función login
if __name__ == "__main__":
    login()
