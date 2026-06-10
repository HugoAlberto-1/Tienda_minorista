import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion

def configurar_estilo():
    """Configuración de estilos CSS para el módulo de editar producto - MODO CLARO"""
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
        
        .warning-box {{
            background: #fff3cd;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
            color: #856404;
        }}
        
        .danger-box {{
            background: #f8d7da;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #dc3545;
            margin: 15px 0;
            color: #721c24;
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
        
        .stSelectbox > div > div {{
            background-color: {COLOR_BUTTON};
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
        }}
        
        .stSelectbox > div > div > div {{
            color: white !important;
        }}
        
        .stSelectbox svg {{
            fill: white !important;
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
        
        .stDataFrame {{
            background-color: {COLOR_CARD} !important;
            border-radius: 12px !important;
            border: 1px solid {COLOR_BORDER} !important;
        }}
        
        [data-testid="stDataFrame"] th {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
            font-weight: 600 !important;
            text-align: center !important;
            padding: 12px 8px !important;
        }}
        
        [data-testid="stDataFrame"] td {{
            color: {COLOR_TEXT} !important;
            text-align: center !important;
            padding: 10px 8px !important;
            background-color: {COLOR_CARD} !important;
        }}
        
        [data-testid="stDataFrame"] tr:nth-child(even) td {{
            background-color: #f8f9fa !important;
        }}
        
        [data-testid="stDataFrame"] tr:hover td {{
            background-color: {COLOR_HOVER} !important;
        }}
        
        hr {{
            border-color: {COLOR_BORDER};
        }}
        </style>
    """, unsafe_allow_html=True)


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


def modulo_editar_producto():
    configurar_estilo()
    
    st.markdown('<div class="module-title">✏️ Editar o eliminar producto</div>', unsafe_allow_html=True)

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

    # ✅ Cargar categorías desde la base de datos
    categorias = obtener_categorias_db(id_tienda)
    
    if not categorias:
        st.warning("⚠️ No hay categorías disponibles. Ve a 'Gestión de Categorías' y crea una primero.")
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⬅ Volver al menú principal", use_container_width=True):
                st.session_state.module = None
                st.rerun()
        return

    cod_barra = st.text_input(
        "🔎 Código de barras del producto",
        placeholder="Ej: 123456789",
        help="Ingresa el código de barras del producto que deseas editar o eliminar"
    )

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
                st.markdown(f'<div class="info-box">📦 Producto encontrado: <strong>{producto[1]}</strong></div>', unsafe_allow_html=True)
                
                nuevo_nombre = st.text_input(
                    "🏷️ Nombre del producto",
                    value=producto[1],
                    placeholder="Ej: Arroz blanco"
                )
                
                # Obtener el índice de la categoría actual desde la lista de la BD
                categoria_actual = producto[2]
                try:
                    indice_categoria = categorias.index(categoria_actual)
                except ValueError:
                    indice_categoria = 0
                
                nueva_categoria = st.selectbox(
                    "📁 Categoría del producto",
                    categorias,
                    index=indice_categoria
                )

                col1, col2 = st.columns(2, gap="large")

                with col1:
                    if st.button("💾 Guardar cambios", use_container_width=True, type="primary"):
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
                        st.markdown(f'<div class="warning-box">⚠️ <strong>Este producto tiene registros asociados:</strong><br>• {compras_count} compra(s) registrada(s)<br>• {ventas_count} venta(s) registrada(s)</div>', unsafe_allow_html=True)
                        st.markdown('<div class="danger-box">⚠️ <strong>Si lo eliminas, se eliminarán TODAS sus compras y ventas asociadas.</strong></div>', unsafe_allow_html=True)
                        
                        confirm = st.checkbox("✅ Confirmo que quiero eliminar el producto y TODAS sus transacciones")
                        if st.button("🗑️ Eliminar producto y todas sus transacciones", use_container_width=True, type="primary"):
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
                        if st.button("🗑️ Eliminar producto", use_container_width=True):
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
                st.warning("⚠️ Producto no encontrado. Verifica el código de barras.")

        except Exception as e:
            st.error(f"❌ Error al buscar el producto: {e}")

    st.markdown("---")
    st.markdown('<div class="module-subtitle">📋 Lista de productos registrados</div>', unsafe_allow_html=True)

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
