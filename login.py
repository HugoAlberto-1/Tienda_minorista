import streamlit as st
from config.conexion import obtener_conexion

def configurar_pagina_login():
    """Configuración de la página con CSS personalizado para el login"""
    st.set_page_config(
        page_title="Sistema de Inventario - Login",
        page_icon="📦",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Paleta de colores corporativos (azul corporativo)
    COLOR_PRIMARY = "#1e3a5f"      # Azul oscuro principal
    COLOR_SECONDARY = "#2c5f8a"    # Azul medio
    COLOR_ACCENT = "#3a7ca5"       # Azul claro
    COLOR_BG = "#f5f7fa"           # Fondo gris muy claro
    COLOR_CARD = "#ffffff"          # Blanco para tarjetas
    COLOR_TEXT = "#333333"          # Texto oscuro
    COLOR_TEXT_LIGHT = "#666666"    # Texto gris
    
    # CSS personalizado para el login
    st.markdown(f"""
        <style>
        /* Fondo general */
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        /* Contenedor principal del login */
        .login-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh;
        }}
        
        /* Tarjeta de login */
        .login-card {{
            background: {COLOR_CARD};
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 450px;
            margin: 0 auto;
            border: 1px solid #e0e0e0;
        }}
        
        /* Título principal */
        .main-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            text-align: center;
            color: {COLOR_SECONDARY};
            font-size: 1em;
            margin-bottom: 30px;
        }}
        
        /* Icono decorativo */
        .login-icon {{
            font-size: 4em;
            margin-bottom: 20px;
        }}
        
        /* Campos de entrada */
        .stTextInput > div > div > input {{
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            padding: 10px 15px;
            font-size: 1em;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLOR_PRIMARY};
            box-shadow: 0 0 0 2px rgba(30,58,95,0.1);
        }}
        
        /* Botón de login */
        .stButton > button {{
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
            padding: 10px 20px;
            width: 100%;
            font-size: 1.1em;
        }}
        
        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY};
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        /* Mensajes de error y éxito */
        .stAlert {{
            border-radius: 10px;
        }}
        
        /* Footer */
        .login-footer {{
            text-align: center;
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.8em;
            margin-top: 30px;
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

        # Traemos también la tienda (y opcionalmente el nivel)
        query = """
            SELECT Id_empleado, nombre, id_tienda, Nivel_usuario
            FROM Empleado
            WHERE Usuario = %s AND contrasena = %s
            LIMIT 1
        """
        cursor.execute(query, (usuario, contrasena))
        resultado = cursor.fetchone()
        return resultado  # None si no encuentra
    finally:
        con.close()


def login():
    # Configurar la página con el estilo
    configurar_pagina_login()
    
    # Contenedor principal
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Tarjeta de login
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Icono y título
        st.markdown('<div class="login-icon">📦</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-title">Sistema de Inventario</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Tienda Cerro de Dios</div>', unsafe_allow_html=True)
        
        # Campos de entrada
        usuario = st.text_input("Usuario", key="usuario_input", placeholder="Ingresa tu usuario")
        contrasena = st.text_input("Contraseña", type="password", key="contrasena_input", placeholder="Ingresa tu contraseña")
        
        # Botón de login
        if st.button("Iniciar sesión", key="login_button", use_container_width=True):
            if not usuario or not contrasena:
                st.warning("⚠️ Por favor, completa todos los campos.")
            else:
                resultado = verificar_usuario(usuario.strip(), contrasena.strip())

                if resultado:
                    # ahora vienen 4 campos
                    id_empleado, nombre_empleado, id_tienda, nivel_usuario = resultado

                    # Validación: el empleado debe tener tienda asignada
                    if id_tienda is None:
                        st.error("⚠️ Este usuario no tiene una tienda asignada. Contacta al administrador.")
                        return

                    st.session_state["logueado"] = True
                    st.session_state["usuario"] = usuario.strip()
                    st.session_state["nombre_empleado"] = nombre_empleado
                    st.session_state["id_empleado"] = id_empleado

                    # ✅ Clave para multi-tienda
                    st.session_state["id_tienda"] = int(id_tienda)

                    # opcional (por roles)
                    st.session_state["nivel_usuario"] = nivel_usuario

                    st.success(f"✔️ ¡Bienvenido, {nombre_empleado}!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        # Footer
        st.markdown('<div class="login-footer">© 2024 - Sistema de Gestión de Inventario</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
