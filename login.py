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
            flex: 2;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
            border-radius: 30px 0 0 30px;
            margin: 20px 0;
            box-shadow: -5px 0 20px rgba(0,0,0,0.05);
        }}
        
        .image-container {{
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            z-index: 2;
        }}
        
        .login-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 30px 0 0 30px;
        }}
        
        /* Overlay opcional para la imagen */
        .image-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.3);
            border-radius: 30px 0 0 30px;
            z-index: 1;
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
    
    # Usar columnas de Streamlit para el diseño de dos columnas (1:2)
    col_form, col_image = st.columns([1, 2], gap="large")
    
    # Columna izquierda - Formulario
    with col_form:
        # Logo y título
        st.markdown('<div class="logo">📦</div>', unsafe_allow_html=True)
        st.markdown('<div class="company-name">TIENDA CERRO DE DIOS</div>', unsafe_allow_html=True)
        st.markdown('<div class="system-name">Sistema de Inventario</div>', unsafe_allow_html=True)
        
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
    
    # Columna derecha - Imagen personalizada
    with col_image:
        # ==========================================
        # 👇 REEMPLAZA ESTA URL CON TU PROPIA IMAGEN
        # ==========================================
        
        # Opción 1: Usar imagen desde URL
        imagen_url = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=2070&auto=format&fit=crop"
        
        # Opción 2: Usar imagen local (descomenta las siguientes líneas y comenta la de arriba)
        # from PIL import Image
        # imagen = Image.open("imagenes/tu-imagen.jpg")
        # st.image(imagen, use_container_width=True)
        
        # Mostrar imagen con estilo
        st.markdown(f"""
            <div class="login-image">
                <div class="image-overlay"></div>
                <img src="{imagen_url}" alt="Imagen de fondo">
            </div>
        """, unsafe_allow_html=True)
        
        # ==========================================
        # FIN DE LA SECCIÓN PARA REEMPLAZAR
        # ==========================================
        
