from io import BytesIO
from html import escape
import streamlit as st

from src.data import customer_profiles, user_recommendations
from src.i18n import tr
from src.style import apply_style, band_card, content_header, html_card, next_page_link
from src.users import user_label

st.set_page_config(page_title=tr("Próximo carrito", "Next basket"), page_icon="🛒", layout="wide")
apply_style()
content_header(
    tr("¿Qué productos tienen mayor propensión a estar en la próxima compra del cliente?", "Which products are most likely to be in the customer's next purchase?"),
    tr("Vista individual para entender al cliente y ordenar los productos con mayor interés esperado.", "Individual view to understand the customer and rank products by expected interest."),
)

try:
    profiles = customer_profiles().sort_values("user_id")
except FileNotFoundError as e:
    st.error(str(e)); st.stop()

header_cols = st.columns([1.35, 1, 1, 1, 1])
with header_cols[0]:
    with st.container(border=True):
        user_id = st.selectbox(
            tr("Cliente seleccionado", "Selected customer"),
            profiles["user_id"].tolist(),
            index=0,
            format_func=user_label,
        )
profile = profiles.loc[profiles.user_id.eq(user_id)].iloc[0]

recs = user_recommendations(int(user_id))
if recs.empty:
    st.warning(tr("Este cliente no tiene recomendaciones exportadas.", "This customer has no exported recommendations.")); st.stop()

with header_cols[1]: html_card(tr("Pedidos", "Orders"), f"{int(profile['historical_orders'])}", tr("históricos", "historical"), "accent-violet")
with header_cols[2]: html_card(tr("Frecuencia", "Frequency"), f"{profile['avg_days_between_orders']:.1f} {tr('días', 'days')}", tr("entre pedidos", "between orders"), "accent-teal")
with header_cols[3]: html_card(tr("Prod. / pedido", "Prod. / order"), f"{profile['avg_products_per_order']:.1f}", tr("promedio", "average"), "accent-purple")
with header_cols[4]: html_card(tr("Última compra", "Latest purchase"), f"{tr('Pedido', 'Order')} #{int(profile['last_historical_order_number'])}", tr("corte histórico", "historical cutoff"), "accent-orange")

st.markdown(
    f"<div class='ranking-heading'><h2>{tr('Ranking de los top 20 del cliente', 'Customer Top 20 ranking')}</h2><span>{tr('Cada producto puede abrir sus factores explicativos.', 'Each product can open its explanatory drivers.')}</span></div>",
    unsafe_allow_html=True,
)

def recommendation_origin(row):
    sources = []
    if row.get("source_previous", 0) == 1:
        sources.append(tr("Histórico", "History"))
    if row.get("source_similar_users", 0) == 1:
        sources.append(tr("Vecinos", "Neighbors"))
    if row.get("source_global_popular", 0) == 1:
        sources.append(tr("Popular", "Popularity"))
    return " + ".join(sources) if sources else tr("Modelo", "Model")


show = recs.sort_values("rank").copy()
show["Origen"] = show.apply(recommendation_origin, axis=1)
rows = []
for _, row in show.iterrows():
    score = float(row["propensity_score"])
    band = str(row["propensity_band"])
    band_display = {
        "Alta": tr("Alta", "High"),
        "Media": tr("Media", "Medium"),
        "Baja": tr("Baja", "Low"),
    }.get(band, band)
    url = f"/Factores?user_id={int(user_id)}&product_id={int(row['product_id'])}"
    rows.append(
        f"<tr>"
        f"<td class='ranking-rank'>{int(row['rank'])}</td>"
        f"<td class='ranking-product' title='{escape(str(row['product_name']))}'>{escape(str(row['product_name']))}</td>"
        f"<td><div class='propensity-cell'><span class='propensity-track'><span class='propensity-fill' style='width:{score * 100:.1f}%'></span></span><span class='propensity-value'>{score:.2f}</span></div></td>"
        f"<td class='ranking-origin'>{escape(str(row['Origen']))}</td>"
        f"<td><span class='band-pill {escape(band.lower())}'>{escape(band_display)}</span></td>"
        f"<td><a class='factor-link' href='{url}' target='_self'>{tr('Ver factores', 'View drivers')} ↓</a></td>"
        f"</tr>"
    )

st.markdown(
    "<div class='ranking-table-wrap'>"
    "<table class='ranking-table'>"
    "<colgroup><col style='width:5%'><col style='width:27%'><col style='width:22%'><col style='width:18%'><col style='width:11%'><col style='width:17%'></colgroup>"
    f"<thead><tr><th>#</th><th>{tr('Producto', 'Product')}</th><th>{tr('Propensión', 'Propensity')}</th><th>{tr('Origen', 'Source')}</th><th>{tr('Banda', 'Band')}</th><th>{tr('Factores', 'Drivers')}</th></tr></thead>"
    "<tbody>" + "".join(rows) + "</tbody>"
    "</table>"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(tr("## Posibles acciones promocionales", "## Potential promotional actions"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('Las bandas convierten el score de propensión en una orientación comercial simple: proteger compras que probablemente ocurran de forma orgánica, activar productos con afinidad intermedia y evitar acciones sobre señales débiles.', 'Propensity bands turn the score into simple commercial guidance: protect purchases likely to happen organically, activate products with intermediate affinity, and avoid acting on weak signals.')}
    </div>
    """,
    unsafe_allow_html=True,
)
band_columns = st.columns(3)
for column, (band, css, title, action) in zip(band_columns, [
    ("Alta", "band-high", tr("PROPENSIÓN ALTA · score ≥ 0.60", "HIGH PROPENSITY · score ≥ 0.60"), tr("Probable compra orgánica · evitar descuento innecesario", "Likely organic purchase · avoid unnecessary discount")),
    ("Media", "band-mid", tr("PROPENSIÓN MEDIA · 0.25 ≤ score < 0.60", "MEDIUM PROPENSITY · 0.25 ≤ score < 0.60"), tr("Hay interés / afinidad · potencial zona promocional · recomendar A/B testing para medir uplift", "Interest / affinity detected · potential promotional zone · recommend A/B testing to measure uplift")),
    ("Baja", "band-low", tr("BAJA PROPENSIÓN · score < 0.25", "LOW PROPENSITY · score < 0.25"), tr("Demasiado ruido · no accionar", "Too much noise · do not activate")),
]):
    names = recs.loc[recs.propensity_band.eq(band), "product_name"].dropna().tolist()
    with column:
        band_card(title, names, action, css)


export_cols = ["user_id","product_id","product_name","department","rank","propensity_score","propensity_band"]
out = BytesIO()
recs[export_cols].to_excel(out, index=False, engine="openpyxl")
_, download_col, _ = st.columns([1, 1.25, 1])
with download_col:
    st.download_button(
        tr("Descargar Excel · cliente seleccionado", "Download Excel · selected customer"),
        data=out.getvalue(),
        file_name=f"next_best_product_user_{user_id}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="content",
    )

next_page_link("Factores", "Drivers de propensión", "Propensity drivers")
