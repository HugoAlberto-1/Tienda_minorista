import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from config.conexion import obtener_conexion


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

COLOR_PRIMARY = "#1e3a5f"
COLOR_SECONDARY = "#2c5f8a"
COLOR_ACCENT = "#3a7ca5"
COLOR_BG = "#f5f7fa"
COLOR_CARD = "#ffffff"
COLOR_TEXT = "#333333"
COLOR_MUTED = "#666666"
COLOR_BORDER = "#e0e0e0"
COLOR_HOVER = "#e8f0fe"


# Categorías que en tu sistema normalmente trabajan por peso
CATEGORIAS_PESO = [
    "Granos y productos a granel",
    "Sopas, pastas y consomés",
]

UNIDADES_PESO = [
    "libra",
    "libras",
    "lb",
    "quintal",
    "quintales",
    "qq",
    "arroba",
    "arrobas",
]


# ============================================================
# PARÁMETROS DEL MODELO DE REORDEN
# La cobertura y el período se configuran en la pantalla.
# El lead time se consulta en Proveedor.lead_time; NO hay valor supuesto.
# El stock de seguridad es el 2 % de la MEDIANA de TOTALES MENSUALES de ventas
# del historial completo, por producto y tienda, en unidades físicas.
# Los meses sin ventas desde la primera compra/venta se incluyen como cero;
# los meses anteriores a la disponibilidad del producto no se incluyen.
# Se usa TODO el historial, incluido el mes en curso (puede estar incompleto).
# ============================================================

TASA_STOCK_SEGURIDAD = 0.02


# ============================================================


# ESTILO
# ============================================================

def configurar_estilo():
    st.markdown(
        f"""
        <style>

        .stApp {{
            background-color: {COLOR_BG};
        }}

        .pronostico-title {{
            text-align: center;
            color: {COLOR_PRIMARY};
            font-size: 2.2em;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .pronostico-subtitle {{
            text-align: center;
            color: {COLOR_SECONDARY};
            font-size: 1.05em;
            margin-bottom: 25px;
        }}

        .info-box {{
            background: {COLOR_HOVER};
            border-left: 4px solid {COLOR_PRIMARY};
            padding: 13px 16px;
            border-radius: 8px;
            color: #1a1a1a;
            margin-bottom: 15px;
        }}

        .section-title {{
            color: {COLOR_PRIMARY};
            font-size: 1.45em;
            font-weight: 700;
            margin-top: 15px;
            margin-bottom: 10px;
        }}

        .metric-card {{
            background: {COLOR_CARD};
            border: 1px solid {COLOR_BORDER};
            border-radius: 14px;
            padding: 19px 15px;
            text-align: left;
            box-shadow: 0 3px 12px rgba(30,58,95,0.05);
            min-height: 112px;
            margin-bottom: 8px;
        }}

        .metric-icon {{
            font-size: 1.25em;
            margin-bottom: 6px;
        }}

        .metric-number {{
            color: {COLOR_PRIMARY};
            font-size: 1.9em;
            font-weight: 750;
        }}

        .metric-label {{
            color: {COLOR_MUTED};
            font-size: 0.86em;
            font-weight: 650;
            text-transform: uppercase;
        }}

        .decision-card {{
            background: white;
            border: 1px solid {COLOR_BORDER};
            border-radius: 10px;
            padding: 13px;
            margin-bottom: 10px;
        }}

        .small-note {{
            color: {COLOR_MUTED};
            font-size: 0.88em;
        }}

        /* Selectores */
        .stSelectbox > div > div,
        .stMultiSelect > div > div {{
            background-color: {COLOR_PRIMARY};
            border-radius: 8px;
        }}

        .stSelectbox div[data-baseweb="select"] *,
        .stMultiSelect div[data-baseweb="select"] * {{
            color: white !important;
        }}

        .stSelectbox input,
        .stMultiSelect input {{
            color: white !important;
        }}

        .stSelectbox input::placeholder,
        .stMultiSelect input::placeholder {{
            color: #dbe7f5 !important;
            opacity: 1 !important;
        }}

        .stSelectbox svg,
        .stMultiSelect svg {{
            fill: white !important;
        }}

        /* Botones */
        .stButton > button {{
            border-radius: 8px;
            font-weight: 600;
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
        }}

        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY};
        }}

        /* Dataframes */
        [data-testid="stDataFrame"] {{
            background: white;
            border: 1px solid {COLOR_BORDER};
            border-radius: 10px;
        }}

        h1, h2, h3, h4 {{
            color: {COLOR_PRIMARY} !important;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FUNCIONES DE UNIDADES
# ============================================================

def normalizar_texto_unidad(unidad):
    if unidad is None:
        return ""
    return str(unidad).strip().lower()


def es_unidad_peso(unidad):
    return normalizar_texto_unidad(unidad) in UNIDADES_PESO


def convertir_a_base(cantidad, unidad):
    """
    Convierte unidades de peso a LIBRAS.
    Los productos normales permanecen en unidades.

    quintal -> 100 lb
    arroba  -> 25 lb
    libra   -> 1 lb
    unidad  -> misma cantidad
    """
    if cantidad is None:
        return 0.0

    try:
        cantidad = float(cantidad)
    except Exception:
        return 0.0

    unidad = normalizar_texto_unidad(unidad)

    if unidad in ["quintal", "quintales", "qq"]:
        return cantidad * 100

    if unidad in ["arroba", "arrobas"]:
        return cantidad * 25

    return cantidad


def determinar_tipo_medida(categoria, unidades_compras=None, unidades_ventas=None):
    """
    Devuelve 'lb' o 'uds'.
    """

    categoria = str(categoria or "").strip()

    if categoria in CATEGORIAS_PESO:
        return "lb"

    unidades = []

    if unidades_compras:
        unidades.extend(unidades_compras)

    if unidades_ventas:
        unidades.extend(unidades_ventas)

    if unidades:
        unidades_normalizadas = [
            normalizar_texto_unidad(x)
            for x in unidades
            if x is not None
        ]

        if any(u in UNIDADES_PESO for u in unidades_normalizadas):
            return "lb"

    return "uds"


def formatear_cantidad(valor, medida):
    if valor is None or pd.isna(valor):
        return "Sin datos"

    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return "Sin datos"

    if not np.isfinite(valor):
        return "Sin datos"

    if medida == "lb":
        return f"{valor:,.2f} lb"

    if abs(valor - round(valor)) < 0.001:
        return f"{int(round(valor)):,} uds"

    return f"{valor:,.2f} uds"


# ============================================================
# FORMATEO DE TIEMPOS / COBERTURA
# ============================================================

def formatear_dias(dias):
    if dias is None:
        return "Sin datos"

    try:
        dias = float(dias)
    except Exception:
        return "Sin datos"

    if np.isnan(dias) or np.isinf(dias):
        return "Sin movimiento"

    if dias < 0:
        dias = 0

    if dias < 1:
        horas = max(1, int(round(dias * 24)))
        return f"{horas} h"

    if dias < 7:
        return f"{dias:.1f} días"

    if dias < 30:
        semanas = dias / 7
        return f"{semanas:.1f} sem."

    if dias < 365:
        meses = dias / 30
        return f"{meses:.1f} meses"

    anios = dias / 365
    return f"{anios:.1f} años"


# ============================================================
# TIENDAS
# ============================================================

def obtener_tiendas():
    conn = obtener_conexion()

    if not conn:
        return pd.DataFrame(columns=["id_tienda", "Tienda"])

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id_tienda, nombre
            FROM tienda
            WHERE activo = 1
            ORDER BY id_tienda
        """)

        datos = cursor.fetchall()

        return pd.DataFrame(
            datos,
            columns=["id_tienda", "Tienda"]
        )

    except Exception as e:
        st.error(f"❌ Error obteniendo tiendas: {e}")
        return pd.DataFrame(columns=["id_tienda", "Tienda"])

    finally:
        cursor.close()
        conn.close()


# ============================================================
# PROVEEDORES Y LEAD TIME REGISTRADO EN LA BASE
# ============================================================

def _clave(valor):
    """Normaliza claves para unir datos recibidos de MySQL."""
    if valor is None or pd.isna(valor):
        return ""
    return str(valor).strip()


def obtener_abastecimiento(productos):
    """Devuelve un LT y un proveedor por producto-tienda cuando existe vínculo.

    Prioridad:
    1) Producto.id_proveedor, si la base tiene esa columna.
    2) Proveedor de la compra más reciente con id_proveedor, si no hay
       asignación. Es PROVISIONAL: confirmarlo antes de ordenar; la última
       compra no acredita un proveedor fijo para el producto.

    Nunca inventa un lead time ni promedia proveedores distintos.
    Sin relación explícita o sin LT, devuelve valores nulos para mostrar
    'Configurar proveedor/LT' en lugar de un PR falso.
    """
    columnas = [
        "ID Producto", "Código", "id_tienda", "ID Proveedor",
        "Proveedor", "Lead time", "Fuente LT",
    ]
    if productos.empty:
        return pd.DataFrame(columns=columnas)

    conn = obtener_conexion()
    if not conn:
        st.error("No se pudo consultar Proveedor: faltan datos para el punto de reorden.")
        return pd.DataFrame(columns=columnas)

    cursor = conn.cursor()
    try:
        cursor.execute("SHOW COLUMNS FROM Proveedor")
        columnas_proveedor = {fila[0].lower() for fila in cursor.fetchall()}
        if "lead_time" not in columnas_proveedor or "id_proveedor" not in columnas_proveedor:
            st.warning("La tabla Proveedor debe contener id_proveedor y lead_time (en días).")
            return pd.DataFrame(columns=columnas)

        campo_nombre = "Nombre" if "nombre" in columnas_proveedor else "id_proveedor"
        cursor.execute(
            f"SELECT id_proveedor, {campo_nombre}, lead_time FROM Proveedor"
        )
        catalogo = {}
        for id_proveedor, nombre, lt in cursor.fetchall():
            try:
                lt_num = float(lt) if lt is not None else np.nan
            except (TypeError, ValueError):
                lt_num = np.nan
            catalogo[_clave(id_proveedor)] = (str(nombre), lt_num)

        cursor.execute("SHOW COLUMNS FROM Producto")
        columnas_producto = {fila[0].lower() for fila in cursor.fetchall()}
        asignado = {}
        if "id_proveedor" in columnas_producto:
            cursor.execute("SELECT id_producto, id_proveedor FROM Producto")
            asignado = {
                _clave(id_producto): _clave(id_proveedor)
                for id_producto, id_proveedor in cursor.fetchall()
                if id_proveedor is not None
            }

        cursor.execute("SHOW COLUMNS FROM Compra")
        columnas_compra = {fila[0].lower() for fila in cursor.fetchall()}
        ultimo_proveedor = {}
        if "id_proveedor" in columnas_compra:
            cursor.execute("""
                SELECT pc.Cod_barra, pc.id_tienda, c.id_proveedor
                FROM ProductoxCompra pc
                INNER JOIN Compra c ON pc.Id_compra = c.Id_compra
                WHERE c.id_proveedor IS NOT NULL
                ORDER BY c.Fecha DESC, c.Id_compra DESC
            """)
            for codigo, id_tienda, id_proveedor in cursor.fetchall():
                llave = (_clave(codigo), _clave(id_tienda))
                if llave not in ultimo_proveedor:
                    ultimo_proveedor[llave] = _clave(id_proveedor)

        if not asignado and not ultimo_proveedor:
            st.warning(
                "No encontré cómo vincular productos con proveedores. "
                "Se necesita Producto.id_proveedor o Compra.id_proveedor; "
                "no se mostrará un punto de reorden supuesto."
            )

        filas = []
        for _, p in productos.iterrows():
            identificador = _clave(p["ID Producto"])
            llave = (_clave(p["Código"]), _clave(p["id_tienda"]))
            proveedor_id = asignado.get(identificador)
            fuente = "Proveedor asignado al producto" if proveedor_id else ""
            if not proveedor_id:
                proveedor_id = ultimo_proveedor.get(llave)
                fuente = "Proveedor de la última compra" if proveedor_id else ""
            nombre, lt_num = catalogo.get(proveedor_id, (None, np.nan))
            if not np.isfinite(lt_num) or lt_num <= 0:
                lt_num = np.nan
            filas.append({
                "ID Producto": p["ID Producto"],
                "Código": p["Código"],
                "id_tienda": p["id_tienda"],
                "ID Proveedor": proveedor_id,
                "Proveedor": nombre,
                "Lead time": lt_num,
                "Fuente LT": fuente,
            })
        return pd.DataFrame(filas, columns=columnas)
    except Exception as e:
        st.error(f"No se pudo obtener el lead time de los proveedores: {e}")
        return pd.DataFrame(columns=columnas)
    finally:
        cursor.close()
        conn.close()


# ============================================================
# STOCK DE SEGURIDAD CON LA MEDIANA DE TODO EL HISTORIAL
# ============================================================

def mediana_ventas_mensuales(ventas_prod, compras_prod, fecha_fin):
    """Mediana de totales mensuales históricos, NO de tickets de venta.

    Incluye TODOS los meses desde la primera compra o venta registrada
    del producto en esa tienda, incluido el mes actual; meses sin ventas
    cuentan como cero. Como el mes actual puede estar incompleto, su
    mediana es una política orientativa, NO garantía de nivel de servicio.
    Si no hay fechas de movimientos, retorna NaN.
    """
    fechas_inicio = []
    for frame in (compras_prod, ventas_prod):
        if not frame.empty:
            fechas = pd.to_datetime(frame["Fecha"], errors="coerce").dropna()
            if not fechas.empty:
                fechas_inicio.append(fechas.min())
    if not fechas_inicio:
        return np.nan, 0

    inicio = min(fechas_inicio).to_period("M")
    fin = pd.Timestamp(fecha_fin).to_period("M")
    if inicio > fin:
        return np.nan, 0

    meses = pd.period_range(inicio, fin, freq="M")
    if ventas_prod.empty:
        ventas_mensuales = pd.Series(0.0, index=meses)
    else:
        fechas = pd.to_datetime(ventas_prod["Fecha"], errors="coerce")
        cantidades = pd.to_numeric(
            ventas_prod["Cantidad_Base"], errors="coerce"
        ).fillna(0)
        ventas_mensuales = (
            pd.DataFrame({"Mes": fechas.dt.to_period("M"), "Cantidad": cantidades})
            .dropna(subset=["Mes"])
            .groupby("Mes")["Cantidad"].sum()
            .reindex(meses, fill_value=0.0)
        )
    return float(ventas_mensuales.median()), len(meses)


# ============================================================
# PRODUCTOS
# ============================================================

def obtener_productos():
    """
    Una fila por producto registrado en cada tienda.
    """

    conn = obtener_conexion()

    if not conn:
        return pd.DataFrame()

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                p.id_producto,
                p.Cod_barra,
                p.Nombre,
                p.categoria,
                p.id_tienda,
                COALESCE(t.nombre, CONCAT('Tienda ', p.id_tienda)) AS Tienda
            FROM Producto p
            LEFT JOIN tienda t
                ON p.id_tienda = t.id_tienda
            WHERE t.activo = 1 OR t.activo IS NULL
            ORDER BY p.Nombre, p.id_tienda
        """)

        datos = cursor.fetchall()

        return pd.DataFrame(
            datos,
            columns=[
                "ID Producto",
                "Código",
                "Producto",
                "Categoría",
                "id_tienda",
                "Tienda",
            ],
        )

    except Exception as e:
        st.error(f"❌ Error obteniendo productos: {e}")
        return pd.DataFrame()

    finally:
        cursor.close()
        conn.close()


# ============================================================
# HISTORIAL DE COMPRAS
# ============================================================

def obtener_compras():
    conn = obtener_conexion()

    if not conn:
        return pd.DataFrame()

    cursor = conn.cursor()

    try:
        # Pedidos pendientes o cancelados no son inventario físico.
        # Si Compra no guarda estado, se mantiene el comportamiento original.
        cursor.execute("SHOW COLUMNS FROM Compra")
        columnas_compra = {fila[0].lower() for fila in cursor.fetchall()}
        condicion = (
            "WHERE (c.estado IS NULL OR LOWER(TRIM(c.estado)) NOT IN "
            "('pendiente', 'cancelada', 'cancelado'))"
            if "estado" in columnas_compra else ""
        )
        cursor.execute(f"""
            SELECT
                pc.cod_barra,
                pc.id_tienda,
                c.Fecha,
                pc.cantidad_comprada,
                pc.unidad
            FROM ProductoxCompra pc
            INNER JOIN Compra c
                ON pc.Id_compra = c.Id_compra
            {condicion}
            ORDER BY c.Fecha
        """)

        datos = cursor.fetchall()

        df = pd.DataFrame(
            datos,
            columns=[
                "Código",
                "id_tienda",
                "Fecha",
                "Cantidad",
                "Unidad",
            ],
        )

        if not df.empty:
            df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce").dt.normalize()
            df["Cantidad"] = pd.to_numeric(
                df["Cantidad"],
                errors="coerce"
            ).fillna(0)

            df["Cantidad_Base"] = df.apply(
                lambda r: convertir_a_base(
                    r["Cantidad"],
                    r["Unidad"]
                ),
                axis=1,
            )

        return df

    except Exception as e:
        st.error(f"❌ Error obteniendo historial de compras: {e}")
        return pd.DataFrame()

    finally:
        cursor.close()
        conn.close()


# ============================================================
# HISTORIAL DE VENTAS
# ============================================================

def obtener_ventas():
    conn = obtener_conexion()

    if not conn:
        return pd.DataFrame()

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                pv.Cod_barra,
                pv.id_tienda,
                v.Fecha,
                pv.Cantidad_vendida,
                pv.unidad
            FROM ProductoxVenta pv
            INNER JOIN Venta v
                ON pv.ID_Venta = v.ID_Venta
            ORDER BY v.Fecha
        """)

        datos = cursor.fetchall()

        df = pd.DataFrame(
            datos,
            columns=[
                "Código",
                "id_tienda",
                "Fecha",
                "Cantidad",
                "Unidad",
            ],
        )

        if not df.empty:
            df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce").dt.normalize()
            df["Cantidad"] = pd.to_numeric(
                df["Cantidad"],
                errors="coerce"
            ).fillna(0)

            df["Cantidad_Base"] = df.apply(
                lambda r: convertir_a_base(
                    r["Cantidad"],
                    r["Unidad"]
                ),
                axis=1,
            )

        return df

    except Exception as e:
        st.error(f"❌ Error obteniendo historial de ventas: {e}")
        return pd.DataFrame()

    finally:
        cursor.close()
        conn.close()


# ============================================================
# PRONÓSTICO
# ============================================================

def calcular_pronostico_30_dias(
    ventas_producto,
    fecha_fin,
    dias_historial=90
):
    """
    Pronóstico sencillo y entendible.

    Se divide el historial reciente en tres bloques:

    últimos 30 días        -> peso 50 %
    de 31 a 60 días        -> peso 30 %
    de 61 a 90 días        -> peso 20 %

    Si el usuario selecciona menos historial, igualmente se utiliza
    la información disponible.

    Devuelve:
        pronostico_30_dias
        demanda_diaria
        ventas_30
        ventas_60
        ventas_90
    """

    if ventas_producto.empty:
        return 0, 0, 0, 0, 0

    fecha_fin = pd.Timestamp(fecha_fin)

    inicio_30 = fecha_fin - pd.Timedelta(days=29)
    inicio_60 = fecha_fin - pd.Timedelta(days=59)
    inicio_90 = fecha_fin - pd.Timedelta(days=89)

    ventas_30 = ventas_producto[
        (ventas_producto["Fecha"] >= inicio_30) &
        (ventas_producto["Fecha"] <= fecha_fin)
    ]["Cantidad_Base"].sum()

    ventas_60_total = ventas_producto[
        (ventas_producto["Fecha"] >= inicio_60) &
        (ventas_producto["Fecha"] <= fecha_fin)
    ]["Cantidad_Base"].sum()

    ventas_90_total = ventas_producto[
        (ventas_producto["Fecha"] >= inicio_90) &
        (ventas_producto["Fecha"] <= fecha_fin)
    ]["Cantidad_Base"].sum()

    bloque_1 = float(ventas_30)

    bloque_2 = max(
        0,
        float(ventas_60_total - ventas_30)
    )

    bloque_3 = max(
        0,
        float(ventas_90_total - ventas_60_total)
    )

    # Si tenemos 90 días completos:
    if dias_historial >= 90:
        pronostico_30 = (
            bloque_1 * 0.50 +
            bloque_2 * 0.30 +
            bloque_3 * 0.20
        )

    elif dias_historial >= 60:
        pronostico_30 = (
            bloque_1 * 0.65 +
            bloque_2 * 0.35
        )

    else:
        pronostico_30 = bloque_1

    # Evitar que una caída repentina deje pronóstico totalmente
    # desconectado del promedio histórico.
    ventas_historial = ventas_producto[
        ventas_producto["Fecha"] >= (
            fecha_fin - pd.Timedelta(days=dias_historial - 1)
        )
    ]["Cantidad_Base"].sum()

    if dias_historial > 0:
        promedio_historico_30 = (
            float(ventas_historial) /
            dias_historial
        ) * 30
    else:
        promedio_historico_30 = 0

    # Combinamos tendencia reciente + histórico
    if pronostico_30 > 0 and promedio_historico_30 > 0:
        pronostico_final = (
            pronostico_30 * 0.70 +
            promedio_historico_30 * 0.30
        )
    elif pronostico_30 > 0:
        pronostico_final = pronostico_30
    else:
        pronostico_final = promedio_historico_30

    demanda_diaria = pronostico_final / 30

    return (
        float(pronostico_final),
        float(demanda_diaria),
        float(ventas_30),
        float(ventas_60_total),
        float(ventas_90_total),
    )


# ============================================================
# CLASIFICACIÓN DE ROTACIÓN
# ============================================================

def clasificar_rotacion(cobertura_dias, demanda_diaria, stock):
    """
    La clasificación se basa principalmente en cuántos días
    duraría el inventario al ritmo pronosticado.

    No necesariamente significa "bueno/malo":
    una rotación alta indica que el producto sale rápidamente.
    """

    if demanda_diaria <= 0:
        if stock > 0:
            return "🔴 Sin movimiento"
        return "⚪ Sin historial"

    if cobertura_dias <= 15:
        return "🟢 Muy alta"

    if cobertura_dias <= 30:
        return "🟢 Alta"

    if cobertura_dias <= 60:
        return "🟡 Media"

    if cobertura_dias <= 90:
        return "🟠 Baja"

    return "🔴 Muy baja"


# ============================================================
# GENERACIÓN DEL ANÁLISIS COMPLETO
# ============================================================

def construir_analisis(
    productos,
    compras,
    ventas,
    fecha_fin,
    dias_historial,
    abastecimiento,
    cobertura_objetivo,
    dias_limpieza,
):
    if productos.empty:
        return pd.DataFrame()

    resultados = []

    fecha_fin = pd.Timestamp(fecha_fin)
    fecha_inicio = fecha_fin - pd.Timedelta(
        days=dias_historial - 1
    )
    asignaciones = {
        (_clave(a["ID Producto"]), _clave(a["id_tienda"])): a
        for _, a in abastecimiento.iterrows()
    } if not abastecimiento.empty else {}

    for _, prod in productos.iterrows():

        codigo = prod["Código"]
        id_tienda = prod["id_tienda"]

        compras_prod = compras[
            (compras["Código"] == codigo) &
            (compras["id_tienda"] == id_tienda)
        ].copy() if not compras.empty else pd.DataFrame()

        ventas_prod = ventas[
            (ventas["Código"] == codigo) &
            (ventas["id_tienda"] == id_tienda)
        ].copy() if not ventas.empty else pd.DataFrame()

        # ----------------------------------------------------
        # Tipo de medida
        # ----------------------------------------------------

        unidades_compras = (
            compras_prod["Unidad"].tolist()
            if not compras_prod.empty
            else []
        )

        unidades_ventas = (
            ventas_prod["Unidad"].tolist()
            if not ventas_prod.empty
            else []
        )

        medida = determinar_tipo_medida(
            prod["Categoría"],
            unidades_compras,
            unidades_ventas,
        )

        # ----------------------------------------------------
        # Stock actual = TODAS las compras - TODAS las ventas
        # ----------------------------------------------------

        total_comprado = (
            compras_prod["Cantidad_Base"].sum()
            if not compras_prod.empty
            else 0
        )

        total_vendido = (
            ventas_prod["Cantidad_Base"].sum()
            if not ventas_prod.empty
            else 0
        )

        stock = max(
            0,
            float(total_comprado) - float(total_vendido)
        )

        # ----------------------------------------------------
        # Historial para pronóstico
        # ----------------------------------------------------

        if not ventas_prod.empty:
            ventas_periodo = ventas_prod[
                (ventas_prod["Fecha"] >= fecha_inicio) &
                (ventas_prod["Fecha"] <= fecha_fin)
            ].copy()
        else:
            ventas_periodo = pd.DataFrame()

        (
            pronostico_30,
            demanda_diaria,
            ventas_30,
            ventas_60,
            ventas_90,
        ) = calcular_pronostico_30_dias(
            ventas_periodo,
            fecha_fin,
            dias_historial,
        )

        # ----------------------------------------------------
        # Última venta y días sin vender
        # ----------------------------------------------------

        if not ventas_prod.empty:
            ultima_venta = pd.to_datetime(
                ventas_prod["Fecha"]
            ).max()

            dias_sin_venta = max(
                0,
                (fecha_fin.normalize() -
                 ultima_venta.normalize()).days
            )
        else:
            ultima_venta = pd.NaT
            dias_sin_venta = None

        # ----------------------------------------------------
        # Cobertura
        # ----------------------------------------------------

        if demanda_diaria > 0:
            cobertura_dias = stock / demanda_diaria
        else:
            cobertura_dias = np.inf

        # ----------------------------------------------------
        # Rotación %
        #
        # ¿Qué porcentaje del stock actual se espera vender
        # durante los próximos 30 días?
        #
        # Puede ser >100%, lo cual significa que el stock
        # actual no alcanzaría para cubrir 30 días.
        # ----------------------------------------------------

        if stock > 0:
            rotacion_pct = (
                pronostico_30 / stock
            ) * 100
        elif pronostico_30 > 0:
            rotacion_pct = 999
        else:
            rotacion_pct = 0

        rotacion_estado = clasificar_rotacion(
            cobertura_dias,
            demanda_diaria,
            stock,
        )

        # ----------------------------------------------------
        # Lead time de Proveedor (NO constante de siete días)
        # ----------------------------------------------------
        a = asignaciones.get((_clave(prod["ID Producto"]), _clave(id_tienda)))
        proveedor = a["Proveedor"] if a is not None else None
        origen_lt = a["Fuente LT"] if a is not None else ""
        lt = a["Lead time"] if a is not None else np.nan
        tiene_lt = pd.notna(lt) and np.isfinite(float(lt)) and float(lt) > 0
        lt = float(lt) if tiene_lt else np.nan

        # ----------------------------------------------------
        # Stock de seguridad = 2 % de la mediana de los totales
        # mensuales de TODO el historial registrado por tienda/producto,
        # incluido el mes en curso (si puede estar incompleto).
        # ----------------------------------------------------
        mediana_mensual, meses_historia = mediana_ventas_mensuales(
            ventas_prod, compras_prod, fecha_fin
        )
        tiene_seguridad = np.isfinite(mediana_mensual)
        stock_seguridad = (
            max(0.0, mediana_mensual) * TASA_STOCK_SEGURIDAD
            if tiene_seguridad else np.nan
        )

        if medida == "uds" and tiene_seguridad:
            stock_seguridad = float(np.ceil(stock_seguridad))

        # No mostrar PR si falta alguno de sus insumos.
        tiene_parametros = tiene_lt and tiene_seguridad
        if tiene_parametros:
            punto_reorden = demanda_diaria * lt + stock_seguridad
            stock_objetivo = (
                demanda_diaria * (cobertura_objetivo + lt) + stock_seguridad
            )
            if medida == "uds":
                punto_reorden = float(np.ceil(punto_reorden))
                stock_objetivo = float(np.ceil(stock_objetivo))
            else:
                punto_reorden = round(punto_reorden, 2)
                stock_objetivo = round(stock_objetivo, 2)
            compra_sugerida = max(0.0, stock_objetivo - stock)
            if medida == "uds":
                compra_sugerida = float(np.ceil(compra_sugerida))
        else:
            punto_reorden = np.nan
            stock_objetivo = np.nan
            compra_sugerida = np.nan



        # ----------------------------------------------------
        # Próximo reorden
        # ----------------------------------------------------

        if not tiene_parametros or demanda_diaria <= 0:
            dias_para_reorden = np.inf

        elif stock <= punto_reorden:
            dias_para_reorden = 0

        else:
            dias_para_reorden = (
                stock - punto_reorden
            ) / demanda_diaria

        # ----------------------------------------------------
        # Acción / decisión
        # ----------------------------------------------------

        accion = ""
        prioridad = 99

        # Sin ventas registradas no es correcto recomendar limpieza automática.
        if stock > 0 and dias_sin_venta is None:
            accion = "⚪ Sin historial de ventas"
            prioridad = 7
            compra_sugerida = 0

        # Producto con stock pero sin ventas recientes
        elif stock > 0 and demanda_diaria <= 0:
            if dias_sin_venta >= dias_limpieza:
                accion = "🧹 Limpieza de inventario"
                prioridad = 5
            else:
                accion = "🚫 No comprar"
                prioridad = 4
            compra_sugerida = 0

        # Lleva demasiado tiempo sin vender
        elif (
            stock > 0 and
            dias_sin_venta is not None and
            dias_sin_venta >= dias_limpieza
        ):
            accion = "🧹 Limpieza de inventario"
            prioridad = 5
            compra_sugerida = 0

        # Si falta LT o historia mensual, no fabricamos un PR.
        elif not tiene_parametros:
            accion = "⚪ Configurar proveedor/LT" if not tiene_lt else "⚪ Sin historial mensual"
            prioridad = 7
            compra_sugerida = np.nan

        # Reorden inmediato
        elif demanda_diaria > 0 and stock <= punto_reorden:
            accion = "🔴 Comprar ahora"
            prioridad = 1

        # Próximo a reorden
        elif demanda_diaria > 0 and dias_para_reorden <= 14:
            accion = "🟡 Próximo a comprar"
            prioridad = 2
            compra_sugerida = 0

        # Inventario excesivo
        elif (
            demanda_diaria > 0 and
            cobertura_dias > 90
        ):
            accion = "🚫 No comprar"
            prioridad = 4
            compra_sugerida = 0

        # Stock superior al deseable
        elif (
            demanda_diaria > 0 and
            cobertura_dias > 60
        ):
            accion = "🟠 Reducir compra"
            prioridad = 3

            # No generar una orden de compra antes de llegar al PR.
            # Se mantiene la etiqueta 'Reducir compra' para revisión de surtido.
            compra_sugerida = 0

        else:
            accion = "🟢 Mantener"
            prioridad = 6
            # Solo recomendar cantidad cuando corresponde reponer ahora.
            compra_sugerida = 0

        # ----------------------------------------------------
        # Texto próximo reorden
        # ----------------------------------------------------

        if not tiene_parametros:
            proximo_reorden_texto = "Sin datos"
        elif demanda_diaria <= 0:
            proximo_reorden_texto = "No comprar"

        elif dias_para_reorden <= 0:
            proximo_reorden_texto = "Ahora"

        elif dias_para_reorden < 1:
            proximo_reorden_texto = "< 1 día"

        else:
            proximo_reorden_texto = formatear_dias(
                dias_para_reorden
            )

        # ----------------------------------------------------
        # Tendencia reciente
        # ----------------------------------------------------

        ventas_anteriores_30 = max(
            0,
            ventas_60 - ventas_30
        )

        if ventas_anteriores_30 > 0:
            variacion = (
                (
                    ventas_30 -
                    ventas_anteriores_30
                ) /
                ventas_anteriores_30
            ) * 100

        elif ventas_30 > 0:
            variacion = 100

        else:
            variacion = 0

        if variacion > 15:
            tendencia = "⬆️ Creciendo"
        elif variacion < -15:
            tendencia = "⬇️ Disminuyendo"
        else:
            tendencia = "➡️ Estable"

        resultados.append({
            "ID Producto": prod["ID Producto"],
            "Código": codigo,
            "Producto": prod["Producto"],
            "Categoría": prod["Categoría"],
            "id_tienda": id_tienda,
            "Tienda": prod["Tienda"],

            "Medida": medida,

            "Stock": round(stock, 2),

            "Ventas 30d": round(ventas_30, 2),
            "Ventas 60d": round(ventas_60, 2),
            "Ventas 90d": round(ventas_90, 2),

            "Pronóstico 30d": round(pronostico_30, 2),
            "Demanda diaria": round(demanda_diaria, 4),

            "Cobertura días": (
                round(cobertura_dias, 1)
                if np.isfinite(cobertura_dias)
                else np.inf
            ),

            "Cobertura": (
                formatear_dias(cobertura_dias)
                if np.isfinite(cobertura_dias)
                else "Sin movimiento"
            ),

            "Rotación %": round(rotacion_pct, 1),
            "Nivel rotación": rotacion_estado,

            "Proveedor": proveedor or "Sin asignar",
            "Fuente LT": origen_lt,
            "Lead time": lt,
            "Mediana mensual": mediana_mensual,
            "Meses historial": meses_historia,
            "Stock seguridad": stock_seguridad,
            "Punto reorden": punto_reorden,
            "Stock objetivo": stock_objetivo,
            "Compra sugerida": compra_sugerida,

            "Días para reorden": (
                round(dias_para_reorden, 1)
                if np.isfinite(dias_para_reorden)
                else np.inf
            ),

            "Próximo reorden": proximo_reorden_texto,

            "Última venta": (
                ultima_venta.strftime("%Y-%m-%d")
                if pd.notna(ultima_venta)
                else "Nunca"
            ),

            "Días sin vender": (
                dias_sin_venta
                if dias_sin_venta is not None
                else np.inf
            ),

            "Tendencia": tendencia,
            "Variación reciente %": round(variacion, 1),

            "Acción": accion,
            "Prioridad": prioridad,
        })

    return pd.DataFrame(resultados)


# ============================================================
# MATRIZ PRODUCTO x TIENDA (VISTA PRINCIPAL)
# ============================================================

# Etiquetas amigables -> columna real del análisis.
MAPA_INDICADORES = {
    "Stock actual": "Stock",
    "Duración estimada": "Cobertura",
    "% Rotación": "Rotación %",
    "Rotación (nivel)": "Nivel rotación",
    "Proveedor": "Proveedor",
    "Lead time": "Lead time",
    "Stock seguridad": "Stock seguridad",
    "Punto de reorden": "Punto reorden",
    "Cuánto comprar": "Compra sugerida",
    "Recomendación": "Acción",
    "Tendencia": "Tendencia",
    "Próximo reorden": "Próximo reorden",
}

# Indicadores que representan una cantidad de producto y por lo
# tanto deben mostrarse con su unidad (lb / uds).
INDICADORES_CANTIDAD = [
    "Stock actual",
    "Stock seguridad",
    "Punto de reorden",
    "Cuánto comprar",
]

# Set fijo de indicadores que se muestran en las tablas principales.
INDICADORES_DEFAULT = [
    "Stock actual",
    "Duración estimada",
    "% Rotación",
    "Proveedor",
    "Lead time",
    "Stock seguridad",
    "Punto de reorden",
    "Cuánto comprar",
    "Recomendación",
]


def construir_tabla_indicadores(
    df_subset,
    columna_fila,
    indicadores,
    columnas_extra=None,
    orden_por=None,
    ascendente=True,
):
    """
    Arma una tabla ya formateada a partir de un subconjunto que
    representa UNA sola tienda o UN solo producto:

    - Si df_subset ya está filtrado a una tienda, usa
      columna_fila="Producto" -> una fila por producto de esa tienda.
    - Si df_subset ya está filtrado a un producto, usa
      columna_fila="Tienda" -> una fila por tienda donde existe
      ese producto, para poder compararlas entre sí.
    """

    if df_subset.empty:
        return pd.DataFrame()

    df_subset = df_subset.copy()

    if orden_por is not None and orden_por in df_subset.columns:
        df_subset = df_subset.sort_values(
            orden_por,
            ascending=ascendente
        )
    else:
        df_subset = df_subset.sort_values(columna_fila)

    df_subset = df_subset.reset_index(drop=True)

    columnas_extra = columnas_extra or []

    resultado = df_subset[[columna_fila] + columnas_extra].copy()

    for indicador in indicadores:

        columna_origen = MAPA_INDICADORES[indicador]

        if indicador in INDICADORES_CANTIDAD:
            resultado[indicador] = df_subset.apply(
                lambda r: formatear_cantidad(
                    r[columna_origen],
                    r["Medida"]
                ),
                axis=1,
            )

        elif indicador == "Lead time":
            resultado[indicador] = df_subset[columna_origen].apply(
                lambda x: f"{float(x):g} días" if pd.notna(x) else "Sin dato"
            )

        elif indicador == "% Rotación":
            resultado[indicador] = df_subset[
                columna_origen
            ].apply(
                lambda x: (
                    f"{x:.1f}%"
                    if x < 999
                    else ">999%"
                )
            )

        else:
            resultado[indicador] = df_subset[columna_origen]

    return resultado


def calcular_altura_tabla(
    n_filas,
    alto_fila=35,
    alto_encabezado=38,
    minimo=120,
    maximo=480,
):
    """
    Calcula una altura razonable para st.dataframe según la
    cantidad de filas que va a mostrar, para no dejar espacio en
    blanco cuando hay pocos productos ni cortar la tabla cuando
    hay muchos (a partir de cierto punto se activa el scroll).
    """

    if n_filas <= 0:
        return minimo

    altura = alto_encabezado + (n_filas * alto_fila)

    return int(min(maximo, max(minimo, altura)))


# ============================================================
# TABLAS DE DECISIONES
# ============================================================

def preparar_tabla_decision(df):
    if df.empty:
        return pd.DataFrame()

    tabla = df.copy()

    tabla["Stock actual"] = tabla.apply(
        lambda r: formatear_cantidad(
            r["Stock"],
            r["Medida"]
        ),
        axis=1,
    )

    tabla["Pronóstico"] = tabla.apply(
        lambda r: formatear_cantidad(
            r["Pronóstico 30d"],
            r["Medida"]
        ),
        axis=1,
    )

    tabla["Reorden"] = tabla.apply(
        lambda r: formatear_cantidad(
            r["Punto reorden"],
            r["Medida"]
        ),
        axis=1,
    )

    tabla["Comprar"] = tabla.apply(
        lambda r: formatear_cantidad(
            r["Compra sugerida"],
            r["Medida"]
        ),
        axis=1,
    )
    tabla["Seguridad"] = tabla.apply(
        lambda r: formatear_cantidad(r["Stock seguridad"], r["Medida"]), axis=1
    )
    tabla["LT"] = tabla["Lead time"].apply(
        lambda x: f"{float(x):g} días" if pd.notna(x) else "Sin dato"
    )

    columnas = [
        "Producto",
        "Código",
        "Tienda",
        "Stock actual",
        "Cobertura",
        "Nivel rotación",
        "Proveedor",
        "LT",
        "Seguridad",
        "Pronóstico",
        "Reorden",
        "Comprar",
        "Próximo reorden",
        "Tendencia",
        "Acción",
    ]

    return tabla[columnas].rename(columns={"Acción": "Recomendación"})


def preparar_tabla_limpieza(df):
    """
    Tabla enfocada en responder una sola pregunta por producto/tienda:
    ¿sigue teniendo sentido seguir vendiendo esto, o se debería retirar?
    """

    if df.empty:
        return pd.DataFrame()

    tabla = df.copy()

    tabla["Stock actual"] = tabla.apply(
        lambda r: formatear_cantidad(
            r["Stock"],
            r["Medida"]
        ),
        axis=1,
    )

    tabla["¿Sigue vendiendo?"] = np.where(
        tabla["Demanda diaria"] > 0,
        "Sí, pero muy poco",
        "No",
    )

    columnas = [
        "Producto",
        "Código",
        "Tienda",
        "Stock actual",
        "Última venta",
        "Días sin vender",
        "¿Sigue vendiendo?",
        "Acción",
    ]

    return tabla[columnas].rename(columns={"Acción": "Recomendación"})


# ============================================================
# TARJETAS DE RESUMEN
# ============================================================

def tarjeta_resumen(icono, valor, etiqueta):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{icono}</div>
            <div class="metric-number">{valor}</div>
            <div class="metric-label">{etiqueta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MÓDULO PRINCIPAL
# ============================================================

def modulo_pronosticos():

    configurar_estilo()

    st.markdown(
        '<div class="pronostico-title">📈 Pronóstico y Punto de Reorden</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="pronostico-subtitle">
            Análisis de rotación, cobertura, reposición y limpieza de inventario
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Validación
    # --------------------------------------------------------

    if not st.session_state.get("logueado"):
        st.error(
            "❌ Debes iniciar sesión para acceder a este módulo."
        )

        if st.button(
            "⬅ Volver al menú principal",
            key="volver_pronostico_login"
        ):
            st.session_state["module"] = None
            st.rerun()

        return

    rol = st.session_state.get(
        "nivel_usuario",
        ""
    )

    id_tienda_sesion = st.session_state.get(
        "id_tienda"
    )

    nombre_tienda_sesion = st.session_state.get(
        "nombre_tienda",
        "Mi Tienda"
    )

    # --------------------------------------------------------
    # Parámetros
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">⚙️ Configuración del pronóstico y reorden</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "El historial seleccionado afecta el pronóstico de demanda; la seguridad "
        "usa todos los meses disponibles de cada producto y tienda, "
        "La cobertura objetivo determina cuánto abastecer cuando corresponda pedir."
    )

    p1, p2 = st.columns(2)

    with p1:
        dias_historial = st.selectbox(
            "Historial de ventas",
            [30, 60, 90, 180, 365],
            index=2,
            format_func=lambda x: f"{x} días",
            help=(
                "Período utilizado para analizar "
                "la demanda reciente."
            ),
        )

    with p2:
        cobertura_objetivo = st.number_input(
            "Cobertura objetivo",
            min_value=7,
            max_value=180,
            value=30,
            step=1,
            help=(
                "Cantidad de días que deseas cubrir "
                "con cada reposición."
            ),
        )

    dias_limpieza = st.slider(
        "Considerar producto para limpieza si lleva sin vender:",
        min_value=30,
        max_value=365,
        value=90,
        step=15,
        format="%d días",
    )

    st.info(
        "**Modelo de reposición:** LT desde `Proveedor.lead_time` y seguridad "
        "del 2 % de la mediana mensual de todo el historial por producto y tienda "
        "(incluido el mes actual). Si falta el vínculo al proveedor o el historial "
        "necesario, el punto de reorden se muestra como no disponible."
    )

    fecha_fin = datetime.now().date()

    # --------------------------------------------------------
    # Carga de información
    # --------------------------------------------------------

    with st.spinner(
        "Analizando compras, ventas e inventario..."
    ):

        tiendas = obtener_tiendas()
        productos = obtener_productos()
        compras = obtener_compras()
        ventas = obtener_ventas()
        abastecimiento = obtener_abastecimiento(productos)

    if productos.empty:
        st.warning(
            "⚠️ No se encontraron productos registrados."
        )
        return

    if tiendas.empty:
        st.warning(
            "⚠️ No se encontraron tiendas activas."
        )
        return

    # --------------------------------------------------------
    # Restricciones por usuario
    # --------------------------------------------------------

    if rol != "Administrador":

        productos = productos[
            productos["id_tienda"] ==
            id_tienda_sesion
        ].copy()

        tiendas = tiendas[
            tiendas["id_tienda"] ==
            id_tienda_sesion
        ].copy()

        if not compras.empty:
            compras = compras[
                compras["id_tienda"] ==
                id_tienda_sesion
            ].copy()

        if not ventas.empty:
            ventas = ventas[
                ventas["id_tienda"] ==
                id_tienda_sesion
            ].copy()

        st.markdown(
            f"""
            <div class="info-box">
                🏪 <strong>Tienda:</strong>
                {nombre_tienda_sesion}
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            """
            <div class="info-box">
                👑 <strong>Administrador:</strong>
                visualización global de inventario y pronósticos.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Construcción del análisis
    # --------------------------------------------------------

    df = construir_analisis(
        productos=productos,
        compras=compras,
        ventas=ventas,
        fecha_fin=fecha_fin,
        dias_historial=dias_historial,
        abastecimiento=abastecimiento,
        cobertura_objetivo=cobertura_objetivo,
        dias_limpieza=dias_limpieza,
    )

    if df.empty:
        st.warning(
            "⚠️ No fue posible construir el análisis."
        )
        return

    # ========================================================
    # FILTROS GENERALES
    # ========================================================

    st.markdown(
        '<div class="section-title">🎛️ Filtros del análisis</div>',
        unsafe_allow_html=True
    )

    categoria_lista = (
        ["Todas"] +
        sorted(
            df["Categoría"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    )

    categoria = st.selectbox(
        "📁 Categoría",
        categoria_lista,
        key="categoria_pronostico",
    )

    df_filtrado = df.copy()

    if categoria != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["Categoría"] ==
            categoria
        ].copy()

    # Un único selector para inventario, tarjetas y centro de decisiones.
    # La comparación de productos sigue utilizando df_filtrado (todas las tiendas).
    st.markdown(
        '<div class="section-title">🏪 Tienda que deseas analizar</div>',
        unsafe_allow_html=True,
    )
    tiendas_disponibles = tiendas[["id_tienda", "Tienda"]].drop_duplicates("id_tienda")
    nombres_por_id = {
        _clave(fila["id_tienda"]): str(fila["Tienda"])
        for _, fila in tiendas_disponibles.iterrows()
    }
    ids_tienda = list(nombres_por_id.keys())
    if not ids_tienda:
        st.warning("No hay tiendas activas disponibles para analizar.")
        return
    if rol != "Administrador":
        ids_tienda = [i for i in ids_tienda if i == _clave(id_tienda_sesion)]
        if not ids_tienda:
            st.error("La cuenta no tiene una tienda activa asignada.")
            return
    tienda_seleccionada = st.selectbox(
        "Selecciona una tienda",
        options=ids_tienda,
        format_func=lambda i: nombres_por_id[i],
        key="tienda_general_pronostico",
        help="Las tarjetas, inventario y acciones se calculan solo para esta tienda. "
             "La pestaña Comparar tiendas permite comparar el mismo producto entre todas.",
    )
    nombre_tienda = nombres_por_id[tienda_seleccionada]
    df_tienda = df_filtrado.loc[
        df_filtrado["id_tienda"].map(_clave) == tienda_seleccionada
    ].copy()
    st.caption(
        f"📍 **{nombre_tienda}** · {len(df_tienda)} productos con el filtro actual. "
        "El comparativo de tiendas mantiene todas las ubicaciones."
    )

    # ========================================================
    # RESUMEN EJECUTIVO
    # ========================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-title">📌 Resumen para toma de decisiones</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Acciones correspondientes únicamente a **{nombre_tienda}**.")

    comprar_ahora = len(
        df_tienda[
            df_tienda["Acción"] ==
            "🔴 Comprar ahora"
        ]
    )

    proximos = len(
        df_tienda[
            df_tienda["Acción"] ==
            "🟡 Próximo a comprar"
        ]
    )

    reducir = len(
        df_tienda[
            df_tienda["Acción"] ==
            "🟠 Reducir compra"
        ]
    )

    no_comprar = len(
        df_tienda[
            df_tienda["Acción"] ==
            "🚫 No comprar"
        ]
    )

    limpieza = len(
        df_tienda[
            df_tienda["Acción"] ==
            "🧹 Limpieza de inventario"
        ]
    )
    pendientes_datos = int(df_tienda["Acción"].str.startswith("⚪", na=False).sum())

    c1, c2, c3 = st.columns(3)

    with c1:
        tarjeta_resumen(
            "🔴",
            comprar_ahora,
            "Comprar ahora"
        )

    with c2:
        tarjeta_resumen(
            "🟡",
            proximos,
            "Próximos"
        )

    with c3:
        tarjeta_resumen(
            "🟠",
            reducir,
            "Reducir compra"
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        tarjeta_resumen(
            "🚫",
            no_comprar,
            "No comprar"
        )

    with c5:
        tarjeta_resumen(
            "🧹",
            limpieza,
            "Limpieza"
        )
    with c6:
        tarjeta_resumen("⚪", pendientes_datos, "Revisar datos")

    st.markdown("---")
    vista_tienda, vista_comparar, vista_decisiones = st.tabs(
        ["🏪 Por tienda", "📊 Comparar tiendas", "🧠 Acciones"]
    )

    with vista_tienda:
        # ========================================================
        # VISTA POR TIENDA: TODOS LOS PRODUCTOS DE UNA TIENDA
        # ========================================================

        st.markdown("---")

        st.markdown(
            '<div class="section-title">📋 Punto de reorden y compra sugerida por tienda</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "Revisa el inventario, proveedor, tiempo de entrega, "
            "seguridad y punto de reorden de cada producto."
        )

        if df_tienda.empty:
            st.info("Esta tienda no tiene productos con los filtros seleccionados.")
        else:
            df_tienda_vista = df_tienda.copy()
            st.caption(f"Inventario de **{nombre_tienda}** · mismo alcance que el resumen.")

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Productos", len(df_tienda_vista))
            k2.metric("Con PR calculado", int(df_tienda_vista["Punto reorden"].notna().sum()))
            k3.metric("Comprar ahora", int((df_tienda_vista["Acción"] == "🔴 Comprar ahora").sum()))
            k4.metric("Revisar datos", int(df_tienda_vista["Acción"].str.startswith("⚪", na=False).sum()))

            if (df_tienda_vista["Fuente LT"] == "Proveedor de la última compra").any():
                st.caption(
                    "ℹ️ Algunos lead times corresponden al proveedor de la última compra. "
                    "Confirma que será también el proveedor de la próxima reposición."
                )

            tabla_tienda = construir_tabla_indicadores(
                df_tienda_vista,
                columna_fila="Producto",
                indicadores=INDICADORES_DEFAULT,
                columnas_extra=["Código"],
                orden_por="Producto",
            )

            st.dataframe(
                tabla_tienda,
                use_container_width=True,
                hide_index=True,
                height=calcular_altura_tabla(len(tabla_tienda)),
            )

        with st.expander(
            "ℹ️ ¿Cómo leer esta tabla?"
        ):
            st.markdown(
                """
                **Stock actual:** cantidad que existe actualmente en esta tienda.

                **Duración estimada:** aproximadamente cuánto tiempo durará
                ese inventario al ritmo de venta pronosticado (equivalente
                a "compré 10 y me duraron 5 meses").

                **% Rotación:** porcentaje del stock actual que se espera
                vender durante los próximos 30 días. Puede superar 100 %,
                lo cual indica que el stock actual no alcanzaría para cubrir
                la demanda pronosticada.

                **Proveedor y lead time:** proveedor vinculado al producto
                y plazo en días registrado en Proveedor.lead_time. Si viene de
                la última compra, confirma que será el proveedor de la siguiente.

                **Stock seguridad:** 2 % de la mediana de totales mensuales de
                todo el historial (incluido el mes en curso, aunque pueda estar incompleto).
                Los meses sin ventas cuentan como cero; si hubo desabastecimiento,
                la cifra puede subestimar la demanda real.

                **Punto de reorden:** demanda diaria × lead time + stock seguridad.

                **Cuánto comprar:** cantidad para alcanzar la cobertura objetivo
                al llegar al punto de reorden; antes se muestra 0.

                **Recomendación:** acción sugerida para ese producto en
                esta tienda.
                """
            )


    with vista_comparar:
        # ========================================================
        # COMPARATIVO DE ROTACIÓN DE UN PRODUCTO ENTRE TIENDAS
        # ========================================================

        st.markdown("---")

        st.markdown(
            '<div class="section-title">📊 Comparativo de rotación de un producto entre tiendas</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "Elige un producto y compáralo entre todas tus tiendas: útil "
            "para detectar, por ejemplo, que el mismo producto rota rápido "
            "en una tienda y casi no se mueve en otra."
        )

        productos_disponibles = sorted(
            df_filtrado["Producto"]
            .dropna()
            .unique()
            .tolist()
        )

        if not productos_disponibles:
            st.info(
                "No hay productos disponibles con los filtros actuales."
            )
        else:

            producto_comparar = st.selectbox(
                "📦 Producto",
                productos_disponibles,
                key="producto_comparar_pronostico",
            )

            df_producto_comparar = df_filtrado[
                df_filtrado["Producto"] == producto_comparar
            ].copy()

            # Comparamos demanda (no la duración del stock) e incluimos
            # tiendas sin ventas recientes: una demanda cero sí es relevante.
            df_valido = df_producto_comparar.loc[
                df_producto_comparar["Demanda diaria"].notna()
            ].copy()

            if len(df_producto_comparar) < 2:
                st.info("Este producto aparece en una sola tienda: no hay comparación entre tiendas.")
            elif len(df_valido) < 2:
                st.info("Faltan datos de demanda para comparar las tiendas.")
            elif (df_valido["Demanda diaria"] <= 0).all():
                st.info("No se registraron ventas recientes de este producto en las tiendas comparadas.")
            else:
                fila_mayor = df_valido.sort_values(
                    "Demanda diaria", ascending=False
                ).iloc[0]
                fila_menor = df_valido.sort_values(
                    "Demanda diaria", ascending=True
                ).iloc[0]
                if np.isclose(fila_mayor["Demanda diaria"], fila_menor["Demanda diaria"]):
                    st.info("La demanda diaria estimada es similar en las tiendas comparadas.")
                else:
                    st.success(
                        f"📈 **{fila_mayor['Tienda']}** presenta la mayor demanda diaria "
                        f"estimada: {formatear_cantidad(fila_mayor['Demanda diaria'], fila_mayor['Medida'])}/día."
                    )
                    if fila_menor["Demanda diaria"] <= 0:
                        st.caption(f"🐢 En **{fila_menor['Tienda']}** no se registraron ventas recientes.")
                    else:
                        st.caption(
                            f"🐢 **{fila_menor['Tienda']}** presenta la menor demanda diaria "
                            f"estimada: {formatear_cantidad(fila_menor['Demanda diaria'], fila_menor['Medida'])}/día."
                        )

            if len(df_producto_comparar) >= 2:
                st.markdown("**Demanda diaria estimada por tienda**")
                st.bar_chart(
                    df_producto_comparar.set_index("Tienda")["Demanda diaria"],
                    use_container_width=True,
                )

            tabla_producto = construir_tabla_indicadores(
                df_producto_comparar,
                columna_fila="Tienda",
                indicadores=INDICADORES_DEFAULT,
                orden_por="Demanda diaria",
                ascendente=False,
            )

            st.dataframe(
                tabla_producto,
                use_container_width=True,
                hide_index=True,
                height=calcular_altura_tabla(len(tabla_producto)),
            )

            st.caption(
                "Ordenada por demanda diaria estimada. La duración del stock "
                "también depende de cuánto inventario tenga cada tienda."
            )


    with vista_decisiones:
        # ========================================================
        # CENTRO DE DECISIONES
        # ========================================================

        st.markdown("---")

        st.markdown(
            '<div class="section-title">🧠 Centro de decisiones</div>',
            unsafe_allow_html=True
        )

        st.caption(
            f"Acciones de {nombre_tienda}: únicamente los productos de esta tienda, "
            "agrupados por la decisión que corresponde a cada uno."
        )

        if df_tienda.empty:
            st.info("No hay productos de esta tienda en la categoría seleccionada.")

        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
            [
                "🔴 Comprar ahora",
                "🟡 Próximos a comprar",
                "🟠 Reducir compra",
                "🚫 No comprar",
                "🧹 Limpieza",
                "🟢 Mantener",
                "⚪ Revisar datos",
            ]
        )

        # --------------------------------------------------------
        # COMPRAR AHORA
        # --------------------------------------------------------

        with tab1:

            datos = df_tienda[
                df_tienda["Acción"] ==
                "🔴 Comprar ahora"
            ].copy()

            datos = datos.sort_values(
                [
                    "Días para reorden",
                    "Cobertura días"
                ],
                ascending=True
            )

            if datos.empty:
                st.info(
                    "No hay productos con reorden inmediato entre los que cuentan "
                    "con proveedor, lead time y suficiente historial mensual."
                )
            else:
                st.warning(
                    f"⚠️ {len(datos)} producto(s) "
                    "alcanzaron su punto de reorden."
                )

                st.dataframe(
                    preparar_tabla_decision(datos),
                    use_container_width=True,
                    hide_index=True,
                )

        # --------------------------------------------------------
        # PRÓXIMOS
        # --------------------------------------------------------

        with tab2:

            datos = df_tienda[
                df_tienda["Acción"] ==
                "🟡 Próximo a comprar"
            ].copy()

            datos = datos.sort_values(
                "Días para reorden"
            )

            if datos.empty:
                st.success(
                    "✅ No hay compras próximas detectadas."
                )
            else:
                st.info(
                    "Estos productos todavía tienen inventario, "
                    "pero se aproximan al nivel de reorden."
                )

                st.dataframe(
                    preparar_tabla_decision(datos),
                    use_container_width=True,
                    hide_index=True,
                )

        # --------------------------------------------------------
        # REDUCIR
        # --------------------------------------------------------

        with tab3:

            datos = df_tienda[
                df_tienda["Acción"] ==
                "🟠 Reducir compra"
            ].copy()

            datos = datos.sort_values(
                "Cobertura días",
                ascending=False
            )

            if datos.empty:
                st.success(
                    "✅ No se detectaron compras que deban reducirse."
                )
            else:
                st.warning(
                    "Estos productos tienen más inventario del "
                    "necesario respecto a su ritmo actual de venta "
                    "en esa tienda."
                )

                st.dataframe(
                    preparar_tabla_decision(datos),
                    use_container_width=True,
                    hide_index=True,
                )

        # --------------------------------------------------------
        # NO COMPRAR
        # --------------------------------------------------------

        with tab4:

            datos = df_tienda[
                df_tienda["Acción"] ==
                "🚫 No comprar"
            ].copy()

            datos = datos.sort_values(
                "Cobertura días",
                ascending=False
            )

            if datos.empty:
                st.success(
                    "✅ No hay productos marcados como 'No comprar'."
                )
            else:
                st.error(
                    "No se recomienda reabastecer estos productos "
                    "por el momento."
                )

                st.dataframe(
                    preparar_tabla_decision(datos),
                    use_container_width=True,
                    hide_index=True,
                )

        # --------------------------------------------------------
        # LIMPIEZA
        # --------------------------------------------------------

        with tab5:

            datos = df_tienda[
                df_tienda["Acción"] ==
                "🧹 Limpieza de inventario"
            ].copy()

            datos = datos.sort_values(
                "Días sin vender",
                ascending=False
            )

            if datos.empty:
                st.success(
                    "✅ No se detectaron productos para limpieza."
                )
            else:

                st.error(
                    "Estos productos tienen inventario pero llevan "
                    "demasiado tiempo sin venderse en esa tienda."
                )

                tabla_limpieza = preparar_tabla_limpieza(
                    datos
                )

                st.dataframe(
                    tabla_limpieza,
                    use_container_width=True,
                    hide_index=True,
                )

                st.markdown(
                    """
                    **Acciones posibles:**
                    realizar promoción, disminuir el precio si corresponde,
                    no volver a comprar temporalmente o trasladar inventario
                    hacia una tienda donde el mismo producto tenga mayor
                    rotación.
                    """
                )

        # --------------------------------------------------------
        # MANTENER
        # --------------------------------------------------------

        with tab6:

            datos = df_tienda[
                df_tienda["Acción"] ==
                "🟢 Mantener"
            ].copy()

            if datos.empty:
                st.info(
                    "No hay productos clasificados como mantener."
                )
            else:
                st.success(
                    "✅ Estos productos presentan un nivel de "
                    "inventario razonable según su demanda."
                )

                st.dataframe(
                    preparar_tabla_decision(datos),
                    use_container_width=True,
                    hide_index=True,
                )


        with tab7:
            pendientes = df_tienda.loc[
                df_tienda["Acción"].str.startswith("⚪", na=False)
            ].copy()
            if pendientes.empty:
                st.success("Todos los productos de esta tienda tienen datos suficientes para las recomendaciones disponibles.")
            else:
                st.warning(
                    f"{len(pendientes)} producto(s) requieren revisar el proveedor, "
                    "su lead time o el historial de ventas."
                )
                st.dataframe(
                    preparar_tabla_decision(pendientes),
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption("Sin datos suficientes, la aplicación no calcula un PR artificial.")

    # ========================================================
    # EXPLICACIÓN DEL MODELO
    # ========================================================

    st.markdown("---")

    with st.expander(
        "🧮 ¿Cómo se realizan las recomendaciones?"
    ):

        st.markdown(
            f"""
            ### Pronóstico

            Se da mayor importancia a las ventas más recientes:

            - últimos 30 días → mayor peso;
            - período anterior → peso intermedio;
            - período más antiguo → menor peso.

            Esto permite que el sistema reaccione cuando un producto
            comienza a venderse más o menos que antes.

            ---

            ### Punto de reorden

            **PR = demanda diaria × lead time del proveedor + stock de seguridad.**

            El lead time se consulta en `Proveedor.lead_time`, asociado a
            cada producto mediante su proveedor asignado o, si no existe
            asignación, al proveedor de la última compra (confirmar antes de pedir).
            Nunca se supone un tiempo general de 7 días.

            ### Stock de seguridad

            **SS = mediana de los totales mensuales históricos × 2 %.**

            Se usan todos los meses desde la primera compra o venta
            del producto en esa tienda, incluido el mes actual; los meses
            sin ventas cuentan como cero. Un mes incompleto puede afectar la mediana.
            Es una política simple, no una garantía estadística del nivel de servicio.

            ### Cuánto comprar

            **Stock objetivo = demanda diaria × (cobertura objetivo + LT) + SS.**
            Al llegar al PR, la compra sugerida es la diferencia entre ese
            objetivo y el stock actual. No incluye pedidos pendientes porque
            el esquema actual no proporciona una posición de inventario confiable.

            ---



            ### Limpieza de inventario

            Un producto puede aparecer para limpieza cuando tiene
            inventario y lleva aproximadamente **{dias_limpieza} días**
            sin ventas suficientes en esa tienda.

            ---

            ### Importante

            Estas recomendaciones son de apoyo para toma de decisiones.
            A medida que tu base de datos acumule más ventas,
            el pronóstico tendrá más información histórica disponible.
            """
        )

    # ========================================================
    # VOLVER
    # ========================================================

    st.markdown("---")

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:
        if st.button(
            "⬅ Volver al menú principal",
            use_container_width=True,
            key="volver_menu_pronosticos"
        ):
            st.session_state["module"] = None
            st.rerun()


# ============================================================
# ALIAS
# ============================================================
# Esto permite que puedas importarlo con cualquiera de estos
# dos nombres dependiendo de cómo armes app.py.

def pronosticos():
    modulo_pronosticos()
