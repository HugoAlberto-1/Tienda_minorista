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
            # Solo los campos que existen en tu tabla tienda
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

        # Obtener lista de tiendas disponibles
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

            if not tiendas_activas:
                st.warning("⚠️ No hay tiendas activas. Crea una tienda primero en la pestaña 'Gestionar Tiendas'.")
            else:
                with st.form("form_nuevo_usuario"):
                    col1, col2 = st.columns(2)

                    with col1:
                        nombre = st.text_input("Nombre completo *", placeholder="Ej: María López")
                        usuario = st.text_input("Usuario *", placeholder="Ej: maria.lopez")
                        dui = st.text_input("DUI", placeholder="Ej: 12345678-9")

                    with col2:
                        contacto = st.text_input("Teléfono", placeholder="Ej: 1234-5678")
                        contrasena = st.text_input("Contraseña *", type="password", placeholder="******")
                        nivel = st.selectbox("Nivel de usuario", ["Vendedora", "Administrador"])

                    # Selector de tienda
                    opciones_tienda = {t["nombre"]: t["id_tienda"] for t in tiendas_activas}
                    tienda_seleccionada = st.selectbox("Tienda donde trabajará *", list(opciones_tienda.keys()))
                    id_tienda_seleccionada = opciones_tienda[tienda_seleccionada]

                    submitted_usuario = st.form_submit_button("👤 Crear Usuario", use_container_width=True)

                    if submitted_usuario:
                        if not nombre or not usuario or not contrasena:
                            st.error("❌ Nombre, usuario y contraseña son obligatorios")
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
                                        cursor.execute("""
                                            INSERT INTO Empleado (Nombre, Usuario, DUI, Contacto, Contrasena, Nivel_usuario, id_tienda)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                                        """, (nombre, usuario, dui, contacto, contrasena, nivel, id_tienda_seleccionada))
                                        conn.commit()
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

        conn = obtener_conexion()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT id_tienda, nombre FROM tienda WHERE activo = 1 ORDER BY nombre")
                tiendas_listado = cursor.fetchall()
            except Exception as e:
                st.error(f"Error al cargar tiendas: {e}")
                tiendas_listado = []
            finally:
                cursor.close()
                conn.close()

            if tiendas_listado:
                opciones_listado = {t["nombre"]: t["id_tienda"] for t in tiendas_listado}
                tienda_ver = st.selectbox("Ver usuarios de:", list(opciones_listado.keys()), key="ver_usuarios")
                id_tienda_ver = opciones_listado[tienda_ver]

                conn = obtener_conexion()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    try:
                        cursor.execute("""
                            SELECT id_empleado, Nombre, Usuario, DUI, Contacto, Nivel_usuario
                            FROM Empleado
                            WHERE id_tienda = %s
                            ORDER BY Nombre
                        """, (id_tienda_ver,))
                        usuarios_lista = cursor.fetchall()
                    except Exception as e:
                        st.error(f"Error al cargar usuarios: {e}")
                        usuarios_lista = []
                    finally:
                        cursor.close()
                        conn.close()

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
                    st.error("❌ No se pudo conectar a la base de datos")
            else:
                st.info("No hay tiendas activas para mostrar usuarios")
        else:
            st.error("❌ No se pudo conectar a la base de datos")

    # Botón para volver al menú principal (fuera de las tabs)
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Volver al menú principal", use_container_width=True):
            st.session_state["macro_modulo"] = None
            st.rerun()
