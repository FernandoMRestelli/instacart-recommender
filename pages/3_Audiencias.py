from io import BytesIO

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from src.data import DATA_DIR, load_parquet, product_catalog
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
band = filters[0].selectbox(tr("Propensión", "Propensity"), list(labels), format_func=labels.get)
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


with st.spinner(tr("Preparando la audiencia…", "Preparing the audience…"), show_time=True):
    band_metrics = load_parquet("audience_band_metrics.parquet")
    product_summaries = load_parquet("audience_product_summary.parquet")
    category_summaries = load_parquet("audience_category_summary.parquet")

by_product = product_summaries.loc[product_summaries.propensity_band.eq(band)].copy()
if product != "Todos":
    by_product = by_product.loc[by_product.product_name.eq(product)]
if category != "Todos":
    by_product = by_product.loc[by_product.department.eq(category)]
by_product = by_product.drop(columns="propensity_band").sort_values(
    ["clientes_elegibles", "propension_mediana"], ascending=[False, False]
)

if product == "Todos":
    by_category = category_summaries.loc[category_summaries.propensity_band.eq(band)].copy()
    if category != "Todos":
        by_category = by_category.loc[by_category.categoria.eq(category)]
    by_category = by_category.drop(columns="propensity_band").sort_values("clientes_unicos", ascending=False)
else:
    by_category = (
        by_product.groupby("department", dropna=False)
        .agg(
            clientes_unicos=("clientes_elegibles", "sum"),
            oportunidades_cliente_producto=("oportunidades", "sum"),
            productos_involucrados=("product_id", "nunique"),
            propension_media=("propension_media", "mean"),
            propension_mediana=("propension_mediana", "mean"),
            porcentaje_origen_historico=("porcentaje_origen_historico", "mean"),
            porcentaje_origen_vecinos=("porcentaje_origen_vecinos", "mean"),
            porcentaje_origen_popular=("porcentaje_origen_popular", "mean"),
        )
        .reset_index(names="categoria")
    )

if product != "Todos":
    metrics = pd.Series({
        "clientes": by_product.clientes_elegibles.sum(),
        "oportunidades": by_product.oportunidades.sum(),
        "productos": by_product.product_id.nunique(),
    })
elif category != "Todos" and not by_category.empty:
    row = by_category.iloc[0]
    metrics = pd.Series({"clientes": row.clientes_unicos, "oportunidades": row.oportunidades_cliente_producto, "productos": row.productos_involucrados})
else:
    metrics = band_metrics.loc[band_metrics.propensity_band.eq(band)].iloc[0]
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
    st.dataframe(by_product.head(200), width="stretch", hide_index=True, height=520)
    st.caption(tr("Se muestran las primeras 200 prioridades. La descarga incluye todo el resumen filtrado.", "The first 200 priorities are shown. The download includes the full filtered summary."))
product_export_key = f"product_summary_{band}_{product}_{category}_{aisle}"
if st.button(tr("Preparar resumen por producto", "Prepare product summary"), width="content"):
    with st.spinner(tr("Preparando Excel…", "Preparing Excel…"), show_time=True):
        st.session_state[product_export_key] = excel_bytes(by_product, tr("Por producto", "By product"))
if product_export_key in st.session_state:
    _, download_col, _ = st.columns([1, 1.2, 1])
    with download_col:
        st.download_button(tr("Descargar resumen por producto", "Download product summary"), st.session_state[product_export_key], tr("audiencia_por_producto.xlsx", "audience_by_product.xlsx"), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Category opportunity.
st.markdown(tr("## Oportunidades por categoría", "## Opportunities by category"))
st.markdown(f"<div class='chart-intro'>{tr('Las categorías permiten pasar de campañas producto a producto a estrategias comerciales de mayor escala.', 'Categories make it possible to move from product-by-product campaigns to broader commercial strategies.')}</div>", unsafe_allow_html=True)
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
st.markdown(f"<div class='chart-intro'>{tr('Los resúmenes anteriores se muestran primero para acelerar la experiencia móvil. Cargue el detalle únicamente cuando necesite trabajar con registros individuales.', 'The summaries above are shown first to speed up the mobile experience. Load the detail only when you need individual records.')}</div>", unsafe_allow_html=True)
show_detail = st.toggle(tr("Cargar tabla detalle", "Load detail table"), value=False)
name_col = tr("Nombre ficticio", "Fictional name")
if show_detail:
    with st.spinner(tr("Cargando detalle filtrado…", "Loading filtered detail…"), show_time=True):
        detail_query = audience_sql("""
            SELECT user_id, product_id, product_name, rank, propensity_score, propensity_band, department
            FROM audience
        """, f"ORDER BY user_id, rank LIMIT {DETAIL_LIMIT}")
        detail = query_frame(*detail_query)
        detail.insert(1, name_col, detail.user_id.map(lambda value: fictional_name(int(value))))
    st.caption(tr(f"Se muestran hasta {DETAIL_LIMIT:,} registros. Use los filtros para acotar la audiencia.", f"Up to {DETAIL_LIMIT:,} records are shown. Use filters to narrow the audience."))
    st.dataframe(detail, width="stretch", hide_index=True, height=520, row_height=34)

prepare_key = f"audience_export_{band}_{product}_{category}_{aisle}"
if st.button(tr("Preparar descarga del detalle", "Prepare detail download"), width="content"):
    with st.spinner(tr("Preparando archivo filtrado…", "Preparing filtered file…"), show_time=True):
        export_query = audience_sql("""
            SELECT user_id, product_id, product_name, rank, propensity_score, propensity_band, department
            FROM audience
        """, f"ORDER BY user_id, rank LIMIT {EXPORT_LIMIT}")
        export = query_frame(*export_query)
        export.insert(1, name_col, export.user_id.map(lambda value: fictional_name(int(value))))
        st.session_state[prepare_key] = csv_bytes(export)
if prepare_key in st.session_state:
    _, download_col, _ = st.columns([1, 1.2, 1])
    with download_col:
        st.download_button(tr("Descargar tabla detalle filtrada", "Download filtered detail table"), st.session_state[prepare_key], tr("audiencia_detalle.csv", "audience_detail.csv"), mime="text/csv")
    st.caption(tr(f"La descarga incluye hasta {EXPORT_LIMIT:,} registros y respeta los filtros activos.", f"The download includes up to {EXPORT_LIMIT:,} records and respects the active filters."))
if not has_aisle:
    st.caption(tr("La exportación actual no incluye aisle/pasillo; el filtro se habilitará cuando la columna esté disponible.", "The current export does not include aisle; the filter will be enabled when the column becomes available."))

next_page_link("Como_Se_Predice", "Motor predictivo", "Predictive engine")
