import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion


# ============================================================
# 🎨 ESTILOS DEL MÓDULO
# ============================================================
def configurar_estilo():
    """Configuración visual del módulo de Comparativa de Costos"""

    COLOR_PRIMARY = "#1e3a5f"
    COLOR_SECONDARY = "#2c5f8a"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_DARK = "#1a1a1a"
    COLOR_HOVER = "#e8f0fe"
    COLOR_BORDER = "#e0e0e0"

    st.markdown(
        f"""
        <style>

        .stApp {{
            background-color: {COLOR_BG};
        }}

        .comparativa-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .comparativa-subtitle {{
            text-align: center;
            color: {COLOR_SECONDARY};
            font-size: 1.1em;
            margin-bottom: 25px;
        }}

        .info-box {{
            background: {COLOR_HOVER};
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid {COLOR_PRIMARY};
            margin: 15px 0 25px 0;
            color: {COLOR_TEXT_DARK};
        }}

        .section-title {{
            color: {COLOR_PRIMARY};
            font-size: 1.4em;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 5px;
        }}

        .section-description {{
            color: #666666;
            font-size: 0.95em;
            margin-bottom: 20px;
        }}

        .legend-box {{
            background-color: {COLOR_CARD};
            border: 1px solid {COLOR_BORDER};
            border-radius: 10px;
            padding: 12px 15px;
            margin-top: 10px;
            margin-bottom: 20px;
            color: {COLOR_TEXT_DARK};
        }}

        .legend-color {{
            display: inline-block;
            width: 18px;
            height: 18px;
            background-color: #d4edda;
            border: 1px solid #28a745;
            border-radius: 4px;
            vertical-align: middle;
            margin-right: 8px;
        }}

        .stDataFrame {{
            background-color: {COLOR_CARD} !important;
        }}

        [data-testid="stDataFrame"] {{
            background-color: {COLOR_CARD} !important;
            border-radius: 12px !important;
            border: 1px solid {COLOR_BORDER} !important;
        }}

        [data-testid="stDataFrame"] th {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
            font-weight: 600 !important;
            text-align: center !important;
        }}

        [data-testid="stDataFrame"] td {{
            color: {COLOR_TEXT} !important;
            text-align: center !important;
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

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 🏪 OBTENER TODAS LAS TIENDAS ACTIVAS
# ============================================================
def obtener_tiendas_activas():
    """
    Obtiene todas las tiendas activas de la base de datos.

    Esto permite que TODAS aparezcan como columnas aunque
    alguna no tenga compras registradas para ciertos productos.
    """

    conn = obtener_conexion()

    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                id_tienda,
                nombre
            FROM tienda
            WHERE activo = 1
            ORDER BY id_tienda ASC
            """
        )

        tiendas = cursor.fetchall()

        return tiendas

    except Exception as e:

        st.error(
            f"❌ Error al obtener las tiendas: {e}"
        )

        return None

    finally:

        cursor.close()
        conn.close()


# ============================================================
# 🗄️ OBTENER DATOS DE COMPRAS
# ============================================================
def obtener_datos_comparativa():
    """
    Obtiene el PRECIO UNITARIO DE COMPRA de los productos.

    IMPORTANTE:
    Se utiliza ProductoxCompra.Precio_Compra.

    NO se utilizan:
    - Precio_minorista
    - Precio_mayorista1
    - Precio_mayorista2

    Por lo tanto, la tabla compara cuánto PAGÓ cada tienda
    por cada producto.
    """

    conn = obtener_conexion()

    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:

        query = """
            SELECT
                pc.cod_barra AS Codigo,
                p.Nombre AS Producto,
                pc.Precio_Compra AS Precio_Unitario_Compra,
                pc.id_tienda AS Id_Tienda,
                t.nombre AS Tienda,
                c.Fecha AS Fecha,
                c.Id_compra AS Id_Compra

            FROM ProductoxCompra pc

            JOIN Compra c
                ON pc.Id_compra = c.Id_compra

            JOIN Producto p
                ON pc.cod_barra = p.Cod_barra
                AND pc.id_tienda = p.id_tienda

            JOIN tienda t
                ON pc.id_tienda = t.id_tienda

            WHERE t.activo = 1

            ORDER BY
                c.Fecha DESC,
                c.Id_compra DESC
        """

        cursor.execute(query)

        resultados = cursor.fetchall()

        return resultados

    except Exception as e:

        st.error(
            f"❌ Error al obtener los datos de compras: {e}"
        )

        return None

    finally:

        cursor.close()
        conn.close()


# ============================================================
# 📊 PREPARAR TABLA COMPARATIVA
# ============================================================
def preparar_tabla_comparativa(datos, tiendas):
    """
    Genera la tabla:

    Producto | Tienda 1 | Cerro de Dios | Abasto Campesina | ...

    Cada celda muestra:
    PRECIO UNITARIO DE COMPRA MÁS RECIENTE.

    Si una tienda nunca compró el producto:
    se mantiene como NaN y luego se muestra como "—".
    """

    if not datos:
        return pd.DataFrame()

    if not tiendas:
        return pd.DataFrame()

    df = pd.DataFrame(datos)

    if df.empty:
        return pd.DataFrame()


    # ============================================================
    # CONVERTIR PRECIO A NUMÉRICO
    # ============================================================

    df["Precio_Unitario_Compra"] = pd.to_numeric(
        df["Precio_Unitario_Compra"],
        errors="coerce"
    )


    # ============================================================
    # CONVERTIR FECHA
    # ============================================================

    df["Fecha"] = pd.to_datetime(
        df["Fecha"],
        errors="coerce"
    )


    # ============================================================
    # ORDENAR PARA QUE LA COMPRA MÁS RECIENTE QUEDE PRIMERO
    # ============================================================

    df = df.sort_values(
        by=[
            "Codigo",
            "Id_Tienda",
            "Fecha",
            "Id_Compra"
        ],
        ascending=[
            True,
            True,
            False,
            False
        ]
    )


    # ============================================================
    # TOMAR SOLO LA COMPRA MÁS RECIENTE
    # DE CADA PRODUCTO EN CADA TIENDA
    # ============================================================

    df_ultimos_precios = df.drop_duplicates(
        subset=[
            "Codigo",
            "Id_Tienda"
        ],
        keep="first"
    ).copy()


    # ============================================================
    # CREAR TABLA HORIZONTAL
    # ============================================================

    tabla = df_ultimos_precios.pivot_table(
        index=[
            "Codigo",
            "Producto"
        ],
        columns="Tienda",
        values="Precio_Unitario_Compra",
        aggfunc="first"
    )


    # ============================================================
    # OBTENER NOMBRES DE TODAS LAS TIENDAS ACTIVAS
    # ============================================================

    nombres_tiendas = [
        tienda["nombre"]
        for tienda in tiendas
    ]


    # ============================================================
    # OBLIGAR A QUE TODAS LAS TIENDAS APAREZCAN
    #
    # Aunque no tengan compras registradas.
    # ============================================================

    tabla = tabla.reindex(
        columns=nombres_tiendas
    )


    # ============================================================
    # QUITAR NOMBRE DEL EJE DE COLUMNAS
    # ============================================================

    tabla.columns.name = None


    # ============================================================
    # REGRESAR CÓDIGO Y PRODUCTO COMO COLUMNAS
    # ============================================================

    tabla = tabla.reset_index()


    tabla = tabla.rename(
        columns={
            "Codigo": "Código"
        }
    )


    # ============================================================
    # ORDENAR PRODUCTOS ALFABÉTICAMENTE
    # ============================================================

    tabla = tabla.sort_values(
        by="Producto",
        key=lambda x: x.astype(str).str.lower(),
        ascending=True
    )


    tabla = tabla.reset_index(
        drop=True
    )


    return tabla


# ============================================================
# 🟢 RESALTAR MENOR PRECIO UNITARIO DE COMPRA
# ============================================================
def resaltar_precio_menor(fila):
    """
    Encuentra el menor precio UNITARIO DE COMPRA de la fila.

    NO analiza precio de venta.

    Las primeras columnas son:
    0 = Código
    1 = Producto

    Desde la posición 2 están las tiendas.
    """

    estilos = [
        ""
    ] * len(fila)


    # ============================================================
    # TOMAR SOLO PRECIOS DE LAS TIENDAS
    # ============================================================

    precios = pd.to_numeric(
        fila.iloc[2:],
        errors="coerce"
    )


    # ============================================================
    # IGNORAR TIENDAS SIN COMPRA REGISTRADA
    # ============================================================

    precios_validos = precios.dropna()


    if precios_validos.empty:
        return estilos


    # ============================================================
    # MENOR PRECIO DE COMPRA
    # ============================================================

    precio_minimo = precios_validos.min()


    # ============================================================
    # RESALTAR EN VERDE
    # ============================================================

    for posicion, precio in enumerate(
        precios,
        start=2
    ):

        if (
            pd.notna(precio)
            and precio == precio_minimo
        ):

            estilos[posicion] = (
                "background-color: #d4edda;"
                "color: #155724;"
                "font-weight: bold;"
                "border: 1px solid #28a745;"
            )


    return estilos


# ============================================================
# 💰 FORMATO MONEDA
# ============================================================
def formato_moneda(valor):
    """
    Ejemplo:

    0.40 -> $0.40

    Si no existe compra:

    NaN -> —
    """

    if pd.isna(valor):
        return "—"

    try:

        return f"${float(valor):,.2f}"

    except (ValueError, TypeError):

        return valor


# ============================================================
# 📋 MOSTRAR TABLA
# ============================================================
def mostrar_tabla_comparativa(tabla):

    if tabla.empty:

        st.info(
            "ℹ️ No hay compras registradas para generar "
            "la comparativa."
        )

        return


    # ============================================================
    # IDENTIFICAR COLUMNAS DE TIENDAS
    # ============================================================

    columnas_tiendas = [
        columna
        for columna in tabla.columns
        if columna not in [
            "Código",
            "Producto"
        ]
    ]


    # ============================================================
    # CREAR ESTILO
    # ============================================================

    tabla_estilizada = tabla.style.apply(
        resaltar_precio_menor,
        axis=1
    )


    # ============================================================
    # FORMATO DE MONEDA
    # ============================================================

    tabla_estilizada = tabla_estilizada.format(
        {
            columna: formato_moneda
            for columna in columnas_tiendas
        },
        na_rep="—"
    )


    # ============================================================
    # ALINEAR PRECIOS
    # ============================================================

    tabla_estilizada = tabla_estilizada.set_properties(
        subset=columnas_tiendas,
        **{
            "text-align": "center"
        }
    )


    # ============================================================
    # ALINEAR PRODUCTO Y CÓDIGO
    # ============================================================

    tabla_estilizada = tabla_estilizada.set_properties(
        subset=[
            "Código",
            "Producto"
        ],
        **{
            "text-align": "left"
        }
    )


    # ============================================================
    # MOSTRAR DATAFRAME
    # ============================================================

    st.dataframe(
        tabla_estilizada,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# ⭐ MÓDULO PRINCIPAL
# ============================================================
def modulo_comparativa_inv():

    configurar_estilo()


    # ============================================================
    # TÍTULO
    # ============================================================

    st.markdown(
        '<div class="comparativa-title">'
        '💰 Comparativa de Costos'
        '</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="comparativa-subtitle">'
        'Comparación del precio unitario de compra de productos entre las diferentes tiendas'
        '</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # 🔐 VALIDAR SESIÓN
    # ============================================================

    if not st.session_state.get(
        "logueado"
    ):

        st.error(
            "❌ No has iniciado sesión."
        )

        st.markdown("---")

        if st.button(
            "⬅ Volver al menú principal",
            use_container_width=True
        ):

            st.session_state["module"] = None

            st.rerun()

        return


    # ============================================================
    # 👑 SOLO ADMINISTRADOR
    # ============================================================

    rol_usuario = st.session_state.get(
        "nivel_usuario",
        ""
    )


    if rol_usuario != "Administrador":

        st.error(
            "⛔ Acceso denegado. "
            "Este módulo está disponible únicamente "
            "para el Administrador."
        )

        st.markdown("---")

        if st.button(
            "⬅ Volver al menú principal",
            use_container_width=True
        ):

            st.session_state["module"] = None

            st.rerun()

        return


    # ============================================================
    # ℹ️ EXPLICACIÓN
    # ============================================================

    st.markdown(
        '<div class="info-box">'
        '📌 <strong>¿Qué muestra esta tabla?</strong><br><br>'
        'Para cada producto se muestra el '
        '<strong>precio unitario al que cada tienda compró el producto</strong> '
        'en su compra más reciente.<br><br>'
        'No se utilizan precios de venta minorista ni mayorista. '
        'La comparación se realiza únicamente con el '
        '<strong>precio unitario de compra</strong>.'
        '</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # 📊 TÍTULO DE TABLA
    # ============================================================

    st.markdown(
        '<div class="section-title">'
        '📊 Comparativa de precios de compra por tienda'
        '</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="section-description">'
        'Las filas representan productos y cada columna representa una tienda activa del sistema.'
        '</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # 🟢 LEYENDA
    # ============================================================

    st.markdown(
        '<div class="legend-box">'
        '<span class="legend-color"></span>'
        '<strong>Menor costo de compra:</strong> '
        'la celda verde indica la tienda que registró el menor precio unitario de compra para ese producto.'
        '</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # ⏳ CARGAR TIENDAS
    # ============================================================

    with st.spinner(
        "Cargando tiendas y precios de compra..."
    ):

        tiendas = obtener_tiendas_activas()

        datos = obtener_datos_comparativa()


    # ============================================================
    # ERROR DE TIENDAS
    # ============================================================

    if tiendas is None:

        st.error(
            "❌ No fue posible obtener las tiendas."
        )


    # ============================================================
    # NO EXISTEN TIENDAS ACTIVAS
    # ============================================================

    elif len(tiendas) == 0:

        st.warning(
            "⚠️ No existen tiendas activas en el sistema."
        )


    # ============================================================
    # ERROR AL OBTENER COMPRAS
    # ============================================================

    elif datos is None:

        st.error(
            "❌ No fue posible cargar los precios de compra."
        )


    # ============================================================
    # NO EXISTEN COMPRAS
    # ============================================================

    elif len(datos) == 0:

        st.info(
            "ℹ️ Las tiendas existen, pero todavía no hay "
            "compras registradas para realizar la comparativa."
        )


    # ============================================================
    # GENERAR TABLA
    # ============================================================

    else:

        tabla_comparativa = preparar_tabla_comparativa(
            datos,
            tiendas
        )


        if tabla_comparativa.empty:

            st.info(
                "ℹ️ No existen datos suficientes para "
                "generar la comparativa."
            )

        else:

            # ====================================================
            # INFORMACIÓN GENERAL
            # ====================================================

            total_productos = len(
                tabla_comparativa
            )

            total_tiendas = len(
                tiendas
            )


            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    label="📦 Productos comparados",
                    value=total_productos
                )


            with col2:

                st.metric(
                    label="🏪 Tiendas activas",
                    value=total_tiendas
                )


            # ====================================================
            # MOSTRAR NOMBRES DE TIENDAS
            # ====================================================

            nombres_tiendas = [
                tienda["nombre"]
                for tienda in tiendas
            ]


            st.caption(
                "Tiendas incluidas: "
                + " • ".join(
                    nombres_tiendas
                )
            )


            st.markdown("---")


            # ====================================================
            # MOSTRAR TABLA
            # ====================================================

            mostrar_tabla_comparativa(
                tabla_comparativa
            )


            # ====================================================
            # ACLARACIONES
            # ====================================================

            st.caption(
                "🟢 Verde = menor precio unitario de compra "
                "registrado para ese producto."
            )

            st.caption(
                "— = esa tienda no tiene una compra registrada "
                "para ese producto."
            )


    # ============================================================
    # 🔙 VOLVER AL MENÚ
    # ============================================================

    st.markdown("---")

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )


    with col2:

        if st.button(
            "🔙 Volver al menú principal",
            use_container_width=True
        ):

            st.session_state["module"] = None

            st.session_state["macro_modulo"] = None

            st.rerun()
