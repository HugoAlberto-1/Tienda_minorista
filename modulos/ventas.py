import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

CONVERSIONES_A_LIBRAS = {
    "libras": 1,
    "arroba": 25,
    "quintal": 100,
}

# 📁 Categorías que se consideran "granos" (mostrarán las 3 unidades)
CATEGORIAS_GRANOS = [
    "Granos y productos a granel",
    "Abarrotes",
    "Sopas, pastas y consomés"
]

# 📁 Categorías que son carnes (usarán la unidad de compra original)
CATEGORIAS_CARNES = [
    "Carnes y congelados"
]

def obtener_unidades_por_categoria(categoria, unidad_compra=None):
    """Retorna las unidades disponibles según la categoría del producto"""
    if categoria in CATEGORIAS_GRANOS:
        return ["libras", "quintal", "arroba"]
    elif categoria in CATEGORIAS_CARNES:
        if unidad_compra:
            return [unidad_compra]
        return ["libras", "unidad"]
    else:
        return ["unidad"]

def modulo_ventas():
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

    if "productos_vendidos" not in st.session_state:
        st.session_state["productos_vendidos"] = []
    if "form_data_codigo_barras" not in st.session_state:
        st.session_state["form_data_codigo_barras"] = ""

    if st.session_state.get("_reset_venta_next_run"):
        st.session_state["_reset_venta_next_run"] = False
        st.session_state["form_data_codigo_barras"] = ""
        st.session_state.pop("venta_fecha", None)
        st.session_state.pop("venta_tipo_cliente", None)
        st.session_state.pop("venta_precio_venta", None)
        st.session_state.pop("venta_cantidad", None)
        st.session_state.pop("unidad_select", None)

    fecha_venta = st.date_input("📅 Fecha de la venta", datetime.now().date(), key="venta_fecha")

    st.info(f"🧑‍💼 Empleado: **{st.session_state.get('nombre_empleado', 'Usuario')}** | 🏪 Tienda ID: **{id_tienda}**")

    st.markdown("---")

    cod_barra = st.text_input(
        "🔍 Código de barras del producto",
        key="form_data_codigo_barras",
        placeholder="Ej: 123456789"
    )

    if cod_barra:
        cursor.execute("""
            SELECT Cod_barra, Nombre, categoria 
            FROM Producto 
            WHERE Cod_barra = %s AND id_tienda = %s
        """, (cod_barra, id_tienda))
        
        producto_base = cursor.fetchone()
        
        if not producto_base:
            st.error("❌ Producto no encontrado en el catálogo de esta tienda.")
        else:
            cod_barra_real, nombre_producto, categoria = producto_base
            st.success(f"✅ Producto encontrado: **{nombre_producto}**")
            st.info(f"📁 Categoría: **{categoria}**")
            
            # 🔍 Obtener TODAS las compras
            cursor.execute("""
                SELECT unidad, cantidad_comprada
                FROM ProductoxCompra
                WHERE Cod_barra = %s AND id_tienda = %s
            """, (cod_barra_real, id_tienda))
            
            compras = cursor.fetchall()
            
            # 🔍 Obtener TODAS las ventas
            cursor.execute("""
                SELECT unidad, Cantidad_vendida
                FROM ProductoxVenta
                WHERE Cod_barra = %s AND id_tienda = %s
            """, (cod_barra_real, id_tienda))
            
            ventas = cursor.fetchall()
            
            # Calcular total en libras para granos
            if categoria in CATEGORIAS_GRANOS:
                # Sumar todas las compras en libras
                total_comprado_libras = 0
                for unidad, cantidad in compras:
                    if unidad == "libras":
                        total_comprado_libras += cantidad
                    elif unidad == "quintal":
                        total_comprado_libras += cantidad * 100
                    elif unidad == "arroba":
                        total_comprado_libras += cantidad * 25
                    else:
                        total_comprado_libras += cantidad
                
                # Sumar todas las ventas en libras
                total_vendido_libras = 0
                for unidad, cantidad in ventas:
                    if unidad == "libras":
                        total_vendido_libras += cantidad
                    elif unidad == "quintal":
                        total_vendido_libras += cantidad * 100
                    elif unidad == "arroba":
                        total_vendido_libras += cantidad * 25
                    else:
                        total_vendido_libras += cantidad
                
                existencia_libras = total_comprado_libras - total_vendido_libras
                
                # Mostrar existencia en las 3 unidades
                st.markdown("**📦 Existencia actual:**")
                
                libras = existencia_libras
                quintales = existencia_libras / 100
                arrobas = existencia_libras / 25
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📦 Libras", f"{libras:.2f}")
                with col2:
                    st.metric("📦 Quintales", f"{quintales:.2f}")
                with col3:
                    st.metric("📦 Arrobas", f"{arrobas:.2f}")
                
                if existencia_libras <= 0:
                    st.error("❌ Este producto no tiene stock disponible para la venta.")
                else:
                    # Obtener precios
                    cursor.execute("""
                        SELECT Precio_minorista, Precio_mayorista1, Precio_mayorista2
                        FROM ProductoxCompra
                        WHERE Cod_barra = %s AND id_tienda = %s
                        ORDER BY Id_compra DESC
                        LIMIT 1
                    """, (cod_barra_real, id_tienda))
                    
                    precios = cursor.fetchone()
                    
                    if precios:
                        precio_minorista = float(precios[0]) if precios[0] else 0
                        precio_mayorista1 = float(precios[1]) if precios[1] else 0
                        precio_mayorista2 = float(precios[2]) if precios[2] else 0
                    else:
                        st.warning("⚠️ Este producto no tiene precios configurados.")
                        precio_minorista = 0
                        precio_mayorista1 = 0
                        precio_mayorista2 = 0
                    
                    if precio_minorista > 0 or precio_mayorista1 > 0 or precio_mayorista2 > 0:
                        st.markdown("**💰 Precios configurados:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Minorista", f"${precio_minorista:.2f}")
                        with col2:
                            st.metric("Mayorista 1", f"${precio_mayorista1:.2f}")
                        with col3:
                            st.metric("Mayorista 2", f"${precio_mayorista2:.2f}")
                    
                    unidades_disponibles = ["libras", "quintal", "arroba"]
                    
                    tipo_cliente = st.radio(
                        "🧾 Seleccione el tipo de cliente",
                        ["Minorista", "Mayorista 1", "Mayorista 2"],
                        key="venta_tipo_cliente"
                    )
                    
                    if tipo_cliente == "Minorista":
                        precio_base = precio_minorista
                    elif tipo_cliente == "Mayorista 1":
                        precio_base = precio_mayorista1
                    else:
                        precio_base = precio_mayorista2
                    
                    if precio_base <= 0:
                        st.error(f"❌ No hay precio configurado para {tipo_cliente}.")
                    else:
                        precio_venta = st.number_input(
                            "💲 Precio de venta",
                            min_value=0.01,
                            value=float(precio_base),
                            step=0.01,
                            format="%.2f",
                            key="venta_precio_venta"
                        )
                        
                        unidad_venta = st.selectbox(
                            "📏 Unidad de venta",
                            unidades_disponibles,
                            key="unidad_select"
                        )
                        
                        # Mostrar información de conversiones
                        st.info("💡 **Factores de conversión:** 1 quintal = 100 libras | 1 arroba = 25 libras")
                        
                        # Calcular stock disponible en la unidad seleccionada
                        if unidad_venta == "libras":
                            stock_disponible = existencia_libras
                            st.caption(f"📦 Stock disponible: {stock_disponible:.2f} libras")
                            
                            cantidad = st.number_input(
                                f"📦 Cantidad vendida (libras)",
                                min_value=0.01,
                                step=0.01,
                                format="%.2f",
                                key="venta_cantidad"
                            )
                            cantidad_en_libras = cantidad
                            cantidad_original = cantidad
                            
                        elif unidad_venta == "quintal":
                            stock_disponible = existencia_libras / 100
                            st.caption(f"📦 Stock disponible: {stock_disponible:.4f} quintales")
                            
                            cantidad = st.number_input(
                                f"📦 Cantidad vendida (quintales)",
                                min_value=0.01,
                                step=0.01,
                                format="%.4f",
                                key="venta_cantidad"
                            )
                            cantidad_en_libras = cantidad * 100  # 1 quintal = 100 libras
                            cantidad_original = cantidad
                            
                            # Mostrar conversión
                            st.caption(f"🔄 {cantidad:.4f} quintal(es) = {cantidad_en_libras:.2f} libras")
                            
                        else:  # arroba
                            stock_disponible = existencia_libras / 25
                            st.caption(f"📦 Stock disponible: {stock_disponible:.4f} arrobas")
                            
                            cantidad = st.number_input(
                                f"📦 Cantidad vendida (arrobas)",
                                min_value=0.01,
                                step=0.01,
                                format="%.4f",
                                key="venta_cantidad"
                            )
                            cantidad_en_libras = cantidad * 25  # 1 arroba = 25 libras
                            cantidad_original = cantidad
                            
                            # Mostrar conversión
                            st.caption(f"🔄 {cantidad:.4f} arroba(s) = {cantidad_en_libras:.2f} libras")
                        
                        # Validar stock
                        if cantidad_en_libras > existencia_libras:
                            st.error(f"❌ No hay suficiente stock. Stock disponible: {stock_disponible:.4f} {unidad_venta}")
                        else:
                            # El precio_venta es por LIBRA (precio por libra)
                            subtotal = round(precio_venta * cantidad_en_libras, 2)
                            
                            # Mostrar resumen de precios
                            if unidad_venta == "libras":
                                st.markdown(f"**💰 Precio por libra:** ${precio_venta:.2f}")
                            elif unidad_venta == "quintal":
                                precio_por_quintal = precio_venta * 100
                                st.markdown(f"**💰 Precio por quintal:** ${precio_por_quintal:.2f} (equiv. a ${precio_venta:.2f}/libra)")
                            else:  # arroba
                                precio_por_arroba = precio_venta * 25
                                st.markdown(f"**💰 Precio por arroba:** ${precio_por_arroba:.2f} (equiv. a ${precio_venta:.2f}/libra)")
                            
                            st.markdown(f"**🧾 Subtotal:** ${subtotal:.2f}")
                            
                            if st.button("🛒 Agregar producto a la venta", type="primary"):
                                producto_venta = {
                                    "cod_barra": cod_barra_real,
                                    "nombre": nombre_producto,
                                    "precio_venta": float(precio_venta),
                                    "cantidad": cantidad_original,
                                    "cantidad_base": cantidad_en_libras,
                                    "unidad": unidad_venta,
                                    "subtotal": float(subtotal),
                                    "tipo_cliente": tipo_cliente,
                                }
                                st.session_state["productos_vendidos"].append(producto_venta)
                                st.session_state["_reset_venta_next_run"] = True
                                st.success("✅ Producto agregado a la venta.")
                                st.rerun()
            
            else:
                # Para otros productos (no granos)
                # Calcular existencias por unidad
                existencias = {}
                for unidad, cantidad in compras:
                    existencias[unidad] = existencias.get(unidad, 0) + cantidad
                
                for unidad, cantidad in ventas:
                    existencias[unidad] = existencias.get(unidad, 0) - cantidad
                
                # Mostrar existencia
                st.markdown("**📦 Existencia actual:**")
                for unidad, cantidad in existencias.items():
                    if cantidad > 0:
                        st.info(f"• **{cantidad:.2f} {unidad}**")
                
                tiene_stock = any(cantidad > 0 for cantidad in existencias.values())
                
                if not tiene_stock:
                    st.error("❌ Este producto no tiene stock disponible para la venta.")
                else:
                    # Obtener precios
                    cursor.execute("""
                        SELECT Precio_minorista, Precio_mayorista1, Precio_mayorista2
                        FROM ProductoxCompra
                        WHERE Cod_barra = %s AND id_tienda = %s
                        ORDER BY Id_compra DESC
                        LIMIT 1
                    """, (cod_barra_real, id_tienda))
                    
                    precios = cursor.fetchone()
                    
                    if precios:
                        precio_minorista = float(precios[0]) if precios[0] else 0
                        precio_mayorista1 = float(precios[1]) if precios[1] else 0
                        precio_mayorista2 = float(precios[2]) if precios[2] else 0
                    else:
                        st.warning("⚠️ Este producto no tiene precios configurados.")
                        precio_minorista = 0
                        precio_mayorista1 = 0
                        precio_mayorista2 = 0
                    
                    if precio_minorista > 0 or precio_mayorista1 > 0 or precio_mayorista2 > 0:
                        st.markdown("**💰 Precios configurados:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Minorista", f"${precio_minorista:.2f}")
                        with col2:
                            st.metric("Mayorista 1", f"${precio_mayorista1:.2f}")
                        with col3:
                            st.metric("Mayorista 2", f"${precio_mayorista2:.2f}")
                    
                    # Unidad de venta para no granos
                    if categoria in CATEGORIAS_CARNES:
                        # Para carnes, usar la unidad que tenga stock
                        unidades_con_stock = [u for u, c in existencias.items() if c > 0]
                        if unidades_con_stock:
                            unidad_principal = unidades_con_stock[0]
                            unidades_disponibles = [unidad_principal]
                        else:
                            unidades_disponibles = ["unidad"]
                    else:
                        unidades_disponibles = ["unidad"]
                    
                    tipo_cliente = st.radio(
                        "🧾 Seleccione el tipo de cliente",
                        ["Minorista", "Mayorista 1", "Mayorista 2"],
                        key="venta_tipo_cliente"
                    )
                    
                    if tipo_cliente == "Minorista":
                        precio_base = precio_minorista
                    elif tipo_cliente == "Mayorista 1":
                        precio_base = precio_mayorista1
                    else:
                        precio_base = precio_mayorista2
                    
                    if precio_base <= 0:
                        st.error(f"❌ No hay precio configurado para {tipo_cliente}.")
                    else:
                        precio_venta = st.number_input(
                            "💲 Precio de venta",
                            min_value=0.01,
                            value=float(precio_base),
                            step=0.01,
                            format="%.2f",
                            key="venta_precio_venta"
                        )
                        
                        unidad_venta = st.selectbox(
                            "📏 Unidad de venta",
                            unidades_disponibles,
                            key="unidad_select"
                        )
                        
                        stock_disponible = existencias.get(unidad_venta, 0)
                        st.caption(f"📦 Stock disponible: {stock_disponible:.2f} {unidad_venta}")
                        
                        if unidad_venta == "unidad":
                            cantidad = st.number_input(
                                f"📦 Cantidad vendida ({unidad_venta})",
                                min_value=1,
                                step=1,
                                format="%d",
                                key="venta_cantidad"
                            )
                            cantidad_base = float(cantidad)
                        else:
                            cantidad = st.number_input(
                                f"📦 Cantidad vendida ({unidad_venta})",
                                min_value=0.01,
                                step=0.01,
                                format="%.2f",
                                key="venta_cantidad"
                            )
                            cantidad_base = cantidad
                        
                        if cantidad_base > stock_disponible:
                            st.error(f"❌ No hay suficiente stock. Disponible: {stock_disponible:.2f} {unidad_venta}")
                        else:
                            subtotal = round(precio_venta * cantidad_base, 2)
                            st.markdown(f"**🧾 Subtotal:** ${subtotal:.2f}")
                            
                            if st.button("🛒 Agregar producto a la venta", type="primary"):
                                producto_venta = {
                                    "cod_barra": cod_barra_real,
                                    "nombre": nombre_producto,
                                    "precio_venta": float(precio_venta),
                                    "cantidad": cantidad,
                                    "cantidad_base": cantidad_base,
                                    "unidad": unidad_venta,
                                    "subtotal": float(subtotal),
                                    "tipo_cliente": tipo_cliente,
                                }
                                st.session_state["productos_vendidos"].append(producto_venta)
                                st.session_state["_reset_venta_next_run"] = True
                                st.success("✅ Producto agregado a la venta.")
                                st.rerun()

    st.markdown("---")

    if st.session_state["productos_vendidos"]:
        st.subheader("🧾 Productos en esta venta")
        
        total_venta = 0.0
        for i, prod in enumerate(st.session_state["productos_vendidos"]):
            total_venta += prod["subtotal"]
            
            # Mostrar información con la unidad original
            if prod["unidad"] == "libras":
                st.markdown(
                    f"**{prod['nombre']}** — {prod['cantidad']:.2f} {prod['unidad']} — "
                    f"Precio: ${prod['precio_venta']:.2f}/libra — "
                    f"Subtotal: ${prod['subtotal']:.2f} — "
                    f"**Cliente:** {prod['tipo_cliente']}"
                )
            elif prod["unidad"] == "quintal":
                precio_por_quintal = prod['precio_venta'] * 100
                st.markdown(
                    f"**{prod['nombre']}** — {prod['cantidad']:.4f} {prod['unidad']} — "
                    f"Precio: ${precio_por_quintal:.2f}/{prod['unidad']} — "
                    f"Subtotal: ${prod['subtotal']:.2f} — "
                    f"**Cliente:** {prod['tipo_cliente']}"
                )
            else:  # arroba
                precio_por_arroba = prod['precio_venta'] * 25
                st.markdown(
                    f"**{prod['nombre']}** — {prod['cantidad']:.4f} {prod['unidad']} — "
                    f"Precio: ${precio_por_arroba:.2f}/{prod['unidad']} — "
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
        
        if st.button("✅ Registrar venta", type="primary"):
            try:
                cursor.execute("SELECT MAX(Id_venta) FROM Venta WHERE id_tienda = %s", (id_tienda,))
                ultimo_id = cursor.fetchone()[0]
                nuevo_id = 1 if ultimo_id is None else int(ultimo_id) + 1
                
                cursor.execute(
                    "INSERT INTO Venta (Id_venta, Fecha, Id_empleado, id_tienda) VALUES (%s, %s, %s, %s)",
                    (nuevo_id, fecha_venta, id_empleado, id_tienda)
                )
                
                for prod in st.session_state["productos_vendidos"]:
                    cursor.execute(
                        """
                        INSERT INTO ProductoxVenta
                        (Id_venta, Cod_barra, Cantidad_vendida, Tipo_de_cliente, Precio_Venta, id_tienda, unidad)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            nuevo_id,
                            prod["cod_barra"],
                            prod["cantidad_base"],
                            prod["tipo_cliente"],
                            round(prod["precio_venta"], 2),
                            id_tienda,
                            prod["unidad"],
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
