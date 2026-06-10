import streamlit as st
from config.conexion import obtener_conexion

def configurar_estilo():
    """Configuración de estilos CSS para el módulo de empleado - MODO CLARO"""
    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_DARK = "#1a1a1a"
    COLOR_HOVER = "#e8f0fe"
    COLOR_BORDER = "#e0e0e0"
    COLOR_BUTTON = "#1e3a5f"
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {COLOR_BG};
        }}
        
        .module-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .module-subtitle {{
            text-align: center;
            color: {COLOR_SECONDARY};
            font-size: 1.1em;
            margin-bottom: 30px;
        }}
        
        .info-box {{
            background: {COLOR_HOVER};
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid {COLOR_PRIMARY};
            margin: 15px 0;
            color: {COLOR_TEXT_DARK};
        }}
        
        .stTextInput > label, .stSelectbox > label {{
            color: {COLOR_TEXT_DARK} !important;
            font-weight: 500 !important;
        }}
        
        .stTextInput > div > div > input {{
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
            background-color: {COLOR_BUTTON};
            color: white !important;
            padding: 10px 15px;
        }}
        
        .stTextInput > div > div > input::placeholder {{
            color: rgba(255,255,255,0.7) !important;
        }}
        
        /* Estilo para inputs deshabilitados - TEXTO OSCURO */
        .stTextInput > div > div > input:disabled {{
            background-color: #e8f0fe !important;
            color: {COLOR_TEXT_DARK} !important;
            border: 1px solid {COLOR_BORDER};
        }}
        
        /* Para asegurar que el texto del input deshabilitado sea visible */
        input:disabled {{
            background-color: #e8f0fe !important;
            color: #1a1a1a !important;
            -webkit-text-fill-color: #1a1a1a !important;
            opacity: 1 !important;
        }}
        
        .stButton > button {{
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
        }}
        
        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY};
            transform: translateY(-1px);
        }}
        
        .stAlert {{
            border-radius: 8px;
        }}
        
        hr {{
            border-color: {COLOR_BORDER};
        }}
        </style>
    """, unsafe_allow_html=True)


def validar_dui(dui):
    """Valida y formatea el DUI (elimina guiones y verifica longitud)"""
    # Eliminar guiones y espacios
    dui_limpio = dui.strip().replace("-", "").replace(" ", "")
    
    # Verificar que solo contenga números
    if not dui_limpio.isdigit():
        return None, "El DUI debe contener solo números (sin guiones)"
    
    # Verificar longitud (DUI de El Salvador tiene 9 dígitos)
    if len(dui_limpio) != 9:
        return None, f"El DUI debe tener 9 dígitos (ingresaste {len(dui_limpio)})"
    
    return dui_limpio, None


def validar_telefono(telefono):
    """Valida el número de teléfono (solo números)"""
    # Eliminar espacios y guiones
    telefono_limpio = telefono.strip().replace("-", "").replace(" ", "")
    
    # Verificar que solo contenga números
    if not telefono_limpio.isdigit():
        return None, "El teléfono debe contener solo números"
    
    # Verificar longitud mínima (teléfono de El Salvador: 8 dígitos)
    if len(telefono_limpio) < 8:
        return None, f"El teléfono debe tener al menos 8 dígitos (ingresaste {len(telefono_limpio)})"
    
    # Verificar longitud máxima
    if len(telefono_limpio) > 15:
        return None, f"El teléfono es demasiado largo (máximo 15 dígitos)"
    
    return telefono_limpio, None


def modulo_empleado():
    configurar_estilo()
    
    st.markdown('<div class="module-title">👥 Registrar Asociada</div>', unsafe_allow_html=True)

    # ✅ Validación multi-tienda
    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.markdown("---")
        if st.button("⬅ Volver al menú principal"):
            st.session_state.module = None
            st.rerun()
        return

    id_tienda = st.session_state["id_tienda"]
    nombre_tienda = st.session_state.get("nombre_tienda", "Mi Tienda")
    
    # Mostrar tienda actual
    st.markdown(f'<div class="info-box">🏪 Tienda: <strong>{nombre_tienda}</strong></div>', unsafe_allow_html=True)

    # Limpiar campos si se acaba de guardar
    if st.session_state.get("reiniciar_empleado"):
        for campo in ["usuario_input", "nombre_input", "dui_input", "contacto_input", "contrasena_input"]:
            st.session_state.pop(campo, None)
        st.session_state.pop("reiniciar_empleado", None)
        st.rerun()

    # Mostrar mensaje de guardado
    if st.session_state.get("empleado_guardado"):
        st.success("✅ Empleado guardado correctamente.")
        st.session_state.pop("empleado_guardado", None)

    st.markdown('<div class="module-subtitle">➕ Agregar nueva asociada</div>', unsafe_allow_html=True)

    # Campos del formulario
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        Usuario = st.text_input(
            "👤 Usuario",
            value=st.session_state.get("usuario_input", ""),
            key="usuario_input",
            placeholder="Ej: maria_lopez"
        )
        
        Nombre = st.text_input(
            "📝 Nombre completo",
            value=st.session_state.get("nombre_input", ""),
            key="nombre_input",
            placeholder="Ej: María López García"
        )
        
        DUI = st.text_input(
            "🆔 DUI (9 dígitos, sin guión)",
            value=st.session_state.get("dui_input", ""),
            key="dui_input",
            placeholder="Ej: 123456789",
            help="Ingresa los 9 dígitos del DUI sin guiones"
        )
    
    with col2:
        Contacto = st.text_input(
            "📞 Teléfono (solo números)",
            value=st.session_state.get("contacto_input", ""),
            key="contacto_input",
            placeholder="Ej: 61234567",
            help="Ingresa solo números, sin guiones ni espacios"
        )
        
        Contrasena = st.text_input(
            "🔒 Contraseña",
            type="password",
            value=st.session_state.get("contrasena_input", ""),
            key="contrasena_input",
            placeholder="Ingrese una contraseña segura"
        )
        
        Nivel_usuario = st.text_input(
            "⭐ Nivel de usuario",
            value="Usuaria",
            disabled=True,
            key="nivel_input"
        )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Guardar asociada", use_container_width=True, type="primary"):
            if not Usuario.strip() or not Nombre.strip() or not DUI.strip() or not Contacto.strip() or not Contrasena.strip():
                st.warning("⚠️ Por favor, completa todos los campos.")
            else:
                # Validar DUI
                dui_validado, error_dui = validar_dui(DUI)
                if error_dui:
                    st.error(f"❌ {error_dui}")
                else:
                    # Validar teléfono
                    telefono_validado, error_telefono = validar_telefono(Contacto)
                    if error_telefono:
                        st.error(f"❌ {error_telefono}")
                    else:
                        conn = obtener_conexion()
                        if not conn:
                            st.error("❌ No se pudo conectar a la base de datos.")
                            st.stop()

                        cursor = conn.cursor()
                        try:
                            # ✅ Validación de usuario por tienda
                            cursor.execute(
                                "SELECT COUNT(*) FROM Empleado WHERE Usuario = %s AND id_tienda = %s",
                                (Usuario.strip(), id_tienda)
                            )
                            existe = cursor.fetchone()[0]

                            if existe:
                                st.error("❌ Ya existe una asociada con ese usuario en esta tienda.")
                            else:
                                # ✅ Validar si el DUI ya existe en la tienda
                                cursor.execute(
                                    "SELECT COUNT(*) FROM Empleado WHERE Dui = %s AND id_tienda = %s",
                                    (dui_validado, id_tienda)
                                )
                                dui_existe = cursor.fetchone()[0]
                                
                                if dui_existe:
                                    st.error("❌ Ya existe una asociada con ese DUI en esta tienda.")
                                else:
                                    # ✅ Insertar empleado
                                    cursor.execute(
                                        """
                                        INSERT INTO Empleado (Usuario, Contrasena, Nombre, Dui, Contacto, Nivel_usuario, id_tienda)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                        """,
                                        (Usuario.strip(), Contrasena.strip(), Nombre.strip(), dui_validado, telefono_validado, Nivel_usuario, id_tienda)
                                    )
                                    conn.commit()

                                    st.session_state["empleado_guardado"] = True
                                    st.session_state["reiniciar_empleado"] = True
                                    st.success(f"✅ Asociada '{Nombre}' registrada correctamente.")
                                    st.rerun()

                        except Exception as e:
                            conn.rollback()
                            st.error(f"❌ Error al guardar el empleado: {e}")

                        finally:
                            cursor.close()
                            conn.close()

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⬅ Volver al menú principal", use_container_width=True):
            st.session_state.module = None
            st.rerun()
