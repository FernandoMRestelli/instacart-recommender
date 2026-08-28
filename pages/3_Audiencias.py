from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data import load_parquet, product_catalog
from src.i18n import tr
from src.style import apply_style, content_header, html_card, style_plotly
from src.users import fictional_name

st.set_page_config(page_title=tr("Activación de audiencias", "Audience activation"), page_icon="👥", layout="wide")
apply_style()
content_header(
    tr("Audiencias accionables con promos", "Actionable promotional audiences"),
    tr("Transformamos las predicciones individuales en grupos de clientes que pueden activarse con campañas.", "We turn individual predictions into customer groups that can be activated through campaigns."),
)


@st.cache_data(show_spinner=False)
def audience_base():
    recommendations = load_parquet("recommendations_top20.parquet")
    catalog = product_catalog()
    return recommendations.merge(catalog, on="product_id", how="left", validate="many_to_one")


@st.cache_data(show_spinner=False)
def product_summary(frame):
    source = frame.copy()
    source["ya_comprador"] = source["user_product_orders"].fillna(0).gt(0)
    source[["source_previous", "source_similar_users", "source_global_popular"]] = source[
        ["source_previous", "source_similar_users", "source_global_popular"]
    ].fillna(0)
    grouping = ["product_id", "product_name", "department"]
    if "aisle" in source.columns:
        grouping.append("aisle")
    summary = (
        source.groupby(grouping, dropna=False)
        .agg(
            clientes_elegibles=("user_id", "nunique"),
            propension_media=("propensity_score", "mean"),
            propension_mediana=("propensity_score", "median"),
            porcentaje_ya_compradores=("ya_comprador", "mean"),
            porcentaje_origen_historico=("source_previous", "mean"),
            porcentaje_origen_vecinos=("source_similar_users", "mean"),
            porcentaje_origen_popular=("source_global_popular", "mean"),
        )
        .reset_index()
        .sort_values(["clientes_elegibles", "propension_mediana"], ascending=[False, False])
    )
    percentage_columns = [
        "porcentaje_ya_compradores",
        "porcentaje_origen_historico",
        "porcentaje_origen_vecinos",
        "porcentaje_origen_popular",
    ]
    summary[percentage_columns] *= 100
    summary.insert(0, "prioridad", range(1, len(summary) + 1))
    return summary


@st.cache_data(show_spinner=False)
def category_summary(frame, category):
    source = frame.copy()
    source[["source_previous", "source_similar_users", "source_global_popular"]] = source[
        ["source_previous", "source_similar_users", "source_global_popular"]
    ].fillna(0)
    summary = (
        source.groupby(category, dropna=False)
        .agg(
            clientes_unicos=("user_id", "nunique"),
            oportunidades_cliente_producto=("product_id", "size"),
            productos_involucrados=("product_id", "nunique"),
            propension_media=("propensity_score", "mean"),
            propension_mediana=("propensity_score", "median"),
            porcentaje_origen_historico=("source_previous", "mean"),
            porcentaje_origen_vecinos=("source_similar_users", "mean"),
            porcentaje_origen_popular=("source_global_popular", "mean"),
        )
        .reset_index()
        .sort_values("clientes_unicos", ascending=False)
    )
    summary[["porcentaje_origen_historico", "porcentaje_origen_vecinos", "porcentaje_origen_popular"]] *= 100
    return summary


@st.cache_data(show_spinner=False)
def excel_bytes(frame, sheet_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return output.getvalue()


@st.cache_data(show_spinner=False)
def csv_bytes(frame):
    return frame.to_csv(index=False).encode("utf-8")


recs = audience_base()
has_aisle = "aisle" in recs.columns and recs["aisle"].notna().any()

filter_columns = st.columns(4 if has_aisle else 3, gap="medium")
band_labels = {"Media": tr("Media", "Medium"), "Alta": tr("Alta", "High"), "Baja": tr("Baja", "Low")}
band = filter_columns[0].selectbox(tr("Banda de propensión", "Propensity band"), ["Media", "Alta", "Baja"], index=0, format_func=band_labels.get)
product_options = ["Todos"] + sorted(recs.product_name.dropna().unique().tolist())
product = filter_columns[1].selectbox(tr("Producto", "Product"), product_options, format_func=lambda value: tr("Todos", "All") if value == "Todos" else value)
department_options = ["Todos"] + sorted(recs.department.dropna().unique().tolist())
department = filter_columns[2].selectbox(tr("Categoría", "Category"), department_options, format_func=lambda value: tr("Todos", "All") if value == "Todos" else value)
aisle = "Todos"
if has_aisle:
    aisle_options = ["Todos"] + sorted(recs.aisle.dropna().unique().tolist())
    aisle = filter_columns[3].selectbox(tr("Pasillo / aisle", "Aisle"), aisle_options, format_func=lambda value: tr("Todos", "All") if value == "Todos" else value)

audience = recs.loc[recs.propensity_band.eq(band)].copy()
if product != "Todos":
    audience = audience.loc[audience.product_name.eq(product)]
if department != "Todos":
    audience = audience.loc[audience.department.eq(department)]
if has_aisle and aisle != "Todos":
    audience = audience.loc[audience.aisle.eq(aisle)]

action, recommendation = {
    "Alta": (tr("Evitar descuento innecesario", "Avoid unnecessary discount"), tr("Probable compra orgánica", "Likely organic purchase")),
    "Media": (tr("Realizar acción promocional", "Run a promotional action"), tr("Recomendación: A/B testing para medir uplift", "Recommendation: A/B testing to measure uplift")),
    "Baja": (tr("No accionar", "Do not activate"), tr("Señal insuficiente para activación", "Signal is insufficient for activation")),
}[band]
m1, m2, m3, m4 = st.columns(4)
with m1:
    html_card(tr("Acción sugerida", "Suggested action"), action, recommendation, "accent-orange")
with m2:
    html_card(tr("Clientes activables", "Activatable customers"), f"{audience.user_id.nunique():,}", tr("clientes únicos", "unique customers"), "accent-violet")
with m3:
    html_card(tr("Ventas potenciales activables*", "Activatable potential sales*"), f"{len(audience):,}", tr("oportunidades cliente-producto", "customer-product opportunities"), "accent-teal")
with m4:
    html_card(tr("Productos", "Products"), f"{audience.product_id.nunique():,}", tr("productos involucrados", "products involved"), "accent-purple")

st.caption(tr("* Cada registro representa una venta potencial cliente-producto. No se consideran múltiples unidades del mismo producto para un mismo cliente.", "* Each record represents one potential customer-product sale. Multiple units of the same product for one customer are not counted."))

if audience.empty:
    st.warning(tr("No hay oportunidades para la combinación de filtros seleccionada.", "There are no opportunities for the selected filter combination."))
    st.stop()

# -----------------------------------------------------------------------------
# AGRUPACIÓN POR PRODUCTO
# -----------------------------------------------------------------------------
st.markdown(tr("## ¿Dónde está la mayor oportunidad de activación?", "## Where is the greatest activation opportunity?"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('Agrupar por producto permite identificar qué artículos concentran una mayor cantidad de clientes con interés suficiente para una acción promocional.', 'Grouping by product identifies which items concentrate the largest number of customers with enough interest for a promotional action.')}
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(tr("Los orígenes pueden superponerse: una oportunidad puede provenir simultáneamente del histórico, de vecinos similares y de popularidad; por eso los porcentajes no necesariamente suman 100%.", "Sources can overlap: an opportunity may come from history, similar neighbors, and popularity at the same time, so percentages do not necessarily add up to 100%."))

by_product = product_summary(audience)
top_n = st.select_slider(tr("Cantidad de productos en el ranking", "Number of products in the ranking"), options=[10, 15, 20], value=15)
top_products = by_product.head(top_n).sort_values("clientes_elegibles")

chart_col, table_col = st.columns([1, 1.25], gap="medium")
with chart_col:
    st.markdown(tr("### Top productos por cantidad de clientes activables", "### Top products by activatable customers"))
    st.markdown(
        f"<div class='chart-intro'>{tr('Permite detectar rápidamente qué productos justifican una campaña propia por su alcance potencial. Cuanto mayor es la barra, más clientes pueden incluirse en una activación del producto.', 'Quickly reveals which products justify a dedicated campaign based on potential reach. The longer the bar, the more customers can be included in a product activation.')}</div>",
        unsafe_allow_html=True,
    )
    product_fig = px.bar(
        top_products,
        x="clientes_elegibles",
        y="product_name",
        orientation="h",
        text="clientes_elegibles",
        custom_data=["porcentaje_origen_historico", "porcentaje_origen_vecinos", "porcentaje_origen_popular"],
        labels={"clientes_elegibles": tr("Clientes activables", "Activatable customers"), "product_name": ""},
    )
    style_plotly(product_fig)
    product_fig.update_traces(
        marker_color="#5b45f5",
        texttemplate="%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            f"<b>%{{y}}</b><br>{tr('Clientes activables', 'Activatable customers')}: %{{x:,}}"
            f"<br>{tr('Origen histórico', 'Historical source')}: %{{customdata[0]:.1f}}%"
            f"<br>{tr('Vecinos similares', 'Similar neighbors')}: %{{customdata[1]:.1f}}%"
            f"<br>{tr('Popularidad global', 'Global popularity')}: %{{customdata[2]:.1f}}%<extra></extra>"
        ),
    )
    product_fig.update_layout(height=520, showlegend=False, margin=dict(l=10, r=70, t=10, b=25), barcornerradius=5)
    product_fig.update_xaxes(title_text=tr("Clientes activables", "Activatable customers"), rangemode="tozero")
    product_fig.update_yaxes(title_text="", tickfont=dict(color="#354156", size=10))
    st.plotly_chart(product_fig, use_container_width=True, config={"displayModeBar": False})

with table_col:
    st.markdown(tr("### Resumen por producto", "### Product summary"))
    st.markdown(
        f"<div class='chart-intro'>{tr('Complementa el ranking con calidad de audiencia: propensión típica, proporción de compradores anteriores y categoría. Sirve para elegir el producto, dimensionar la campaña y decidir si conviene recompra o captación.', 'Adds audience quality to the ranking: typical propensity, share of previous buyers, and category. It helps choose the product, size the campaign, and decide between repurchase and acquisition.')}</div>",
        unsafe_allow_html=True,
    )
    product_view_columns = [
        "prioridad", "product_id", "product_name", "clientes_elegibles",
        "propension_media", "propension_mediana", "porcentaje_ya_compradores", "department",
        "porcentaje_origen_historico", "porcentaje_origen_vecinos", "porcentaje_origen_popular",
    ]
    if has_aisle:
        product_view_columns.append("aisle")
    product_view = by_product[product_view_columns].copy()
    st.dataframe(
        product_view,
        width="stretch",
        hide_index=True,
        height=520,
        column_config={
            "prioridad": st.column_config.NumberColumn(tr("Prioridad", "Priority"), format="%d"),
            "product_id": st.column_config.NumberColumn("Product ID", format="%d"),
            "product_name": st.column_config.TextColumn(tr("Producto", "Product"), width="large"),
            "clientes_elegibles": st.column_config.NumberColumn(tr("Clientes elegibles", "Eligible customers"), format="%,d"),
            "propension_media": st.column_config.NumberColumn(tr("Prop. media", "Avg. propensity"), format="%.3f"),
            "propension_mediana": st.column_config.NumberColumn(tr("Prop. mediana", "Median propensity"), format="%.3f"),
            "porcentaje_ya_compradores": st.column_config.NumberColumn(tr("Ya compradores", "Previous buyers"), format="%.1f%%"),
            "porcentaje_origen_historico": st.column_config.NumberColumn(tr("Origen histórico", "Historical source"), format="%.1f%%"),
            "porcentaje_origen_vecinos": st.column_config.NumberColumn(tr("Origen vecinos", "Neighbor source"), format="%.1f%%"),
            "porcentaje_origen_popular": st.column_config.NumberColumn(tr("Origen popularidad", "Popularity source"), format="%.1f%%"),
            "department": st.column_config.TextColumn(tr("Categoría", "Category")),
            "aisle": st.column_config.TextColumn(tr("Pasillo / aisle", "Aisle")),
        },
    )

_, product_download, _ = st.columns([1, 1.2, 1])
with product_download:
    st.download_button(
        tr("Descargar resumen por producto", "Download product summary"),
        excel_bytes(product_view, tr("Por producto", "By product")),
        tr("audiencia_por_producto.xlsx", "audience_by_product.xlsx"),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# -----------------------------------------------------------------------------
# AGRUPACIÓN POR CATEGORÍA
# -----------------------------------------------------------------------------
st.markdown(tr("## Oportunidades por categoría", "## Opportunities by category"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('Las agrupaciones por categoría permiten pasar de campañas producto a producto a estrategias comerciales de mayor escala.', 'Category groupings make it possible to move from product-by-product campaigns to broader commercial strategies.')}
    </div>
    """,
    unsafe_allow_html=True,
)

category_name = tr("Categoría", "Category")
unique_customers = tr("Clientes únicos", "Unique customers")
opportunity_col = tr("Oportunidades cliente-producto", "Customer-product opportunities")
products_involved = tr("Productos involucrados", "Products involved")
average_propensity = tr("Propensión media", "Average propensity")
median_propensity = tr("Propensión mediana", "Median propensity")
history_source = tr("% origen histórico", "% historical source")
neighbor_source = tr("% origen vecinos", "% neighbor source")
popularity_source = tr("% origen popularidad", "% popularity source")
category_frame = category_summary(audience, "department").rename(
    columns={
        "department": category_name,
        "clientes_unicos": unique_customers,
        "oportunidades_cliente_producto": opportunity_col,
        "productos_involucrados": products_involved,
        "propension_media": average_propensity,
        "propension_mediana": median_propensity,
        "porcentaje_origen_historico": history_source,
        "porcentaje_origen_vecinos": neighbor_source,
        "porcentaje_origen_popular": popularity_source,
    }
)
chart_value = unique_customers
download_name = tr("audiencia_por_categoria.xlsx", "audience_by_category.xlsx")
download_label = tr("Descargar resumen por categoría", "Download category summary")

category_top = category_frame.head(15).sort_values(chart_value)
category_chart_col, category_table_col = st.columns([1, 1.25], gap="medium")
with category_chart_col:
    st.markdown(tr("### Clientes activables por categoría", "### Activatable customers by category"))
    st.markdown(
        f"<div class='chart-intro'>{tr('Muestra en qué categorías se concentra la mayor escala comercial. Es útil para priorizar presupuesto, espacios promocionales y campañas que abarcan varios productos relacionados.', 'Shows which categories concentrate the greatest commercial scale. It helps prioritize budget, promotional placements, and campaigns spanning several related products.')}</div>",
        unsafe_allow_html=True,
    )
    category_fig = px.bar(
        category_top,
        x=chart_value,
        y=category_name,
        orientation="h",
        text=chart_value,
        custom_data=[history_source, neighbor_source, popularity_source],
        labels={chart_value: tr("Clientes activables", "Activatable customers"), category_name: ""},
    )
    style_plotly(category_fig)
    category_fig.update_traces(
        marker_color="#168f83",
        texttemplate="%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            f"<b>%{{y}}</b><br>{tr('Clientes activables', 'Activatable customers')}: %{{x:,}}"
            f"<br>{tr('Origen histórico', 'Historical source')}: %{{customdata[0]:.1f}}%"
            f"<br>{tr('Vecinos similares', 'Similar neighbors')}: %{{customdata[1]:.1f}}%"
            f"<br>{tr('Popularidad global', 'Global popularity')}: %{{customdata[2]:.1f}}%<extra></extra>"
        ),
    )
    category_fig.update_layout(height=470, showlegend=False, margin=dict(l=10, r=70, t=10, b=25), barcornerradius=5)
    category_fig.update_yaxes(title_text="", tickfont=dict(color="#354156", size=10))
    st.plotly_chart(category_fig, use_container_width=True, config={"displayModeBar": False})

with category_table_col:
    st.markdown(f"### {tr('Resumen por', 'Summary by')} {category_name.lower()}")
    st.markdown(
        f"<div class='chart-intro'>{tr('Detalla el tamaño y la diversidad de cada oportunidad: clientes únicos, ventas potenciales activables, cantidad de productos y nivel de propensión. Permite comparar categorías más allá del volumen.', 'Details the scale and diversity of each opportunity: unique customers, activatable potential sales, product count, and propensity level. This allows categories to be compared beyond volume alone.')}</div>",
        unsafe_allow_html=True,
    )
    st.dataframe(category_frame, width="stretch", hide_index=True, height=470)

_, category_download, _ = st.columns([1, 1.2, 1])
with category_download:
    st.download_button(
        download_label,
        excel_bytes(category_frame, category_name),
        download_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

if not category_frame.empty:
    selected_category = st.selectbox(
        f"{tr('Ver principales productos dentro de', 'View leading products within')} {category_name.lower()}",
        category_frame[category_name].dropna().tolist(),
    )
    category_products = product_summary(audience.loc[audience.department.eq(selected_category)]).head(15)
    st.markdown(f"### {tr('Principales productos', 'Leading products')} · {selected_category}")
    st.markdown(
        f"<div class='chart-intro'>{tr('Identifica qué productos explican la oportunidad dentro de la categoría seleccionada. Ayuda a definir el surtido concreto de una campaña categorial y priorizar los artículos con mayor audiencia.', 'Identifies which products explain the opportunity within the selected category. It helps define the concrete assortment for a category campaign and prioritize items with the largest audience.')}</div>",
        unsafe_allow_html=True,
    )
    st.dataframe(
        category_products[["prioridad", "product_id", "product_name", "clientes_elegibles", "propension_mediana", "porcentaje_ya_compradores"]],
        width="stretch",
        hide_index=True,
        row_height=34,
        column_config={
            "prioridad": tr("Prioridad", "Priority"),
            "product_id": "Product ID",
            "product_name": tr("Producto", "Product"),
            "clientes_elegibles": st.column_config.NumberColumn(tr("Clientes elegibles", "Eligible customers"), format="%,d"),
            "propension_mediana": st.column_config.ProgressColumn(tr("Prop. mediana", "Median propensity"), min_value=0, max_value=1, format="%.3f"),
            "porcentaje_ya_compradores": st.column_config.ProgressColumn(tr("Ya compradores", "Previous buyers"), min_value=0, max_value=100, format="%.1f%%"),
        },
    )

# -----------------------------------------------------------------------------
# DETALLE CLIENTE-PRODUCTO
# -----------------------------------------------------------------------------
st.markdown(tr("## Detalle cliente-producto", "## Customer-product detail"))
st.markdown(
    f"<div class='chart-intro'>{tr('Vista operativa de las oportunidades individuales que componen los resúmenes anteriores.', 'Operational view of the individual opportunities that make up the summaries above.')}</div>",
    unsafe_allow_html=True,
)
name_map = {int(uid): fictional_name(int(uid)) for uid in audience.user_id.unique()}
detail = audience.copy()
fictional_col = tr("Nombre ficticio", "Fictional name")
detail[fictional_col] = detail.user_id.map(name_map)
detail_columns = ["user_id", fictional_col, "product_id", "product_name", "rank", "propensity_score", "propensity_band", "department"]
if has_aisle:
    detail_columns.append("aisle")
detail_view = detail[detail_columns].sort_values(["user_id", "rank"])
customer_id_col = tr("ID cliente", "Customer ID")
product_col = tr("Producto", "Product")
propensity_col = tr("Propensión", "Propensity")
band_col = tr("Banda", "Band")
category_col = tr("Categoría", "Category")
aisle_col = tr("Pasillo / aisle", "Aisle")
detail_view.columns = [customer_id_col, fictional_col, "Product ID", product_col, "Rank", propensity_col, band_col, category_col] + ([aisle_col] if has_aisle else [])
band_visual = {"Alta": f"🟢 {tr('Alta', 'High')}", "Media": f"🟠 {tr('Media', 'Medium')}", "Baja": f"⚪ {tr('Baja', 'Low')}"}
detail_display = detail_view.copy(deep=False)
detail_display[band_col] = detail_display[band_col].map(band_visual).fillna(detail_display[band_col])
st.dataframe(
    detail_display,
    width="stretch",
    hide_index=True,
    height=520,
    row_height=34,
    column_config={
        customer_id_col: st.column_config.NumberColumn(customer_id_col, format="%d", width="small"),
        fictional_col: st.column_config.TextColumn(fictional_col, width="medium"),
        "Product ID": st.column_config.NumberColumn("Product ID", format="%d", width="small"),
        product_col: st.column_config.TextColumn(product_col, width="large"),
        "Rank": st.column_config.NumberColumn("Rank", format="%d", width="small"),
        propensity_col: st.column_config.ProgressColumn(propensity_col, min_value=0, max_value=1, format="%.3f", width="medium"),
        band_col: st.column_config.TextColumn(band_col, width="small"),
        category_col: st.column_config.TextColumn(category_col, width="medium"),
    },
)

_, detail_download, _ = st.columns([1, 1.2, 1])
with detail_download:
    st.download_button(
        tr("Descargar tabla detalle filtrada", "Download filtered detail table"),
        csv_bytes(detail_view),
        tr("audiencia_detalle.csv", "audience_detail.csv"),
        mime="text/csv",
    )

if not has_aisle:
    st.caption(tr("La exportación actual no incluye la variable aisle/pasillo. El filtro y los resúmenes por pasillo se habilitarán automáticamente cuando esa columna esté disponible.", "The current export does not include the aisle variable. Aisle filters and summaries will be enabled automatically when that column becomes available."))
