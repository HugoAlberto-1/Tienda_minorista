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

        .stTextInput > label,
        .stSelectbox > label {{
            color: {COLOR_TEXT_DARK} !important;
            font-weight: 500 !important;
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

        .evaluador-title {{
            color: {COLOR_PRIMARY};
            font-size: 1.25em;
            font-weight: 700;
            margin-top: 18px;
            margin-bottom: 4px;
        }}

        .evaluador-subtitle {{
            color: #6b7280;
            font-size: 0.92em;
            margin-bottom: 14px;
        }}

        .evaluador-label {{
            color: {COLOR_PRIMARY};
            font-weight: 700;
            font-size: 0.92em;
            margin-bottom: 7px;
        }}

        .aviso-caro {{
            background-color: #fff4e5;
            border: 1px solid #f0ad4e;
            border-left: 5px solid #f0ad4e;
            color: #7a4b00;
            padding: 13px 15px;
            border-radius: 10px;
            margin-top: 12px;
        }}

        .aviso-optimo {{
            background-color: #eaf7ee;
            border: 1px solid #28a745;
            border-left: 5px solid #28a745;
            color: #155724;
            padding: 13px 15px;
            border-radius: 10px;
            margin-top: 12px;
        }}

        .aviso-neutral {{
            background-color: #eef4fb;
            border: 1px solid #7aa7d9;
            border-left: 5px solid #7aa7d9;
            color: #214d75;
            padding: 13px 15px;
            border-radius: 10px;
            margin-top: 12px;
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
    Obtiene todas las tiendas activas, para que todas aparezcan en la
    tabla aunque alguna no tenga compra registrada de cierto producto.
    """
    conn = obtener_conexion()
    if not conn:
        return None

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_tienda, nombre
            FROM tienda
            WHERE activo = 1
            ORDER BY id_tienda ASC
            """
        )
        return cursor.fetchall()

    except Exception as e:
        st.error(f"❌ Error al obtener las tiendas activas: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================
# 🔎 OBTENER CATÁLOGO PARA EL BUSCADOR
# ============================================================
def obtener_catalogo_productos():
    """
    Obtiene los productos pertenecientes a tiendas ACTIVAS para alimentar
    el buscador/autocompletado.

    El buscador mostrará:
        Nombre del producto  |  Código de barras

    De esta forma el usuario puede escribir tanto letras como números.
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
                p.Cod_barra AS Codigo,
                p.Nombre AS Producto
            FROM Producto p
            JOIN tienda t
                ON p.id_tienda = t.id_tienda
            WHERE t.activo = 1
            ORDER BY p.Nombre ASC, p.Cod_barra ASC
            """
        )
        registros = cursor.fetchall()

        if not registros:
            return []

        # Un mismo código puede estar registrado en varias tiendas.
        # Elegimos un solo nombre representativo por código para no repetir
        # sugerencias en el desplegable.
        df = pd.DataFrame(registros)

        if df.empty or "Codigo" not in df.columns or "Producto" not in df.columns:
            return []

        df["Codigo"] = df["Codigo"].astype(str).str.strip()
        df["Producto"] = df["Producto"].fillna("").astype(str).str.strip()

        df = df[(df["Codigo"] != "") & (df["Producto"] != "")].copy()

        if df.empty:
            return []

        catalogo = (
            df.groupby("Codigo", as_index=False)["Producto"]
            .agg(
                lambda serie: (
                    serie[serie != ""].value_counts().idxmax()
                    if not serie[serie != ""].empty
                    else ""
                )
            )
        )

        catalogo = catalogo.sort_values(
            by="Producto",
            key=lambda x: x.astype(str).str.lower()
        )

        return catalogo.to_dict("records")

    except Exception as e:
        st.error(f"❌ Error al cargar los productos para el buscador: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================
# 🗄️ OBTENER PRECIOS UNITARIOS DE COMPRA
# ============================================================
def obtener_datos_comparativa(codigo_filtro=None):
    """
    Obtiene el HISTORIAL de precios unitarios de compra
    (ProductoxCompra.Precio_Compra) de las tiendas activas.

    Después, preparar_tabla_comparativa() selecciona ÚNICAMENTE la compra
    MÁS RECIENTE de cada producto en cada tienda, usando:
        1) Fecha DESC
        2) Id_Compra DESC como desempate

    No se usan precios de venta.

    Si se selecciona un producto en el buscador, se filtra por su código
    de barras exacto. Si no se selecciona ninguno, se muestran todos.
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
        """

        params = []

        if codigo_filtro is not None and str(codigo_filtro).strip() != "":
            # CAST permite comparar correctamente aunque el código venga
            # desde Python como texto.
            query += " AND CAST(pc.cod_barra AS CHAR) = %s"
            params.append(str(codigo_filtro).strip())

        query += " ORDER BY c.Fecha DESC, c.Id_compra DESC"

        cursor.execute(query, tuple(params))
        return cursor.fetchall()

    except Exception as e:
        st.error(f"❌ Error al obtener los precios de compra: {e}")
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
    Construye la tabla ancha:
    Código | Producto | Tienda A | Tienda B | ... | Tienda más barata

    Usa exclusivamente el precio unitario de la ÚLTIMA COMPRA REGISTRADA
    para cada producto en cada tienda activa.

    La última compra se determina por Fecha más reciente y, si dos compras
    tienen la misma Fecha, por el Id_Compra más alto.
    """
    if not datos or not tiendas:
        return pd.DataFrame()

    df = pd.DataFrame(datos)
    if df.empty:
        return pd.DataFrame()

    # Seguridad adicional: trabajar únicamente con tiendas activas recibidas
    # desde obtener_tiendas_activas(), incluso si en el futuro cambia la consulta.
    ids_tiendas_activas = {
        tienda.get("id_tienda")
        for tienda in tiendas
        if tienda.get("id_tienda") is not None
    }

    if ids_tiendas_activas and "Id_Tienda" in df.columns:
        df = df[df["Id_Tienda"].isin(ids_tiendas_activas)].copy()

    if df.empty:
        return pd.DataFrame()

    columnas_necesarias = [
        "Codigo",
        "Producto",
        "Precio_Unitario_Compra",
        "Id_Tienda",
        "Tienda",
        "Fecha",
        "Id_Compra"
    ]

    faltantes = [c for c in columnas_necesarias if c not in df.columns]

    if faltantes:
        st.error(
            "❌ Faltan columnas necesarias para generar la comparativa: "
            + ", ".join(faltantes)
        )
        return pd.DataFrame()

    # El código se mantiene como texto para no perder el formato visual
    # si la BD lo almacena como VARCHAR/CHAR.
    df["Codigo"] = df["Codigo"].astype(str).str.strip()

    df["Precio_Unitario_Compra"] = pd.to_numeric(
        df["Precio_Unitario_Compra"],
        errors="coerce"
    )

    df["Fecha"] = pd.to_datetime(
        df["Fecha"],
        errors="coerce"
    )

    df["Id_Compra"] = pd.to_numeric(
        df["Id_Compra"],
        errors="coerce"
    )

    # IMPORTANTE:
    # Para comparar tiendas NO usamos un promedio ni el precio mínimo histórico.
    # Primero buscamos la ÚLTIMA COMPRA de ese producto en CADA tienda.
    #
    # Orden:
    #   - Código
    #   - Tienda
    #   - Fecha más reciente primero
    #   - Id_Compra más alto primero (desempate si la fecha es igual)
    df = df.sort_values(
        by=["Codigo", "Id_Tienda", "Fecha", "Id_Compra"],
        ascending=[True, True, False, False]
    )

    # Como cada grupo Código + Tienda ya quedó ordenado de más reciente
    # a más antiguo, keep="first" conserva exactamente la última compra
    # registrada para ese producto en esa tienda.
    df_ultimos = df.drop_duplicates(
        subset=["Codigo", "Id_Tienda"],
        keep="first"
    ).copy()

    # Cada tienda puede tener pequeñas variaciones en Producto.Nombre.
    # Elegimos un único nombre representativo por código.
    nombre_representativo = (
        df_ultimos.groupby("Codigo")["Producto"]
        .agg(lambda serie: serie.value_counts().idxmax())
    )

    df_ultimos["Producto"] = df_ultimos["Codigo"].map(
        nombre_representativo
    )

    nombres_tiendas = []

    for tienda in tiendas:
        nombre = tienda.get("nombre")

        if nombre and nombre not in nombres_tiendas:
            nombres_tiendas.append(nombre)

    if not nombres_tiendas:
        return pd.DataFrame()

    tabla = df_ultimos.pivot_table(
        index=["Codigo", "Producto"],
        columns="Tienda",
        values="Precio_Unitario_Compra",
        aggfunc="first",
        dropna=False
    )

    # Mostrar todas las tiendas activas aunque alguna no tenga una compra
    # registrada para ese producto.
    tabla = tabla.reindex(columns=nombres_tiendas)
    tabla.columns.name = None

    tabla = tabla.reset_index().rename(
        columns={"Codigo": "Código"}
    )

    columnas_finales = (
        ["Código", "Producto"]
        + nombres_tiendas
    )

    tabla = tabla[
        [c for c in columnas_finales if c in tabla.columns]
    ]

    columnas_precios = [
        c for c in nombres_tiendas
        if c in tabla.columns
    ]

    if columnas_precios:
        precios_num = tabla[columnas_precios].apply(
            pd.to_numeric,
            errors="coerce"
        )

        # Eliminar filas donde ninguna tienda tenga un precio registrado.
        tiene_algun_precio = precios_num.notna().any(axis=1)

        tabla = tabla[tiene_algun_precio].copy()
        precios_num = precios_num[tiene_algun_precio]

        # Siempre mostrar el nombre de la tienda con el menor precio,
        # incluso cuando el producto solamente esté en una tienda.
        tabla["🏆 Tienda más barata"] = precios_num.idxmin(axis=1)

    if "Producto" in tabla.columns:
        tabla = tabla.sort_values(
            by="Producto",
            key=lambda x: x.astype(str).str.lower(),
            ascending=True
        )

    return tabla.reset_index(drop=True)


# ============================================================
# 🟢 CREAR MATRIZ DE ESTILOS
# ============================================================
def crear_estilos_precios(dataframe, columnas_tiendas):
    """
    Resalta únicamente el menor precio unitario de compra de cada producto.
    """
    estilos = pd.DataFrame(
        "",
        index=dataframe.index,
        columns=dataframe.columns
    )

    if not columnas_tiendas:
        return estilos

    for indice in dataframe.index:
        precios = {}

        for columna in columnas_tiendas:
            if columna not in dataframe.columns:
                continue

            valor = dataframe.at[indice, columna]

            try:
                if pd.notna(valor):
                    precios[columna] = float(valor)

            except (ValueError, TypeError):
                continue

        if not precios:
            continue

        precio_minimo = min(precios.values())

        for columna, precio in precios.items():
            if precio == precio_minimo:
                estilos.at[indice, columna] = (
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
    if tabla is None or tabla.empty:
        st.info(
            "ℹ️ No hay compras registradas para generar la comparativa."
        )
        return

    tabla_mostrar = tabla.copy()

    columnas_tiendas = [
        t for t in nombres_tiendas
        if t in tabla_mostrar.columns
    ]

    for columna in columnas_tiendas:
        tabla_mostrar[columna] = pd.to_numeric(
            tabla_mostrar[columna],
            errors="coerce"
        )

    matriz_estilos = crear_estilos_precios(
        tabla_mostrar,
        columnas_tiendas
    )

    tabla_estilizada = tabla_mostrar.style

    tabla_estilizada = tabla_estilizada.apply(
        lambda _: matriz_estilos,
        axis=None
    )

    formatos = {
        columna: formato_moneda
        for columna in columnas_tiendas
    }

    if formatos:
        tabla_estilizada = tabla_estilizada.format(
            formatos,
            na_rep="—"
        )

    tabla_estilizada = tabla_estilizada.set_properties(
        **{"text-align": "center"}
    )

    columnas_texto = [
        c
        for c in [
            "Código",
            "Producto",
            "🏆 Tienda más barata"
        ]
        if c in tabla_mostrar.columns
    ]

    if columnas_texto:
        tabla_estilizada = tabla_estilizada.set_properties(
            subset=columnas_texto,
            **{"text-align": "left"}
        )

    st.dataframe(
        tabla_estilizada,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 🧮 OBTENER PRECIO VERDE ACTUAL DE UN PRODUCTO
# ============================================================
def obtener_precio_verde_producto(codigo_producto, tiendas):
    """
    Obtiene exactamente la misma referencia usada por la tabla:
    la última compra registrada de ese producto en cada tienda activa
    y, entre esas últimas compras, toma el menor precio.
    """
    datos_producto = obtener_datos_comparativa(
        codigo_filtro=codigo_producto
    )

    if datos_producto is None or len(datos_producto) == 0:
        return None, None

    tabla_producto = preparar_tabla_comparativa(
        datos_producto,
        tiendas
    )

    if tabla_producto.empty:
        return None, None

    nombres_tiendas = []
    for tienda in tiendas:
        nombre = tienda.get("nombre")
        if nombre and nombre not in nombres_tiendas:
            nombres_tiendas.append(nombre)

    fila = tabla_producto.iloc[0]

    precios = {}

    for nombre_tienda in nombres_tiendas:
        if nombre_tienda not in tabla_producto.columns:
            continue

        valor = fila.get(nombre_tienda)

        try:
            if pd.notna(valor):
                precios[nombre_tienda] = float(valor)
        except (TypeError, ValueError):
            continue

    if not precios:
        return None, None

    precio_verde = min(precios.values())
    tienda_verde = min(precios, key=precios.get)

    return precio_verde, tienda_verde


# ============================================================
# 🔄 REINICIAR CAMPOS DEL EVALUADOR
# ============================================================
def reiniciar_campos_evaluador():
    """
    Limpia los valores temporales del evaluador.
    """
    st.session_state.pop("evaluador_precio_unitario", None)
    st.session_state.pop("evaluador_costo_extra", None)


# ============================================================
# 🧩 FRAGMENTO DEL EVALUADOR
# ============================================================
_fragment = st.fragment if hasattr(st, "fragment") else (lambda func: func)


# ============================================================
# 🧾 EVALUAR NUEVO PROVEEDOR
# ============================================================
@_fragment
def mostrar_evaluador_nuevo_proveedor(tiendas, catalogo_productos):
    """
    Herramienta temporal para comparar un precio ofrecido por un nuevo
    proveedor contra el precio verde actual.

    No guarda información ni modifica la base de datos.
    """
    if not tiendas or not catalogo_productos:
        return

    st.markdown("---")

    st.markdown(
        '<div class="evaluador-title">🧮 Evaluar nuevo proveedor</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="evaluador-subtitle">'
        'Compara un nuevo precio contra el mejor precio actual registrado para el producto.'
        '</div>',
        unsafe_allow_html=True
    )

    etiquetas_productos = {}

    for producto in catalogo_productos:
        codigo = str(producto.get("Codigo", "")).strip()
        nombre = str(producto.get("Producto", "")).strip()

        if codigo and nombre:
            etiquetas_productos[codigo] = (
                f"{nombre}  |  Código: {codigo}"
            )

    opciones_codigos = list(etiquetas_productos.keys())

    # Las 4 columnas existen para conservar el diseño,
    # pero Costo extra y Costo total NO se dibujan hasta validar el precio.
    col_producto, col_precio, col_extra, col_total = st.columns(
        [1.55, 1, 1, 1]
    )

    # --------------------------------------------------------
    # PRODUCTO
    # --------------------------------------------------------
    with col_producto:
        st.markdown(
            '<div class="evaluador-label">Nombre del producto</div>',
            unsafe_allow_html=True
        )

        codigo_evaluar = st.selectbox(
            "Nombre del producto a evaluar",
            options=opciones_codigos,
            index=None,
            placeholder="Escribe nombre o código...",
            format_func=lambda codigo: etiquetas_productos.get(
                codigo,
                str(codigo)
            ),
            label_visibility="collapsed",
            key="evaluador_producto"
        )

    # --------------------------------------------------------
    # REINICIO REAL AL CAMBIAR DE PRODUCTO
    # --------------------------------------------------------
    # Se compara el producto actual contra el último producto evaluado.
    # Si cambió, se limpian Precio unitario y Costo extra ANTES de crear
    # esos widgets, evitando que aparezca el valor del producto anterior.
    producto_anterior = st.session_state.get(
        "evaluador_producto_anterior"
    )

    if codigo_evaluar != producto_anterior:
        reiniciar_campos_evaluador()
        st.session_state["evaluador_producto_anterior"] = codigo_evaluar

    precio_verde = None
    tienda_verde = None

    if codigo_evaluar is not None:
        precio_verde, tienda_verde = obtener_precio_verde_producto(
            codigo_evaluar,
            tiendas
        )

    # --------------------------------------------------------
    # PRECIO UNITARIO
    # --------------------------------------------------------
    with col_precio:
        st.markdown(
            '<div class="evaluador-label">Precio unitario</div>',
            unsafe_allow_html=True
        )

        precio_unitario = st.number_input(
            "Precio unitario nuevo",
            min_value=0.0,
            value=None,
            step=0.01,
            format="%.2f",
            placeholder="Digite el precio",
            disabled=(
                codigo_evaluar is None
                or precio_verde is None
            ),
            label_visibility="collapsed",
            key="evaluador_precio_unitario"
        )

        if precio_verde is not None:
            st.caption(
                f"Actual: ${precio_verde:,.2f}"
            )

    # --------------------------------------------------------
    # VALIDAR PRECIO UNITARIO
    # --------------------------------------------------------
    precio_unitario_valido = (
        precio_verde is not None
        and precio_unitario is not None
        and precio_unitario > 0
        and precio_unitario < precio_verde
    )

    # --------------------------------------------------------
    # COSTO EXTRA Y COSTO TOTAL
    # --------------------------------------------------------
    # IMPORTANTE:
    # Estas dos cajas NO aparecen mientras el precio unitario:
    # - esté vacío
    # - sea igual al actual
    # - sea mayor al actual
    #
    # Solo aparecen cuando el precio unitario nuevo ya fue validado
    # como MENOR que el valor verde.
    costo_extra = None
    costo_total = None

    if precio_unitario_valido:
        with col_extra:
            st.markdown(
                '<div class="evaluador-label">Costo extra</div>',
                unsafe_allow_html=True
            )

            costo_extra = st.number_input(
                "Costo extra",
                min_value=0.0,
                value=None,
                step=0.01,
                format="%.2f",
                placeholder="Digite el costo extra",
                label_visibility="collapsed",
                key="evaluador_costo_extra"
            )

        if costo_extra is not None:
            costo_total = (
                float(precio_unitario)
                + float(costo_extra)
            )

        with col_total:
            st.markdown(
                '<div class="evaluador-label">Costo total</div>',
                unsafe_allow_html=True
            )

            st.text_input(
                "Costo total calculado",
                value=(
                    f"${costo_total:,.2f}"
                    if costo_total is not None
                    else ""
                ),
                placeholder="Se calcula al terminar",
                disabled=True,
                label_visibility="collapsed",
                key=f"evaluador_total_visual_{codigo_evaluar}"
            )

    # --------------------------------------------------------
    # MENSAJES DE DECISIÓN
    # --------------------------------------------------------
    if codigo_evaluar is None:
        return

    if precio_verde is None:
        st.markdown(
            '<div class="aviso-neutral">'
            'ℹ️ Este producto no tiene una compra registrada en las tiendas activas, '
            'por lo que todavía no existe un precio de referencia para compararlo.'
            '</div>',
            unsafe_allow_html=True
        )
        return

    # Mientras Precio unitario esté vacío, no mostramos mensajes.
    if precio_unitario is None or precio_unitario <= 0:
        return

    nombre_producto = etiquetas_productos.get(
        codigo_evaluar,
        str(codigo_evaluar)
    ).split("  |  Código:")[0]

    # Si el precio nuevo es mayor, avisar y NO mostrar los otros campos.
    if precio_unitario > precio_verde:
        st.markdown(
            f'<div class="aviso-caro">'
            f'⚠️ <strong>Este precio es mayor a los que ya existen en el sistema.</strong> '
            f'Para <strong>{nombre_producto}</strong>, el precio unitario digitado '
            f'es <strong>${precio_unitario:,.2f}</strong>, mientras que el mejor '
            f'precio actual es <strong>${precio_verde:,.2f}</strong> '
            f'en <strong>{tienda_verde}</strong>.'
            f'</div>',
            unsafe_allow_html=True
        )
        return

    # Si es igual, tampoco se muestran Costo extra ni Costo total.
    if precio_unitario == precio_verde:
        st.markdown(
            f'<div class="aviso-neutral">'
            f'ℹ️ El precio unitario digitado es igual al mejor precio actual '
            f'(<strong>${precio_verde:,.2f}</strong>).'
            f'</div>',
            unsafe_allow_html=True
        )
        return

    # Si el precio unitario es menor, NO se recomienda cambiar todavía.
    # Primero esperamos a que el usuario termine de ingresar Costo extra
    # y exista un Costo total.
    if costo_total is None:
        return

    # Solo aquí, después de calcular el Costo total, se emite la decisión.
    if costo_total < precio_verde:
        ahorro = precio_verde - costo_total

        st.markdown(
            f'<div class="aviso-optimo">'
            f'✅ <strong>Este nuevo proveedor es la mejor opción para '
            f'{nombre_producto}.</strong> '
            f'El costo total calculado del nuevo proveedor es '
            f'<strong>${costo_total:,.2f}</strong>, menor que el mejor costo '
            f'actual de <strong>${precio_verde:,.2f}</strong> en '
            f'<strong>{tienda_verde}</strong>. '
            f'Se sugiere considerar comprar este producto al nuevo proveedor. '
            f'La diferencia favorable es de '
            f'<strong>${ahorro:,.2f}</strong> por unidad.'
            f'</div>',
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            f'<div class="aviso-caro">'
            f'⚠️ <strong>El precio unitario es menor, pero el costo total ya no conviene.</strong> '
            f'Al sumar el costo extra, el nuevo proveedor queda en '
            f'<strong>${costo_total:,.2f}</strong>, frente al mejor precio actual '
            f'de <strong>${precio_verde:,.2f}</strong> en '
            f'<strong>{tienda_verde}</strong>.'
            f'</div>',
            unsafe_allow_html=True
        )


# ============================================================
# ⭐ MÓDULO PRINCIPAL
# ============================================================
def modulo_comparativa_precios():
    configurar_estilo()

    st.markdown(
        '<div class="comparativa-title">💰 Comparativa de Costos</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="comparativa-subtitle">'
        'Comparación del precio unitario de compra de productos entre las diferentes tiendas'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # 🔐 VALIDACIÓN DE SESIÓN
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # 🔐 VALIDACIÓN DE ROL
    # --------------------------------------------------------
    rol_usuario = st.session_state.get(
        "nivel_usuario",
        ""
    )

    if rol_usuario != "Administrador":
        st.error(
            "⛔ Acceso denegado. Este módulo está disponible únicamente para el Administrador."
        )

        st.markdown("---")

        if st.button(
            "⬅ Volver al menú principal",
            use_container_width=True
        ):
            st.session_state["module"] = None
            st.rerun()

        return

    # --------------------------------------------------------
    # ℹ️ INFORMACIÓN
    # --------------------------------------------------------
    st.markdown(
        '<div class="info-box">'
        '📌 <strong>¿Qué muestra esta tabla?</strong><br><br>'
        'Para cada producto se muestra el <strong>precio unitario de la última compra '
        'registrada de ese producto en cada tienda</strong>.<br><br>'
        'La comparación utiliza únicamente el <strong>precio unitario de compra</strong>. '
        'No se utilizan precios de venta minorista ni mayorista.'
        '</div>',
        unsafe_allow_html=True
    )

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

    st.markdown(
        '<div class="legend-box">'
        '<span class="legend-color"></span>'
        '<strong>Menor costo unitario de compra:</strong> '
        'primero se toma la última compra registrada del producto en cada tienda '
        'y luego se comparan esos precios. La celda verde identifica el menor.'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # 🏪 CARGAR TIENDAS Y CATÁLOGO DEL BUSCADOR
    # --------------------------------------------------------
    with st.spinner(
        "Cargando tiendas y productos..."
    ):
        tiendas = obtener_tiendas_activas()
        catalogo_productos = obtener_catalogo_productos()

    # --------------------------------------------------------
    # 🔎 BUSCADOR CON AUTOCOMPLETADO
    # --------------------------------------------------------
    codigo_seleccionado = None

    if catalogo_productos is None:
        st.error(
            "❌ No fue posible cargar el catálogo de productos."
        )

    elif len(catalogo_productos) == 0:
        st.warning(
            "⚠️ No existen productos registrados en tiendas activas."
        )

    else:
        # Diccionario:
        # código -> "Nombre | Código"
        #
        # El buscador interno de st.selectbox permite escribir texto.
        # Como la etiqueta contiene NOMBRE y CÓDIGO, acepta ambos.
        etiquetas_productos = {}

        for producto in catalogo_productos:
            codigo = str(
                producto.get("Codigo", "")
            ).strip()

            nombre = str(
                producto.get("Producto", "")
            ).strip()

            if codigo and nombre:
                etiquetas_productos[codigo] = (
                    f"{nombre}  |  Código: {codigo}"
                )

        opciones_codigos = list(
            etiquetas_productos.keys()
        )

        codigo_seleccionado = st.selectbox(
            "🔎 Buscar por nombre o código de barras:",
            options=opciones_codigos,
            index=None,
            placeholder="Escribe parte del nombre o del código...",
            format_func=lambda codigo: etiquetas_productos.get(
                codigo,
                str(codigo)
            ),
            help=(
                "Puedes escribir, por ejemplo: Sal, salutaris, SALUTARIS "
                "o parte del código de barras. "
                "El desplegable irá filtrando las coincidencias."
            ),
            key="comparativa_buscador_producto"
        )

        if codigo_seleccionado is not None:
            etiqueta = etiquetas_productos.get(
                codigo_seleccionado,
                str(codigo_seleccionado)
            )

            st.caption(
                f"🔎 Producto seleccionado: {etiqueta}"
            )

    # --------------------------------------------------------
    # 🗄️ CARGAR PRECIOS
    # --------------------------------------------------------
    with st.spinner(
        "Cargando precios unitarios de compra..."
    ):
        datos = obtener_datos_comparativa(
            codigo_filtro=codigo_seleccionado
        )

    # --------------------------------------------------------
    # 📊 MOSTRAR RESULTADOS
    # --------------------------------------------------------
    if tiendas is None:
        st.error(
            "❌ No fue posible obtener la información de las tiendas."
        )

    elif len(tiendas) == 0:
        st.warning(
            "⚠️ No existen tiendas activas en el sistema."
        )

    elif datos is None:
        st.error(
            "❌ No fue posible obtener los precios unitarios de compra."
        )

    else:
        nombres_tiendas = []

        for tienda in tiendas:
            nombre = tienda.get("nombre")

            if nombre and nombre not in nombres_tiendas:
                nombres_tiendas.append(nombre)

        if len(datos) == 0:
            if codigo_seleccionado is not None:
                st.info(
                    "ℹ️ El producto seleccionado no tiene compras registradas "
                    "en las tiendas activas."
                )
            else:
                st.info(
                    "ℹ️ Las tiendas están registradas, pero todavía no "
                    "existen compras para generar la comparativa."
                )

        else:
            tabla_comparativa = preparar_tabla_comparativa(
                datos,
                tiendas
            )

            if tabla_comparativa.empty:
                st.info(
                    "ℹ️ No existen datos suficientes para generar la comparativa."
                )

            else:
                mostrar_tabla_comparativa(
                    tabla_comparativa,
                    nombres_tiendas
                )

                st.caption(
                    "🟢 Verde = menor precio UNITARIO DE COMPRA "
                    "registrado para ese producto."
                )

                st.caption(
                    "— = esa tienda no tiene una compra registrada "
                    "para ese producto."
                )

    # --------------------------------------------------------
    # 🧮 EVALUADOR TEMPORAL DE NUEVO PROVEEDOR
    # --------------------------------------------------------
    mostrar_evaluador_nuevo_proveedor(
        tiendas,
        catalogo_productos
    )

    # --------------------------------------------------------
    # 🔙 VOLVER
    # --------------------------------------------------------
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
