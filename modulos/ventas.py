import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from config.conexion import obtener_conexion


def configurar_estilo():
    """Configuración de estilos CSS para el módulo de ventas - MODO CLARO"""

    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_ACCENT = "#3a7ca5"
    COLOR_LIGHT_BLUE = "#e8f0fe"
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

        .product-section-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 25px;
            margin-top: 20px;
        }}

        .info-box {{
            background: {COLOR_HOVER};
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid {COLOR_PRIMARY};
            margin: 15px 0;
            color: {COLOR_TEXT_DARK};
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

        .total-venta {{
            background: {COLOR_LIGHT_BLUE};
            color: {COLOR_PRIMARY};
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            margin: 20px 0;
            font-size: 1.3em;
            font-weight: bold;
            border: 1px solid {COLOR_BORDER};
        }}

        /* ============================================================
           LABELS
           ============================================================ */

        .stTextInput > label,
        .stSelectbox > label,
        .stNumberInput > label,
        .stDateInput > label {{
            color: {COLOR_TEXT_DARK} !important;
            font-weight: 500 !important;
        }}

        /* ============================================================
           TEXT INPUT
           ============================================================ */

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

        /* ============================================================
           NUMBER INPUT
           ============================================================ */

        .stNumberInput > div > div > input {{
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
            background-color: {COLOR_BUTTON};
            color: white !important;
            padding: 10px 15px;
        }}

        /* ============================================================
           SELECTBOX - FONDO AZUL Y TEXTO BLANCO
           ============================================================ */

        div[data-baseweb="select"] > div {{
            background-color: {COLOR_BUTTON} !important;
            border-radius: 8px !important;
            border: 1px solid {COLOR_BORDER} !important;
        }}

        div[data-baseweb="select"] * {{
            color: white !important;
            -webkit-text-fill-color: white !important;
        }}

        div[data-baseweb="select"] svg {{
            fill: white !important;
            color: white !important;
        }}

        /* ============================================================
           DATE INPUT
           ============================================================ */

        .stDateInput > div > div > input {{
            background-color: {COLOR_BUTTON};
            color: white !important;
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
        }}

        .price-text {{
            color: {COLOR_TEXT_DARK} !important;
            font-weight: 600 !important;
            font-size: 1.1em !important;
        }}

        /* ============================================================
           BOTONES
           ============================================================ */

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

        /* ============================================================
           MÉTRICAS
           ============================================================ */

        [data-testid="stMetric"] {{
            background-color: {COLOR_HOVER};
            border-radius: 10px;
            padding: 10px;
        }}

        [data-testid="stMetricLabel"] {{
            color: {COLOR_PRIMARY} !important;
            font-weight: 600 !important;
        }}

        [data-testid="stMetricValue"] {{
            color: {COLOR_TEXT_DARK} !important;
            font-weight: bold !important;
        }}

        .stCaption {{
            color: {COLOR_TEXT_DARK} !important;
        }}

        .stMarkdown p {{
            color: {COLOR_TEXT_DARK} !important;
        }}

        </style>
    """, unsafe_allow_html=True)


# ============================================================
# CONSTANTES
# ============================================================

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


def obtener_unidades_por_categoria(categoria, unidad_compra=None):

    if categoria in CATEGORIAS_GRANOS:

        return [
            "libras",
            "quintal",
            "arroba"
        ]

    elif categoria in CATEGORIAS_CARNES:

        if unidad_compra:
            return [unidad_compra]

        return [
            "libras",
            "unidad"
        ]

    else:

        return ["unidad"]


# ============================================================
# MÓDULO DE VENTAS
# ============================================================

def modulo_ventas():

    configurar_estilo()

    st.markdown(
        '<div class="module-title">💵 Registro de Ventas</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # VALIDACIÓN DE SESIÓN
    # ============================================================

    if (
        not st.session_state.get("logueado")
        or "id_empleado" not in st.session_state
        or "id_tienda" not in st.session_state
    ):

        st.error(
            "⚠️ Debes iniciar sesión para registrar ventas."
        )

        st.markdown("---")

        if st.button("⬅ Volver al menú principal"):

            st.session_state["module"] = None
            st.rerun()

        return


    # ============================================================
    # DATOS DEL USUARIO
    # ============================================================

    id_tienda = st.session_state["id_tienda"]

    id_empleado = st.session_state["id_empleado"]

    nombre_empleado = st.session_state.get(
        "nombre_empleado",
        "Usuario"
    )

    nombre_tienda = st.session_state.get(
        "nombre_tienda",
        "Mi Tienda"
    )


    # ============================================================
    # CONEXIÓN
    # ============================================================

    conn = obtener_conexion()

    if not conn:

        st.error(
            "❌ No se pudo conectar a la base de datos."
        )

        st.stop()


    cursor = conn.cursor()


    # ============================================================
    # VARIABLES DE SESIÓN
    # ============================================================

    if "productos_vendidos" not in st.session_state:

        st.session_state[
            "productos_vendidos"
        ] = []


    if "form_data_codigo_barras" not in st.session_state:

        st.session_state[
            "form_data_codigo_barras"
        ] = ""


    # ============================================================
    # REINICIAR FORMULARIO DEL PRODUCTO
    # ============================================================

    if st.session_state.get(
        "_reset_venta_next_run"
    ):

        st.session_state[
            "_reset_venta_next_run"
        ] = False

        st.session_state[
            "form_data_codigo_barras"
        ] = ""

        st.session_state.pop(
            "venta_tipo_cliente",
            None
        )

        st.session_state.pop(
            "venta_precio_venta",
            None
        )

        st.session_state.pop(
            "_precio_venta_contexto",
            None
        )

        st.session_state.pop(
            "venta_cantidad",
            None
        )

        st.session_state.pop(
            "unidad_select",
            None
        )


    # ============================================================
    # REINICIAR FECHA DESPUÉS DE REGISTRAR VENTA
    # ============================================================

    if st.session_state.get(
        "_reset_fecha_venta_next_run"
    ):

        st.session_state[
            "_reset_fecha_venta_next_run"
        ] = False

        st.session_state.pop(
            "venta_fecha",
            None
        )


    # ============================================================
    # FECHA ACTUAL DE EL SALVADOR
    # ============================================================

    hoy_el_salvador = datetime.now(
        ZoneInfo("America/El_Salvador")
    ).date()


    # ============================================================
    # FECHA / EMPLEADO / TIENDA
    # ============================================================

    col1, col2 = st.columns(2)


    with col1:

        fecha_venta = st.date_input(
            "📅 Fecha de la venta",
            hoy_el_salvador,
            key="venta_fecha"
        )


    with col2:

        st.markdown(
            f'<div class="info-box">'
            f'🧑‍💼 Empleado: '
            f'<strong>{nombre_empleado}</strong>'
            f'<br>'
            f'🏪 Tienda: '
            f'<strong>{nombre_tienda}</strong>'
            f'</div>',
            unsafe_allow_html=True
        )


    st.markdown("---")


    # ============================================================
    # CÓDIGO DE BARRAS
    # ============================================================

    cod_barra = st.text_input(
        "🔍 Código de barras del producto",
        key="form_data_codigo_barras",
        placeholder="Ej: 123456789"
    )


    if cod_barra:

        cursor.execute(
            """
            SELECT
                Cod_barra,
                Nombre,
                categoria,
                id_producto
            FROM Producto
            WHERE Cod_barra = %s
            AND id_tienda = %s
            """,
            (
                cod_barra,
                id_tienda
            )
        )


        producto_base = cursor.fetchone()


        if not producto_base:

            st.error(
                "❌ Producto no encontrado en el catálogo de esta tienda."
            )


        else:

            (
                cod_barra_real,
                nombre_producto,
                categoria,
                id_producto
            ) = producto_base


            st.markdown(
                f'<div class="info-box">'
                f'✅ Producto encontrado: '
                f'<strong>{nombre_producto}</strong>'
                f'<br>'
                f'📁 Categoría: '
                f'<strong>{categoria}</strong>'
                f'<br>'
                f'🆔 ID: '
                f'<strong>{id_producto}</strong>'
                f'</div>',
                unsafe_allow_html=True
            )


            # ========================================================
            # COMPRAS DEL PRODUCTO
            # ========================================================

            cursor.execute(
                """
                SELECT
                    unidad,
                    cantidad_comprada
                FROM ProductoxCompra
                WHERE Cod_barra = %s
                AND id_tienda = %s
                """,
                (
                    cod_barra_real,
                    id_tienda
                )
            )


            compras = cursor.fetchall()


            # ========================================================
            # VENTAS DEL PRODUCTO
            # ========================================================

            cursor.execute(
                """
                SELECT
                    unidad,
                    Cantidad_vendida
                FROM ProductoxVenta
                WHERE Cod_barra = %s
                AND id_tienda = %s
                """,
                (
                    cod_barra_real,
                    id_tienda
                )
            )


            ventas = cursor.fetchall()


            # ========================================================
            # GRANOS / PRODUCTOS CONVERSIBLES A LIBRAS
            # ========================================================

            if categoria in CATEGORIAS_GRANOS:

                total_comprado_libras = 0


                for unidad, cantidad in compras:

                    if unidad == "libras":

                        total_comprado_libras += cantidad

                    elif unidad == "quintal":

                        total_comprado_libras += (
                            cantidad * 100
                        )

                    elif unidad == "arroba":

                        total_comprado_libras += (
                            cantidad * 25
                        )


                total_vendido_libras = 0


                for unidad, cantidad in ventas:

                    if unidad == "libras":

                        total_vendido_libras += cantidad

                    elif unidad == "quintal":

                        total_vendido_libras += (
                            cantidad * 100
                        )

                    elif unidad == "arroba":

                        total_vendido_libras += (
                            cantidad * 25
                        )


                existencia_libras = (
                    total_comprado_libras
                    - total_vendido_libras
                )


                st.markdown(
                    '<div class="module-subtitle">'
                    '📦 Existencia actual'
                    '</div>',
                    unsafe_allow_html=True
                )


                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "Libras",
                        f"{existencia_libras:.2f}"
                    )


                with col2:

                    st.metric(
                        "Quintales",
                        f"{existencia_libras / 100:.2f}"
                    )


                with col3:

                    st.metric(
                        "Arrobas",
                        f"{existencia_libras / 25:.2f}"
                    )


                if existencia_libras <= 0:

                    st.error(
                        "❌ Producto sin stock."
                    )


                else:

                    # ====================================================
                    # ÚLTIMOS PRECIOS CONFIGURADOS
                    # ====================================================

                    cursor.execute(
                        """
                        SELECT
                            Precio_minorista,
                            Precio_mayorista1,
                            Precio_mayorista2
                        FROM ProductoxCompra
                        WHERE Cod_barra = %s
                        AND id_tienda = %s
                        ORDER BY Id_compra DESC
                        LIMIT 1
                        """,
                        (
                            cod_barra_real,
                            id_tienda
                        )
                    )


                    precios = cursor.fetchone()


                    if precios:

                        precio_por_libra_minorista = (
                            float(precios[0])
                            if precios[0]
                            else 0
                        )

                        precio_por_libra_mayorista1 = (
                            float(precios[1])
                            if precios[1]
                            else 0
                        )

                        precio_por_libra_mayorista2 = (
                            float(precios[2])
                            if precios[2]
                            else 0
                        )


                    else:

                        st.warning(
                            "⚠️ No hay precios configurados."
                        )

                        precio_por_libra_minorista = 0
                        precio_por_libra_mayorista1 = 0
                        precio_por_libra_mayorista2 = 0


                    # ====================================================
                    # MOSTRAR PRECIOS CONFIGURADOS
                    # ====================================================

                    st.markdown(
                        '<div class="module-subtitle">'
                        '💰 Precios configurados'
                        '</div>',
                        unsafe_allow_html=True
                    )


                    col1, col2, col3 = st.columns(3)


                    with col1:

                        st.metric(
                            "Minorista",
                            f"${precio_por_libra_minorista:.2f}"
                        )


                    with col2:

                        st.metric(
                            "Mayorista 1",
                            f"${precio_por_libra_mayorista1:.2f}"
                        )


                    with col3:

                        st.metric(
                            "Mayorista 2",
                            f"${precio_por_libra_mayorista2:.2f}"
                        )


                    unidades_disponibles = [
                        "libras",
                        "quintal",
                        "arroba"
                    ]


                    # ====================================================
                    # TIPO DE CLIENTE
                    # ====================================================

                    tipo_cliente = st.selectbox(
                        "🧾 Seleccione el tipo de cliente",
                        [
                            "Minorista",
                            "Mayorista 1",
                            "Mayorista 2"
                        ],
                        key="venta_tipo_cliente"
                    )


                    # ====================================================
                    # PRECIO BASE SEGÚN TIPO DE CLIENTE
                    # ====================================================

                    if tipo_cliente == "Minorista":

                        precio_por_libra = (
                            precio_por_libra_minorista
                        )


                    elif tipo_cliente == "Mayorista 1":

                        precio_por_libra = (
                            precio_por_libra_mayorista1
                        )


                    else:

                        precio_por_libra = (
                            precio_por_libra_mayorista2
                        )


                    if precio_por_libra <= 0:

                        st.error(
                            f"❌ No hay precio para {tipo_cliente}."
                        )


                    else:

                        # ====================================================
                        # PRECIO DE VENTA EDITABLE
                        # ====================================================

                        contexto_precio = (
                            cod_barra_real,
                            tipo_cliente
                        )


                        if (
                            st.session_state.get(
                                "_precio_venta_contexto"
                            )
                            != contexto_precio
                        ):

                            st.session_state[
                                "venta_precio_venta"
                            ] = float(
                                precio_por_libra
                            )

                            st.session_state[
                                "_precio_venta_contexto"
                            ] = contexto_precio


                        precio_venta_editable = st.number_input(
                            "💰 Precio de venta por libra",
                            min_value=0.01,
                            step=0.01,
                            format="%.2f",
                            key="venta_precio_venta"
                        )


                        # ====================================================
                        # UNIDAD DE VENTA
                        # ====================================================

                        unidad_venta = st.selectbox(
                            "📏 Unidad de venta",
                            unidades_disponibles,
                            key="unidad_select"
                        )


                        st.info(
                            "💡 **Factores de conversión:** "
                            "1 quintal = 100 libras | "
                            "1 arroba = 25 libras"
                        )


                        # ====================================================
                        # LIBRAS
                        # ====================================================

                        if unidad_venta == "libras":

                            stock_disponible = (
                                existencia_libras
                            )

                            st.caption(
                                f"📦 Stock disponible: "
                                f"{stock_disponible:.2f} libras"
                            )

                            cantidad = st.number_input(
                                "📦 Cantidad vendida (libras)",
                                min_value=0.01,
                                step=0.01,
                                format="%.2f",
                                key="venta_cantidad"
                            )

                            cantidad_en_libras = cantidad

                            cantidad_original = cantidad


                        # ====================================================
                        # QUINTAL
                        # ====================================================

                        elif unidad_venta == "quintal":

                            stock_disponible = (
                                existencia_libras / 100
                            )

                            st.caption(
                                f"📦 Stock disponible: "
                                f"{stock_disponible:.2f} quintales"
                            )

                            cantidad = st.number_input(
                                "📦 Cantidad vendida (quintales)",
                                min_value=0.01,
                                step=0.01,
                                format="%.2f",
                                key="venta_cantidad"
                            )

                            cantidad_en_libras = (
                                cantidad * 100
                            )

                            cantidad_original = cantidad


                            st.caption(
                                f"🔄 {cantidad:.2f} quintal(es) "
                                f"= {cantidad_en_libras:.2f} libras"
                            )


                        # ====================================================
                        # ARROBA
                        # ====================================================

                        else:

                            stock_disponible = (
                                existencia_libras / 25
                            )

                            st.caption(
                                f"📦 Stock disponible: "
                                f"{stock_disponible:.2f} arrobas"
                            )

                            cantidad = st.number_input(
                                "📦 Cantidad vendida (arrobas)",
                                min_value=0.01,
                                step=0.01,
                                format="%.2f",
                                key="venta_cantidad"
                            )

                            cantidad_en_libras = (
                                cantidad * 25
                            )

                            cantidad_original = cantidad


                            st.caption(
                                f"🔄 {cantidad:.2f} arroba(s) "
                                f"= {cantidad_en_libras:.2f} libras"
                            )


                        # ====================================================
                        # SUBTOTAL
                        # ====================================================

                        subtotal = round(
                            precio_venta_editable
                            * cantidad_en_libras,
                            2
                        )


                        st.markdown(
                            f'<p class="price-text">'
                            f'🧾 Subtotal: ${subtotal:.2f}'
                            f'</p>',
                            unsafe_allow_html=True
                        )


                        # ====================================================
                        # VALIDAR STOCK
                        # ====================================================

                        if (
                            cantidad_en_libras
                            > existencia_libras
                        ):

                            st.error(
                                f"❌ No hay suficiente stock. "
                                f"Stock disponible: "
                                f"{stock_disponible:.2f} "
                                f"{unidad_venta}"
                            )


                        else:

                            col1, col2, col3 = (
                                st.columns(
                                    [1, 2, 1]
                                )
                            )


                            with col2:

                                if st.button(
                                    "🛒 Agregar producto a la venta",
                                    use_container_width=True,
                                    type="primary"
                                ):

                                    producto_venta = {

                                        "cod_barra":
                                            cod_barra_real,

                                        "id_producto":
                                            id_producto,

                                        "nombre":
                                            nombre_producto,

                                        "precio_venta":
                                            precio_venta_editable,

                                        "cantidad":
                                            cantidad_original,

                                        "unidad":
                                            unidad_venta,

                                        "subtotal":
                                            subtotal,

                                        "tipo_cliente":
                                            tipo_cliente,
                                    }


                                    st.session_state[
                                        "productos_vendidos"
                                    ].append(
                                        producto_venta
                                    )


                                    st.session_state[
                                        "_reset_venta_next_run"
                                    ] = True


                                    st.success(
                                        "✅ Producto agregado a la venta."
                                    )


                                    st.rerun()


            # ========================================================
            # OTROS PRODUCTOS
            # ========================================================

            else:

                existencias = {}


                # ====================================================
                # SUMAR COMPRAS
                # ====================================================

                for unidad, cantidad in compras:

                    existencias[unidad] = (
                        existencias.get(
                            unidad,
                            0
                        )
                        + cantidad
                    )


                # ====================================================
                # RESTAR VENTAS
                # ====================================================

                for unidad, cantidad in ventas:

                    existencias[unidad] = (
                        existencias.get(
                            unidad,
                            0
                        )
                        - cantidad
                    )


                st.markdown(
                    '<div class="module-subtitle">'
                    '📦 Existencia actual'
                    '</div>',
                    unsafe_allow_html=True
                )


                if existencias:

                    cols = st.columns(
                        len(existencias)
                    )


                    for idx, (
                        unidad,
                        cantidad
                    ) in enumerate(
                        existencias.items()
                    ):

                        if cantidad > 0:

                            with cols[idx]:

                                st.metric(
                                    f"{unidad.capitalize()}",
                                    f"{cantidad:.2f}"
                                )


                else:

                    st.info(
                        "No hay stock disponible"
                    )


                tiene_stock = any(
                    c > 0
                    for c in existencias.values()
                )


                if not tiene_stock:

                    st.error(
                        "❌ Producto sin stock."
                    )


                else:

                    # ====================================================
                    # PRECIOS CONFIGURADOS
                    # ====================================================

                    cursor.execute(
                        """
                        SELECT
                            Precio_minorista,
                            Precio_mayorista1,
                            Precio_mayorista2
                        FROM ProductoxCompra
                        WHERE Cod_barra = %s
                        AND id_tienda = %s
                        ORDER BY Id_compra DESC
                        LIMIT 1
                        """,
                        (
                            cod_barra_real,
                            id_tienda
                        )
                    )


                    precios = cursor.fetchone()


                    if precios:

                        precio_minorista = (
                            float(precios[0])
                            if precios[0]
                            else 0
                        )

                        precio_mayorista1 = (
                            float(precios[1])
                            if precios[1]
                            else 0
                        )

                        precio_mayorista2 = (
                            float(precios[2])
                            if precios[2]
                            else 0
                        )


                    else:

                        precio_minorista = 0
                        precio_mayorista1 = 0
                        precio_mayorista2 = 0


                    # ====================================================
                    # MOSTRAR PRECIOS
                    # ====================================================

                    if precio_minorista > 0:

                        st.markdown(
                            '<div class="module-subtitle">'
                            '💰 Precios configurados'
                            '</div>',
                            unsafe_allow_html=True
                        )


                        col1, col2, col3 = (
                            st.columns(3)
                        )


                        with col1:

                            st.metric(
                                "Minorista",
                                f"${precio_minorista:.2f}"
                            )


                        with col2:

                            st.metric(
                                "Mayorista 1",
                                f"${precio_mayorista1:.2f}"
                            )


                        with col3:

                            st.metric(
                                "Mayorista 2",
                                f"${precio_mayorista2:.2f}"
                            )


                    # ====================================================
                    # UNIDADES DISPONIBLES
                    # ====================================================

                    if categoria in CATEGORIAS_CARNES:

                        unidades_con_stock = [
                            u
                            for u, c
                            in existencias.items()
                            if c > 0
                        ]


                        unidades_disponibles = (
                            [unidades_con_stock[0]]
                            if unidades_con_stock
                            else ["unidad"]
                        )


                    else:

                        unidades_disponibles = [
                            "unidad"
                        ]


                    # ====================================================
                    # TIPO DE CLIENTE
                    # ====================================================

                    tipo_cliente = st.selectbox(
                        "🧾 Seleccione el tipo de cliente",
                        [
                            "Minorista",
                            "Mayorista 1",
                            "Mayorista 2"
                        ],
                        key="venta_tipo_cliente"
                    )


                    # ====================================================
                    # PRECIO BASE SEGÚN CLIENTE
                    # ====================================================

                    if tipo_cliente == "Minorista":

                        precio_base = (
                            precio_minorista
                        )


                    elif tipo_cliente == "Mayorista 1":

                        precio_base = (
                            precio_mayorista1
                        )


                    else:

                        precio_base = (
                            precio_mayorista2
                        )


                    if precio_base <= 0:

                        st.error(
                            f"❌ No hay precio para {tipo_cliente}."
                        )


                    else:

                        # ====================================================
                        # PRECIO DE VENTA EDITABLE
                        # ====================================================

                        contexto_precio = (
                            cod_barra_real,
                            tipo_cliente
                        )


                        if (
                            st.session_state.get(
                                "_precio_venta_contexto"
                            )
                            != contexto_precio
                        ):

                            st.session_state[
                                "venta_precio_venta"
                            ] = float(
                                precio_base
                            )

                            st.session_state[
                                "_precio_venta_contexto"
                            ] = contexto_precio


                        precio_venta_editable = st.number_input(
                            "💰 Precio de venta",
                            min_value=0.01,
                            step=0.01,
                            format="%.2f",
                            key="venta_precio_venta"
                        )


                        # ====================================================
                        # UNIDAD
                        # ====================================================

                        unidad_venta = st.selectbox(
                            "📏 Unidad de venta",
                            unidades_disponibles,
                            key="unidad_select"
                        )


                        # ====================================================
                        # STOCK
                        # ====================================================

                        stock_disponible = (
                            existencias.get(
                                unidad_venta,
                                0
                            )
                        )


                        st.caption(
                            f"📦 Stock disponible: "
                            f"{stock_disponible:.2f} "
                            f"{unidad_venta}"
                        )


                        # ====================================================
                        # CANTIDAD
                        # ====================================================

                        if unidad_venta == "unidad":

                            cantidad = (
                                st.number_input(
                                    f"📦 Cantidad vendida "
                                    f"({unidad_venta})",
                                    min_value=1,
                                    step=1,
                                    format="%d",
                                    key="venta_cantidad"
                                )
                            )


                        else:

                            cantidad = (
                                st.number_input(
                                    f"📦 Cantidad vendida "
                                    f"({unidad_venta})",
                                    min_value=0.01,
                                    step=0.01,
                                    format="%.2f",
                                    key="venta_cantidad"
                                )
                            )


                        # ====================================================
                        # VALIDACIÓN STOCK
                        # ====================================================

                        if (
                            cantidad
                            > stock_disponible
                        ):

                            st.error(
                                f"❌ Stock insuficiente. "
                                f"Disponible: "
                                f"{stock_disponible:.2f} "
                                f"{unidad_venta}"
                            )


                        else:

                            # =================================================
                            # SUBTOTAL CON PRECIO EDITADO
                            # =================================================

                            subtotal = round(
                                precio_venta_editable
                                * cantidad,
                                2
                            )


                            st.markdown(
                                f'<p class="price-text">'
                                f'🧾 Subtotal: '
                                f'${subtotal:.2f}'
                                f'</p>',
                                unsafe_allow_html=True
                            )


                            col1, col2, col3 = (
                                st.columns(
                                    [1, 2, 1]
                                )
                            )


                            with col2:

                                if st.button(
                                    "🛒 Agregar producto a la venta",
                                    use_container_width=True,
                                    type="primary"
                                ):

                                    producto_venta = {

                                        "cod_barra":
                                            cod_barra_real,

                                        "id_producto":
                                            id_producto,

                                        "nombre":
                                            nombre_producto,

                                        "precio_venta":
                                            precio_venta_editable,

                                        "cantidad":
                                            cantidad,

                                        "unidad":
                                            unidad_venta,

                                        "subtotal":
                                            subtotal,

                                        "tipo_cliente":
                                            tipo_cliente,
                                    }


                                    st.session_state[
                                        "productos_vendidos"
                                    ].append(
                                        producto_venta
                                    )


                                    st.session_state[
                                        "_reset_venta_next_run"
                                    ] = True


                                    st.success(
                                        "✅ Producto agregado a la venta."
                                    )


                                    st.rerun()


    # ============================================================
    # PRODUCTOS DE LA VENTA
    # ============================================================

    st.markdown("---")


    if st.session_state[
        "productos_vendidos"
    ]:


        st.markdown(
            '<div class="product-section-title">'
            '🧾 Productos en esta venta'
            '</div>',
            unsafe_allow_html=True
        )


        total_venta = 0.0


        for i, prod in enumerate(
            st.session_state[
                "productos_vendidos"
            ]
        ):

            total_venta += (
                prod["subtotal"]
            )


            # ========================================================
            # TARJETA DE PRODUCTO
            # ========================================================

            html_producto = (
                '<div class="product-card">'
                f'<div class="product-name">'
                f'📦 {prod["nombre"]}'
                f'</div>'
                f'<div class="product-details">'
                f'<strong>Cantidad:</strong> '
                f'{prod["cantidad"]:.2f} '
                f'{prod["unidad"]}'
                f'</div>'
                f'<div class="product-details">'
                f'<strong>Precio unitario:</strong> '
                f'${prod["precio_venta"]:.2f}'
                f'</div>'
                f'<div class="product-details">'
                f'<strong>Subtotal:</strong> '
                f'${prod["subtotal"]:.2f}'
                f'</div>'
                f'<div class="product-details">'
                f'<strong>Cliente:</strong> '
                f'{prod["tipo_cliente"]}'
                f'</div>'
                '</div>'
            )


            st.markdown(
                html_producto,
                unsafe_allow_html=True
            )


            # ========================================================
            # ELIMINAR PRODUCTO
            # ========================================================

            col1, col2, col3 = (
                st.columns(
                    [1, 3, 1]
                )
            )


            with col2:

                if st.button(
                    "🗑️ Eliminar",
                    key=f"eliminar_venta_{i}",
                    use_container_width=True
                ):

                    st.session_state[
                        "productos_vendidos"
                    ].pop(i)

                    st.rerun()


        # ========================================================
        # TOTAL
        # ========================================================

        html_total = (
            '<div class="total-venta">'
            f'💵 Total de la venta: '
            f'${total_venta:.2f}'
            '</div>'
        )


        st.markdown(
            html_total,
            unsafe_allow_html=True
        )


        # ========================================================
        # REGISTRAR VENTA
        # ========================================================

        col1, col2, col3 = (
            st.columns(
                [1, 2, 1]
            )
        )


        with col2:

            if st.button(
                "✅ Registrar venta",
                use_container_width=True,
                type="primary"
            ):

                try:

                    # ====================================================
                    # OBTENER NUEVO ID
                    # ====================================================

                    cursor.execute(
                        """
                        SELECT MAX(Id_venta)
                        FROM Venta
                        """
                    )


                    ultimo_id = (
                        cursor.fetchone()[0]
                    )


                    nuevo_id = (
                        1
                        if ultimo_id is None
                        else int(ultimo_id) + 1
                    )


                    # ====================================================
                    # REGISTRAR CABECERA DE VENTA
                    # ====================================================

                    cursor.execute(
                        """
                        INSERT INTO Venta
                        (
                            Id_venta,
                            Fecha,
                            Id_empleado,
                            id_tienda
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        """,
                        (
                            nuevo_id,
                            fecha_venta,
                            id_empleado,
                            id_tienda
                        )
                    )


                    # ====================================================
                    # REGISTRAR PRODUCTOS
                    # ====================================================

                    for prod in st.session_state[
                        "productos_vendidos"
                    ]:


                        if "id_producto" not in prod:

                            st.error(
                                f"❌ Error: El producto "
                                f"{prod.get('nombre', 'desconocido')} "
                                f"no tiene id_producto"
                            )

                            continue


                        cursor.execute(
                            """
                            INSERT INTO ProductoxVenta
                            (
                                Id_venta,
                                Cod_barra,
                                id_producto,
                                Cantidad_vendida,
                                Tipo_de_cliente,
                                Precio_Venta,
                                id_tienda,
                                unidad
                            )
                            VALUES
                            (
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s
                            )
                            """,
                            (
                                nuevo_id,

                                prod[
                                    "cod_barra"
                                ],

                                prod[
                                    "id_producto"
                                ],

                                prod[
                                    "cantidad"
                                ],

                                prod[
                                    "tipo_cliente"
                                ],

                                round(
                                    prod[
                                        "precio_venta"
                                    ],
                                    2
                                ),

                                id_tienda,

                                prod[
                                    "unidad"
                                ],
                            ),
                        )


                    # ====================================================
                    # CONFIRMAR TRANSACCIÓN
                    # ====================================================

                    conn.commit()


                    st.success(
                        f"✅ Venta registrada exitosamente "
                        f"con ID {nuevo_id}."
                    )


                    # ====================================================
                    # LIMPIAR VENTA
                    # ====================================================

                    st.session_state[
                        "productos_vendidos"
                    ] = []


                    st.session_state[
                        "_reset_venta_next_run"
                    ] = True


                    st.session_state[
                        "_reset_fecha_venta_next_run"
                    ] = True


                    st.rerun()


                except Exception as e:

                    conn.rollback()


                    st.error(
                        f"⚠️ Error al registrar la venta: {e}"
                    )


    # ============================================================
    # VOLVER
    # ============================================================

    st.divider()


    col1, col2, col3 = (
        st.columns(
            [1, 2, 1]
        )
    )


    with col2:

        if st.button(
            "🔙 Volver al menú principal",
            use_container_width=True
        ):

            st.session_state[
                "module"
            ] = None


            st.session_state[
                "productos_vendidos"
            ] = []


            st.session_state[
                "_reset_venta_next_run"
            ] = True


            st.rerun()


    cursor.close()
    conn.close()
