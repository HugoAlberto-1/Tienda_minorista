import streamlit as st
from config.conexion import obtener_conexion

# ==================== FUNCIONES DE BASE DE DATOS ====================

def obtener_categorias(id_tienda):
    """Obtiene todas las categorías activas de una tienda"""
    conn = obtener_conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT id_categoria, nombre, descripcion, fecha_creacion 
               FROM Categoria 
               WHERE id_tienda = %s AND activo = 1 
               ORDER BY nombre""",
            (id_tienda,)
        )
        categorias = cursor.fetchall()
        return categorias
    except Exception as e:
        st.error(f"Error al obtener categorías: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def obtener_categorias_solo_nombres(id_tienda):
    """Obtiene solo los nombres de las categorías (para los selectbox)"""
    conn = obtener_conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT nombre 
               FROM Categoria 
               WHERE id_tienda = %s AND activo = 1 
               ORDER BY nombre""",
            (id_tienda,)
        )
        resultados = cursor.fetchall()
        return [row[0] for row in resultados]
    except Exception as e:
        st.error(f"Error al obtener nombres de categorías: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def crear_categoria(id_tienda, nombre, descripcion):
    """Crea una nueva categoría"""
    conn = obtener_conexion()
    if not conn:
        return False, "No se pudo conectar a la base de datos"
    cursor = conn.cursor()
    try:
        # Verificar si ya existe una categoría con el mismo nombre
        cursor.execute(
            "SELECT COUNT(*) FROM Categoria WHERE nombre = %s AND id_tienda = %s AND activo = 1",
            (nombre, id_tienda)
        )
        existe = cursor.fetchone()[0]
        
        if existe > 0:
            return False, f"Ya existe una categoría activa con el nombre '{nombre}'"
        
        cursor.execute(
            """INSERT INTO Categoria (nombre, descripcion, id_tienda, fecha_creacion, activo) 
               VALUES (%s, %s, %s, CURRENT_DATE, 1)""",
            (nombre, descripcion, id_tienda)
        )
        conn.commit()
        return True, f"Categoría '{nombre}' creada exitosamente"
    except Exception as e:
        conn.rollback()
        return False, f"Error al crear la categoría: {e}"
    finally:
        cursor.close()
        conn.close()

def actualizar_categoria(id_categoria, nombre, descripcion, id_tienda):
    """Actualiza una categoría existente"""
    conn = obtener_conexion()
    if not conn:
        return False, "No se pudo conectar a la base de datos"
    cursor = conn.cursor()
    try:
        # Verificar si ya existe otra categoría con el mismo nombre
        cursor.execute(
            """SELECT COUNT(*) FROM Categoria 
               WHERE nombre = %s AND id_tienda = %s AND id_categoria != %s AND activo = 1""",
            (nombre, id_tienda, id_categoria)
        )
        existe = cursor.fetchone()[0]
        
        if existe > 0:
            return False, f"Ya existe otra categoría activa con el nombre '{nombre}'"
        
        cursor.execute(
            """UPDATE Categoria 
               SET nombre = %s, descripcion = %s 
               WHERE id_categoria = %s AND id_tienda = %s""",
            (nombre, descripcion, id_categoria, id_tienda)
        )
        conn.commit()
        return True, f"Categoría '{nombre}' actualizada exitosamente"
    except Exception as e:
        conn.rollback()
        return False, f"Error al actualizar la categoría: {e}"
    finally:
        cursor.close()
        conn.close()

def eliminar_categoria(id_categoria, id_tienda):
    """Elimina (soft delete) una categoría"""
    conn = obtener_conexion()
    if not conn:
        return False, "No se pudo conectar a la base de datos"
    cursor = conn.cursor()
    try:
        # Verificar si hay productos usando esta categoría
        cursor.execute(
            "SELECT COUNT(*) FROM Producto WHERE categoria = (SELECT nombre FROM Categoria WHERE id_categoria = %s) AND id_tienda = %s",
            (id_categoria, id_tienda)
        )
        productos_asociados = cursor.fetchone()[0]
        
        if productos_asociados > 0:
            return False, f"No se puede eliminar la categoría porque tiene {productos_asociados} producto(s) asociado(s). Primero reasigna esos productos."
        
        cursor.execute(
            "UPDATE Categoria SET activo = 0 WHERE id_categoria = %s AND id_tienda = %s",
            (id_categoria, id_tienda)
        )
        conn.commit()
        return True, "Categoría eliminada exitosamente"
    except Exception as e:
        conn.rollback()
        return False, f"Error al eliminar la categoría: {e}"
    finally:
        cursor.close()
        conn.close()

# ==================== INTERFAZ DE USUARIO ====================

def modulo_categoria():
    st.title("📁 Gestión de Categorías")
    
    # Validación de sesión
    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.stop()
    
    id_tienda = st.session_state["id_tienda"]
    
    # Pestañas para las diferentes acciones
    tab1, tab2, tab3 = st.tabs(["📋 Lista de categorías", "➕ Crear nueva categoría", "✏️ Editar/Eliminar"])
    
    with tab1:
        mostrar_lista_categorias(id_tienda)
    
    with tab2:
        mostrar_formulario_crear(id_tienda)
    
    with tab3:
        mostrar_formulario_editar_eliminar(id_tienda)
    
    # Botón para volver al menú principal
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⬅ Volver al menú principal", use_container_width=True):
            st.session_state["module"] = None
            st.rerun()

def mostrar_lista_categorias(id_tienda):
    """Muestra la lista de categorías activas"""
    categorias = obtener_categorias(id_tienda)
    
    if not categorias:
        st.info("ℹ️ No hay categorías registradas. Crea una en la pestaña 'Crear nueva categoría'.")
    else:
        st.write(f"**Total de categorías:** {len(categorias)}")
        st.markdown("---")
        
        for cat in categorias:
            id_cat, nombre, descripcion, fecha = cat
            with st.expander(f"📁 {nombre}"):
                st.write(f"**ID:** {id_cat}")
                st.write(f"**Descripción:** {descripcion if descripcion else 'Sin descripción'}")
                st.write(f"**Fecha de creación:** {fecha}")

def mostrar_formulario_crear(id_tienda):
    """Formulario para crear nueva categoría"""
    with st.form("form_crear_categoria"):
        nombre = st.text_input(
            "📝 Nombre de la categoría", 
            placeholder="Ej: Bebidas, Lácteos, Carnes, etc.",
            help="El nombre debe ser único para esta tienda"
        )
        descripcion = st.text_area(
            "📄 Descripción (opcional)", 
            placeholder="Describe qué productos pertenecen a esta categoría...",
            help="Una breve descripción de la categoría"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submitted = st.form_submit_button("✅ Crear categoría", type="primary", use_container_width=True)
        
        if submitted:
            if not nombre.strip():
                st.error("❌ El nombre de la categoría es obligatorio.")
            else:
                exito, mensaje = crear_categoria(id_tienda, nombre.strip(), descripcion.strip() if descripcion else None)
                if exito:
                    st.success(mensaje)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(mensaje)

def mostrar_formulario_editar_eliminar(id_tienda):
    """Formulario para editar o eliminar categorías existentes"""
    categorias = obtener_categorias(id_tienda)
    
    if not categorias:
        st.info("ℹ️ No hay categorías para editar o eliminar.")
        return
    
    # Crear opciones para el selectbox
    opciones = {f"{cat[1]}": cat[0] for cat in categorias}
    
    categoria_seleccionada_nombre = st.selectbox(
        "🔍 Selecciona una categoría",
        list(opciones.keys()),
        key="select_categoria_editar"
    )
    
    if categoria_seleccionada_nombre:
        id_categoria = opciones[categoria_seleccionada_nombre]
        # Buscar la categoría seleccionada
        cat_seleccionada = next((cat for cat in categorias if cat[0] == id_categoria), None)
        
        if cat_seleccionada:
            with st.form("form_editar_categoria"):
                nuevo_nombre = st.text_input("📝 Nombre", value=cat_seleccionada[1])
                nueva_descripcion = st.text_area("📄 Descripción", value=cat_seleccionada[2] if cat_seleccionada[2] else "")
                
                st.warning("⚠️ **Nota:** Si cambias el nombre de la categoría, los productos existentes mantendrán el nombre anterior. Deberás actualizarlos manualmente.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Guardar cambios", type="primary", use_container_width=True):
                        if not nuevo_nombre.strip():
                            st.error("❌ El nombre es obligatorio.")
                        else:
                            exito, mensaje = actualizar_categoria(
                                id_categoria, 
                                nuevo_nombre.strip(), 
                                nueva_descripcion.strip() if nueva_descripcion else None, 
                                id_tienda
                            )
                            if exito:
                                st.success(mensaje)
                                st.rerun()
                            else:
                                st.error(mensaje)
                
                with col2:
                    if st.form_submit_button("🗑️ Eliminar categoría", type="secondary", use_container_width=True):
                        exito, mensaje = eliminar_categoria(id_categoria, id_tienda)
                        if exito:
                            st.success(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)
