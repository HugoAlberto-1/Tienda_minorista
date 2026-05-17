import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

CONVERSIONES_A_LIBRAS = {
    "libras": 1,
    "arroba": 25,
    "quintal": 100,
}

CATEGORIAS_GRANOS = [
    "Granos y productos a granel",
    "Abarrotes",
    "Sopas, pastas y consomés"
]

CATEGORIAS_CARNES = [
    "Carnes y congelados"
]

def obtener_unidades_por_categoria(categoria):
    if categoria in CATEGORIAS_GRANOS:
        return ["libras", "quintal", "arroba"]
    elif categoria in CATEGORIAS_CARNES:
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
            
            # ✅ Obtener TODAS las compras para calcular existencia POR UNIDAD
            cursor.execute("""
                SELECT unidad, SUM(cantidad_comprada) as total_comprado
                FROM ProductoxCompra
                WHERE Cod_barra = %s AND id_tienda = %s
                GROUP BY unidad
            """, (cod_barra_real, id_tienda))
            
            compras_por_unidad = cursor.fetchall()
            
            # Calcular ventas por unidad
            cursor.execute("""
                SELECT unidad, SUM(Cantidad_vendida) as total_vendido
                FROM ProductoxVenta
                WHERE Cod_barra = %s AND id_tienda = %s
                GROUP BY unidad
            """, (cod_barra_real, id_tienda))
            
            ventas_por_unidad = cursor.fetchall()
            
            # Crear diccionarios de existencias por unidad
            existencias = {}
            for unidad, total_comprado in compras_por_unidad:
                existencias[unidad] = total_comprado
            
            for unidad, total_vendido in ventas_por_unidad:
                existencias[unidad] = existencias.get(unidad, 0) - total_vendido
            
            # ✅ Mostrar existencia en CADA unidad que tiene stock
            st.markdown("**📦 Existencia actual por unidad:**")
            for unidad, cantidad in existencias.items():
                if cantidad > 0:
                    st.info(f"• **{cantidad:.2f} {unidad}**")
            
            # Calcular existencia total en libras para validación
            existencia_total_libras = 0
            for unidad, cantidad in existencias.items():
                factor = CONVERSIONES_A_LIBRAS.get(unidad, 1)
                existencia_total_libras += cantidad * factor
            
            if existencia_total_libras <= 0:
                st.error("❌ Este producto no tiene stock disponible para la venta.")
            else:
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
                        st.metric("Minorista", f"${precio_minorista:.2f}" if precio_minorista > 0 else "No configurado")
                    with col2:
                        st.metric("Mayorista 1", f"${precio_mayorista1:.2f}" if precio_mayorista1 > 0 else "No configurado")
                    with col3:
                        st.metric("Mayorista 2", f"${precio_mayorista2:.2f}" if precio_mayorista2 > 0 else "No configurado")
                
                unidades_disponibles = obtener_unidades_por_categoria(categoria)
                
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
                    
                    if unidad_venta == "unidad":
                        cantidad = st.number_input(
                            "📦 Cantidad vendida (unidades)",
                            min_value=1,
                            step=1,
                            format="%.0f",
                            key="venta_cantidad"
                        )
                        cantidad_guardar = float(cantidad)
                    else:
                        cantidad = st.number_input(
                            f"📦 Cantidad vendida ({unidad_venta})",
                            min_value=0.01,
                            step=0.01,
                            format="%.2f",
                            key="venta_cantidad"
                        )
                        cantidad_guardar = cantidad
                    
                    # Verificar si hay suficiente stock en la unidad seleccionada
                    stock_en_unidad = existencias.get(unidad_venta, 0)
                    
                    if unidad_venta in existencias:
                        if cantidad_guardar > stock_en_unidad:
                            st.error(f"❌ No hay suficiente stock en {unidad_venta}. Disponible: {stock_en_unidad:.2f} {unidad_venta}")
                        else:
                            subtotal = round(precio_venta * cantidad_guardar, 2)
                            st.markdown(f"**🧾 Subtotal:** ${subtotal:.2f}")
                            
                            if st.button("🛒 Agregar producto a la venta", type="primary"):
                                producto_venta = {
                                    "cod_barra": cod_barra_real,
                                    "nombre": nombre_producto,
                                    "precio_venta": float(precio_venta),
                                    "cantidad": cantidad_guardar,
                                    "unidad": unidad_venta,
                                    "subtotal": float(subtotal),
                                    "tipo_cliente": tipo_cliente,
                                }
                                st.session_state["productos_vendidos"].append(producto_venta)
                                st.session_state["_reset_venta_next_run"] = True
                                st.success("✅ Producto agregado a la venta.")
                                st.rerun()
                    else:
                        st.warning(f"⚠️ No hay stock en {unidad_venta}. Las existencias disponibles son: {', '.join([f'{v:.2f} {u}' for u, v in existencias.items() if v > 0])}")

    st.markdown("---")

    if st.session_state["productos_vendidos"]:
        st.subheader("🧾 Productos en esta venta")
        
        total_venta = 0.0
        for i, prod in enumerate(st.session_state["productos_vendidos"]):
            total_venta += prod["subtotal"]
            
            st.markdown(
                f"**{prod['nombre']}** — {prod['cantidad']:.2f} {prod['unidad']} — "
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
                            prod["cantidad"],
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
