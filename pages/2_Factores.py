import pandas as pd
import duckdb
import plotly.express as px
import streamlit as st

from src.data import (
    customer_profiles,
    mba_effectiveness,
    user_recommendations,
)
from src.i18n import tr
from src.style import apply_style, content_header, factor_card, next_page_link, style_plotly
from src.users import customer_selector, user_context

st.set_page_config(page_title=tr("Drivers de propensión", "Propensity drivers"), page_icon="🔎", layout="wide")
apply_style()
content_header(
    tr("Factores que explican la propensión", "Drivers that explain propensity"),
    tr("Señales que explican el interés esperado de cada producto para el cliente seleccionado.", "Signals that explain the expected interest in each product for the selected customer."),
)

profiles = customer_profiles().sort_values("user_id")
user_id = customer_selector(
    profiles,
    tr("Cliente", "Customer"),
    key="drivers_customer_id",
)
user_context(user_id)

recs = user_recommendations(int(user_id)).sort_values("rank")
if recs.empty:
    st.warning(tr("Este cliente no tiene recomendaciones exportadas.", "This customer has no exported recommendations."))
    st.stop()

product_names = recs.product_name.tolist()
requested_product = st.query_params.get("product_id")
requested_product = int(requested_product) if requested_product and requested_product.isdigit() else None
matching_product = recs.loc[recs.product_id.eq(requested_product), "product_name"]
product_index = product_names.index(matching_product.iloc[0]) if not matching_product.empty else 0
selected_name = st.selectbox(tr("Producto a explicar", "Product to explain"), product_names, index=product_index)
r = recs.loc[recs.product_name.eq(selected_name)].iloc[0]

def observed_range(column, decimals=2, percent=False, suffix=""):
    values = pd.to_numeric(recs[column], errors="coerce").dropna()
    if values.empty:
        return tr("Sin rango disponible", "No range available")
    low, high = values.min(), values.max()
    if percent:
        return f"{tr('Mín.–máx. Top 20', 'Top 20 min–max')}: {low:.1%}–{high:.1%}"
    return f"{tr('Mín.–máx. Top 20', 'Top 20 min–max')}: {low:.{decimals}f}–{high:.{decimals}f}{suffix}"


def strength(value, medium_threshold, strong_threshold):
    if pd.isna(value) or value < medium_threshold:
        return "Débil"
    if value < strong_threshold:
        return "Media"
    return "Fuerte"


historical_level = strength(r["user_product_order_share"], 0.20, 0.50)
if r["neighbor_buyers"] == 0 or r["neighbor_similarity_mean"] < 0.25:
    collaborative_level = "Débil"
elif r["neighbor_buyers"] >= 3 and r["neighbor_similarity_mean"] >= 0.45:
    collaborative_level = "Fuerte"
else:
    collaborative_level = "Media"
association_level = strength(r["max_lift_last_basket"], 1.20, 2.00)
penetration_q25 = recs["global_product_penetration"].quantile(0.25)
penetration_q75 = recs["global_product_penetration"].quantile(0.75)
popularity_level = strength(r["global_product_penetration"], penetration_q25, penetration_q75)


due_ratio = f"{r['reorder_due_ratio']:.2f}" if pd.notna(r["reorder_due_ratio"]) else tr("Sin historial suficiente", "Insufficient history")
level_label = {
    "Débil": tr("débil", "weak"),
    "Media": tr("media", "medium"),
    "Fuerte": tr("fuerte", "strong"),
}
factor_columns = st.columns(2, gap="medium")
with factor_columns[0]:
    factor_card(
        tr("1 · Histórico cliente-producto", "1 · Customer-product history"),
        tr("Resume la relación directa entre este cliente y el producto a lo largo de sus compras.", "Summarizes the direct relationship between this customer and product across past purchases."),
        [
            (tr("Pedidos con el producto", "Orders with product"), f"{int(r['user_product_orders'])}", tr("Cantidad de pedidos del cliente que incluyeron este producto.", "Number of the customer's orders that included this product."), observed_range("user_product_orders", 0)),
            ("Share", f"{r['user_product_order_share']:.1%}", tr("Proporción de los pedidos del cliente en los que aparece el producto.", "Share of the customer's orders in which the product appears."), tr("Escala", "Scale") + " 0%–100% · " + observed_range("user_product_order_share", percent=True)),
            (tr("Recencia", "Recency"), f"{r['days_since_user_product']:.0f} {tr('días', 'days')}", tr("Días transcurridos desde la última compra del producto; menor implica una compra más reciente.", "Days since the product was last purchased; lower means more recent."), observed_range("days_since_user_product", 0, suffix=f" {tr('días', 'days')}")),
            ("Due ratio", due_ratio, tr("Compara recencia y cadencia: menor a 1 aún no estaría vencido; cerca de 1 estaría en fecha; mayor a 1 estaría demorado.", "Compares recency with cadence: below 1 is not due yet, near 1 is on time, and above 1 is overdue."), observed_range("reorder_due_ratio")),
        ],
        "#5b45f5",
        (historical_level, tr(f"Relación histórica {historical_level.lower()}: el producto aparece en {r['user_product_order_share']:.1%} de los pedidos del cliente.", f"{level_label[historical_level].capitalize()} historical relationship: the product appears in {r['user_product_order_share']:.1%} of the customer's orders.")),
    )
with factor_columns[1]:
    factor_card(
        tr("2 · Filtrado colaborativo", "2 · Collaborative filtering"),
        tr("Mide cuánto respaldo recibe el producto entre clientes con comportamientos de compra similares.", "Measures how much support the product receives from customers with similar purchasing behavior."),
        [
            (tr("Vecinos compradores", "Buyer neighbors"), f"{int(r['neighbor_buyers'])}", tr("Cantidad de clientes similares que compraron el producto.", "Number of similar customers who purchased the product."), observed_range("neighbor_buyers", 0)),
            (tr("Similitud acumulada", "Cumulative similarity"), f"{r['neighbor_similarity_sum']:.2f}", tr("Suma de las similitudes; aumenta tanto por cantidad como por afinidad de los vecinos.", "Sum of similarities; it increases with both the number and affinity of neighbors."), observed_range("neighbor_similarity_sum")),
            (tr("Similitud máxima", "Maximum similarity"), f"{r['neighbor_similarity_max']:.2f}", tr("Afinidad con el vecino comprador más parecido; cuanto más cerca de 1, mayor similitud.", "Affinity with the closest buyer neighbor; values closer to 1 indicate greater similarity."), tr("Escala", "Scale") + " 0–1 · " + observed_range("neighbor_similarity_max")),
            (tr("Similitud promedio", "Average similarity"), f"{r['neighbor_similarity_mean']:.2f}", tr("Afinidad media de los vecinos compradores; cuanto más cerca de 1, mayor similitud.", "Average affinity among buyer neighbors; values closer to 1 indicate greater similarity."), tr("Escala", "Scale") + " 0–1 · " + observed_range("neighbor_similarity_mean")),
        ],
        "#168f83",
        (collaborative_level, tr(f"Respaldo colaborativo {collaborative_level.lower()}: {int(r['neighbor_buyers'])} vecinos compradores con similitud media de {r['neighbor_similarity_mean']:.2f}.", f"{level_label[collaborative_level].capitalize()} collaborative support: {int(r['neighbor_buyers'])} buyer neighbors with an average similarity of {r['neighbor_similarity_mean']:.2f}.")),
    )

factor_columns = st.columns(2, gap="medium")
with factor_columns[0]:
    factor_card(
        "3 · Market Basket Analysis",
        tr("Evalúa asociaciones entre el producto candidato y los productos recientes o característicos del cliente.", "Evaluates associations between the candidate product and the customer's recent or characteristic products."),
        [
            (tr("Lift máximo", "Maximum lift"), f"{r['max_lift_last_basket']:.2f}x", tr("Fuerza máxima de asociación; 1 es neutral y valores mayores indican afinidad positiva.", "Maximum association strength; 1 is neutral and higher values indicate positive affinity."), observed_range("max_lift_last_basket", suffix="x")),
            (tr("Confidence máxima", "Maximum confidence"), f"{r['max_confidence_last_basket']:.3f}", tr("Probabilidad observada de comprar el candidato cuando aparece el producto asociado.", "Observed probability of buying the candidate when the associated product appears."), tr("Escala", "Scale") + " 0–1 · " + observed_range("max_confidence_last_basket", 3)),
            (tr("Productos asociados", "Associated products"), f"{int(r['count_last_basket_products'])}", tr("Cantidad de productos del último carrito con una asociación detectada.", "Number of products in the latest basket with a detected association."), observed_range("count_last_basket_products", 0)),
        ],
        "#9948e8",
        (association_level, tr(f"Asociación {association_level.lower()}: el lift máximo observado es {r['max_lift_last_basket']:.2f}x.", f"{level_label[association_level].capitalize()} association: the maximum observed lift is {r['max_lift_last_basket']:.2f}x.")),
    )
with factor_columns[1]:
    factor_card(
        tr("4 · Popularidad y cobertura", "4 · Popularity and coverage"),
        tr("Aporta una señal global para productos relevantes incluso cuando el historial individual es limitado.", "Provides a global signal for relevant products even when individual history is limited."),
        [
            (tr("Penetración global", "Global penetration"), f"{r['global_product_penetration']:.1%}", tr("Porcentaje de clientes históricos que compraron el producto.", "Percentage of historical customers who purchased the product."), tr("Escala", "Scale") + " 0%–100% · " + observed_range("global_product_penetration", percent=True)),
            (tr("Compradores únicos", "Unique buyers"), f"{int(r['global_unique_buyers']):,}", tr("Cantidad de clientes distintos que compraron el producto.", "Number of distinct customers who purchased the product."), observed_range("global_unique_buyers", 0)),
            (tr("Compras históricas", "Historical purchases"), f"{int(r['global_purchase_count']):,}", tr("Cantidad total de pedidos históricos que incluyeron el producto.", "Total number of historical orders that included the product."), observed_range("global_purchase_count", 0)),
        ],
        "#c66205",
        (popularity_level, tr(f"Popularidad {popularity_level.lower()}: penetración de {r['global_product_penetration']:.1%} frente al resto del Top 20.", f"{level_label[popularity_level].capitalize()} popularity: {r['global_product_penetration']:.1%} penetration versus the rest of the Top 20.")),
    )

st.markdown(tr("### ¿La señal de asociación entre productos diferencia compras reales?", "### Does the product-association signal distinguish actual purchases?"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('Compara el valor medio de cada señal de asociación entre los productos que finalmente fueron comprados y los que no. Una barra más alta en “Comprado” indica que la señal ayuda a distinguir productos con mayor probabilidad de aparecer en el próximo carrito.', 'Compares the average value of each association signal between products that were eventually purchased and those that were not. A higher “Purchased” bar indicates that the signal helps distinguish products that are more likely to appear in the next basket.')}
    </div>
    """,
    unsafe_allow_html=True,
)
try:
    eff = mba_effectiveness()
    selected_features = [
        "max_lift_last_basket",
        "mean_lift_last_basket",
        "max_lift_core_products",
        "sum_weighted_lift_core_products",
    ]
    eff = eff[eff.feature.isin(selected_features)].copy()
    label_map = {
        "max_lift_last_basket": tr("Lift máximo · último carrito", "Maximum lift · latest basket"),
        "mean_lift_last_basket": tr("Lift medio · último carrito", "Average lift · latest basket"),
        "max_lift_core_products": tr("Lift máximo · productos históricos del cliente", "Maximum lift · customer's historical products"),
        "sum_weighted_lift_core_products": tr("Lift ponderado · productos históricos del cliente", "Weighted lift · customer's historical products"),
    }
    signal_col = tr("Señal", "Signal")
    result_col = tr("Resultado", "Outcome")
    not_bought = tr("No comprado", "Not purchased")
    bought = tr("Comprado", "Purchased")
    eff[signal_col] = eff["feature"].map(label_map)
    eff[result_col] = eff["target"].map({0: not_bought, 1: bought})
    fig = px.bar(
        eff,
        x=signal_col,
        y="mean",
        color=result_col,
        barmode="group",
        text="mean",
        labels={"mean": tr("Valor medio de la señal", "Average signal value")},
        color_discrete_map={not_bought: "#9bcaf3", bought: "#5b45f5"},
        category_orders={result_col: [not_bought, bought]},
    )
    style_plotly(fig)
    fig.update_traces(
        texttemplate="%{y:.2f}",
        textposition="outside",
        textfont=dict(color="#263247", size=11),
        cliponaxis=False,
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:.2f}<extra></extra>",
    )
    max_value = eff["mean"].max()
    fig.update_layout(
        height=440,
        bargap=0.28,
        bargroupgap=0.08,
        barcornerradius=6,
        hoverlabel=dict(bgcolor="#101d32", font_color="#ffffff", font_size=12),
        legend=dict(
            title_text="",
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="right",
            x=1,
            font=dict(color="#354156", size=12),
            bgcolor="rgba(255,255,255,.9)",
        ),
    )
    fig.update_xaxes(title_text="", tickfont=dict(color="#465166", size=11))
    fig.update_yaxes(
        title_text=tr("Valor medio de la señal", "Average signal value"),
        range=[0, max_value * 1.18],
        tickfont=dict(color="#465166", size=11),
        title_font=dict(color="#2f3a4d", size=12),
        gridcolor="#e6eaf0",
    )
    st.plotly_chart(fig, use_container_width=True)
    purchased_mean = eff.loc[eff.target.eq(1), "mean"].mean()
    not_purchased_mean = eff.loc[eff.target.eq(0), "mean"].mean()
    relative_difference = purchased_mean / not_purchased_mean if not_purchased_mean else 0
    st.markdown(
        f"""
        <div class="chart-reading">
          <strong>{tr('Lectura', 'Reading')}:</strong> {tr(f'en promedio, las señales son {relative_difference:.1f} veces mayores en los productos comprados. Esto muestra capacidad para discriminar y ordenar candidatos, pero no implica causalidad.', f'on average, signals are {relative_difference:.1f} times higher for purchased products. This shows an ability to discriminate and rank candidates, but it does not imply causality.')}
        </div>
        """,
        unsafe_allow_html=True,
    )
except (FileNotFoundError, duckdb.InvalidInputException):
    pass

next_page_link("Audiencias", "Activación de audiencias", "Audience activation")
