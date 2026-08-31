from __future__ import annotations

from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data import model_deciles, model_metrics
from src.i18n import tr
from src.style import apply_style, hero, next_page_link, style_plotly


def light_table(data: pd.DataFrame, emphasis_columns: set[str] | None = None) -> str:
    emphasis_columns = emphasis_columns or set()
    headers = "".join(f"<th>{escape(str(column))}</th>" for column in data.columns)
    rows = []
    for _, row in data.iterrows():
        cells = "".join(
            f'<td class="{"table-emphasis" if column in emphasis_columns else ""}">{escape(str(row[column]))}</td>'
            for column in data.columns
        )
        rows.append(f"<tr>{cells}</tr>")
    return f'<div class="light-table-wrap"><table class="light-table"><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

st.set_page_config(page_title=tr("Performance del modelo", "Model performance"), page_icon="📈", layout="wide")
apply_style()
hero(
    tr("¿Qué tan bien funciona el modelo?", "How well does the model perform?"),
    tr("Calidad del ranking personalizado frente a estrategias simples de popularidad y recompra histórica.", "Quality of the personalized ranking versus simple popularity and historical repurchase strategies."),
)

m = model_metrics().sort_values("k").reset_index(drop=True)

st.markdown(tr("## Resultado ejecutivo", "## Executive result"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('Evaluamos si el modelo recupera productos del carrito real y si logra ubicarlos en las primeras posiciones. La comparación se realiza sobre el último pedido de cada cliente, que quedó fuera del entrenamiento y la optimización.', 'We evaluate whether the model recovers products from the actual basket and places them near the top. The comparison uses each customer’s final order, which was excluded from training and optimization.')}
    </div>
    """,
    unsafe_allow_html=True,
)

selected_k = st.select_slider(
    tr("Profundidad del ranking evaluado", "Evaluated ranking depth"),
    options=m["k"].astype(int).tolist(),
    value=20,
    format_func=lambda value: f"Top {value}",
    help=tr("K indica cuántas recomendaciones superiores se consideran para calcular las métricas.", "K indicates how many top recommendations are considered when calculating the metrics."),
)
selected = m.loc[m.k.eq(selected_k)].iloc[0]
previous_columns = {
    "previous_baseline_precision",
    "previous_baseline_recall",
    "previous_baseline_ndcg",
}
has_previous_baseline = previous_columns.issubset(m.columns)
if has_previous_baseline:
    reference_precision = selected.previous_baseline_precision
    reference_recall = selected.previous_baseline_recall
    reference_ndcg = selected.previous_baseline_ndcg
    reference_label = tr("baseline histórico", "historical baseline")
else:
    reference_precision = selected.baseline_precision
    reference_recall = selected.baseline_recall
    reference_ndcg = selected.baseline_ndcg
    reference_label = tr("baseline popularidad", "popularity baseline")

metric_config = [
    ("Precision", selected.precision, selected.baseline_precision, selected.get("previous_baseline_precision", selected.baseline_precision), tr("De cada recomendación mostrada, cuántas terminaron comprándose.", "How many displayed recommendations were eventually purchased."), "#5b45f5", True),
    ("Recall", selected.recall, selected.baseline_recall, selected.get("previous_baseline_recall", selected.baseline_recall), tr("Del carrito real, cuánto logró recuperar el modelo.", "How much of the actual basket the model recovered."), "#168f83", True),
    ("NDCG", selected.ndcg, selected.baseline_ndcg, selected.get("previous_baseline_ndcg", selected.baseline_ndcg), tr("Qué tan arriba quedaron los productos realmente comprados.", "How highly the actually purchased products were ranked."), "#9948e8", False),
]

comparison_cards = []
for name, model_value, popularity_value, historical_value, note, color, as_percent in metric_config:
    popularity_lift = model_value / popularity_value
    historical_lift = model_value / historical_value
    value_text = f"{model_value:.1%}" if as_percent else f"{model_value:.3f}"
    popularity_text = f"{popularity_value:.1%}" if as_percent else f"{popularity_value:.3f}"
    historical_text = f"{historical_value:.1%}" if as_percent else f"{historical_value:.3f}"
    popularity_difference = f"+{model_value - popularity_value:.1%}" if as_percent else f"+{model_value - popularity_value:.3f}"
    historical_difference = f"+{model_value - historical_value:.1%}" if as_percent else f"+{model_value - historical_value:.3f}"
    comparison_cards.append(
        f"""
        <article class="metric-comparison-card" style="--metric-color:{color}">
          <div class="metric-comparison-top">
            <span>{name}@{selected_k}</span>
            <div class="metric-lift-badges">
              <b class="popularity">{popularity_lift:.2f}× {tr('popularidad', 'popularity')}</b>
              <b>{historical_lift:.2f}× {tr('histórico', 'historical')}</b>
            </div>
          </div>
          <div class="metric-comparison-value">{value_text}</div>
          <div class="metric-comparison-baselines">
            <div class="metric-comparison-baseline"><span>{tr('Baseline popularidad', 'Popularity baseline')} {popularity_text}</span><strong>{popularity_difference}</strong></div>
            <div class="metric-comparison-baseline history"><span>{tr('Baseline histórico', 'Historical baseline')} {historical_text}</span><strong>{historical_difference}</strong></div>
          </div>
          <p>{note}</p>
        </article>
        """
    )
st.html(f'<div class="metric-comparison-grid">{"".join(comparison_cards)}</div>')

precision_lift = selected.precision / reference_precision
recall_lift = selected.recall / reference_recall
ndcg_lift = selected.ndcg / reference_ndcg
st.html(
    f"""
    <div class="metric-success-callout">
      <div class="metric-success-icon">✓</div>
      <div><span>{tr('¿Por qué es un buen resultado?', 'Why is this a strong result?')}</span>
        <strong>{tr('El modelo híbrido supera incluso a una regla histórica personalizada.', 'The hybrid model outperforms even a personalized historical rule.')}</strong>
        <p>{tr(f'En el Top {selected_k}, frente al baseline histórico obtiene {precision_lift:.2f}× la precisión, {recall_lift:.2f}× el recall y {ndcg_lift:.2f}× el NDCG. La mejora proviene de combinar el historial propio con vecinos similares, popularidad y asociaciones entre productos, incorporando oportunidades que una regla de recompra no puede descubrir.', f'At Top {selected_k}, versus the historical baseline it achieves {precision_lift:.2f}× precision, {recall_lift:.2f}× recall, and {ndcg_lift:.2f}× NDCG. The gain comes from combining each customer’s history with similar neighbors, popularity, and product associations, uncovering opportunities a repurchase rule cannot discover.')}</p>
      </div>
    </div>
    """
)

st.markdown(tr("## Cómo se construye la mejora", "## How the improvement is built"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('La comparación no enfrenta al modelo únicamente contra una referencia débil. Cada nivel incorpora más información: primero demanda general, luego comportamiento individual y finalmente señales colaborativas e híbridas.', 'The comparison does not test the model only against a weak reference. Each level adds more information: first general demand, then individual behavior, and finally collaborative and hybrid signals.')}
    </div>
    """,
    unsafe_allow_html=True,
)

historical_precision = selected.get("previous_baseline_precision", selected.baseline_precision)
historical_recall = selected.get("previous_baseline_recall", selected.baseline_recall)
historical_ndcg = selected.get("previous_baseline_ndcg", selected.baseline_ndcg)
hybrid_gain = selected.ndcg / historical_ndcg - 1
st.html(
    f"""
    <div class="model-progression">
      <article class="progression-step" style="--progress-color:#758092">
        <div class="progression-number">01 · {tr('Punto de partida', 'Starting point')}</div>
        <div class="progression-title">{tr('Baseline de popularidad', 'Popularity baseline')}</div>
        <div class="progression-level">{tr('Demanda global · sin personalización', 'Global demand · no personalization')}</div>
        <p>{tr('Recomienda los mismos productos populares a todos los clientes. Aporta cobertura, pero ignora preferencias individuales.', 'Recommends the same popular products to every customer. It provides coverage but ignores individual preferences.')}</p>
        <div class="progression-metrics"><span>Precision<b>{selected.baseline_precision:.1%}</b></span><span>Recall<b>{selected.baseline_recall:.1%}</b></span><span>NDCG<b>{selected.baseline_ndcg:.3f}</b></span></div>
      </article>
      <div class="progression-arrow"><b>→</b><span>{tr('Agrega historial individual', 'Adds individual history')}</span></div>
      <article class="progression-step" style="--progress-color:#168f83">
        <div class="progression-number">02 · {tr('Personalización básica', 'Basic personalization')}</div>
        <div class="progression-title">{tr('Baseline histórico', 'Historical baseline')}</div>
        <div class="progression-level">{tr('Frecuencia + recencia de recompra', 'Repurchase frequency + recency')}</div>
        <p>{tr('Ordena los productos que cada cliente ya compró. Es una referencia fuerte, aunque sólo puede repetir relaciones conocidas.', 'Ranks products each customer already purchased. It is a strong reference, although it can only repeat known relationships.')}</p>
        <div class="progression-metrics"><span>Precision<b>{historical_precision:.1%}</b></span><span>Recall<b>{historical_recall:.1%}</b></span><span>NDCG<b>{historical_ndcg:.3f}</b></span></div>
      </article>
      <div class="progression-arrow"><b>→</b><span>{tr('Suma vecinos y señales híbridas', 'Adds neighbors and hybrid signals')}</span></div>
      <article class="progression-step hybrid" style="--progress-color:#5b45f5">
        <div class="progression-number">03 · {tr('Modelo final', 'Final model')}</div>
        <div class="progression-title">{tr('Modelo híbrido LightGBM', 'Hybrid LightGBM model')}</div>
        <div class="progression-level">{tr('Historial + KNN + popularidad + asociaciones', 'History + KNN + popularity + associations')}</div>
        <p>{tr('Combina la recompra con productos elegidos por vecinos similares y relaciones de canasta. Así descubre afinidades más allá del historial directo.', 'Combines repurchase with products selected by similar neighbors and basket relationships, discovering affinity beyond direct history.')}</p>
        <div class="progression-metrics"><span>Precision<b>{selected.precision:.1%}</b></span><span>Recall<b>{selected.recall:.1%}</b></span><span>NDCG<b>{selected.ndcg:.3f}</b></span></div>
        <div class="progression-gain">+{hybrid_gain:.1%} NDCG {tr('vs. histórico', 'vs. historical')}</div>
      </article>
    </div>
    """
)

st.markdown(tr("## ¿Contra qué baselines se compara?", "## Which baselines are used for comparison?"))
baseline_columns = st.columns(2, gap="medium")
with baseline_columns[0]:
    st.html(
        f"""
        <div class="baseline-card">
          <div class="baseline-kicker">{tr('Baseline de popularidad', 'Popularity baseline')}</div>
          <div class="baseline-title">{tr('La misma lista para todos', 'The same list for everyone')}</div>
          <p>{tr('Ordena los productos por compradores únicos y cantidad de compras históricas. Luego recomienda el mismo Top K global a cada cliente.', 'Ranks products by unique buyers and historical purchase count, then recommends the same global Top K to every customer.')}</p>
          <div class="baseline-rule">{tr('Sin personalización', 'No personalization')}</div>
        </div>
        """
    )
with baseline_columns[1]:
    st.html(
        f"""
        <div class="baseline-card baseline-card-history">
          <div class="baseline-kicker">{tr('Baseline de recompra histórica', 'Historical repurchase baseline')}</div>
          <div class="baseline-title">{tr('Los favoritos de cada cliente', 'Each customer’s favorites')}</div>
          <p>{tr('Recomienda los productos ya comprados por el cliente, ordenados por frecuencia histórica y, ante empate, por la compra más reciente.', 'Recommends products previously purchased by the customer, ranked by historical frequency and then most recent purchase.')}</p>
          <div class="baseline-rule">{tr('Personalizado · sin Machine Learning', 'Personalized · no Machine Learning')}</div>
          {'' if has_previous_baseline else f'<div class="baseline-pending">{tr("Disponible al reexportar la notebook", "Available after re-exporting the notebook")}</div>'}
        </div>
        """
    )

st.html(
    f"""
    <div class="baseline-explanation baseline-explanation-wide">
      <div><span>01</span><p><b>{tr('Dos niveles de dificultad', 'Two difficulty levels')}</b>{tr('Popularidad prueba contra una lista general; recompra histórica prueba contra una regla personalizada fuerte.', 'Popularity tests against a general list; historical repurchase tests against a strong personalized rule.')}</p></div>
      <div><span>02</span><p><b>{tr('Comparación justa', 'Fair comparison')}</b>{tr('Todos utilizan los mismos clientes, el mismo pedido objetivo y la misma cantidad de recomendaciones.', 'All approaches use the same customers, target order, and number of recommendations.')}</p></div>
      <div><span>03</span><p><b>{tr('Sin información futura', 'No future information')}</b>{tr('Ambos baselines se construyen exclusivamente con compras anteriores al pedido de Test.', 'Both baselines use only purchases made before the Test order.')}</p></div>
      <div><span>04</span><p><b>{tr('Valor incremental', 'Incremental value')}</b>{tr('Superar la recompra histórica demuestra que el modelo agrega valor más allá de repetir favoritos conocidos.', 'Beating historical repurchase shows that the model adds value beyond repeating known favorites.')}</p></div>
    </div>
    """
)

st.markdown(f"## {tr('Modelo híbrido vs. los dos baselines', 'Hybrid model vs. both baselines')} · Top {selected_k}")
metric_col = tr("Métrica", "Metric")
model_col = tr("Modelo personalizado", "Personalized model")
popularity_col = tr("Baseline popularidad", "Popularity baseline")
chart_data = pd.DataFrame(
    {
        metric_col: ["Precision", "Recall", "NDCG"],
        model_col: [selected.precision, selected.recall, selected.ndcg],
        popularity_col: [selected.baseline_precision, selected.baseline_recall, selected.baseline_ndcg],
    }
)
fig = go.Figure()
fig.add_bar(name=model_col, x=chart_data[metric_col], y=chart_data[model_col], marker_color="#5b45f5", text=chart_data[model_col], texttemplate="%{text:.1%}", textposition="outside")
fig.add_bar(name=popularity_col, x=chart_data[metric_col], y=chart_data[popularity_col], marker_color="#aeb7c5", text=chart_data[popularity_col], texttemplate="%{text:.1%}", textposition="outside")
if has_previous_baseline:
    previous_values = [
        selected.previous_baseline_precision,
        selected.previous_baseline_recall,
        selected.previous_baseline_ndcg,
    ]
    fig.add_bar(
        name=tr("Baseline productos históricos", "Historical products baseline"),
        x=chart_data[metric_col],
        y=previous_values,
        marker_color="#168f83",
        text=previous_values,
        texttemplate="%{text:.1%}",
        textposition="outside",
    )
style_plotly(fig)
fig.update_layout(barmode="group", height=390, bargap=0.32, bargroupgap=0.08, legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1), hoverlabel=dict(bgcolor="#101d32", font_color="#ffffff"))
fig.update_traces(cliponaxis=False, hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:.3f}<extra></extra>")
fig.update_yaxes(title=tr("Valor de la métrica", "Metric value"), tickformat=".0%", range=[0, chart_data[model_col].max() * 1.22], gridcolor="#e6eaf0")
fig.update_xaxes(title="")
st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

st.markdown(tr("## Cómo interpretar cada métrica", "## How to interpret each metric"))
interpretation_cards = [
    ("Precision@K", tr("¿Cuántas recomendaciones acertó?", "How many recommendations were correct?"), tr("Hits dentro del Top K ÷ cantidad de recomendaciones.", "Hits within Top K ÷ number of recommendations."), tr(f"En Top {selected_k}, aproximadamente {selected.precision:.1%} de los productos recomendados aparecen en el carrito real, frente a {reference_precision:.1%} del {reference_label}.", f"At Top {selected_k}, about {selected.precision:.1%} of recommended products appear in the actual basket, versus {reference_precision:.1%} for the {reference_label}."), tr("Es importante cuando cada contacto, espacio o incentivo tiene un costo y se busca evitar recomendaciones irrelevantes.", "It matters when every contact, placement, or incentive has a cost and irrelevant recommendations should be avoided."), "#5b45f5"),
    ("Recall@K", tr("¿Cuánto del carrito recuperó?", "How much of the basket was recovered?"), tr("Hits dentro del Top K ÷ productos reales comprados.", "Hits within Top K ÷ products actually purchased."), tr(f"En Top {selected_k}, el modelo recupera {selected.recall:.1%} del carrito real, frente a {reference_recall:.1%} del {reference_label}.", f"At Top {selected_k}, the model recovers {selected.recall:.1%} of the actual basket, versus {reference_recall:.1%} for the {reference_label}."), tr("Es valioso para lograr cobertura: reduce la cantidad de compras probables que quedan fuera de la selección.", "It is valuable for coverage because it reduces the number of likely purchases left outside the selection."), "#168f83"),
    ("NDCG@K", tr("¿Los aciertos quedaron arriba?", "Were the correct items ranked near the top?"), tr("Ganancia acumulada con descuento según la posición.", "Discounted cumulative gain based on position."), tr(f"El valor {selected.ndcg:.3f} indica una calidad de orden {ndcg_lift:.1f} veces superior al {reference_label} de {reference_ndcg:.3f}.", f"The value {selected.ndcg:.3f} indicates ordering quality {ndcg_lift:.1f} times higher than the {reference_label} at {reference_ndcg:.3f}."), tr("Es la métrica central del recomendador porque no sólo exige acertar: premia que los productos relevantes aparezcan primero.", "It is the recommender’s central metric because it rewards not only correctness, but placing relevant products first."), "#9948e8"),
]
interpretation_html = "".join(
    f"""
    <article class="metric-definition-card" style="--metric-color:{color}">
      <div class="metric-definition-name">{name}</div><div class="metric-definition-question">{question}</div>
      <div class="metric-definition-formula">{formula}</div>
      <p><b>{tr('Lectura actual.', 'Current reading.')}</b> {reading}</p><p><b>{tr('Por qué importa.', 'Why it matters.')}</b> {importance}</p>
    </article>
    """
    for name, question, formula, reading, importance, color in interpretation_cards
)
st.html(f'<div class="metric-definition-grid">{interpretation_html}</div>')

st.markdown(tr("## Comportamiento según la profundidad del ranking", "## Behavior by ranking depth"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('Un ranking corto concentra más aciertos y favorece Precision. Al ampliar K se recupera una mayor parte del carrito y aumenta Recall. NDCG permite verificar que el orden conserve calidad durante ese intercambio.', 'A short ranking concentrates more hits and favors Precision. Increasing K recovers more of the basket and raises Recall. NDCG verifies that ordering quality is preserved through this tradeoff.')}
    </div>
    """,
    unsafe_allow_html=True,
)
comparison = m.copy()
if has_previous_baseline:
    comparison["Lift Precision"] = comparison.precision / comparison.previous_baseline_precision
    comparison["Lift Recall"] = comparison.recall / comparison.previous_baseline_recall
    comparison["Lift NDCG"] = comparison.ndcg / comparison.previous_baseline_ndcg
else:
    comparison["Lift Precision"] = comparison.precision / comparison.baseline_precision
    comparison["Lift Recall"] = comparison.recall / comparison.baseline_recall
    comparison["Lift NDCG"] = comparison.ndcg / comparison.baseline_ndcg
comparison_columns = ["k", "precision", "recall", "ndcg", "baseline_precision", "baseline_recall", "baseline_ndcg"]
if has_previous_baseline:
    comparison_columns += ["previous_baseline_precision", "previous_baseline_recall", "previous_baseline_ndcg"]
comparison_columns += ["Lift Precision", "Lift Recall", "Lift NDCG"]
model_precision = tr("Precision modelo", "Model Precision")
model_recall = tr("Recall modelo", "Model Recall")
model_ndcg = tr("NDCG modelo", "Model NDCG")
popularity_precision = tr("Precision popularidad", "Popularity Precision")
popularity_recall = tr("Recall popularidad", "Popularity Recall")
popularity_ndcg = tr("NDCG popularidad", "Popularity NDCG")
repurchase_precision = tr("Precision recompra", "Repurchase Precision")
repurchase_recall = tr("Recall recompra", "Repurchase Recall")
repurchase_ndcg = tr("NDCG recompra", "Repurchase NDCG")
comparison = comparison[comparison_columns].rename(columns={
    "k": "Top K",
    "precision": model_precision,
    "recall": model_recall,
    "ndcg": model_ndcg,
    "baseline_precision": popularity_precision,
    "baseline_recall": popularity_recall,
    "baseline_ndcg": popularity_ndcg,
    "previous_baseline_precision": repurchase_precision,
    "previous_baseline_recall": repurchase_recall,
    "previous_baseline_ndcg": repurchase_ndcg,
})
for column in [model_precision, model_recall, popularity_precision, popularity_recall]:
    comparison[column] = comparison[column].map(lambda value: f"{value:.1%}")
for column in [model_ndcg, popularity_ndcg]:
    comparison[column] = comparison[column].map(lambda value: f"{value:.3f}")
if has_previous_baseline:
    comparison[repurchase_precision] = comparison[repurchase_precision].map(lambda value: f"{value:.1%}")
    comparison[repurchase_recall] = comparison[repurchase_recall].map(lambda value: f"{value:.1%}")
    comparison[repurchase_ndcg] = comparison[repurchase_ndcg].map(lambda value: f"{value:.3f}")
for column in ["Lift Precision", "Lift Recall", "Lift NDCG"]:
    comparison[column] = comparison[column].map(lambda value: f"{value:.2f}×")
lift_labels = {
    "Lift Precision": tr("Lift Precision vs. histórico", "Precision lift vs. historical"),
    "Lift Recall": tr("Lift Recall vs. histórico", "Recall lift vs. historical"),
    "Lift NDCG": tr("Lift NDCG vs. histórico", "NDCG lift vs. historical"),
}
comparison = comparison.rename(columns=lift_labels)
st.html(light_table(comparison, set(lift_labels.values())))

st.markdown(tr("## Poder de discriminación por deciles", "## Discrimination power by decile"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('Ordenamos todas las combinaciones cliente-producto de Validation desde el score más alto hasta el más bajo y las dividimos en diez grupos iguales. Si el modelo discrimina correctamente, las compras reales deben concentrarse en los primeros deciles.', 'We rank all customer-product pairs in Validation from highest to lowest score and divide them into ten equal groups. If the model discriminates correctly, actual purchases should concentrate in the first deciles.')}
    </div>
    """,
    unsafe_allow_html=True,
)
deciles = model_deciles().sort_values("decile").reset_index(drop=True)
base_positive_rate = deciles.positives.sum() / deciles.observations.sum()
deciles["cumulative_capture"] = deciles.positives.cumsum() / deciles.positives.sum()
top_decile = deciles.iloc[0]
top_two_capture = deciles.iloc[1].cumulative_capture

decile_summary = [
    (tr("Tasa promedio", "Average rate"), f"{base_positive_rate:.1%}", tr("Compra real en toda la base", "Actual purchase across the full base"), "#687386"),
    (tr("Primer decil", "First decile"), f"{top_decile.positive_rate:.1%}", tr("Compra real entre los scores más altos", "Actual purchase among the highest scores"), "#5b45f5"),
    (tr("Lift del primer decil", "First-decile lift"), f"{top_decile.lift:.2f}×", tr("Veces sobre la tasa promedio", "Times the average rate"), "#168f83"),
    (tr("Captura Top 20%", "Top 20% capture"), f"{top_two_capture:.1%}", tr("Compras positivas en dos deciles", "Positive purchases in two deciles"), "#9948e8"),
]
decile_cards = "".join(
    f'<article class="decile-summary-card" style="--decile-color:{color}"><span>{label}</span><strong>{value}</strong><p>{note}</p></article>'
    for label, value, note, color in decile_summary
)
st.html(f'<div class="decile-summary-grid">{decile_cards}</div>')
st.html(
    f"""
    <div class="decile-reading"><strong>{tr('Lectura principal', 'Key reading')}:</strong> {tr(f'el 10% de pares con mayor score concentra {top_decile.cumulative_capture:.1%} de todas las compras positivas y presenta una tasa de compra de {top_decile.positive_rate:.1%}, frente al promedio general de {base_positive_rate:.1%}. Esto confirma que el modelo concentra correctamente las oportunidades más probables en la parte superior del ranking.', f'the top-scoring 10% of pairs concentrates {top_decile.cumulative_capture:.1%} of all positive purchases and has a purchase rate of {top_decile.positive_rate:.1%}, versus the overall average of {base_positive_rate:.1%}. This confirms that the model correctly concentrates the most likely opportunities at the top of the ranking.')}</div>
    """
)

decile_fig = go.Figure(
    go.Bar(
        x=[f"{tr('Decil', 'Decile')} {int(value)}" for value in deciles.decile],
        y=deciles.lift,
        marker_color=["#5b45f5", "#8b7df8"] + ["#cfd5df"] * 8,
        text=deciles.lift,
        texttemplate="%{text:.2f}×",
        textposition="outside",
        customdata=deciles[["positive_rate", "cumulative_capture"]],
        hovertemplate=f"<b>%{{x}}</b><br>Lift: %{{y:.2f}}×<br>{tr('Tasa de compra', 'Purchase rate')}: %{{customdata[0]:.1%}}<br>{tr('Captura acumulada', 'Cumulative capture')}: %{{customdata[1]:.1%}}<extra></extra>",
    )
)
style_plotly(decile_fig)
decile_fig.add_hline(y=1, line_dash="dash", line_color="#c66205", annotation_text=tr("Promedio de la base · 1×", "Base average · 1×"), annotation_position="top right")
decile_fig.update_layout(height=400, showlegend=False, bargap=0.25)
decile_fig.update_xaxes(title=tr("Mayor score → menor score", "Higher score → lower score"), tickfont=dict(size=10))
decile_fig.update_yaxes(title=tr("Lift sobre la tasa promedio", "Lift over average rate"), range=[0, deciles.lift.max() * 1.2], gridcolor="#e6eaf0")
decile_fig.update_traces(cliponaxis=False)
st.plotly_chart(decile_fig, use_container_width=True, config={"displaylogo": False})

decile_table = deciles.copy()
decile_col = tr("Decil", "Decile")
pairs_col = tr("Pares evaluados", "Pairs evaluated")
purchases_col = tr("Compras reales", "Actual purchases")
purchase_rate_col = tr("Tasa de compra", "Purchase rate")
avg_score_col = tr("Score promedio", "Average score")
capture_col = tr("Captura acumulada", "Cumulative capture")
decile_table[decile_col] = decile_table.decile.map(lambda value: f"{decile_col} {int(value)}")
decile_table[pairs_col] = decile_table.observations.map(lambda value: f"{int(value):,}")
decile_table[purchases_col] = decile_table.positives.map(lambda value: f"{int(value):,}")
decile_table[purchase_rate_col] = decile_table.positive_rate.map(lambda value: f"{value:.2%}")
decile_table[avg_score_col] = decile_table.avg_probability.map(lambda value: f"{value:.1%}")
decile_table["Lift"] = decile_table.lift.map(lambda value: f"{value:.2f}×")
decile_table[capture_col] = decile_table.cumulative_capture.map(lambda value: f"{value:.1%}")
decile_display = decile_table[[decile_col, pairs_col, purchases_col, purchase_rate_col, avg_score_col, "Lift", capture_col]]
st.html(light_table(decile_display, {"Lift", capture_col}))
st.caption(
    tr(
        "Decil 1 = 10% de combinaciones con mayor score. Decil 10 = 10% con menor score. Una compra positiva significa que el cliente compró ese producto en el pedido objetivo de Validation.",
        "Decile 1 = the 10% of pairs with the highest score. Decile 10 = the 10% with the lowest score. A positive purchase means the customer bought that product in the Validation target order.",
    )
)

st.html(
    f"""
    <div class="metric-caveat"><strong>{tr('Lectura responsable', 'Responsible reading')}:</strong> {tr('estas métricas prueban calidad predictiva y de ranking sobre Test. No prueban que una promoción cause compras adicionales; el uplift debe medirse posteriormente mediante A/B testing.', 'these metrics demonstrate predictive and ranking quality on Test. They do not prove that a promotion causes additional purchases; uplift must be measured later through A/B testing.')}</div>
    """
)

next_page_link("", "Volver a Inicio", "Back to Home")
