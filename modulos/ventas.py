import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

CONVERSIONES_A_LIBRAS = {
    "libras": 1,
    "arroba": 25,
    "quintal": 100,
}

# 📁 Categorías que se consideran "granos" (usarán libras, quintal, arroba)
CATEGORIAS_GRANOS = [
    "Granos y productos a granel",
    "Abarrotes",
    "Sopas, pastas y consomés"
]

# 📁 Categorías que son carnes (usarán libras y unidad)
CATEGORIAS_CARNES = [
    "Carnes y congelados"
]

def obtener_unidades_por_categoria(categoria):
    """Retorna las unidades disponibles según la categoría del producto"""
    if categoria in CATEGORIAS_GRANOS:
        return ["libras", "quintal", "arroba"]
    elif categoria in CATEGORIAS_CARNES:
        return ["libras", "unidad"]
    else:
        return ["unidad"]

def obtener_precios_producto(cursor, cod_barra, id_tienda):
    """Obtiene los precios del producto desde la última compra"""
    cursor.execute("""
        SELECT p.Nombre, p.categoria,
               pc.Precio_minorista, pc.Precio_mayorista1, pc.Precio_mayorista2
        FROM ProductoxCompra pc
        JOIN Producto p ON p.Cod_barra = pc.Cod_barra
        WHERE pc.Cod_barra = %s
          AND pc.id_tienda = %s
          AND p.id_tienda = %s
        ORDER BY pc.Id_compra DESC
        LIMIT 1
    """, (cod_barra, id_tienda, id_tienda))
    
    resultado = cursor.fetchone()
    if resultado:
        return {
            "nombre": resultado[0],
            "categoria": resultado[1],
            "precio_minorista": float(resultado[2]) if resultado[2] else 0,
            "precio_mayorista1": float(resultado[3]) if resultado[3] else 0,
            "precio_mayorista2": float(resultado[4]) if resultado[4] else 0,
        }
    return None

def obtener_existencia(cursor, cod_barra, id_tienda):
    """Calcula la existencia actual del producto en la tienda"""
    cursor.execute("""
        SELECT
            COALESCE((SELECT SUM(pc.cantidad_comprada)
                      FROM ProductoxCompra pc
                      WHERE pc.Cod_barra = %s AND pc.id_tienda = %s), 0) -
            COALESCE((SELECT SUM(pv.Cantidad_vendida)
                      FROM ProductoxVenta pv
                      WHERE pv.Cod_barra = %s AND pv.id_tienda = %s), 0)
        AS existencia
    """, (cod_barra, id_tienda, cod_barra, id_tienda))
    row = cursor.fetchone()
    return float(row[0]) if row and row[0] is not None else 0.0

def modulo_ventas():
    # ✅ Validación multi-tienda
    if not st.session_state.get("logueado") or "id_empleado" not in st.session_state or "id_tienda" not in st.session_state:
        st.error("⚠️ Debes iniciar sesión para registrar ventas.")
        st.stop()

    id_tienda = st.session_state["id_tienda"]
    id_empleado = st.session_state["id_empleado"]

    st.title("💵 Registro de Ventas")

    conn = obtener_conexion()
    if not conn:
        st.error("❌ No se pudo conectar a la base de datos.")
        st.stop()

    cursor = conn.cursor()

    # ---- Estado base ----
    if "productos_vendidos" not in st.session_state:
        st.session_state["productos_vendidos"] = []
    if "form_data_codigo_barras" not in st.session_state:
        st.session_state["form_data_codigo_barras"] = ""

    # flag para reiniciar en el próximo ciclo
    if st.session_state.get("_reset_venta_next_run"):
        st.session_state["_reset_venta_next_run"] = False
        st.session_state["form_data_codigo_barras"] = ""
        st.session_state.pop("venta_fecha", None)
        st.session_state.pop("venta_tipo_cliente", None)
        st.session_state.pop("venta_precio_venta", None)
        st.session_state.pop("venta_cantidad", None)
        st.session_state.pop("unidad_select", None)

    # --- Fecha de venta ---
    fecha_venta = st.date_input("📅 Fecha de la venta", datetime.now().date(), key="venta_fecha")

    st.info(f"🧑‍💼 Empleado: **{st.session_state.get('nombre_empleado', 'Usuario')}** | 🏪 Tienda ID: **{id_tienda}**")

    st.markdown("---")

    # ---- Código de barras ----
    cod_barra = st.text_input(
        "🔍 Código de barras del producto",
        key="form_data_codigo_barras",
        placeholder="Ej: 123456789"
    )

    producto_info = None
    existencia = 0
    unidades_disponibles = ["unidad"]

    if cod_barra:
        # Obtener existencia
        existencia = obtener_existencia(cursor, cod_barra, id_tienda)
        st.info(f"📦 Existencia actual: **{existencia:.2f}**")
        
        if existencia <= 0:
            st.error("❌ Este producto no tiene stock disponible para la venta.")
        else:
            # Obtener información del producto
            producto_info = obtener_precios_producto(cursor, cod_barra, id_tienda)
            
            if producto_info:
                st.success(f"✅ Producto encontrado: **{producto_info['nombre']}**")
                st.info(f"📁 Categoría: **{producto_info['categoria']}**")
                
                # 🔥 Determinar unidades según la categoría
                unidades_disponibles = obtener_unidades_por_categoria(producto_info['categoria'])
                
                # Mostrar precios disponibles
                st.markdown("**💰 Precios configurados:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Minorista", f"${producto_info['precio_minorista']:.2f}")
                with col2:
                    st.metric("Mayorista 1", f"${producto_info['precio_mayorista1']:.2f}")
                with col3:
                    st.metric("Mayorista 2", f"${producto_info['precio_mayorista2']:.2f}")
                
                # ---- Tipo de cliente ----
                tipo_cliente = st.radio(
                    "🧾 Seleccione el tipo de cliente",
                    ["Minorista", "Mayorista 1", "Mayorista 2"],
                    key="venta_tipo_cliente"
                )
                
                # Seleccionar precio según tipo de cliente
                if tipo_cliente == "Minorista":
                    precio_base = producto_info['precio_minorista']
                elif tipo_cliente == "Mayorista 1":
                    precio_base = producto_info['precio_mayorista1']
                else:
                    precio_base = producto_info['precio_mayorista2']
                
                if precio_base <= 0:
                    st.error("❌ No hay precio configurado para este tipo de cliente.")
                else:
                    # ---- Precio de venta (editable) ----
                    precio_venta = st.number_input(
                        "💲 Precio de venta",
                        min_value=0.01,
                        value=float(precio_base),
                        step=0.01,
                        format="%.2f",
                        key="venta_precio_venta"
                    )
                    
                    # ---- Unidad de venta (solo si hay unidades disponibles) ----
                    unidad = st.selectbox(
                        "📏 Unidad de venta",
                        unidades_disponibles,
                        key="unidad_select"
                    )
                    
                    # ---- Cantidad vendida ----
                    cantidad = st.number_input(
                        "📦 Cantidad vendida",
                        min_value=0.01 if unidad != "unidad" else 1,
                        step=0.01 if unidad != "unidad" else 1,
                        format="%.2f" if unidad != "unidad" else "%.0f",
                        key="venta_cantidad"
                    )
                    
                    # ---- Conversión a libras (solo para unidades que no sean "unidad") ----
                    if unidad in ["libras", "quintal", "arroba"]:
                        factor_conversion = CONVERSIONES_A_LIBRAS.get(unidad, 1)
                        cantidad_convertida = cantidad * factor_conversion
                        st.markdown(f"**🔄 Valor convertido en libras:** {cantidad_convertida:.2f} libras")
                        cantidad_guardar = cantidad_convertida
                    else:
                        cantidad_guardar = cantidad
                    
                    # ---- Subtotal ----
                    subtotal = round(precio_venta * cantidad_guardar, 2)
                    st.markdown(f"**🧾 Subtotal:** ${subtotal:.2f}")
                    
                    # ---- Agregar a la venta ----
                    if st.button("🛒 Agregar producto a la venta", type="primary"):
                        if cantidad_guardar > existencia:
                            st.error(f"❌ No hay suficiente stock. Disponible: {existencia:.2f}")
                        else:
                            producto_venta = {
                                "cod_barra": cod_barra,
                                "nombre": producto_info['nombre'],
                                "precio_venta": float(precio_venta),
                                "cantidad": cantidad_guardar,
                                "cantidad_original": cantidad,
                                "unidad": unidad,
                                "subtotal": float(subtotal),
                                "tipo_cliente": tipo_cliente,
                            }
                            st.session_state["productos_vendidos"].append(producto_venta)
                            st.session_state["_reset_venta_next_run"] = True
                            st.success("✅ Producto agregado a la venta.")
                            st.rerun()
            else:
                st.warning("❌ Producto no encontrado o sin precios configurados.")

    st.markdown("---")

    # ---- Listado de productos vendidos ----
    if st.session_state["productos_vendidos"]:
        st.subheader("🧾 Productos en esta venta")
        
        total_venta = 0.0
        for i, prod in enumerate(st.session_state["productos_vendidos"]):
            total_venta += prod["subtotal"]
            
            # Mostrar información del producto
            unidad_mostrar = prod.get("unidad", "unidad")
            cantidad_mostrar = prod.get("cantidad_original", prod["cantidad"])
            
            st.markdown(
                f"**{prod['nombre']}** — {cantidad_mostrar:.2f} {unidad_mostrar} — "
                f"Precio: ${prod['precio_venta']:.2f} — "
                f"Subtotal: ${prod['subtotal']:.2f} — "
                f"**Cliente:** {prod['tipo_cliente']}"
            )
            
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button(f"✏️ Editar", key=f"editar_venta_{i}"):
                    st.info("Funcionalidad de edición en desarrollo")
            with col2:
                if st.button(f"❌ Eliminar", key=f"eliminar_venta_{i}"):
                    st.session_state["productos_vendidos"].pop(i)
                    st.success("🗑️ Producto eliminado de la venta.")
                    st.rerun()
        
        st.markdown("---")
        st.markdown(f"### 💵 Total de la venta: **${total_venta:.2f}**")
        
        # ---- Registrar venta ----
        if st.button("✅ Registrar venta", type="primary"):
            try:
                # Obtener último ID de venta para esta tienda
                cursor.execute("SELECT MAX(Id_venta) FROM Venta WHERE id_tienda = %s", (id_tienda,))
                ultimo_id = cursor.fetchone()[0]
                nuevo_id = 1 if ultimo_id is None else int(ultimo_id) + 1
                
                # Insertar venta
                cursor.execute(
                    "INSERT INTO Venta (Id_venta, Fecha, Id_empleado, id_tienda) VALUES (%s, %s, %s, %s)",
                    (nuevo_id, fecha_venta, id_empleado, id_tienda)
                )
                
                # Insertar detalles
                for prod in st.session_state["productos_vendidos"]:
                    cursor.execute(
                        """
                        INSERT INTO ProductoxVenta
                        (Id_venta, Cod_barra, Cantidad_vendida, Tipo_de_cliente, Precio_Venta, id_tienda)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            nuevo_id,
                            prod["cod_barra"],
                            prod["cantidad"],
                            prod["tipo_cliente"],
                            round(prod["precio_venta"], 2),
                            id_tienda,
                        ),
                    )
                
                conn.commit()
                st.success(f"✅ Venta registrada exitosamente con ID {nuevo_id}.")
                st.session_state["productos_vendidos"] = []
                st.session_state["_reset_venta_next_run"] = True
                st.rerun()
                
            except Exception as e:
                conn.rollback()
                st.error(f"⚠️ Error al registrar la venta: {e}")
    
    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.session_state["productos_vendidos"] = []
        st.session_state["_reset_venta_next_run"] = True
        st.rerun()
    
    cursor.close()
    conn.close()
