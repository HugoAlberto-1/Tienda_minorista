import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def configurar_estilo():
    """Configuración de estilos CSS para el módulo de compras - MODO CLARO"""
    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_ACCENT = "#3a7ca5"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_DARK = "#1a1a1a"
    COLOR_TEXT_LIGHT = "#ffffff"
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
            color: {COLOR_TEXT_DARK} !important;
        }}
        
        .product-card {{
            background: {COLOR_CARD};
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid {COLOR_BORDER};
            transition: all 0.3s ease;
        }}
        
        .product-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
            border-color: {COLOR_ACCENT};
        }}
        
        .product-name {{
            font-size: 1.1em;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            margin-bottom: 8px;
        }}
        
        .product-details {{
            color: {COLOR_TEXT};
            font-size: 0.9em;
            margin: 5px 0;
        }}
        
        .product-details strong {{
            color: {COLOR_PRIMARY};
        }}
        
        .total-compra {{
            background: {COLOR_HOVER};
            color: {COLOR_PRIMARY};
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            margin: 20px 0;
            font-size: 1.3em;
            font-weight: bold;
            border: 1px solid {COLOR_BORDER};
        }}
        
        .stTextInput > label, .stSelectbox > label, .stNumberInput > label, .stDateInput > label {{
            color: {COLOR_TEXT_DARK} !important;
            font-weight: 500 !important;
        }}
        
        /* Forzar color oscuro en radio buttons */
        .stRadio label {{
            color: {COLOR_TEXT_DARK} !important;
        }}
        
        .stRadio div[role="radiogroup"] label {{
            color: {COLOR_TEXT_DARK} !important;
        }}
        
        .stRadio div[role="radiogroup"] div {{
            color: {COLOR_TEXT_DARK} !important;
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
        
        .stNumberInput > div > div > input {{
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
            background-color: {COLOR_BUTTON};
            color: white !important;
            padding: 10px 15px;
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
        
        .stDateInput > div > div > input {{
            background-color: {COLOR_BUTTON};
            color: white !important;
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
        }}
        
        .stButton > button {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY} !important;
            transform: translateY(-1px) !important;
        }}
        
        .stAlert {{
            border-radius: 8px;
        }}
        
        hr {{
            border-color: {COLOR_BORDER};
        }}
        </style>
    """, unsafe_allow_html=True)


CONVERSIONES_A_LIBRAS = {
    "libras": 1,
    "arroba": 25,
    "quintal": 100,
}

# 📁 Categorías que se consideran "granos"
CATEGORIAS_GRANOS = [
    "Granos y productos a granel",
    "Sopas, pastas y consomés"
]

def obtener_unidades_por_categoria(categoria):
    """Devuelve las unidades disponibles según la categoría del producto"""
    if categoria in CATEGORIAS_GRANOS:
        return ["libras", "quintal", "arroba"]
    elif categoria == "Carnes y congelados":
        return ["libras", "unidad"]
    else:
        return ["unidad"]


def obtener_id_producto(cursor, cod_barra, id_tienda):
    """Obtiene el id_producto a partir del código de barras"""
    cursor.execute(
        "SELECT id_producto FROM Producto WHERE Cod_barra = %s AND id_tienda = %s",
        (cod_barra, id_tienda)
    )
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None


def obtener_proximo_id_compra(cursor):
    """Obtiene el próximo ID disponible para una compra (global)"""
    cursor.execute("SELECT MAX(Id_compra) FROM Compra")
    ultimo_id = cursor.fetchone()[0]
    return 1 if ultimo_id is None else int(ultimo_id) + 1


def modulo_compras():
    configurar_estilo()
    
    st.markdown('<div class="module-title">🧾 Registro de Compras</div>', unsafe_allow_html=True)

    if not st.session_state.get("logueado") or "id_empleado" not in st.session_state or "id_tienda" not in st.session_state:
        st.error("⚠️ Debes iniciar sesión para registrar compras.")
        st.markdown("---")
        if st.button("⬅ Volver al menú principal"):
            st.session_state["module"] = None
            st.rerun()
        return

    id_tienda = st.session_state["id_tienda"]
    nombre_tienda = st.session_state.get("nombre_tienda", "Mi Tienda")
    nombre_empleado = st.session_state.get("nombre_empleado", "Usuario")

    st.markdown(f'<div class="info-box">🏪 Tienda: <strong>{nombre_tienda}</strong> | 👤 Empleado: <strong>{nombre_empleado}</strong></div>', unsafe_allow_html=True)

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

    # ============================================================
    # 🆕 TIPO DE COMPRA (Propia / Global) - TEXTO OSCURO FORZADO
    # ============================================================
    # Título "Tipo de Compra" en color oscuro
    st.markdown('<p style="color: #1a1a1a; font-size: 1.1em; font-weight: 600; margin-bottom: 5px;">📋 Tipo de Compra</p>', unsafe_allow_html=True)
    
    col_tipo1, col_tipo2 = st.columns(2)
    with col_tipo1:
        # Label "Seleccione el tipo de compra:" en color oscuro
        st.markdown('<p style="color: #1a1a1a; font-weight: 400; margin-bottom: 5px;">Seleccione el tipo de compra:</p>', unsafe_allow_html=True)
        tipo_compra = st.radio(
            "",
            ["Propia", "Global"],
            horizontal=True,
            key="tipo_compra",
            label_visibility="collapsed"
        )
    with col_tipo2:
        if tipo_compra == "Propia":
            st.markdown('<div style="background: #e8f0fe; padding: 12px; border-radius: 8px; border-left: 4px solid #1e3a5f; color: #1a1a1a;">🏪 Compra para esta tienda</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: #e8f0fe; padding: 12px; border-radius: 8px; border-left: 4px solid #1e3a5f; color: #1a1a1a;">🌎 Compra global para todas las tiendas</div>', unsafe_allow_html=True)

    st.markdown("---")

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
    id_producto_actual = None
    
    if codigo_buscado and not codigo_barras_disabled:
        producto_encontrado = next(
            (p for p in productos if p[0] == codigo_buscado),
            None,
        )
        if producto_encontrado:
            codigo, nombre, categoria_producto = producto_encontrado
            id_producto_actual = obtener_id_producto(cursor, codigo, id_tienda)
            
            st.markdown(f'<div class="info-box">✅ Producto encontrado: <strong>{nombre}</strong><br>📁 Categoría: <strong>{categoria_producto}</strong><br>🆔 ID Producto: <strong>{id_producto_actual}</strong></div>', unsafe_allow_html=True)
            
            unidades_disponibles = obtener_unidades_por_categoria(categoria_producto)
            
            if st.session_state["form_data"]["unidad"] not in unidades_disponibles:
                st.session_state["form_data"]["unidad"] = unidades_disponibles[0]
            
            if categoria_producto != "Granos y productos a granel":
                st.session_state["form_data"]["fecha_vencimiento"] = st.date_input(
                    "📅 Fecha de vencimiento (opcional)",
                    key="form_data_fecha_vencimiento",
                    value=None
                )
        else:
            st.error("⚠️ Producto no encontrado.")

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
        "💰 Precio de compra unitario",
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
    st.markdown(f'<p style="color: #1a1a1a; font-weight: 600;">🧾 Subtotal del producto actual: ${subtotal_actual:.2f}</p>', unsafe_allow_html=True)

    precio_minorista = round(precio_compra / 0.70, 2)
    st.markdown(f'<p style="color: #1a1a1a;">💡 <strong>Precio de venta sugerido (Al Detalle):</strong> ${precio_minorista:.2f}</p>', unsafe_allow_html=True)

    precio_sugerido2 = round(precio_compra / 0.75, 2)
    st.markdown(f'<p style="color: #1a1a1a;">💡 <strong>Precio de venta sugerido (Mayorista #1):</strong> ${precio_sugerido2:.2f}</p>', unsafe_allow_html=True)

    precio_sugerido = round(precio_compra / 0.80, 2)
    st.markdown(f'<p style="color: #1a1a1a;">💡 <strong>Precio de venta sugerido (Mayorista #2):</strong> ${precio_sugerido:.2f}</p>', unsafe_allow_html=True)

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
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(boton_texto, use_container_width=True, type="primary"):
            if producto_encontrado or codigo_barras_disabled:
                if st.session_state["editar_indice"] is not None:
                    prod_ref = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
                    producto = {
                        "cod_barra": codigo_buscado,
                        "id_producto": prod_ref.get("id_producto"),
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
                        "id_producto": id_producto_actual,
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
        st.markdown('<div class="module-subtitle">📦 Productos en la compra actual</div>', unsafe_allow_html=True)
        total_compra = 0.0
        
        for i, prod in enumerate(st.session_state["productos_seleccionados"]):
            subtotal = round(prod["precio_compra"] * prod["cantidad"], 2)
            total_compra += subtotal
            
            unidad_texto = prod["unidad"]
            if prod["unidad"] == "libras":
                unidad_texto = "lb"
            elif prod["unidad"] == "quintal":
                unidad_texto = "qq"
            
            st.markdown(f"""
                <div class="product-card">
                    <div class="product-name">📦 {prod['nombre']}</div>
                    <div class="product-details"><strong>Cantidad:</strong> {prod['cantidad']} {unidad_texto}</div>
                    <div class="product-details"><strong>Precio unitario:</strong> ${prod['precio_compra']:.2f}</div>
                    <div class="product-details"><strong>Subtotal:</strong> ${subtotal:.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"✏️ Editar", key=f"editar_{i}", use_container_width=True):
                    st.session_state["editar_indice"] = i
                    st.rerun()
            with col2:
                if st.button(f"🗑️ Eliminar", key=f"eliminar_{i}", use_container_width=True):
                    st.session_state["productos_seleccionados"].pop(i)
                    st.success("🗑️ Producto eliminado.")
                    st.rerun()

        st.markdown("---")
        st.markdown(f"""
            <div class="total-compra">
                🧮 Total de la compra: ${total_compra:.2f}
            </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ Registrar compra", use_container_width=True, type="primary"):
            if not st.session_state["productos_seleccionados"]:
                st.error("❌ No hay productos agregados.")
            else:
                try:
                    # Obtener el próximo ID disponible (global)
                    nuevo_id = obtener_proximo_id_compra(cursor)

                    fecha = datetime.now().strftime("%Y-%m-%d")
                    id_empleado = st.session_state["id_empleado"]

                    # Insertar la compra con el tipo de compra
                    cursor.execute(
                        "INSERT INTO Compra (Id_compra, Fecha, Id_empleado, id_tienda, Tipo_Compra) VALUES (%s, %s, %s, %s, %s)",
                        (nuevo_id, fecha, id_empleado, id_tienda, tipo_compra),
                    )

                    # Insertar los productos de la compra
                    for prod in st.session_state["productos_seleccionados"]:
                        cursor.execute(
                            """
                            INSERT INTO ProductoxCompra
                            (Id_compra, cod_barra, id_producto, cantidad_comprada, precio_compra, unidad, fecha_vencimiento,
                             Precio_minorista, Precio_mayorista1, Precio_mayorista2, id_tienda)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                nuevo_id,
                                prod["cod_barra"],
                                prod["id_producto"],
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
                    st.success(f"📦 Compra registrada exitosamente con ID {nuevo_id} (Tipo: {tipo_compra}).")
                    st.session_state["productos_seleccionados"] = []
                    st.session_state["_reset_form_next_run"] = True
                    st.rerun()

                except Exception as e:
                    conn.rollback()
                    st.error(f"⚠️ Error al guardar en la base de datos: {e}")

    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Volver al menú principal", use_container_width=True):
            st.session_state["module"] = None
            st.session_state["productos_seleccionados"] = []
            st.session_state["_reset_form_next_run"] = True
            st.rerun()

    cursor.close()
    conn.close()
