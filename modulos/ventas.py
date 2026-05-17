import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

CONVERSIONES_A_LIBRAS = {
    "libras": 1,
    "arroba": 25,
    "quintal": 100,
}

# 📁 Categorías que se consideran "granos"
CATEGORIAS_GRANOS = [
    "Granos y productos a granel",
    "Abarrotes",
    "Sopas, pastas y consomés"
]

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

    if cod_barra:
        # 🔍 Verificar que el producto existe
        cursor.execute("""
            SELECT p.Cod_barra, p.Nombre, p.categoria,
                   pc.unidad, pc.cantidad_comprada, pc.Precio_minorista, 
                   pc.Precio_mayorista1, pc.Precio_mayorista2
            FROM Producto p
            JOIN ProductoxCompra pc ON p.Cod_barra = pc.Cod_barra
            WHERE p.Cod_barra = %s AND p.id_tienda = %s AND pc.id_tienda = %s
            ORDER BY pc.Id_compra DESC
            LIMIT 1
        """, (cod_barra, id_tienda, id_tienda))
        
        producto_info = cursor.fetchone()
        
        if not producto_info:
            st.error("❌ Producto no encontrado o no tiene compras registradas.")
        else:
            (cod_barra_real, nombre_producto, categoria, 
             unidad_compra, cantidad_comprada, 
             precio_minorista, precio_mayorista1, precio_mayorista2) = producto_info
            
            st.success(f"✅ Producto encontrado: **{nombre_producto}**")
            st.info(f"📁 Categoría: **{categoria}**")
            
            # 🔍 Calcular existencia total en la unidad de compra
            cursor.execute("""
                SELECT 
                    COALESCE((SELECT SUM(pc.cantidad_comprada) 
                              FROM ProductoxCompra pc 
                              WHERE pc.Cod_barra = %s AND pc.id_tienda = %s), 0) -
                    COALESCE((SELECT SUM(pv.Cantidad_vendida) 
                              FROM ProductoxVenta pv 
                              WHERE pv.Cod_barra = %s AND pv.id_tienda = %s), 0)
                    AS existencia
            """, (cod_barra_real, id_tienda, cod_barra_real, id_tienda))
            
            resultado_existencia = cursor.fetchone()
            existencia = float(resultado_existencia[0]) if resultado_existencia else 0
            
            # Mostrar existencia en la unidad de compra
            st.info(f"📦 Existencia actual: **{existencia:.2f} {unidad_compra}**")
            
            if existencia <= 0:
                st.error("❌ Este producto no tiene stock disponible para la venta.")
            else:
                # Mostrar precios
                st.markdown("**💰 Precios configurados:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Minorista", f"${precio_minorista:.2f}" if precio_minorista else "No configurado")
                with col2:
                    st.metric("Mayorista 1", f"${precio_mayorista1:.2f}" if precio_mayorista1 else "No configurado")
                with col3:
                    st.metric("Mayorista 2", f"${precio_mayorista2:.2f}" if precio_mayorista2 else "No configurado")
                
                # ---- Tipo de cliente ----
                tipo_cliente = st.radio(
                    "🧾 Seleccione el tipo de cliente",
                    ["Minorista", "Mayorista 1", "Mayorista 2"],
                    key="venta_tipo_cliente"
                )
                
                # Seleccionar precio según tipo de cliente
                if tipo_cliente == "Minorista":
                    precio_base = precio_minorista
                elif tipo_cliente == "Mayorista 1":
                    precio_base = precio_mayorista1
                else:
                    precio_base = precio_mayorista2
                
                if not precio_base or precio_base <= 0:
                    st.error(f"❌ No hay precio configurado para {tipo_cliente}. Registre una compra primero.")
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
                    
                    # ---- Unidad de venta: SOLO la unidad de compra ----
                    st.info(f"📏 Este producto se vende en **{unidad_compra}** (unidad de compra original)")
                    
                    # ---- Si es grano, mostrar opción de venta en libras también ----
                    unidades_venta = [unidad_compra]
                    if categoria in CATEGORIAS_GRANOS and unidad_compra != "libras":
                        unidades_venta.append("libras")
                    
                    if len(unidades_venta) > 1:
                        unidad_venta = st.selectbox(
                            "📏 Unidad de venta",
                            unidades_venta,
                            key="unidad_select"
                        )
                    else:
                        unidad_venta = unidad_compra
                        st.markdown(f"**Unidad de venta:** {unidad_venta}")
                    
                    # ---- Cantidad vendida ----
                    if unidad_venta == "libras" and unidad_compra != "libras":
                        # Convertir de libras a la unidad de compra
                        st.caption(f"⚠️ Estás vendiendo en libras. La existencia está en {unidad_compra}")
                        
                        cantidad_libras = st.number_input(
                            f"📦 Cantidad vendida (libras)",
                            min_value=0.01,
                            step=0.01,
                            format="%.2f",
                            key="venta_cantidad"
                        )
                        # Convertir libras a la unidad de compra
                        factor_a_libras = CONVERSIONES_A_LIBRAS.get(unidad_compra, 1)
                        cantidad_en_unidad = cantidad_libras / factor_a_libras
                        cantidad_guardar = cantidad_en_unidad
                        st.caption(f"🔄 Equivalente en {unidad_compra}: {cantidad_en_unidad:.4f} {unidad_compra}")
                    else:
                        cantidad = st.number_input(
                            f"📦 Cantidad vendida ({unidad_venta})",
                            min_value=0.01 if unidad_venta != "unidad" else 1,
                            step=0.01 if unidad_venta != "unidad" else 1,
                            format="%.2f" if unidad_venta != "unidad" else "%.0f",
                            key="venta_cantidad"
                        )
                        cantidad_guardar = float(cantidad)
                    
                    # Validar que no exceda el stock
                    if cantidad_guardar > existencia:
                        st.error(f"❌ No hay suficiente stock. Disponible: {existencia:.2f} {unidad_compra}")
                    else:
                        # Calcular subtotal (en la unidad de compra original)
                        subtotal = round(precio_venta * cantidad_guardar, 2)
                        st.markdown(f"**🧾 Subtotal:** ${subtotal:.2f}")
                        
                        # ---- Agregar a la venta ----
                        if st.button("🛒 Agregar producto a la venta", type="primary"):
                            producto_venta = {
                                "cod_barra": cod_barra_real,
                                "nombre": nombre_producto,
                                "precio_venta": float(precio_venta),
                                "cantidad": cantidad_guardar,
                                "cantidad_mostrar": cantidad if unidad_venta != "libras" else cantidad_libras,
                                "unidad": unidad_venta,
                                "unidad_compra": unidad_compra,
                                "subtotal": float(subtotal),
                                "tipo_cliente": tipo_cliente,
                            }
                            st.session_state["productos_vendidos"].append(producto_venta)
                            st.session_state["_reset_venta_next_run"] = True
                            st.success("✅ Producto agregado a la venta.")
                            st.rerun()

    st.markdown("---")

    # ---- Listado de productos vendidos ----
    if st.session_state["productos_vendidos"]:
        st.subheader("🧾 Productos en esta venta")
        
        total_venta = 0.0
        for i, prod in enumerate(st.session_state["productos_vendidos"]):
            total_venta += prod["subtotal"]
            
            cantidad_mostrar = prod.get("cantidad_mostrar", prod["cantidad"])
            unidad_mostrar = prod.get("unidad", prod["unidad_compra"])
            
            st.markdown(
                f"**{prod['nombre']}** — {cantidad_mostrar:.2f} {unidad_mostrar} — "
                f"Precio: ${prod['precio_venta']:.2f} — "
                f"Subtotal: ${prod['subtotal']:.2f} — "
                f"**Cliente:** {prod['tipo_cliente']}"
            )
            
            col1, col2 = st.columns([1, 5])
            with col1:
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
