import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion

def modulo_gestion_admin():
    st.title("👑 Panel de Administración")
    st.subheader("Gestión de Tiendas y Usuarios")

    # Verificar que sea administrador
    if st.session_state.get("nivel_usuario") != "Administrador":
        st.error("⛔ Acceso denegado. Solo administradores.")
        st.stop()

    # Crear pestañas para organizar
    tab1, tab2, tab3 = st.tabs(["🏪 Gestionar Tiendas", "👥 Gestionar Usuarios", "📋 Listados"])

    # ============================================================
    # TAB 1: GESTIONAR TIENDAS
    # ============================================================
    with tab1:
        st.markdown("### 📝 Crear Nueva Tienda")

        with st.form("form_nueva_tienda"):
            nombre = st.text_input(
                "Nombre de la tienda *",
                placeholder="Ej: Tienda Centro Histórico"
            )
            activo = st.checkbox("Tienda activa", value=True)

            submitted = st.form_submit_button("🏪 Crear Tienda", use_container_width=True)

            if submitted:
                if not nombre:
                    st.error("❌ El nombre de la tienda es obligatorio")
                else:
                    conn = obtener_conexion()
                    if conn:
                        cursor = conn.cursor()
                        try:
                            cursor.execute("""
                                INSERT INTO tienda (nombre, activo)
                                VALUES (%s, %s)
                            """, (nombre, 1 if activo else 0))
                            conn.commit()
                            st.success(f"✅ Tienda '{nombre}' creada exitosamente")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al crear tienda: {e}")
                        finally:
                            cursor.close()
                            conn.close()
                    else:
                        st.error("❌ No se pudo conectar a la base de datos")

        st.divider()

        # Mostrar tiendas existentes
        st.markdown("### 📋 Tiendas Registradas")

        conn = obtener_conexion()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("""
                    SELECT id_tienda, nombre, activo
                    FROM tienda
                    ORDER BY nombre
                """)
                tiendas = cursor.fetchall()
            except Exception as e:
                st.error(f"Error al cargar tiendas: {e}")
                tiendas = []
            finally:
                cursor.close()
                conn.close()

            if tiendas:
                df = pd.DataFrame(tiendas)
                df = df.rename(columns={
                    "id_tienda": "ID",
                    "nombre": "Nombre",
                    "activo": "Activa"
                })
                df["Activa"] = df["Activa"].apply(lambda x: "✅ Sí" if x == 1 else "❌ No")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay tiendas registradas aún.")

    # ============================================================
    # TAB 2: GESTIONAR USUARIOS
    # ============================================================
    with tab2:
        st.markdown("### 📝 Crear Nuevo Usuario")
        
        # Opción para elegir el tipo de usuario
        tipo_usuario = st.radio(
            "Tipo de usuario a crear:",
            ["👑 Administrador (Dueño de todas las tiendas)", "👥 Vendedor / Cajero (Asignado a una tienda)"],
            horizontal=True
        )
        
        st.divider()

        # Obtener lista de tiendas disponibles (solo se necesita si no es administrador)
        conn = obtener_conexion()
        if not conn:
            st.error("❌ No se pudo conectar a la base de datos")
        else:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT id_tienda, nombre FROM tienda WHERE activo = 1 ORDER BY nombre")
                tiendas_activas = cursor.fetchall()
            except Exception as e:
                st.error(f"Error al cargar tiendas: {e}")
                tiendas_activas = []
            finally:
                cursor.close()
                conn.close()

            with st.form("form_nuevo_usuario"):
                col1, col2 = st.columns(2)

                with col1:
                    nombre = st.text_input("Nombre completo *", placeholder="Ej: María López")
                    usuario = st.text_input("Usuario *", placeholder="Ej: maria.lopez")
                    dui = st.text_input("DUI", placeholder="Ej: 12345678-9")

                with col2:
                    contacto = st.text_input("Teléfono", placeholder="Ej: 1234-5678")
                    contrasena = st.text_input("Contraseña *", type="password", placeholder="******")
                    
                    # Si es Administrador (Dueño), no se muestra selector de tienda
                    if "Administrador" in tipo_usuario:
                        nivel = "Administrador"
                        tienda_seleccionada = "Ninguna (Dueño de todas las tiendas)"
                        id_tienda_seleccionada = None
                        st.info("👑 El Administrador será dueño de TODAS las tiendas (sin tienda asignada)")
                    else:
                        nivel = st.selectbox("Nivel de usuario", ["Vendedor", "Cajero"])
                        # Selector de tienda solo para vendedores/cajeros
                        if tiendas_activas:
                            opciones_tienda = {t["nombre"]: t["id_tienda"] for t in tiendas_activas}
                            tienda_seleccionada = st.selectbox("Tienda donde trabajará *", list(opciones_tienda.keys()))
                            id_tienda_seleccionada = opciones_tienda[tienda_seleccionada]
                        else:
                            st.warning("⚠️ No hay tiendas activas. Crea una tienda primero en la pestaña 'Gestionar Tiendas'.")
                            id_tienda_seleccionada = None

                submitted_usuario = st.form_submit_button("👤 Crear Usuario", use_container_width=True)

                if submitted_usuario:
                    if not nombre or not usuario or not contrasena:
                        st.error("❌ Nombre, usuario y contraseña son obligatorios")
                    elif "Vendedor" in tipo_usuario and not tiendas_activas:
                        st.error("❌ No hay tiendas activas. Crea una tienda primero.")
                    elif "Vendedor" in tipo_usuario and id_tienda_seleccionada is None:
                        st.error("❌ Debes seleccionar una tienda para el vendedor/cajero")
                    else:
                        conn = obtener_conexion()
                        if conn:
                            cursor = conn.cursor()
                            try:
                                # Verificar si el usuario ya existe
                                cursor.execute(
                                    "SELECT id_empleado FROM Empleado WHERE Usuario = %s",
                                    (usuario,)
                                )
                                if cursor.fetchone():
                                    st.error(f"❌ El usuario '{usuario}' ya existe")
                                else:
                                    # Si es Administrador, id_tienda = NULL
                                    # Si es Vendedor/Cajero, id_tienda = tienda seleccionada
                                    cursor.execute("""
                                        INSERT INTO Empleado (Nombre, Usuario, DUI, Contacto, Contrasena, Nivel_usuario, id_tienda)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    """, (nombre, usuario, dui, contacto, contrasena, nivel, id_tienda_seleccionada))
                                    conn.commit()
                                    
                                    if "Administrador" in tipo_usuario:
                                        st.success(f"✅ Administrador '{usuario}' creado exitosamente (Dueño de todas las tiendas)")
                                    else:
                                        st.success(f"✅ Usuario '{usuario}' creado exitosamente en la tienda '{tienda_seleccionada}'")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al crear usuario: {e}")
                            finally:
                                cursor.close()
                                conn.close()
                        else:
                            st.error("❌ No se pudo conectar a la base de datos")

    # ============================================================
    # TAB 3: LISTADOS COMPLETOS
    # ============================================================
    with tab3:
        st.markdown("### 📊 Usuarios por Tienda")
        
        # Mostrar también los Administradores (Dueños) que tienen id_tienda = NULL
        st.info("👑 Los Administradores (Dueños) aparecen en 'Todas las tiendas' porque no pertenecen a una específica")
        
        # Opción para ver todos los usuarios o por tienda
        vista = st.radio(
            "Ver:",
            ["👑 Administradores (Dueños)", "🏪 Usuarios por tienda", "📋 Todos los usuarios"],
            horizontal=True
        )
        
        conn = obtener_conexion()
        if not conn:
            st.error("❌ No se pudo conectar a la base de datos")
        else:
            cursor = conn.cursor(dictionary=True)
            
            try:
                if vista == "👑 Administradores (Dueños)":
                    # Mostrar solo usuarios con id_tienda = NULL (dueños)
                    cursor.execute("""
                        SELECT id_empleado, Nombre, Usuario, DUI, Contacto, Nivel_usuario
                        FROM Empleado
                        WHERE id_tienda IS NULL AND Nivel_usuario = 'Administrador'
                        ORDER BY Nombre
                    """)
                    usuarios_lista = cursor.fetchall()
                    
                    if usuarios_lista:
                        df = pd.DataFrame(usuarios_lista)
                        df = df.rename(columns={
                            "id_empleado": "ID",
                            "Nombre": "Nombre",
                            "Usuario": "Usuario",
                            "DUI": "DUI",
                            "Contacto": "Contacto",
                            "Nivel_usuario": "Nivel"
                        })
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No hay administradores (dueños) registrados aún.")
                
                elif vista == "🏪 Usuarios por tienda":
                    # Mostrar selector de tienda para usuarios normales
                    cursor.execute("SELECT id_tienda, nombre FROM tienda WHERE activo = 1 ORDER BY nombre")
                    tiendas_listado = cursor.fetchall()
                    
                    if tiendas_listado:
                        opciones_listado = {t["nombre"]: t["id_tienda"] for t in tiendas_listado}
                        tienda_ver = st.selectbox("Ver usuarios de:", list(opciones_listado.keys()), key="ver_usuarios")
                        id_tienda_ver = opciones_listado[tienda_ver]
                        
                        cursor.execute("""
                            SELECT id_empleado, Nombre, Usuario, DUI, Contacto, Nivel_usuario
                            FROM Empleado
                            WHERE id_tienda = %s
                            ORDER BY Nombre
                        """, (id_tienda_ver,))
                        usuarios_lista = cursor.fetchall()
                        
                        if usuarios_lista:
                            df = pd.DataFrame(usuarios_lista)
                            df = df.rename(columns={
                                "id_empleado": "ID",
                                "Nombre": "Nombre",
                                "Usuario": "Usuario",
                                "DUI": "DUI",
                                "Contacto": "Contacto",
                                "Nivel_usuario": "Nivel"
                            })
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info(f"No hay usuarios registrados en '{tienda_ver}'")
                    else:
                        st.info("No hay tiendas activas para mostrar usuarios")
                
                else:  # Todos los usuarios
                    cursor.execute("""
                        SELECT id_empleado, Nombre, Usuario, DUI, Contacto, Nivel_usuario, 
                               CASE 
                                   WHEN id_tienda IS NULL THEN '👑 Dueño (Todas las tiendas)'
                                   ELSE (SELECT nombre FROM tienda WHERE id_tienda = e.id_tienda)
                               END as Tienda
                        FROM Empleado e
                        ORDER BY 
                            CASE WHEN id_tienda IS NULL THEN 0 ELSE 1 END,
                            Nombre
                    """)
                    usuarios_lista = cursor.fetchall()
                    
                    if usuarios_lista:
                        df = pd.DataFrame(usuarios_lista)
                        df = df.rename(columns={
                            "id_empleado": "ID",
                            "Nombre": "Nombre",
                            "Usuario": "Usuario",
                            "DUI": "DUI",
                            "Contacto": "Contacto",
                            "Nivel_usuario": "Nivel",
                            "Tienda": "Tienda asignada"
                        })
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No hay usuarios registrados aún.")
                        
            except Exception as e:
                st.error(f"Error al cargar datos: {e}")
            finally:
                cursor.close()
                conn.close()

    # Botón para volver al menú principal (fuera de las tabs)
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Volver al menú principal", use_container_width=True):
            st.session_state["macro_modulo"] = None
            st.rerun()
