import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion

# Lista de categorías (debe coincidir con la de producto.py)
CATEGORIAS = [
    "Abarrotes",
    "Granos y productos a granel",
    "Sopas, pastas y consomés",
    "Condimentos y salsas",
    "Bebidas",
    "Lácteos y derivados",
    "Snacks y boquitas",
    "Dulces y chocolates",
    "Panadería y repostería",
    "Ingredientes para hornear",
    "Carnes y congelados",
    "Enlatados y conservas",
    "Desechables y empaques",
    "Limpieza del hogar",
    "Higiene personal",
    "Cuidado del bebé",
    "Medicamentos y botiquín",
    "Papelería y útiles escolares",
    "Juguetes y regalos",
    "Accesorios personales y belleza",
    "Hogar y utensilios",
    "Ferretería básica y eléctricos",
    "Mascotas",
    "Productos naturales y especias",
    "Productos de temporada y fiesta"
]

def modulo_editar_producto():
    st.title("✏️ Editar o eliminar producto")

    # ✅ Validación multi-tienda
    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.stop()

    id_tienda = st.session_state["id_tienda"]

    cod_barra = st.text_input("🔎 Ingresar código de barras del producto")

    # --- Sección de edición/eliminación ---
    if cod_barra:
        try:
            conn = obtener_conexion()
            if not conn:
                st.error("❌ No se pudo conectar a la base de datos.")
                st.stop()

            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT Cod_barra, Nombre, categoria
                FROM Producto
                WHERE Cod_barra = %s AND id_tienda = %s
                """,
                (cod_barra, id_tienda)
            )
            producto = cursor.fetchone()
            cursor.close()
            conn.close()

            if producto:
                nuevo_nombre = st.text_input("Nombre del producto", value=producto[1])
                
                # Obtener el índice de la categoría actual
                categoria_actual = producto[2]
                try:
                    indice_categoria = CATEGORIAS.index(categoria_actual)
                except ValueError:
                    indice_categoria = 0
                
                nueva_categoria = st.selectbox(
                    "📁 Categoría del producto",
                    CATEGORIAS,
                    index=indice_categoria
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("💾 Guardar cambios"):
                        try:
                            conn = obtener_conexion()
                            cursor = conn.cursor()
                            cursor.execute(
                                """
                                UPDATE Producto
                                SET Nombre = %s,
                                    categoria = %s
                                WHERE Cod_barra = %s AND id_tienda = %s
                                """,
                                (nuevo_nombre, nueva_categoria, cod_barra, id_tienda)
                            )
                            conn.commit()
                            st.success("✅ Producto actualizado correctamente.")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"❌ Error al actualizar: {e}")
                        finally:
                            cursor.close()
                            conn.close()

                with col2:
                    # Verificar si el producto tiene referencias antes de permitir eliminar
                    conn_check = obtener_conexion()
                    cursor_check = conn_check.cursor()
                    
                    # Verificar en ProductoxCompra
                    cursor_check.execute(
                        "SELECT COUNT(*) FROM ProductoxCompra WHERE Cod_barra = %s AND id_tienda = %s",
                        (cod_barra, id_tienda)
                    )
                    compras_count = cursor_check.fetchone()[0]
                    
                    # Verificar en ProductoxVenta
                    cursor_check.execute(
                        "SELECT COUNT(*) FROM ProductoxVenta WHERE Cod_barra = %s AND id_tienda = %s",
                        (cod_barra, id_tienda)
                    )
                    ventas_count = cursor_check.fetchone()[0]
                    
                    cursor_check.close()
                    conn_check.close()
                    
                    if compras_count > 0 or ventas_count > 0:
                        st.warning(f"⚠️ **Este producto tiene registros asociados:**")
                        if compras_count > 0:
                            st.warning(f"   • {compras_count} compra(s) registrada(s)")
                        if ventas_count > 0:
                            st.warning(f"   • {ventas_count} venta(s) registrada(s)")
                        st.error("⚠️ **Si lo eliminas, se eliminarán TODAS sus compras y ventas asociadas.**")
                        
                        confirm = st.checkbox("✅ Confirmo que quiero eliminar el producto y TODAS sus transacciones")
                        if st.button("🗑️ Eliminar producto y todas sus transacciones", type="primary"):
                            if not confirm:
                                st.warning("☝️ Marca la casilla para confirmar la eliminación.")
                            else:
                                try:
                                    conn = obtener_conexion()
                                    cursor = conn.cursor()
                                    
                                    # Iniciar transacción
                                    conn.autocommit = False
                                    
                                    # 1. Eliminar compras asociadas
                                    cursor.execute(
                                        "DELETE FROM ProductoxCompra WHERE Cod_barra = %s AND id_tienda = %s",
                                        (cod_barra, id_tienda)
                                    )
                                    st.info(f"✅ Eliminadas {compras_count} compras asociadas")
                                    
                                    # 2. Eliminar ventas asociadas
                                    cursor.execute(
                                        "DELETE FROM ProductoxVenta WHERE Cod_barra = %s AND id_tienda = %s",
                                        (cod_barra, id_tienda)
                                    )
                                    st.info(f"✅ Eliminadas {ventas_count} ventas asociadas")
                                    
                                    # 3. Finalmente eliminar el producto
                                    cursor.execute(
                                        "DELETE FROM Producto WHERE Cod_barra = %s AND id_tienda = %s",
                                        (cod_barra, id_tienda)
                                    )
                                    
                                    # Confirmar todas las operaciones
                                    conn.commit()
                                    st.success("🗑️ Producto y todas sus transacciones eliminados correctamente.")
                                    st.rerun()
                                    
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"❌ Error al eliminar: {e}")
                                finally:
                                    conn.autocommit = True
                                    cursor.close()
                                    conn.close()
                    else:
                        # Producto sin transacciones, eliminación simple
                        confirm = st.checkbox("¿Estás seguro que deseas eliminar este producto?")
                        if st.button("🗑️ Eliminar producto"):
                            if not confirm:
                                st.warning("☝️ Marca la casilla para confirmar la eliminación.")
                            else:
                                try:
                                    conn = obtener_conexion()
                                    cursor = conn.cursor()
                                    cursor.execute(
                                        "DELETE FROM Producto WHERE Cod_barra = %s AND id_tienda = %s",
                                        (cod_barra, id_tienda)
                                    )
                                    conn.commit()
                                    st.success("🗑️ Producto eliminado correctamente.")
                                    st.rerun()
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"❌ Error al eliminar: {e}")
                                finally:
                                    cursor.close()
                                    conn.close()
            else:
                st.warning("⚠️ Producto no encontrado (verifique el código de barras).")

        except Exception as e:
            st.error(f"❌ Error al buscar el producto: {e}")

    st.markdown("---")
    st.subheader("📋 Lista de productos registrados")

    try:
        conn = obtener_conexion()
        if not conn:
            st.error("❌ No se pudo conectar a la base de datos.")
            st.stop()

        cursor = conn.cursor()

        if cod_barra:
            cursor.execute(
                """
                SELECT Cod_barra, Nombre, categoria
                FROM Producto
                WHERE id_tienda = %s AND Cod_barra LIKE %s
                ORDER BY Nombre
                """,
                (id_tienda, '%' + cod_barra + '%')
            )
        else:
            cursor.execute(
                """
                SELECT Cod_barra, Nombre, categoria
                FROM Producto
                WHERE id_tienda = %s
                ORDER BY Nombre
                """,
                (id_tienda,)
            )

        productos = cursor.fetchall()
        cursor.close()
        conn.close()

        df = pd.DataFrame(productos, columns=["Código de barras", "Nombre", "Categoría"])
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al cargar la lista de productos: {e}")

    st.markdown("---")
    
    # Usamos columnas para centrar el botón visualmente
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⬅ Volver al menú principal", use_container_width=True):
            st.session_state.module = None
            st.rerun()
