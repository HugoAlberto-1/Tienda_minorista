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
    Obtiene todas las tiendas activas.

    De esta forma todas las tiendas aparecerán en la tabla,
    aunque alguna no tenga compra registrada de cierto producto.
    """

    conn = obtener_conexion()

    if not conn:
        return None

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

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
            f"❌ Error al obtener las tiendas activas: {e}"
        )
        return None

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# 🗄️ OBTENER PRECIOS UNITARIOS DE COMPRA
# ============================================================
def obtener_datos_comparativa():
    """
    Obtiene exclusivamente el PRECIO UNITARIO DE COMPRA.

    Se utiliza:
        ProductoxCompra.Precio_Compra

    NO se utilizan:
        Precio_minorista
        Precio_mayorista1
        Precio_mayorista2

    Por tanto, esta información representa cuánto PAGÓ
    cada tienda por cada producto.
    """

    conn = obtener_conexion()

    if not conn:
        return None

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

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
            f"❌ Error al obtener los precios de compra: {e}"
        )
        return None

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# 📊 PREPARAR TABLA COMPARATIVA
# ============================================================
def preparar_tabla_comparativa(datos, tiendas):
    """
    Construye una tabla del tipo:

    Código | Producto | Tienda 1 | Cerro de Dios |
    Abasto Campesina | Canasta Comunitaria

    Cada celda contiene el precio unitario de la COMPRA
    MÁS RECIENTE del producto en esa tienda.
    """

    if datos is None or len(datos) == 0:
        return pd.DataFrame()

    if tiendas is None or len(tiendas) == 0:
        return pd.DataFrame()

    df = pd.DataFrame(datos)

    if df.empty:
        return pd.DataFrame()


    # ============================================================
    # VALIDAR COLUMNAS NECESARIAS
    # ============================================================

    columnas_necesarias = [
        "Codigo",
        "Producto",
        "Precio_Unitario_Compra",
        "Id_Tienda",
        "Tienda",
        "Fecha",
        "Id_Compra"
    ]

    faltantes = [
        columna
        for columna in columnas_necesarias
        if columna not in df.columns
    ]

    if faltantes:
        st.error(
            "❌ Faltan columnas necesarias para generar "
            f"la comparativa: {', '.join(faltantes)}"
        )
        return pd.DataFrame()


    # ============================================================
    # PRECIO UNITARIO DE COMPRA A NUMÉRICO
    # ============================================================

    df["Precio_Unitario_Compra"] = pd.to_numeric(
        df["Precio_Unitario_Compra"],
        errors="coerce"
    )


    # ============================================================
    # FECHA
    # ============================================================

    df["Fecha"] = pd.to_datetime(
        df["Fecha"],
        errors="coerce"
    )


    # ============================================================
    # ID COMPRA
    # ============================================================

    df["Id_Compra"] = pd.to_numeric(
        df["Id_Compra"],
        errors="coerce"
    )


    # ============================================================
    # ORDENAR PARA IDENTIFICAR LA COMPRA MÁS RECIENTE
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
    #
    # Ejemplo:
    #
    # Tienda 1 compra arroz:
    # Enero → $0.50
    # Marzo → $0.47
    # Junio → $0.42
    #
    # La tabla mostrará $0.42.
    # ============================================================

    df_ultimos = df.drop_duplicates(
        subset=[
            "Codigo",
            "Id_Tienda"
        ],
        keep="first"
    ).copy()


    # ============================================================
    # NOMBRES DE LAS TIENDAS ACTIVAS
    # ============================================================

    nombres_tiendas = []

    for tienda in tiendas:

        nombre = tienda.get("nombre")

        if nombre and nombre not in nombres_tiendas:
            nombres_tiendas.append(nombre)


    if not nombres_tiendas:
        return pd.DataFrame()


    # ============================================================
    # CREAR TABLA PIVOT
    # ============================================================

    tabla = df_ultimos.pivot_table(
        index=[
            "Codigo",
            "Producto"
        ],
        columns="Tienda",
        values="Precio_Unitario_Compra",
        aggfunc="first",
        dropna=False
    )


    # ============================================================
    # OBLIGAR A MOSTRAR TODAS LAS TIENDAS ACTIVAS
    #
    # Si están activas:
    #
    # Tienda 1
    # Cerro de Dios
    # Abasto Campesina
    # Canasta Comunitaria
    #
    # las cuatro aparecerán aunque tengan celdas vacías.
    # ============================================================

    tabla = tabla.reindex(
        columns=nombres_tiendas
    )


    tabla.columns.name = None


    # ============================================================
    # VOLVER ÍNDICES A COLUMNAS NORMALES
    # ============================================================

    tabla = tabla.reset_index()


    # ============================================================
    # RENOMBRAR CÓDIGO
    # ============================================================

    tabla = tabla.rename(
        columns={
            "Codigo": "Código"
        }
    )


    # ============================================================
    # ASEGURAR ORDEN DE COLUMNAS
    # ============================================================

    columnas_finales = [
        "Código",
        "Producto"
    ] + nombres_tiendas

    columnas_existentes = [
        columna
        for columna in columnas_finales
        if columna in tabla.columns
    ]

    tabla = tabla[columnas_existentes]


    # ============================================================
    # ELIMINAR FILAS QUE REALMENTE NO TENGAN NINGÚN PRECIO
    # ============================================================

    columnas_precios = [
        columna
        for columna in nombres_tiendas
        if columna in tabla.columns
    ]

    if columnas_precios:

        tiene_algun_precio = tabla[
            columnas_precios
        ].notna().any(axis=1)

        tabla = tabla[
            tiene_algun_precio
        ].copy()


    # ============================================================
    # ORDENAR POR NOMBRE DE PRODUCTO
    # ============================================================

    if "Producto" in tabla.columns:

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
# 🟢 CREAR MATRIZ DE ESTILOS
# ============================================================
def crear_estilos_precios(dataframe, columnas_tiendas):
    """
    Crea una matriz de estilos con exactamente el mismo
    tamaño que el DataFrame.

    Esto evita los KeyError que se estaban produciendo
    anteriormente con Pandas Styler.

    Se resalta únicamente el menor PRECIO UNITARIO DE COMPRA
    de cada producto.
    """

    estilos = pd.DataFrame(
        "",
        index=dataframe.index,
        columns=dataframe.columns
    )


    if not columnas_tiendas:
        return estilos


    # ============================================================
    # RECORRER PRODUCTO POR PRODUCTO
    # ============================================================

    for indice in dataframe.index:

        precios = {}

        for columna in columnas_tiendas:

            if columna not in dataframe.columns:
                continue

            valor = dataframe.at[
                indice,
                columna
            ]

            try:

                if pd.notna(valor):

                    precio = float(valor)

                    precios[columna] = precio

            except (ValueError, TypeError):

                continue


        # ========================================================
        # SI EL PRODUCTO NO TIENE PRECIOS, NO HACER NADA
        # ========================================================

        if not precios:
            continue


        # ========================================================
        # ENCONTRAR MENOR PRECIO UNITARIO DE COMPRA
        # ========================================================

        precio_minimo = min(
            precios.values()
        )


        # ========================================================
        # RESALTAR LA O LAS TIENDAS CON MENOR COSTO
        # ========================================================

        for columna, precio in precios.items():

            if precio == precio_minimo:

                estilos.at[
                    indice,
                    columna
                ] = (
                    "background-color: #d4edda;"
                    "color: #155724;"
                    "font-weight: bold;"
                    "border: 1px solid #28a745;"
                )


    return estilos


# ============================================================
# 💰 FORMATEAR PRECIO
# ============================================================
def formato_moneda(valor):
    """
    Convierte:

    0.4 → $0.40

    Si no existe compra:

    NaN → —
    """

    if pd.isna(valor):
        return "—"

    try:
        return f"${float(valor):,.2f}"

    except (ValueError, TypeError):
        return str(valor)


# ============================================================
# 📋 MOSTRAR TABLA COMPARATIVA
# ============================================================
def mostrar_tabla_comparativa(tabla, nombres_tiendas):
    """
    Muestra la tabla comparativa y resalta
    el menor precio unitario de compra.
    """

    if tabla is None or tabla.empty:

        st.info(
            "ℹ️ No hay compras registradas para generar "
            "la comparativa."
        )

        return


    # ============================================================
    # COPIA SEGURA
    # ============================================================

    tabla_mostrar = tabla.copy()


    # ============================================================
    # IDENTIFICAR COLUMNAS DE TIENDAS
    #
    # Solamente usamos tiendas que realmente estén
    # presentes en la tabla.
    # ============================================================

    columnas_tiendas = [
        tienda
        for tienda in nombres_tiendas
        if tienda in tabla_mostrar.columns
    ]


    # ============================================================
    # CONVERTIR TODAS LAS COLUMNAS DE PRECIOS A NUMÉRICO
    # ============================================================

    for columna in columnas_tiendas:

        tabla_mostrar[columna] = pd.to_numeric(
            tabla_mostrar[columna],
            errors="coerce"
        )


    # ============================================================
    # CREAR MATRIZ DE ESTILOS
    # ============================================================

    matriz_estilos = crear_estilos_precios(
        tabla_mostrar,
        columnas_tiendas
    )


    # ============================================================
    # CREAR STYLER
    # ============================================================

    tabla_estilizada = tabla_mostrar.style


    # ============================================================
    # APLICAR LOS ESTILOS
    #
    # axis=None permite aplicar una matriz completa de estilos
    # con las mismas filas y columnas del DataFrame.
    # ============================================================

    tabla_estilizada = tabla_estilizada.apply(
        lambda _: matriz_estilos,
        axis=None
    )


    # ============================================================
    # FORMATO DE PRECIOS
    # ============================================================

    formatos = {}

    for columna in columnas_tiendas:

        formatos[columna] = formato_moneda


    if formatos:

        tabla_estilizada = tabla_estilizada.format(
            formatos,
            na_rep="—"
        )


    # ============================================================
    # ALINEACIÓN GENERAL
    # ============================================================

    tabla_estilizada = tabla_estilizada.set_properties(
        **{
            "text-align": "center"
        }
    )


    # ============================================================
    # CÓDIGO Y PRODUCTO A LA IZQUIERDA
    # ============================================================

    columnas_texto = []

    if "Código" in tabla_mostrar.columns:
        columnas_texto.append("Código")

    if "Producto" in tabla_mostrar.columns:
        columnas_texto.append("Producto")


    if columnas_texto:

        tabla_estilizada = tabla_estilizada.set_properties(
            subset=columnas_texto,
            **{
                "text-align": "left"
            }
        )


    # ============================================================
    # MOSTRAR
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
    # 🔐 VERIFICAR SESIÓN
    # ============================================================

    if not st.session_state.get(
        "logueado"
    ):

        st.error(
            "❌ No has iniciado sesión. "
            "Inicia sesión primero."
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
        'La comparación utiliza únicamente el '
        '<strong>precio unitario de compra</strong>. '
        'No se utilizan precios de venta minorista ni mayorista.'
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
        'Cada fila representa un producto y cada columna representa una tienda activa del sistema.'
        '</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # 🟢 LEYENDA
    # ============================================================

    st.markdown(
        '<div class="legend-box">'
        '<span class="legend-color"></span>'
        '<strong>Menor costo unitario de compra:</strong> '
        'la celda verde identifica la tienda que registró '
        'el menor precio unitario de compra para ese producto.'
        '</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # ⏳ CARGAR INFORMACIÓN
    # ============================================================

    with st.spinner(
        "Cargando tiendas y precios unitarios de compra..."
    ):

        tiendas = obtener_tiendas_activas()

        datos = obtener_datos_comparativa()


    # ============================================================
    # ERROR AL OBTENER TIENDAS
    # ============================================================

    if tiendas is None:

        st.error(
            "❌ No fue posible obtener la información "
            "de las tiendas."
        )


    # ============================================================
    # SIN TIENDAS
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
            "❌ No fue posible obtener los precios "
            "unitarios de compra."
        )


    # ============================================================
    # NOMBRES DE LAS TIENDAS
    # ============================================================

    else:

        nombres_tiendas = []

        for tienda in tiendas:

            nombre = tienda.get("nombre")

            if nombre and nombre not in nombres_tiendas:
                nombres_tiendas.append(nombre)


        # ========================================================
        # MOSTRAR LAS TIENDAS DETECTADAS
        # ========================================================

        if nombres_tiendas:

            st.caption(
                "🏪 Tiendas incluidas: "
                + " • ".join(nombres_tiendas)
            )


        # ========================================================
        # NO HAY COMPRAS
        # ========================================================

        if len(datos) == 0:

            st.info(
                "ℹ️ Las tiendas están registradas, pero todavía "
                "no existen compras para generar la comparativa."
            )


        # ========================================================
        # GENERAR TABLA
        # ========================================================

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

                # ================================================
                # MÉTRICAS
                # ================================================

                total_productos = len(
                    tabla_comparativa
                )

                total_tiendas = len(
                    nombres_tiendas
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


                st.markdown("---")


                # ================================================
                # TABLA
                # ================================================

                mostrar_tabla_comparativa(
                    tabla_comparativa,
                    nombres_tiendas
                )


                # ================================================
                # ACLARACIONES
                # ================================================

                st.caption(
                    "🟢 Verde = menor precio UNITARIO DE COMPRA "
                    "registrado para ese producto."
                )

                st.caption(
                    "— = esa tienda no tiene una compra "
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
