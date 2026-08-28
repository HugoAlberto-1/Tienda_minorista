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
# PARÁMETROS FIJOS DEL MODELO DE REORDEN
#
# Antes eran configurables desde la pantalla principal, pero en la
# práctica casi no cambian y solo agregaban ruido visual. Se dejan
# aquí como constantes: si en algún momento necesitas ajustarlos,
# basta con modificar estos dos valores.
# ============================================================

DIAS_REPOSICION = 7   # días que tarda en llegar un pedido nuevo
DIAS_SEGURIDAD = 7    # colchón adicional de días de inventario


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
            border-radius: 12px;
            padding: 16px 10px;
            text-align: center;
            box-shadow: 0 2px 7px rgba(0,0,0,0.06);
            min-height: 125px;
        }}

        .metric-icon {{
            font-size: 1.6em;
            margin-bottom: 3px;
        }}

        .metric-number {{
            color: {COLOR_PRIMARY};
            font-size: 1.8em;
            font-weight: 700;
        }}

        .metric-label {{
            color: {COLOR_MUTED};
            font-size: 0.83em;
            font-weight: 600;
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

        .stSelectbox > div > div > div {{
            color: white !important;
        }}

        .stSelectbox svg {{
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
    try:
        valor = float(valor)
    except Exception:
        valor = 0

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
        cursor.execute("""
            SELECT
                pc.cod_barra,
                pc.id_tienda,
                c.Fecha,
                pc.cantidad_comprada,
                pc.unidad
            FROM ProductoxCompra pc
            INNER JOIN Compra c
                ON pc.Id_compra = c.Id_compra
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
            df["Fecha"] = pd.to_datetime(df["Fecha"])
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
            df["Fecha"] = pd.to_datetime(df["Fecha"])
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
    dias_reposicion,
    dias_seguridad,
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
        # Punto de reorden
        #
        # Demanda durante tiempo de reposición
        # + inventario de seguridad
        # ----------------------------------------------------

        punto_reorden = demanda_diaria * (
            dias_reposicion + dias_seguridad
        )

        # ----------------------------------------------------
        # Stock objetivo
        #
        # Queremos cubrir:
        # cobertura objetivo
        # + tiempo de reposición
        # + seguridad
        # ----------------------------------------------------

        stock_objetivo = demanda_diaria * (
            cobertura_objetivo +
            dias_reposicion +
            dias_seguridad
        )

        compra_sugerida = max(
            0,
            stock_objetivo - stock
        )

        # ----------------------------------------------------
        # Próximo reorden
        # ----------------------------------------------------

        if demanda_diaria <= 0:
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

        # Producto con stock pero sin ventas
        if stock > 0 and demanda_diaria <= 0:

            if (
                dias_sin_venta is None
                or dias_sin_venta >= dias_limpieza
            ):
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

        # Reorden inmediato
        elif demanda_diaria > 0 and stock <= punto_reorden:
            accion = "🔴 Comprar ahora"
            prioridad = 1

        # Próximo a reorden
        elif demanda_diaria > 0 and dias_para_reorden <= 14:
            accion = "🟡 Próximo a comprar"
            prioridad = 2

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

            # Si la sugerencia matemática dio algo,
            # reducimos todavía más la reposición.
            compra_sugerida = max(
                0,
                compra_sugerida * 0.50
            )

        else:
            accion = "🟢 Mantener"
            prioridad = 6

        # ----------------------------------------------------
        # Texto próximo reorden
        # ----------------------------------------------------

        if demanda_diaria <= 0:
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

            "Punto reorden": round(punto_reorden, 2),
            "Stock objetivo": round(stock_objetivo, 2),
            "Compra sugerida": round(compra_sugerida, 2),

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
# El orden de este diccionario define el orden en el multiselect.
MAPA_INDICADORES = {
    "Stock actual": "Stock",
    "Duración estimada": "Cobertura",
    "% Rotación": "Rotación %",
    "Rotación (nivel)": "Nivel rotación",
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
    "Punto de reorden",
    "Cuánto comprar",
]

INDICADORES_DEFAULT = [
    "Stock actual",
    "Duración estimada",
    "% Rotación",
    "Punto de reorden",
    "Cuánto comprar",
    "Recomendación",
]


def construir_tabla_general(
    df,
    tiendas_seleccionadas,
    indicadores,
):
    """
    Una fila por producto y columnas dinámicas por tienda.

    Ejemplo:

    Producto |
    Tienda 1 - Stock actual |
    Tienda 1 - Duración estimada |
    Tienda 2 - Stock actual |
    Tienda 2 - Duración estimada
    """

    if df.empty:
        return pd.DataFrame()

    columnas_base = [
        "Código",
        "Producto",
        "Categoría",
    ]

    productos_base = (
        df[columnas_base]
        .drop_duplicates(subset=["Código", "Producto"])
        .sort_values("Producto")
        .reset_index(drop=True)
    )

    resultado = productos_base.copy()

    for tienda in tiendas_seleccionadas:

        df_tienda = df[
            df["Tienda"] == tienda
        ].copy()

        for indicador in indicadores:

            columna_origen = MAPA_INDICADORES[indicador]

            temp = df_tienda[
                [
                    "Código",
                    "Producto",
                    columna_origen,
                    "Medida"
                ]
            ].copy()

            nombre_columna = f"{tienda} | {indicador}"

            if indicador in INDICADORES_CANTIDAD:
                temp[nombre_columna] = temp.apply(
                    lambda r: formatear_cantidad(
                        r[columna_origen],
                        r["Medida"]
                    ),
                    axis=1,
                )

            elif indicador == "% Rotación":
                temp[nombre_columna] = temp[
                    columna_origen
                ].apply(
                    lambda x: (
                        f"{x:.1f}%"
                        if x < 999
                        else ">999%"
                    )
                )

            else:
                temp[nombre_columna] = temp[
                    columna_origen
                ]

            temp = temp[
                [
                    "Código",
                    "Producto",
                    nombre_columna
                ]
            ]

            resultado = resultado.merge(
                temp,
                on=["Código", "Producto"],
                how="left"
            )

    return resultado


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

    columnas = [
        "Producto",
        "Código",
        "Tienda",
        "Stock actual",
        "Cobertura",
        "Nivel rotación",
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
# DETALLE DE PRODUCTO
# ============================================================

def mostrar_detalle_producto(df):
    st.markdown(
        '<div class="section-title">🔎 Análisis individual de producto</div>',
        unsafe_allow_html=True
    )

    if df.empty:
        return

    productos = sorted(
        df["Producto"]
        .dropna()
        .unique()
        .tolist()
    )

    producto = st.selectbox(
        "Selecciona un producto:",
        productos,
        key="detalle_producto_pronostico",
    )

    detalle = df[
        df["Producto"] == producto
    ].copy()

    for _, fila in detalle.iterrows():

        st.markdown(
            f"#### 🏪 {fila['Tienda']}"
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Stock",
                formatear_cantidad(
                    fila["Stock"],
                    fila["Medida"]
                )
            )

        with c2:
            st.metric(
                "Cobertura",
                fila["Cobertura"]
            )

        with c3:
            st.metric(
                "Pronóstico 30 días",
                formatear_cantidad(
                    fila["Pronóstico 30d"],
                    fila["Medida"]
                )
            )

        with c4:
            st.metric(
                "Compra sugerida",
                formatear_cantidad(
                    fila["Compra sugerida"],
                    fila["Medida"]
                )
            )

        st.markdown(
            f"""
            <div class="decision-card">
                <strong>Rotación:</strong> {fila['Nivel rotación']}
                &nbsp;&nbsp; | &nbsp;&nbsp;
                <strong>Rotación proyectada:</strong> {fila['Rotación %']:.1f}%
                <br>
                <strong>Punto de reorden:</strong>
                {formatear_cantidad(fila['Punto reorden'], fila['Medida'])}
                &nbsp;&nbsp; | &nbsp;&nbsp;
                <strong>Próximo reorden:</strong> {fila['Próximo reorden']}
                <br>
                <strong>Tendencia:</strong> {fila['Tendencia']}
                &nbsp;&nbsp; | &nbsp;&nbsp;
                <strong>Última venta:</strong> {fila['Última venta']}
                <br><br>
                <strong>Sugerencia:</strong> {fila['Acción']}
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

    with st.expander(
        "⚙️ Configuración del pronóstico y reorden",
        expanded=False
    ):

        st.caption(
            "Estos parámetros permiten adaptar la recomendación "
            "de compra a la forma real en que trabajas."
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

        st.caption(
            f"ℹ️ El punto de reorden asume un tiempo de reposición fijo "
            f"de {DIAS_REPOSICION} días y un stock de seguridad fijo de "
            f"{DIAS_SEGURIDAD} días."
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
        dias_reposicion=DIAS_REPOSICION,
        dias_seguridad=DIAS_SEGURIDAD,
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

    f1, f2 = st.columns([2, 1])

    with f1:
        buscador = st.text_input(
            "🔎 Buscar producto",
            placeholder=(
                "Escribe nombre o código de barras..."
            ),
            key="buscar_producto_pronostico",
        )

    with f2:
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

    if buscador:
        texto = buscador.strip().lower()

        df_filtrado = df_filtrado[
            df_filtrado["Producto"]
            .astype(str)
            .str.lower()
            .str.contains(
                texto,
                na=False,
                regex=False
            )
            |
            df_filtrado["Código"]
            .astype(str)
            .str.lower()
            .str.contains(
                texto,
                na=False,
                regex=False
            )
        ]

    if categoria != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["Categoría"] ==
            categoria
        ]

    # ========================================================
    # RESUMEN EJECUTIVO
    # ========================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-title">📌 Resumen para toma de decisiones</div>',
        unsafe_allow_html=True
    )

    comprar_ahora = len(
        df_filtrado[
            df_filtrado["Acción"] ==
            "🔴 Comprar ahora"
        ]
    )

    proximos = len(
        df_filtrado[
            df_filtrado["Acción"] ==
            "🟡 Próximo a comprar"
        ]
    )

    reducir = len(
        df_filtrado[
            df_filtrado["Acción"] ==
            "🟠 Reducir compra"
        ]
    )

    no_comprar = len(
        df_filtrado[
            df_filtrado["Acción"] ==
            "🚫 No comprar"
        ]
    )

    limpieza = len(
        df_filtrado[
            df_filtrado["Acción"] ==
            "🧹 Limpieza de inventario"
        ]
    )

    c1, c2, c3, c4, c5 = st.columns(5)

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

    # ========================================================
    # MATRIZ PRINCIPAL: PRODUCTO x TIENDA
    # ========================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-title">📋 Punto de reorden y compra sugerida por tienda</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Esta es la vista principal para decidir cuánto comprar: cada "
        "fila es un producto, y puedes comparar tienda por tienda su "
        "stock, rotación, punto de reorden y cuánto conviene comprar. "
        "Así es fácil notar cuando un mismo producto rota distinto de "
        "una tienda a otra."
    )

    nombres_tiendas = (
        df_filtrado["Tienda"]
        .dropna()
        .unique()
        .tolist()
    )

    controles1, controles2 = st.columns(2)

    with controles1:

        tiendas_visibles = st.multiselect(
            "🏪 Tiendas visibles",
            options=nombres_tiendas,
            default=nombres_tiendas,
            key="tiendas_visibles_pronostico",
        )

    with controles2:

        indicadores_visibles = st.multiselect(
            "👁️ Información visible",
            options=list(MAPA_INDICADORES.keys()),
            default=INDICADORES_DEFAULT,
            key="indicadores_visibles_pronostico",
        )

    if not tiendas_visibles:
        st.warning(
            "⚠️ Selecciona al menos una tienda."
        )

    elif not indicadores_visibles:
        st.warning(
            "⚠️ Selecciona al menos un dato para mostrar."
        )

    else:

        tabla_general = construir_tabla_general(
            df_filtrado,
            tiendas_visibles,
            indicadores_visibles,
        )

        st.dataframe(
            tabla_general,
            use_container_width=True,
            hide_index=True,
            height=450,
        )

    with st.expander(
        "ℹ️ ¿Cómo leer esta tabla?"
    ):
        st.markdown(
            """
            **Stock actual:** cantidad que existe actualmente en esa tienda.

            **Duración estimada:** aproximadamente cuánto tiempo durará
            ese inventario al ritmo de venta pronosticado (equivalente
            a "compré 10 y me duraron 5 meses").

            **% Rotación:** porcentaje del stock actual que se espera
            vender durante los próximos 30 días. Puede superar 100 %,
            lo cual indica que el stock actual no alcanzaría para cubrir
            la demanda pronosticada.

            **Punto de reorden:** nivel de inventario en el cual
            conviene volver a comprar.

            **Cuánto comprar:** cantidad estimada necesaria para
            alcanzar la cobertura objetivo.

            **Recomendación:** acción sugerida para ese producto en
            esa tienda específica.
            """
        )

    # ========================================================
    # CENTRO DE DECISIONES
    # ========================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-title">🧠 Centro de decisiones</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Los mismos productos de la tabla de arriba, ahora agrupados "
        "por la acción recomendada — útil cuando quieres trabajar "
        "una lista a la vez (por ejemplo, todo lo que hay que comprar hoy)."
    )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "🔴 Comprar ahora",
            "🟡 Próximos a comprar",
            "🟠 Reducir compra",
            "🚫 No comprar",
            "🧹 Limpieza",
            "🟢 Mantener",
        ]
    )

    # --------------------------------------------------------
    # COMPRAR AHORA
    # --------------------------------------------------------

    with tab1:

        datos = df_filtrado[
            df_filtrado["Acción"] ==
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
            st.success(
                "✅ Ningún producto requiere compra inmediata."
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

        datos = df_filtrado[
            df_filtrado["Acción"] ==
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

        datos = df_filtrado[
            df_filtrado["Acción"] ==
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

        datos = df_filtrado[
            df_filtrado["Acción"] ==
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

        datos = df_filtrado[
            df_filtrado["Acción"] ==
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

        datos = df_filtrado[
            df_filtrado["Acción"] ==
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

    # ========================================================
    # DETALLE POR PRODUCTO
    # ========================================================

    st.markdown("---")

    mostrar_detalle_producto(
        df_filtrado
    )

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

            **Punto de reorden = demanda diaria ×
            (tiempo de reposición + stock de seguridad)**

            Se utilizan valores fijos para mantener la pantalla simple:

            - Tiempo de reposición: **{DIAS_REPOSICION} días**
            - Stock de seguridad: **{DIAS_SEGURIDAD} días**

            Si en tu operación estos tiempos varían mucho de un
            producto a otro (por ejemplo, proveedores distintos con
            tiempos de entrega distintos), lo ideal a futuro sería
            registrarlos por producto o por proveedor en la base de
            datos; por ahora se manejan como un promedio general para
            todos los productos y tiendas.

            ---

            ### Cuánto comprar

            El sistema estima cuánto inventario debería existir para
            cubrir:

            - la cobertura objetivo;
            - el tiempo de reposición;
            - el stock de seguridad.

            Después resta el inventario existente.

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
