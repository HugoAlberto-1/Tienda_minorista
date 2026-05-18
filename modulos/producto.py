import streamlit as st
from config.conexion import obtener_conexion

# ✅ Función para obtener categorías desde la base de datos
def obtener_categorias_db(id_tienda):
    """Obtiene las categorías activas desde la base de datos"""
    conn = obtener_conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT nombre FROM Categoria WHERE id_tienda = %s AND activo = 1 ORDER BY nombre",
            (id_tienda,)
        )
        resultados = cursor.fetchall()
        return [row[0] for row in resultados]
    except Exception as e:
        st.error(f"Error al cargar categorías: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def modulo_producto():
    st.title("📦 Registro de productos")

    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.stop()

    id_tienda = st.session_state["id_tienda"]

    # ✅ Cargar categorías desde la base de datos
    categorias = obtener_categorias_db(id_tienda)
    
    if not categorias:
        st.warning("⚠️ No hay categorías disponibles. Ve a 'Gestión de Categorías' y crea una primero.")
        st.stop()

    # Reset seguro del formulario
    if st.session_state.get("reiniciar_formulario"):
        st.session_state.pop("cod_barra_input", None)
        st.session_state.pop("nombre_producto_input", None)
        st.session_state.pop("categoria_input", None)
        st.session_state.pop("reiniciar_formulario", None)
        st.rerun()

    if st.session_state.get("producto_guardado"):
        st.success("✅ Producto guardado correctamente.")
        st.session_state.pop("producto_guardado", None)

    st.subheader("➕ Agregar nuevo producto")

    Cod_barra = st.text_input(
        "📦 Código de barras",
        value=st.session_state.get("cod_barra_input", ""),
        key="cod_barra_input",
        placeholder="Ej: 123456789"
    )

    Nombre = st.text_input(
        "🏷️ Nombre del producto",
        value=st.session_state.get("nombre_producto_input", ""),
        key="nombre_producto_input",
        placeholder="Ej: Arroz blanco"
    )

    # 🔽 SELECTOR DE CATEGORÍA (cargado desde la BD)
    categoria = st.selectbox(
        "📁 Categoría del producto:",
        categorias,
        index=0,
        key="categoria_input",
        help="Selecciona la categoría a la que pertenece este producto"
    )

    if st.button("💾 Guardar producto", type="primary"):
        if not Cod_barra.strip() or not Nombre.strip() or not categoria:
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            conn = obtener_conexion()
            if not conn:
                st.error("❌ No se pudo conectar a la base de datos.")
                st.stop()

            cursor = conn.cursor()
            try:
                # Verificar duplicado por tienda
                cursor.execute(
                    "SELECT COUNT(*) FROM Producto WHERE Cod_barra = %s AND id_tienda = %s",
                    (Cod_barra.strip(), id_tienda)
                )
                existe = cursor.fetchone()[0]

                if existe:
                    st.error("❌ Ya existe un producto con ese código de barras en esta tienda.")
                else:
                    # Insertar producto con la categoría seleccionada
                    cursor.execute(
                        """
                        INSERT INTO Producto (Cod_barra, Nombre, categoria, id_tienda)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (Cod_barra.strip(), Nombre.strip(), categoria, id_tienda)
                    )
                    conn.commit()

                    st.session_state["producto_guardado"] = True
                    st.session_state["reiniciar_formulario"] = True
                    st.success(f"✅ Producto '{Nombre}' guardado correctamente en categoría '{categoria}'")
                    st.rerun()

            except Exception as e:
                conn.rollback()
                st.error(f"❌ Error al guardar el producto: {e}")

            finally:
                cursor.close()
                conn.close()

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⬅ Volver al menú principal", use_container_width=True):
            st.session_state["module"] = None
            st.rerun()
