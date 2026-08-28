from io import BytesIO

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from src.data import DATA_DIR, product_catalog
from src.i18n import tr
from src.style import apply_style, content_header, html_card, next_page_link, style_plotly
from src.users import fictional_name

st.set_page_config(page_title=tr("Activación de audiencias", "Audience activation"), page_icon="👥", layout="wide")
apply_style()
content_header(
    tr("Audiencias accionables con promos", "Actionable promotional audiences"),
    tr("Transformamos las predicciones individuales en grupos de clientes que pueden activarse con campañas.", "We turn individual predictions into customer groups that can be activated through campaigns."),
)

RECS = DATA_DIR / "recommendations_top20.parquet"
CATALOG = DATA_DIR / "product_catalog.parquet"
DETAIL_LIMIT = 5_000
EXPORT_LIMIT = 100_000


@st.cache_data(show_spinner=False)
def query_frame(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Query parquet in DuckDB so the full scoring data never enters app memory."""
    with duckdb.connect() as con:
        con.execute("SET threads = 2")
        return con.execute(sql, list(params)).fetchdf()


@st.cache_data(show_spinner=False)
def excel_bytes(frame: pd.DataFrame, sheet: str) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name=sheet[:31])
    return output.getvalue()


@st.cache_data(show_spinner=False)
def csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8")


catalog = product_catalog()
has_aisle = "aisle" in catalog.columns and catalog.aisle.notna().any()
filters = st.columns(4 if has_aisle else 3, gap="medium")
labels = {"Media": tr("Media", "Medium"), "Alta": tr("Alta", "High"), "Baja": tr("Baja", "Low")}
band = filters[0].selectbox(tr("Banda de propensión", "Propensity band"), list(labels), format_func=labels.get)
product = filters[1].selectbox(
    tr("Producto", "Product"), ["Todos"] + sorted(catalog.product_name.dropna().unique()),
    format_func=lambda value: tr("Todos", "All") if value == "Todos" else value,
)
category = filters[2].selectbox(
    tr("Categoría", "Category"), ["Todos"] + sorted(catalog.department.dropna().unique()),
    format_func=lambda value: tr("Todos", "All") if value == "Todos" else value,
)
aisle = "Todos"
if has_aisle:
    aisle = filters[3].selectbox(
        tr("Pasillo / aisle", "Aisle"), ["Todos"] + sorted(catalog.aisle.dropna().unique()),
        format_func=lambda value: tr("Todos", "All") if value == "Todos" else value,
    )


def audience_sql(select_sql: str, suffix: str = "") -> tuple[str, tuple]:
    aisle_select = ", c.aisle" if has_aisle else ""
    conditions = ["r.propensity_band = ?"]
    params = [str(RECS), str(CATALOG), band]
    if product != "Todos":
        conditions.append("c.product_name = ?")
        params.append(product)
    if category != "Todos":
        conditions.append("c.department = ?")
        params.append(category)
    if has_aisle and aisle != "Todos":
        conditions.append("c.aisle = ?")
        params.append(aisle)
    return f"""
        WITH audience AS (
            SELECT r.*, c.product_name, c.department{aisle_select}
            FROM read_parquet(?) r
            LEFT JOIN read_parquet(?) c USING (product_id)
            WHERE {' AND '.join(conditions)}
        )
        {select_sql} {suffix}
    """, tuple(params)


metrics = query_frame(*audience_sql("""
    SELECT count(DISTINCT user_id) AS clientes, count(*) AS oportunidades,
           count(DISTINCT product_id) AS productos FROM audience
""")).iloc[0]
action, recommendation = {
    "Alta": (tr("Evitar descuento innecesario", "Avoid unnecessary discount"), tr("Probable compra orgánica", "Likely organic purchase")),
    "Media": (tr("Realizar acción promocional", "Run a promotional action"), tr("Recomendación: A/B testing para medir uplift", "Recommendation: A/B testing to measure uplift")),
    "Baja": (tr("No accionar", "Do not activate"), tr("Señal insuficiente para activación", "Signal is insufficient for activation")),
}[band]
m1, m2, m3, m4 = st.columns(4)
with m1:
    html_card(tr("Acción sugerida", "Suggested action"), action, recommendation, "accent-orange")
with m2:
    html_card(tr("Clientes activables", "Activatable customers"), f"{int(metrics.clientes):,}", tr("clientes únicos", "unique customers"), "accent-violet")
with m3:
    html_card(tr("Ventas potenciales activables*", "Activatable potential sales*"), f"{int(metrics.oportunidades):,}", tr("oportunidades cliente-producto", "customer-product opportunities"), "accent-teal")
with m4:
    html_card(tr("Productos", "Products"), f"{int(metrics.productos):,}", tr("productos involucrados", "products involved"), "accent-purple")
st.caption(tr("* Cada registro representa una venta potencial cliente-producto. No se consideran múltiples unidades del mismo producto para un mismo cliente.", "* Each record represents one potential customer-product sale. Multiple units of the same product for one customer are not counted."))
if int(metrics.oportunidades) == 0:
    st.warning(tr("No hay oportunidades para los filtros seleccionados.", "There are no opportunities for the selected filters."))
    st.stop()

# Product opportunity: aggregation is executed inside DuckDB.
st.markdown(tr("## ¿Dónde está la mayor oportunidad de activación?", "## Where is the greatest activation opportunity?"))
st.markdown(f"<div class='chart-intro'>{tr('Agrupar por producto permite identificar qué artículos concentran más clientes con interés suficiente para una acción promocional.', 'Grouping by product identifies which items concentrate more customers with enough interest for a promotional action.')}</div>", unsafe_allow_html=True)
st.caption(tr("Los orígenes pueden superponerse; por eso sus porcentajes no necesariamente suman 100%.", "Sources can overlap, so their percentages do not necessarily add up to 100%."))
aisle_group = ", aisle" if has_aisle else ""
product_query = audience_sql(f"""
    SELECT product_id, product_name, department{aisle_group},
           count(DISTINCT user_id) AS clientes_elegibles,
           avg(propensity_score) AS propension_media,
           median(propensity_score) AS propension_mediana,
           100*avg(CASE WHEN coalesce(user_product_orders,0)>0 THEN 1 ELSE 0 END) AS porcentaje_ya_compradores,
           100*avg(coalesce(source_previous,0)) AS porcentaje_origen_historico,
           100*avg(coalesce(source_similar_users,0)) AS porcentaje_origen_vecinos,
           100*avg(coalesce(source_global_popular,0)) AS porcentaje_origen_popular
    FROM audience GROUP BY product_id, product_name, department{aisle_group}
""", "ORDER BY clientes_elegibles DESC, propension_mediana DESC")
by_product = query_frame(*product_query)
by_product.insert(0, "prioridad", range(1, len(by_product) + 1))
top_n = st.select_slider(tr("Cantidad de productos en el ranking", "Number of products in the ranking"), [10, 15, 20], value=15)
top_products = by_product.head(top_n).sort_values("clientes_elegibles")
chart_col, table_col = st.columns([1, 1.25], gap="medium")
with chart_col:
    st.markdown(tr("### Top productos por cantidad de clientes activables", "### Top products by activatable customers"))
    st.markdown(f"<div class='chart-intro'>{tr('Permite detectar qué productos justifican una campaña propia por su alcance potencial.', 'Reveals which products justify a dedicated campaign based on potential reach.')}</div>", unsafe_allow_html=True)
    fig = px.bar(top_products, x="clientes_elegibles", y="product_name", orientation="h", text="clientes_elegibles", custom_data=["porcentaje_origen_historico", "porcentaje_origen_vecinos", "porcentaje_origen_popular"])
    style_plotly(fig)
    fig.update_traces(marker_color="#5b45f5", texttemplate="%{x:,.0f}", textposition="outside", cliponaxis=False,
                      hovertemplate=f"<b>%{{y}}</b><br>{tr('Clientes activables','Activatable customers')}: %{{x:,}}<br>{tr('Origen histórico','Historical source')}: %{{customdata[0]:.1f}}%<br>{tr('Vecinos similares','Similar neighbors')}: %{{customdata[1]:.1f}}%<br>{tr('Popularidad global','Global popularity')}: %{{customdata[2]:.1f}}%<extra></extra>")
    fig.update_layout(height=520, showlegend=False, margin=dict(l=10, r=70, t=10, b=25), barcornerradius=5)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
with table_col:
    st.markdown(tr("### Resumen por producto", "### Product summary"))
    st.markdown(f"<div class='chart-intro'>{tr('Complementa el ranking con propensión, compradores anteriores y categoría.', 'Adds propensity, previous buyers, and category to the ranking.')}</div>", unsafe_allow_html=True)
    st.dataframe(by_product, width="stretch", hide_index=True, height=520)
_, download_col, _ = st.columns([1, 1.2, 1])
with download_col:
    st.download_button(tr("Descargar resumen por producto", "Download product summary"), excel_bytes(by_product, tr("Por producto", "By product")), tr("audiencia_por_producto.xlsx", "audience_by_product.xlsx"), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Category opportunity.
st.markdown(tr("## Oportunidades por categoría", "## Opportunities by category"))
st.markdown(f"<div class='chart-intro'>{tr('Las categorías permiten pasar de campañas producto a producto a estrategias comerciales de mayor escala.', 'Categories make it possible to move from product-by-product campaigns to broader commercial strategies.')}</div>", unsafe_allow_html=True)
category_query = audience_sql("""
    SELECT department AS categoria, count(DISTINCT user_id) AS clientes_unicos,
           count(*) AS oportunidades_cliente_producto, count(DISTINCT product_id) AS productos_involucrados,
           avg(propensity_score) AS propension_media, median(propensity_score) AS propension_mediana,
           100*avg(coalesce(source_previous,0)) AS porcentaje_origen_historico,
           100*avg(coalesce(source_similar_users,0)) AS porcentaje_origen_vecinos,
           100*avg(coalesce(source_global_popular,0)) AS porcentaje_origen_popular
    FROM audience GROUP BY department
""", "ORDER BY clientes_unicos DESC")
by_category = query_frame(*category_query)
chart_col, table_col = st.columns([1, 1.25], gap="medium")
with chart_col:
    st.markdown(tr("### Clientes activables por categoría", "### Activatable customers by category"))
    st.markdown(f"<div class='chart-intro'>{tr('Muestra dónde se concentra la mayor escala comercial y ayuda a priorizar presupuesto.', 'Shows where the greatest commercial scale is concentrated and helps prioritize budget.')}</div>", unsafe_allow_html=True)
    fig = px.bar(by_category.head(15).sort_values("clientes_unicos"), x="clientes_unicos", y="categoria", orientation="h", text="clientes_unicos")
    style_plotly(fig)
    fig.update_traces(marker_color="#168f83", texttemplate="%{x:,.0f}", textposition="outside", cliponaxis=False)
    fig.update_layout(height=470, showlegend=False, margin=dict(l=10, r=70, t=10, b=25), barcornerradius=5)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
with table_col:
    st.markdown(tr("### Resumen por categoría", "### Category summary"))
    st.markdown(f"<div class='chart-intro'>{tr('Compara clientes, ventas potenciales, productos y propensión más allá del volumen.', 'Compares customers, potential sales, products, and propensity beyond volume.')}</div>", unsafe_allow_html=True)
    st.dataframe(by_category, width="stretch", hide_index=True, height=470)
_, download_col, _ = st.columns([1, 1.2, 1])
with download_col:
    st.download_button(tr("Descargar resumen por categoría", "Download category summary"), excel_bytes(by_category, tr("Por categoría", "By category")), tr("audiencia_por_categoria.xlsx", "audience_by_category.xlsx"), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if not by_category.empty:
    selected = st.selectbox(tr("Ver principales productos dentro de la categoría", "View leading products within the category"), by_category.categoria.dropna().tolist())
    selected_products = by_product.loc[by_product.department.eq(selected)].head(15)
    st.markdown(f"### {tr('Principales productos', 'Leading products')} · {selected}")
    st.markdown(f"<div class='chart-intro'>{tr('Identifica qué productos explican la oportunidad dentro de la categoría seleccionada.', 'Identifies which products explain the opportunity within the selected category.')}</div>", unsafe_allow_html=True)
    st.dataframe(selected_products[["prioridad", "product_id", "product_name", "clientes_elegibles", "propension_mediana", "porcentaje_ya_compradores"]], width="stretch", hide_index=True)

# The operational table is deliberately bounded; filters still affect every row.
st.markdown(tr("## Detalle cliente-producto", "## Customer-product detail"))
st.markdown(f"<div class='chart-intro'>{tr(f'Vista de las primeras {DETAIL_LIMIT:,} oportunidades. El límite protege la estabilidad; use los filtros para acotar la audiencia.', f'View of the first {DETAIL_LIMIT:,} opportunities. The limit protects stability; use filters to narrow the audience.')}</div>", unsafe_allow_html=True)
detail_query = audience_sql("""
    SELECT user_id, product_id, product_name, rank, propensity_score, propensity_band, department
    FROM audience
""", f"ORDER BY user_id, rank LIMIT {DETAIL_LIMIT}")
detail = query_frame(*detail_query)
name_col = tr("Nombre ficticio", "Fictional name")
detail.insert(1, name_col, detail.user_id.map(lambda value: fictional_name(int(value))))
st.dataframe(detail, width="stretch", hide_index=True, height=520, row_height=34)

export_query = audience_sql("""
    SELECT user_id, product_id, product_name, rank, propensity_score, propensity_band, department
    FROM audience
""", f"ORDER BY user_id, rank LIMIT {EXPORT_LIMIT}")
export = query_frame(*export_query)
export.insert(1, name_col, export.user_id.map(lambda value: fictional_name(int(value))))
_, download_col, _ = st.columns([1, 1.2, 1])
with download_col:
    st.download_button(tr("Descargar tabla detalle filtrada", "Download filtered detail table"), csv_bytes(export), tr("audiencia_detalle.csv", "audience_detail.csv"), mime="text/csv")
st.caption(tr(f"La descarga incluye hasta {EXPORT_LIMIT:,} registros y respeta los filtros activos.", f"The download includes up to {EXPORT_LIMIT:,} records and respects the active filters."))
if not has_aisle:
    st.caption(tr("La exportación actual no incluye aisle/pasillo; el filtro se habilitará cuando la columna esté disponible.", "The current export does not include aisle; the filter will be enabled when the column becomes available."))

next_page_link("Como_Se_Predice", "Motor predictivo", "Predictive engine")
