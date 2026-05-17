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

def obtener_unidades_por_categoria(categoria):
    """Devuelve las unidades disponibles según la categoría del producto"""
    if categoria in CATEGORIAS_GRANOS:
        return ["libras", "quintal", "arroba"]
    elif categoria == "Carnes y congelados":
        # Carnes puede ser comprado en libras o en unidades
        return ["libras", "unidad"]
    else:
        return ["unidad"]

def modulo_compras():
    if not st.session_state.get("logueado") or "id_empleado" not in st.session_state or "id_tienda" not in st.session_state:
        st.error("⚠️ Debes iniciar sesión para registrar compras.")
        st.stop()

    id_tienda = st.session_state["id_tienda"]

    st.title("🧾 Registro de Compras")

    conn = obtener_conexion()
    if not conn:
        st.error("❌ No se pudo conectar a la base de datos.")
        st.stop()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT Cod_barra, Nombre, categoria FROM Producto WHERE id_tienda = %s",
        (id_tienda,)
    )
    productos = cursor.fetchall()

    if not productos:
        st.warning("⚠️ No hay productos disponibles para esta tienda.")
        cursor.close()
        conn.close()
        return

    if "productos_seleccionados" not in st.session_state:
        st.session_state["productos_seleccionados"] = []
    if "editar_indice" not in st.session_state:
        st.session_state["editar_indice"] = None
    if "form_data" not in st.session_state:
        st.session_state["form_data"] = {
            "precio_compra": 0.01,
            "cantidad": 1,
            "unidad": "libras",
            "fecha_vencimiento": None,
        }
    if "form_data_codigo_barras" not in st.session_state:
        st.session_state["form_data_codigo_barras"] = ""

    if st.session_state.get("_reset_form_next_run"):
        st.session_state["_reset_form_next_run"] = False
        st.session_state["form_data"] = {
            "precio_compra": 0.01,
            "cantidad": 1,
            "unidad": "libras",
            "fecha_vencimiento": None,
        }
        st.session_state["form_data_codigo_barras"] = ""
        st.session_state.pop("form_data_fecha_vencimiento", None)

    if st.session_state["editar_indice"] is not None and "edit_loaded" not in st.session_state:
        prod_edit = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
        st.session_state["form_data_codigo_barras"] = prod_edit["cod_barra"]
        st.session_state["form_data"] = {
            "precio_compra": float(prod_edit["precio_compra"]),
            "cantidad": int(prod_edit["cantidad"]),
            "unidad": prod_edit["unidad"],
            "fecha_vencimiento": prod_edit.get("fecha_vencimiento"),
        }
        st.session_state["edit_loaded"] = True

    codigo_barras_disabled = st.session_state["editar_indice"] is not None

    codigo_buscado = st.text_input(
        "🔍 Código de barras del producto",
        key="form_data_codigo_barras",
        disabled=codigo_barras_disabled,
        placeholder="Ej: 123456789"
    )

    producto_encontrado = None
    categoria_producto = None
    unidades_disponibles = ["unidad"]
    
    if codigo_buscado and not codigo_barras_disabled:
        producto_encontrado = next(
            (p for p in productos if p[0] == codigo_buscado),
            None,
        )
        if producto_encontrado:
            codigo, nombre, categoria_producto = producto_encontrado
            st.success(f"✅ Producto encontrado: **{nombre}**")
            st.info(f"📁 Categoría: **{categoria_producto}**")
            
            unidades_disponibles = obtener_unidades_por_categoria(categoria_producto)
            
            # Si la unidad actual no está disponible, seleccionar la primera
            if st.session_state["form_data"]["unidad"] not in unidades_disponibles:
                st.session_state["form_data"]["unidad"] = unidades_disponibles[0]
            
            # Solo mostrar fecha de vencimiento para productos perecederos
            if categoria_producto != "Granos y productos a granel":
                st.session_state["form_data"]["fecha_vencimiento"] = st.date_input(
                    "📅 Fecha de vencimiento (opcional)",
                    key="form_data_fecha_vencimiento",
                    value=None
                )
        else:
            st.warning("⚠️ Producto no encontrado.")

    if producto_encontrado:
        st.session_state["form_data"]["unidad"] = st.selectbox(
            "📏 Unidad de compra",
            unidades_disponibles,
            index=unidades_disponibles.index(st.session_state["form_data"]["unidad"]) if st.session_state["form_data"]["unidad"] in unidades_disponibles else 0,
            key="unidad_select"
        )
    else:
        st.selectbox(
            "📏 Unidad de compra",
            ["Seleccione un producto primero"],
            disabled=True,
        )

    unidad = st.session_state["form_data"]["unidad"]

    precio_compra = st.number_input(
        "💰 Precio de compra",
        min_value=0.01,
        step=0.01,
        key="form_data_precio_compra",
        value=st.session_state["form_data"].get("precio_compra", 0.01),
    )
    st.session_state["form_data"]["precio_compra"] = precio_compra

    st.session_state["form_data"]["cantidad"] = st.number_input(
        "📦 Cantidad comprada",
        min_value=1,
        max_value=10000,
        step=1,
        value=st.session_state["form_data"]["cantidad"],
    )
    cantidad = st.session_state["form_data"]["cantidad"]

    subtotal_actual = round(precio_compra * cantidad, 2)
    st.markdown(f"**🧾 Subtotal del producto actual:** ${subtotal_actual:.2f}")

    precio_minorista = round(precio_compra / 0.70, 2)
    st.markdown(f"💡 **Precio de venta sugerido (Al Detalle):** ${precio_minorista:.2f}")

    precio_sugerido2 = round(precio_compra / 0.75, 2)
    st.markdown(f"💡 **Precio de venta sugerido (Mayorista #1):** ${precio_sugerido2:.2f}")

    precio_sugerido = round(precio_compra / 0.80, 2)
    st.markdown(f"💡 **Precio de venta sugerido (Mayorista #2):** ${precio_sugerido:.2f}")

    precio_venta = st.number_input(
        "💰 Precio de venta al detalle",
        min_value=0.01,
        value=precio_minorista,
        format="%.2f",
    )
    precio_venta2 = st.number_input(
        "💰 Precio de venta mayorista #1",
        min_value=0.01,
        value=precio_sugerido2,
        format="%.2f",
    )
    precio_venta3 = st.number_input(
        "💰 Precio de venta mayorista #2",
        min_value=0.01,
        value=precio_sugerido,
        format="%.2f",
    )

    boton_texto = "💾 Actualizar producto" if st.session_state["editar_indice"] is not None else "💾 Agregar producto"
    if st.button(boton_texto, type="primary"):
        if producto_encontrado or codigo_barras_disabled:
            if st.session_state["editar_indice"] is not None:
                prod_ref = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
                producto = {
                    "cod_barra": codigo_buscado,
                    "nombre": prod_ref["nombre"],
                    "cantidad": cantidad,
                    "precio_compra": precio_compra,
                    "precio_venta2": precio_venta2,
                    "precio_venta3": precio_venta3,
                    "precio_venta": precio_venta,
                    "unidad": unidad,
                    "fecha_vencimiento": st.session_state["form_data"].get("fecha_vencimiento"),
                }
                st.session_state["productos_seleccionados"][st.session_state["editar_indice"]] = producto
                st.success("✅ Producto actualizado correctamente.")
                st.session_state["editar_indice"] = None
                st.session_state.pop("edit_loaded", None)
            else:
                producto = {
                    "cod_barra": codigo_buscado,
                    "nombre": producto_encontrado[1],
                    "cantidad": cantidad,
                    "precio_compra": precio_compra,
                    "precio_venta2": precio_venta2,
                    "precio_venta3": precio_venta3,
                    "precio_venta": precio_venta,
                    "unidad": unidad,
                    "fecha_vencimiento": st.session_state["form_data"].get("fecha_vencimiento"),
                }
                st.session_state["productos_seleccionados"].append(producto)
                st.success("✅ Producto agregado a la compra.")
                st.session_state["_reset_form_next_run"] = True
                st.rerun()
        else:
            st.error("⚠️ Código de barras inválido.")

    if st.session_state["productos_seleccionados"]:
        st.markdown("---")
        st.subheader("📦 Productos en la compra actual")
        total_compra = 0.0
        for i, prod in enumerate(st.session_state["productos_seleccionados"]):
            subtotal = round(prod["precio_compra"] * prod["cantidad"], 2)
            total_compra += subtotal
            # Mostrar la unidad utilizada
            unidad_texto = prod["unidad"]
            if prod["unidad"] == "libras":
                unidad_texto = "lb"
            elif prod["unidad"] == "quintal":
                unidad_texto = "qq"
            
            st.markdown(
                f"**{prod['nombre']}** — {prod['cantidad']} {unidad_texto} — "
                f"Precio: ${prod['precio_compra']:.2f} — "
                f"**Subtotal:** ${subtotal:.2f}"
            )
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"✏️ Editar #{i+1}", key=f"editar_{i}"):
                    st.session_state["editar_indice"] = i
                    st.rerun()
            with col2:
                if st.button(f"❌ Eliminar #{i+1}", key=f"eliminar_{i}"):
                    st.session_state["productos_seleccionados"].pop(i)
                    st.success("🗑️ Producto eliminado.")
                    st.rerun()

        st.markdown("---")
        st.markdown(f"### 🧮 Total de la compra: **${total_compra:.2f}**")

    if st.button("✅ Registrar compra", type="primary"):
        if not st.session_state["productos_seleccionados"]:
            st.error("❌ No hay productos agregados.")
        else:
            try:
                cursor.execute("SELECT MAX(Id_compra) FROM Compra WHERE id_tienda = %s", (id_tienda,))
                ultimo_id = cursor.fetchone()[0]
                nuevo_id = 1 if ultimo_id is None else int(ultimo_id) + 1

                fecha = datetime.now().strftime("%Y-%m-%d")
                id_empleado = st.session_state["id_empleado"]

                cursor.execute(
                    "INSERT INTO Compra (Id_compra, Fecha, Id_empleado, id_tienda) VALUES (%s, %s, %s, %s)",
                    (nuevo_id, fecha, id_empleado, id_tienda),
                )

                for prod in st.session_state["productos_seleccionados"]:
                    cursor.execute(
                        """
                        INSERT INTO ProductoxCompra
                        (Id_compra, cod_barra, cantidad_comprada, precio_compra, unidad, fecha_vencimiento,
                         Precio_minorista, Precio_mayorista1, Precio_mayorista2, id_tienda)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            nuevo_id,
                            prod["cod_barra"],
                            prod["cantidad"],
                            prod["precio_compra"],
                            prod["unidad"],
                            prod.get("fecha_vencimiento"),
                            prod["precio_venta"],
                            prod["precio_venta2"],
                            prod["precio_venta3"],
                            id_tienda,
                        ),
                    )

                conn.commit()
                st.success(f"📦 Compra registrada exitosamente con ID {nuevo_id}.")
                st.session_state["productos_seleccionados"] = []
                st.session_state["_reset_form_next_run"] = True
                st.rerun()

            except Exception as e:
                conn.rollback()
                st.error(f"⚠️ Error al guardar en la base de datos: {e}")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.session_state["productos_seleccionados"] = []
        st.session_state["_reset_form_next_run"] = True
        st.rerun()

    cursor.close()
    conn.close()
