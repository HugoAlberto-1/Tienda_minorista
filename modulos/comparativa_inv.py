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
    COLOR_ACCENT = "#3a7ca5"
    COLOR_BG = "#f5f7fa"
    COLOR_CARD = "#ffffff"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_DARK = "#1a1a1a"
    COLOR_HOVER = "#e8f0fe"
    COLOR_BORDER = "#e0e0e0"

    st.markdown(f"""
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

        [data-testid="stDataFrame"] table {{
            background-color: {COLOR_CARD} !important;
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

        .volver-btn button {{
            background-color: #6c757d !important;
            color: white !important;
            border: none !important;
        }}

        .volver-btn button:hover {{
            background-color: #5a6268 !important;
            color: white !important;
        }}

        </style>
    """, unsafe_allow_html=True)


# ============================================================
# 🗄️ OBTENER DATOS PARA LA COMPARATIVA
# ============================================================
def obtener_datos_comparativa():
    """
    Obtiene los precios unitarios de compra registrados
    para cada producto en cada tienda.
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
                pc.Precio_Compra AS Precio_Unitario,
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
            f"❌ Error al obtener los datos para la comparativa: {e}"
        )

        return None

    finally:

        cursor.close()
        conn.close()


# ============================================================
# 📊 PREPARAR TABLA COMPARATIVA
# ============================================================
def preparar_tabla_comparativa(datos):
    """
    Crea una tabla donde:

    Filas = Productos
    Columnas = Tiendas
    Valores = Precio unitario de la compra más reciente
    """

    if not datos:
        return pd.DataFrame()

    df = pd.DataFrame(datos)

    if df.empty:
        return pd.DataFrame()

    # Convertir precios a valores numéricos
    df["Precio_Unitario"] = pd.to_numeric(
        df["Precio_Unitario"],
        errors="coerce"
    )

    # Convertir fechas
    df["Fecha"] = pd.to_datetime(
        df["Fecha"],
        errors="coerce"
    )

    # Ordenar para que la compra más reciente quede primero
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

    # Quedarnos únicamente con la compra más reciente
    # de cada producto en cada tienda
    df_ultimos_precios = df.drop_duplicates(
        subset=[
            "Codigo",
            "Id_Tienda"
        ],
        keep="first"
    ).copy()

    # Crear tabla comparativa
    tabla = df_ultimos_precios.pivot_table(
        index=[
            "Codigo",
            "Producto"
        ],
        columns="Tienda",
        values="Precio_Unitario",
        aggfunc="first"
    )

    tabla.columns.name = None

    tabla = tabla.reset_index()

    tabla = tabla.rename(
        columns={
            "Codigo": "Código"
        }
    )

    # Ordenar alfabéticamente por producto
    tabla = tabla.sort_values(
        by="Producto",
        key=lambda x: x.astype(str).str.lower(),
        ascending=True
    )

    tabla = tabla.reset_index(drop=True)

    return tabla


# ============================================================
# 🟢 RESALTAR PRECIO MÁS BAJO
# ============================================================
def resaltar_precio_menor(fila):
    """
    Resalta el menor precio de cada producto.

    Si existe empate entre dos o más tiendas,
    todos los precios mínimos quedan resaltados.
    """

    estilos = [""] * len(fila)

    # Código y Producto son las primeras dos columnas.
    # Las demás columnas representan tiendas.
    precios = pd.to_numeric(
        fila.iloc[2:],
        errors="coerce"
    )

    precios_validos = precios.dropna()

    if precios_validos.empty:
        return estilos

    precio_minimo = precios_validos.min()

    for posicion, precio in enumerate(
        precios,
        start=2
    ):

        if pd.notna(precio) and precio == precio_minimo:

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
    Convierte:
    0.4 -> $0.40

    Si no existe precio:
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
            "la comparativa de precios."
        )

        return

    columnas_tiendas = [
        columna
        for columna in tabla.columns
        if columna not in ["Código", "Producto"]
    ]

    # Aplicar estilos
    tabla_estilizada = tabla.style.apply(
        resaltar_precio_menor,
        axis=1
    )

    # Formato monetario
    tabla_estilizada = tabla_estilizada.format(
        {
            columna: formato_moneda
            for columna in columnas_tiendas
        },
        na_rep="—"
    )

    # Centrar precios
    tabla_estilizada = tabla_estilizada.set_properties(
        subset=columnas_tiendas,
        **{
            "text-align": "center"
        }
    )

    # Alinear Código y Producto a la izquierda
    tabla_estilizada = tabla_estilizada.set_properties(
        subset=["Código", "Producto"],
        **{
            "text-align": "left"
        }
    )

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
        '<div class="comparativa-title">💰 Comparativa de Costos</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="comparativa-subtitle">Comparación del precio unitario de compra de productos entre las diferentes tiendas</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # 🔐 VERIFICAR SESIÓN
    # ============================================================

    if not st.session_state.get("logueado"):

        st.error(
            "❌ No has iniciado sesión. Inicia sesión primero."
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
    # ℹ️ INFORMACIÓN
    # ============================================================

    st.markdown(
        '<div class="info-box">'
        '📌 <strong>¿Qué muestra esta tabla?</strong><br><br>'
        'Para cada producto se muestra el <strong>precio unitario de la compra más reciente</strong> registrada por cada tienda.<br><br>'
        'Esto permite comparar rápidamente qué tienda está consiguiendo cada producto a un menor costo.'
        '</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # 📊 PRIMERA TABLA
    # ============================================================

    st.markdown(
        '<div class="section-title">📊 Comparativa de precios por tienda</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">Las filas representan productos y las columnas representan las tiendas activas del sistema.</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # 🟢 LEYENDA
    # ============================================================

    st.markdown(
        '<div class="legend-box">'
        '<span class="legend-color"></span>'
        '<strong>Mejor precio:</strong> '
        'la celda resaltada indica el precio unitario más bajo registrado para ese producto.'
        '</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # ⏳ CARGAR DATOS
    # ============================================================

    with st.spinner(
        "Cargando comparativa de precios..."
    ):

        datos = obtener_datos_comparativa()


    # ============================================================
    # ERROR DE CONEXIÓN
    # ============================================================

    if datos is None:

        st.error(
            "❌ No fue posible cargar la información "
            "de la base de datos."
        )


    # ============================================================
    # SIN DATOS
    # ============================================================

    elif len(datos) == 0:

        st.info(
            "ℹ️ Actualmente no existen compras registradas "
            "para realizar la comparativa."
        )


    # ============================================================
    # MOSTRAR DATOS
    # ============================================================

    else:

        tabla_comparativa = preparar_tabla_comparativa(
            datos
        )

        if tabla_comparativa.empty:

            st.info(
                "ℹ️ No existen datos suficientes para "
                "generar la comparativa."
            )

        else:

            total_productos = len(
                tabla_comparativa
            )

            columnas_tiendas = [
                columna
                for columna in tabla_comparativa.columns
                if columna not in [
                    "Código",
                    "Producto"
                ]
            ]

            total_tiendas = len(
                columnas_tiendas
            )


            # ====================================================
            # MÉTRICAS
            # ====================================================

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    label="📦 Productos comparados",
                    value=total_productos
                )

            with col2:

                st.metric(
                    label="🏪 Tiendas comparadas",
                    value=total_tiendas
                )


            st.markdown("---")


            # ====================================================
            # TABLA
            # ====================================================

            mostrar_tabla_comparativa(
                tabla_comparativa
            )


            st.caption(
                "— significa que esa tienda no tiene una compra "
                "registrada para ese producto."
            )


    # ============================================================
    # 🔙 VOLVER
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
